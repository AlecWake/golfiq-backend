# golfiq-backend

Practice-to-course transfer analytics platform that helps golfers determine
whether practice habits and swing thoughts improve on-course performance.

## API

GolfIQ exposes version **v1** under `/api/v1`. Register or sign in through the
Authentication endpoints to obtain a JWT, then send it to protected endpoints as
`Authorization: Bearer <access_token>`. The health check and account registration
and sign-in endpoints do not require authentication.

With the API running locally:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI document: `http://localhost:8000/openapi.json`

Major endpoint groups cover authentication, golfer profiles, clubs, practice
sessions, swing thoughts, rounds, round statistics, hole scores, analytics,
recommendations, the dashboard, and recent activity.

For development, start PostgreSQL, apply Alembic migrations, run Uvicorn with
reload, and execute the full pytest suite before opening a pull request. The same
stack can be started with `docker compose up --build`; the API container waits for
PostgreSQL and applies existing migrations before serving traffic. GitHub Actions
repeats compilation, migration, and pytest checks for pushes and pull requests.
Detailed commands follow below.

## Local development

The existing direct-Python workflow is still supported. Copy `.env.example` to
`.env`, start PostgreSQL, activate the virtual environment, migrate, and run
Uvicorn with reload enabled:

```powershell
Copy-Item .env.example .env
docker compose up -d postgres
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

The host API uses `DATABASE_URL` from `.env` and connects to PostgreSQL at
`localhost:5433`. Tests continue to use the separate `golfiq_test` database.

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

## Continuous integration

GitHub Actions validates pushes to `main` and pull requests targeting `main`.
The pipeline starts PostgreSQL, applies all Alembic migrations, compiles the
application, and runs the full pytest suite. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## AWS EC2 deployment

The first production deployment uses one Ubuntu LTS EC2 instance, the existing
API image, PostgreSQL 16, and `docker-compose.production.yml`. PostgreSQL has a
persistent named volume and no published host port. Only the API on port 8000 and
restricted SSH access should be allowed through the EC2 security group.

On the instance, copy `.env.production.example` to `.env.production`, generate
unique production secrets, validate the Compose configuration, and start it:

```bash
cp .env.production.example .env.production
chmod 600 .env.production
docker compose --env-file .env.production -f docker-compose.production.yml config --quiet
docker compose --env-file .env.production -f docker-compose.production.yml up -d --build
```

The API waits for PostgreSQL, applies Alembic migrations, and then starts FastAPI
on port 8000. See the complete [EC2 deployment runbook](docs/ec2-deployment.md)
for instance setup, Docker installation, security, environment variables, health
checks, updates, backups, and rollback steps.

This initial deployment intentionally uses plain HTTP. Add a reverse proxy and
HTTPS before transmitting production credentials or sensitive data; those are
planned as separate work and are not part of this deployment preparation.
