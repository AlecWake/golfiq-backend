# golfiq-backend
Practice-to-course transfer analytics platform that helps golfers determine whether practice habits and swing thoughts improve on-course performance.

## Docker

Docker Desktop with Docker Compose is required. Copy `.env.example` to `.env` if
you do not already have a local environment file. The example credentials and JWT
secret are for development only; production must use strong, unique secrets.

### Fully containerized

Start PostgreSQL and the API:

```powershell
docker compose up --build
```

Add `-d` to run in the background. The API is available at
`http://localhost:8000`, Swagger UI at `http://localhost:8000/docs`, and the
unauthenticated health endpoint at `http://localhost:8000/api/v1/health`.

The API waits for PostgreSQL to become healthy, applies the existing Alembic
migrations with `alembic upgrade head`, and starts only if migration succeeds.
Inside Compose it connects to `postgres:5432`; PostgreSQL remains accessible from
the host at `localhost:5433` by default.

Useful commands:

```powershell
docker compose ps
docker compose logs -f api
docker compose down
```

Use `docker compose down -v` only when you intentionally want to delete all data
in the local PostgreSQL named volume.

### Local hybrid development

To keep running the API directly from Windows, start only PostgreSQL, activate the
existing virtual environment, apply migrations, and start Uvicorn:

```powershell
docker compose up -d postgres
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

This workflow uses the host `DATABASE_URL` from `.env`, which points to
`localhost:5433`. Tests continue to use the separate `golfiq_test` database.

## Continuous integration

GitHub Actions validates pushes to `main` and pull requests targeting `main`.
The pipeline starts PostgreSQL, applies all Alembic migrations, compiles the
application, and runs the full pytest suite. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
