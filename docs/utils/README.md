# Utilities — Migrations & Deployment

## Local setup

```bash
# Activate virtualenv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Unix/macOS

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

`.env` is loaded by `blogs/settings.py` via `python-dotenv`. Required vars:

| Var | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key. |
| `DEBUG` | `True`/`False`. Defaults to `True` if unset. |
| `DATABASE_URL` | Required when `VERCEL=1`. Parsed by `dj-database-url`. |
| `VERCEL` | If set, switches DB to PostgreSQL via `DATABASE_URL`. |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origin list. |
| `MIGRATION_SECRET_TOKEN` | Required for the remote migration endpoint (see below). |

Without `VERCEL`, the project runs on local SQLite (`db.sqlite3`).

## Vercel deployment

Config: `vercel.json`.

- WSGI entry: `blogs/wsgi.py`
- Runtime: `python3.11`
- Max Lambda size: `100mb`
- Build command: `bash build.sh`
- All routes proxy to the Django WSGI app

## Remote migrations

`POST /migrate/` runs `manage.py migrate --noinput` on the deployed instance (`blogs/views.py:run_migrations`).

Auth: header `X-Migration-Token: <MIGRATION_SECRET_TOKEN>`. Returns `401` if the token mismatches, `500` if the env var is unset.

```bash
curl -X POST https://<host>/migrate/ \
  -H "X-Migration-Token: $MIGRATION_SECRET_TOKEN"
```

## Static files

WhiteNoise serves static files with `CompressedManifestStaticFilesStorage`. Run `python manage.py collectstatic` before deploy (typically handled in `build.sh`).

## Profiling

Django Silk is mounted at `/silk/`. Useful when chasing N+1s or slow endpoints during local development.
