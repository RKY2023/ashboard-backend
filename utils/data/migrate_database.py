"""
Database Migration Script
=========================
Migrate data between local SQLite and production PostgreSQL databases.

Usage:
    python utils/data/migrate_database.py --mode [local_to_prod|prod_to_local|sync]

Modes:
    local_to_prod  : Migrate data from local SQLite to production PostgreSQL
    prod_to_local  : Migrate data from production PostgreSQL to local SQLite
    sync           : Sync data (merge changes from both databases)
"""

import os
import sys
import django
import argparse
from pathlib import Path
from django.core import serializers
from django.apps import apps
from django.db import connections
from django.conf import settings

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogs.settings')


def setup_databases(mode):
    """Configure database connections based on migration mode"""
    from django.conf import settings

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')

    if mode in ['local_to_prod', 'prod_to_local', 'sync']:
        # Configure both databases
        import dj_database_url

        prod_db_url = os.getenv('DATABASE_URL', '')
        if not prod_db_url:
            raise ValueError("DATABASE_URL not found in environment variables. Please set it in .env file.")

        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': project_root / 'db.sqlite3',
            },
            'production': dj_database_url.parse(prod_db_url, conn_max_age=600, ssl_require=True)
        }

        # Swap default based on mode
        if mode == 'prod_to_local':
            settings.DATABASES['default'], settings.DATABASES['production'] = \
                settings.DATABASES['production'], settings.DATABASES['default']

    django.setup()


def get_models_to_migrate():
    """Get list of models to migrate (excluding built-in Django models)"""
    exclude_apps = ['contenttypes', 'auth', 'admin', 'sessions', 'silk', 'authtoken']
    models = []

    for app_config in apps.get_app_configs():
        if app_config.name.split('.')[-1] not in exclude_apps and not app_config.name.startswith('django'):
            models.extend(app_config.get_models())

    # Sort models by dependencies (foreign keys)
    sorted_models = []
    model_deps = {}

    for model in models:
        deps = []
        for field in model._meta.get_fields():
            if field.is_relation and field.related_model and field.related_model in models:
                deps.append(field.related_model)
        model_deps[model] = deps

    # Simple topological sort
    while model_deps:
        # Find models with no dependencies
        no_deps = [m for m, deps in model_deps.items() if not deps]
        if not no_deps:
            # Circular dependency - just take remaining models
            no_deps = list(model_deps.keys())

        sorted_models.extend(no_deps)
        for m in no_deps:
            del model_deps[m]

        # Remove resolved dependencies
        for m in model_deps:
            model_deps[m] = [d for d in model_deps[m] if d not in no_deps]

    return sorted_models


def migrate_local_to_prod():
    """Migrate data from local SQLite to production PostgreSQL"""
    print("\n" + "=" * 70)
    print("MIGRATING: Local SQLite → Production PostgreSQL")
    print("=" * 70 + "\n")

    models = get_models_to_migrate()

    for model in models:
        model_name = f"{model._meta.app_label}.{model.__name__}"
        print(f"Migrating {model_name}...", end=" ")

        try:
            # Get data from local (default)
            local_data = model.objects.using('default').all()
            count = local_data.count()

            if count == 0:
                print("(no data)")
                continue

            # Serialize and deserialize to production
            serialized = serializers.serialize('json', local_data)

            # Delete existing data in production
            model.objects.using('production').all().delete()

            # Load into production
            for obj in serializers.deserialize('json', serialized):
                obj.save(using='production')

            print(f"✅ {count} records migrated")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

    print("\n" + "=" * 70)
    print("✅ Migration completed: Local → Production")
    print("=" * 70)


