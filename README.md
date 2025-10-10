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
- Username-based authentication (not email)

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
- `user` - Custom user model
- `vendor` - Vendor management (linked to User via ForeignKey)
- `product` - Product catalog
- `order` - Order and OrderItem models with custom manager
- `userprofile` - User profile information

**Geographical data apps**:
- `region`, `state`, `country` - Location hierarchy

**Pizza-specific apps**:
- `pizza` - Pizza models
- `topping` - Topping models

**Utility apps**:
- `commoninfo` - Abstract models for inheritance
- `dairyentry` - Diary/journal functionality
- `api` - General API home view

### API Architecture

The codebase uses **Django REST Framework Generic Views** (not ViewSets):
- `ListCreateAPIView` for list + create operations
- `RetrieveUpdateDestroyAPIView` for detail operations
- Filtering via `django-filter` with `DjangoFilterBackend`
- Pagination configured globally (10 items per page)

**Key patterns**:
- User-scoped queries: `UserOrderListCreateAPIView` filters orders by `vendor__user=user`
- Query optimization: Uses `prefetch_related('items__product')` for order listings
- Commented-out code shows evolution from APIView → Generic Views

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
- `drf-spectacular` - OpenAPI/Swagger documentation
- `django-filter` - Query filtering
- `django-silk` - Performance profiling
- `whitenoise` - Static file serving
- `psycopg2-binary` - PostgreSQL adapter
- `pillow` - Image processing

### Deployment

**Vercel Configuration** (`vercel.json`):
- Uses Python 3.11 runtime
- WSGI entry: `blogs/wsgi.py`
- Max Lambda size: 100mb
- All routes proxy to Django WSGI app

### Settings Notes
- `DEBUG` controlled by environment variable (defaults to False)
- `ALLOWED_HOSTS = ['*']` (should be restricted in production)
- Static files served via WhiteNoise with compression
- SECRET_KEY is hardcoded (should use environment variable in production)

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
