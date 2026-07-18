# ADR-006: Use Docker for Runtime Packaging

## Status

Accepted

## Context

GolfIQ depends on a specific Python runtime, Python packages, PostgreSQL, and
database migrations. Local development, CI, and production should minimize
environment drift. Deployment should use a repeatable artifact and an explicit
startup sequence.

## Decision

Package the API in a Docker image and use Docker Compose to coordinate the API
and PostgreSQL for local and initial production deployments. Build dependencies
from the pinned requirements, run the application as a non-root user, wait for
database health, apply existing Alembic migrations, and then start Uvicorn.
Persist PostgreSQL data in a named volume and configure services through
environment variables.

## Consequences

- The application runtime is repeatable across machines.
- New contributors can start the complete stack with a small number of commands.
- Health checks and service ordering make startup behavior explicit.
- The same image structure supports local and production workflows.
- Image builds and container orchestration add tooling and storage overhead.
- Local file mounting, networking, and database hostnames differ from direct
  host execution and must be understood.
- Docker does not replace production secret management, backups, or monitoring.

## Alternatives Considered

- **Host-managed virtual environments:** lightweight for local work, but more
  vulnerable to runtime and system-library drift.
- **Virtual machines:** provide stronger isolation but are heavier and slower for
  this application.
- **Managed platform without a project image:** may reduce operations, but can
  make local-to-production parity dependent on provider-specific build behavior.