def migrate_prod_to_local():
    """Migrate data from production PostgreSQL to local SQLite"""
    print("\n" + "=" * 70)
    print("MIGRATING: Production PostgreSQL → Local SQLite")
    print("=" * 70 + "\n")

    models = get_models_to_migrate()

    for model in models:
        model_name = f"{model._meta.app_label}.{model.__name__}"
        print(f"Migrating {model_name}...", end=" ")

        try:
            # Get data from production (now default due to swap)
            prod_data = model.objects.using('default').all()
            count = prod_data.count()

            if count == 0:
                print("(no data)")
                continue

            # Serialize and deserialize to local
            serialized = serializers.serialize('json', prod_data)

            # Delete existing data in local
            model.objects.using('production').all().delete()

            # Load into local
            for obj in serializers.deserialize('json', serialized):
                obj.save(using='production')

            print(f"✅ {count} records migrated")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

    print("\n" + "=" * 70)
    print("✅ Migration completed: Production → Local")
    print("=" * 70)


def sync_databases():
    """Sync data between local and production (merge based on updated_at)"""
    print("\n" + "=" * 70)
    print("SYNCING: Local SQLite ↔ Production PostgreSQL")
    print("=" * 70 + "\n")

    models = get_models_to_migrate()

    for model in models:
        model_name = f"{model._meta.app_label}.{model.__name__}"
        print(f"Syncing {model_name}...", end=" ")

        try:
            # Check if model has updated_at field
            has_updated_at = hasattr(model, 'updated_at')

            local_data = list(model.objects.using('default').all())
            prod_data = list(model.objects.using('production').all())

            if not local_data and not prod_data:
                print("(no data)")
                continue

            # Create dictionaries for faster lookup
            local_dict = {obj.pk: obj for obj in local_data}
            prod_dict = {obj.pk: obj for obj in prod_data}

            synced = 0

            # Sync from local to prod
            for pk, local_obj in local_dict.items():
                if pk not in prod_dict:
                    # New in local, copy to prod
                    serialized = serializers.serialize('json', [local_obj])
                    for obj in serializers.deserialize('json', serialized):
                        obj.object.pk = pk
                        obj.save(using='production')
                    synced += 1
                elif has_updated_at:
                    # Compare timestamps
                    prod_obj = prod_dict[pk]
                    if local_obj.updated_at > prod_obj.updated_at:
                        # Local is newer
                        serialized = serializers.serialize('json', [local_obj])
                        for obj in serializers.deserialize('json', serialized):
                            obj.object.pk = pk
                            obj.save(using='production')
                        synced += 1

            # Sync from prod to local
            for pk, prod_obj in prod_dict.items():
                if pk not in local_dict:
                    # New in prod, copy to local
                    serialized = serializers.serialize('json', [prod_obj])
                    for obj in serializers.deserialize('json', serialized):
                        obj.object.pk = pk
                        obj.save(using='default')
                    synced += 1
                elif has_updated_at:
                    # Compare timestamps
                    local_obj = local_dict[pk]
                    if prod_obj.updated_at > local_obj.updated_at:
                        # Prod is newer
                        serialized = serializers.serialize('json', [prod_obj])
                        for obj in serializers.deserialize('json', serialized):
                            obj.object.pk = pk
                            obj.save(using='default')
                        synced += 1

            print(f"✅ {synced} records synced")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

    print("\n" + "=" * 70)
    print("✅ Sync completed")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='Migrate data between local and production databases',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python utils/data/migrate_database.py --mode local_to_prod
  python utils/data/migrate_database.py --mode prod_to_local
  python utils/data/migrate_database.py --mode sync
        """
    )

    parser.add_argument(
        '--mode',
        choices=['local_to_prod', 'prod_to_local', 'sync'],
        required=True,
        help='Migration mode'
    )

    args = parser.parse_args()

    # Setup databases
    setup_databases(args.mode)

    # Execute migration based on mode
    if args.mode == 'local_to_prod':
        migrate_local_to_prod()
    elif args.mode == 'prod_to_local':
        migrate_prod_to_local()
    elif args.mode == 'sync':
        sync_databases()


if __name__ == '__main__':
    main()
