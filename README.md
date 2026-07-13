# golfiq-backend
Practice-to-course transfer analytics platform that helps golfers determine whether practice habits and swing thoughts improve on-course performance.

## Continuous integration

GitHub Actions validates pushes to `main` and pull requests targeting `main`.
The pipeline starts PostgreSQL, applies all Alembic migrations, compiles the
application, and runs the full pytest suite. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
