# API

Top-level API surface for the project.

## Entry point

- `GET /api/` — `ApiHomeView` returns a sanity payload pulling from the `region` app (legacy/dev placeholder, see `api/views.py`).

## Auth (JWT)

Login is **email + password** (commit `a6291c5`); `LoginView` also accepts a mobile number in the `email` field.

| Endpoint | Purpose |
|---|---|
| `POST /api/token/` | `TokenObtainPairView` — get access + refresh tokens (SimpleJWT default). |
| `POST /api/token/refresh/` | Rotate access token. |
| `POST /api/token/verify/` | Verify a token. |
| `POST /user/register/` | `RegisterView` — sign up; returns user + tokens. |
| `POST /user/login/` | `LoginView` — email-or-mobile + password; returns tokens. |
| `POST /user/logout/` | Stub. |

DRF authentication classes (configured in `REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']`):
1. `JWTAuthentication` (primary)
2. `CsrfExemptSessionAuthentication` (custom, `blogs/authentication.py`)
3. `TokenAuthentication`

## Schema and docs

| Endpoint | Purpose |
|---|---|
| `/api/schema/` | OpenAPI 3 schema (drf-spectacular). |
| `/api/schema/swagger-ui/` | `DarkSwaggerView` — custom dark Swagger UI. |
| `/api/schema/redoc/` | ReDoc UI. |

## CORS

Configured via `corsheaders`. Origins come from `CORS_ALLOWED_ORIGINS` (env var, comma-separated) plus regex allow-list:
- `https://*.vercel.app`
- `https://*.rajkumaryd.in`

`CORS_ALLOW_CREDENTIALS = True`.

## Conventions

- New diary endpoints: DRF `ViewSet`s registered via `DefaultRouter`.
- Older order/product/region endpoints: DRF generic views (`ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`).
- User-scoped views override `get_queryset()` to filter by `request.user`.
- Use `select_related` / `prefetch_related` for FK/M2M traversals (see `UserOrderListCreateAPIView` for an example).
