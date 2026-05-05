# ashboard-backend

## Development
https://dev.ashback.rajkumaryd.in/


## Project Overview

This is a Django REST Framework backend for a personal dashboard system featuring diary entries, expense tracking, and more. The project uses Django 5.2.4 with DRF and is deployed on Vercel with PostgreSQL (development uses SQLite).

**Main project name**: `blogs` (Django project root)

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

- **[Documentation Index](docs/README.md)** - Complete documentation hub
- **[Diary Entry Module](docs/dairyentry/)** - Personal diary, timeline events, food tracking
- **[Expenses Module](docs/expenses/)** - Expense tracking and financial management
- **[API Documentation](docs/api/)** - API conversion notes and export endpoints
- **[Utilities](docs/utils/)** - Migration and deployment guides
- **[Swagger UI](http://localhost:8000/api/schema/swagger-ui/)** - Interactive API documentation (local)

## Commands

### Setup and Development
```bash
# Activate virtual environment (if not already activated)
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/Mac

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Create new migrations after model changes
python manage.py makemigrations

# Run specific app migrations
python manage.py migrate <app_name>
```

### Testing and Utilities
```bash
# Check for problems in project
python manage.py check

# Open Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

## Architecture

### Database Configuration
- **Local development**: SQLite (`db.sqlite3`)
- **Production (Vercel)**: PostgreSQL via `dj-database-url`
- Database switching is controlled by `VERCEL` environment variable in `blogs/settings.py:111-124`

### Custom User Model
- Custom user model: `user.User` (extends `AbstractUser`)
- Configured via `AUTH_USER_MODEL = 'user.User'` in settings
- Login is **email + password** (`user/views.py:LoginView`); the same field also accepts a mobile number
- JWT auth via `rest_framework_simplejwt` — see `/api/token/`, `/api/token/refresh/`, `/api/token/verify/`

### Model Patterns

#### Abstract Models
The `commoninfo` app defines abstract base models:
- `CommonInfo`: Provides `created_at` and `updated_at` fields
- Used for shared timestamp fields across models
- Models can inherit from multiple abstract models (see `TestChildAbstract`)

#### Custom Managers and QuerySets
The `Order` model uses custom manager pattern:
- `OrderQuerySet`: Provides query methods like `approved()`, `locked()`, `approvable_by(user)`, `lockable_by(user)`
- `OrderManager`: Exposes queryset methods at manager level
- Custom permissions: `can_approve`, `can_lock` defined in Order Meta

### Apps Structure

**Core business apps**:
- `user` - Custom user model with email/mobile-based JWT login
- `userprofile` - User profile information
- `dairyentry` - Diary entries, timeline events, food routine, tags, attachments (mounted at `/diaryentry/` and `/api/diaryentry/`)
- `expenses` - Bank statement upload + parsing, transactions, expense categorisation
- `vendor` - Vendor management (linked to User via ForeignKey)
- `product` - Product catalog
- `order` - Order and OrderItem models with custom manager

**Geographical data apps**:
- `region`, `state`, `country` - Location hierarchy

**Legacy / sample apps** (still in `INSTALLED_APPS`):
- `pizza`, `topping` - Sample pizza/topping models from earlier scaffolding

**Utility apps**:
- `commoninfo` - Abstract `CommonInfo` model providing `created_at`/`updated_at`
- `api` - General API home view

### API Architecture

The codebase mixes two DRF patterns:

**Generic Views** (older apps: `order`, `product`, `region`, etc.):
- `ListCreateAPIView` for list + create
- `RetrieveUpdateDestroyAPIView` for detail
- User-scoped queries filter via `get_queryset()` (e.g. `UserOrderListCreateAPIView` filters by `vendor__user=user`)

**ViewSets + DefaultRouter** (newer apps: `dairyentry`, `expenses`):
- Full CRUD ViewSets registered through `rest_framework.routers.DefaultRouter`
- Auto-generated routes (`/diary-entries/`, `/bank-statements/`, etc.)

**Common to both**:
- Filtering via `django-filter` with `DjangoFilterBackend`
- Pagination configured globally (10 items per page)
- `prefetch_related` / `select_related` for relationship traversal (e.g. `prefetch_related('items__product')` on order listings)

### URL Structure
- Root URLs in `blogs/urls.py`
- Each app has its own `urls.py` included via `include()`
- API documentation via drf-spectacular:
  - `/api/schema/` - OpenAPI schema
  - `/api/schema/swagger-ui/` - Swagger UI
  - `/api/schema/redoc/` - ReDoc UI
- `/silk/` - Django Silk profiling (enabled)

### Third-Party Integrations

**Installed packages**:
- `djangorestframework` - API framework
- `djangorestframework-simplejwt` - JWT auth (access/refresh tokens)
- `drf-spectacular` (+ `drf-spectacular-sidecar`) - OpenAPI/Swagger documentation
- `django-cors-headers` - CORS handling
- `django-filter` - Query filtering
- `django-silk` - Performance profiling (mounted at `/silk/`)
- `whitenoise` - Static file serving
- `psycopg2-binary` - PostgreSQL adapter
- `dj-database-url` - Parse `DATABASE_URL` for production
- `python-dotenv` - Load `.env` in development
- `pillow` - Image processing

### Deployment

**Vercel Configuration** (`vercel.json`):
- Uses Python 3.11 runtime
- WSGI entry: `blogs/wsgi.py`
- Max Lambda size: 100mb
- All routes proxy to Django WSGI app

### Settings Notes
- `DEBUG` controlled by environment variable (defaults to `True` if unset — should be set explicitly in production)
- `SECRET_KEY` read from `DJANGO_SECRET_KEY` env var (loaded from `.env` via `python-dotenv`)
- `ALLOWED_HOSTS = ['*']` (should be restricted in production)
- Static files served via WhiteNoise with compression (`CompressedManifestStaticFilesStorage`)
- CORS allow-list comes from `CORS_ALLOWED_ORIGINS` env var plus regex allow-list for `*.vercel.app` and `*.rajkumaryd.in`
- Remote migrations: `POST /migrate/` with header `X-Migration-Token: <MIGRATION_SECRET_TOKEN>` (`blogs/views.py:run_migrations`)

## Development Patterns

### When Adding New Models
1. Inherit from `CommonInfo` if you need timestamp fields
2. Add custom managers/querysets for complex filtering
3. Define custom permissions in Meta if needed
4. Use `settings.AUTH_USER_MODEL` for User ForeignKeys

### When Adding New Endpoints
1. Use Generic Views (`generics.ListCreateAPIView`, etc.) not APIView or ViewSets
2. Add `DjangoFilterBackend` and define `filterset_fields` for filtering
3. Use `prefetch_related` / `select_related` for relationship optimization
4. For user-specific data, override `get_queryset()` to filter by request.user

### Query Optimization
- Order listings use: `Order.objects.prefetch_related('items__product')`
- This prevents N+1 queries when accessing order items and their products



Website monitoring 
- server down
  - SBI, other bank, govt website, Tolliinfo
- Website status changes, page updated.
- 

All these updates leads to news feedback
Notification services 
  - Calendar
  - home alarms
  - Updates (entry, exit, light, electricity, monitoring devices)
