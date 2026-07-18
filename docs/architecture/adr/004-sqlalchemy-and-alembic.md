# ADR-004: Use SQLAlchemy and Alembic for Persistence

## Status

Accepted

## Context

The application needs typed mappings between Python objects and relational
tables, explicit query control, relationship loading, and repeatable database
changes. Database structure must be reproducible in local development, CI, and
production without relying on manual SQL changes.

## Decision

Use SQLAlchemy for engine and session management, declarative model mappings,
relationships, and queries. Keep SQLAlchemy models in the database layer and use
Pydantic schemas at the API boundary. Use Alembic as the only supported mechanism
for versioned schema changes. Apply committed migrations before starting the API
in containerized environments.

## Consequences

- Persistence mappings and relationships are centralized and reviewable.
- Sessions provide a clear transaction boundary for service operations.
- Migrations create an ordered, auditable history of schema evolution.
- API schemas can evolve independently from database models.
- Developers must understand session lifecycle, loading strategies, and migration
  review.
- Model changes and migration changes must be kept synchronized.
- Automatic migration generation still requires human review.

## Alternatives Considered

- **Raw SQL throughout services:** provides maximum control but increases
  repetitive mapping and transaction code.
- **SQLModel:** offers tighter FastAPI integration, but coupling persistence and
  API models would reduce the separation chosen for GolfIQ.
- **Manual SQL scripts:** easy to begin with, but lack Alembic's revision graph,
  upgrade workflow, and integration with SQLAlchemy metadata.
