 Usage:
# Local → Production
python utils/data/migrate_database.py --mode local_to_prod

# Production → Local  
python utils/data/migrate_database.py --mode prod_to_local

# Sync (merge both, newest wins)
python utils/data/migrate_database.py --mode sync