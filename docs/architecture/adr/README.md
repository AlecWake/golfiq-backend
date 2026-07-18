# GolfIQ Architecture Decision Records

Architecture Decision Records (ADRs) capture significant engineering choices,
the context in which they were made, and their expected tradeoffs. They describe
the current GolfIQ backend architecture and provide a durable reference for
maintainers.

ADRs are historical records. If a decision changes, add a new ADR that supersedes
the earlier record rather than rewriting the original rationale.

| ADR | Decision | Summary |
| --- | --- | --- |
| [ADR-001](001-layered-architecture.md) | Layered architecture | Separates HTTP routing, business services, persistence, schemas, and middleware. |
| [ADR-002](002-fastapi.md) | FastAPI | Uses FastAPI for typed HTTP APIs, dependency injection, validation, and OpenAPI documentation. |
| [ADR-003](003-postgresql.md) | PostgreSQL | Uses a relational database for transactional, constrained, and queryable domain data. |
| [ADR-004](004-sqlalchemy-and-alembic.md) | SQLAlchemy and Alembic | Uses SQLAlchemy for persistence mapping and Alembic for versioned schema evolution. |
| [ADR-005](005-jwt-authentication.md) | JWT authentication | Uses signed bearer tokens for stateless API authentication. |
| [ADR-006](006-docker.md) | Docker | Packages a repeatable application runtime and coordinates local and production services. |
| [ADR-007](007-testing-philosophy.md) | Testing philosophy | Favors API-focused integration tests, targeted unit tests, and an isolated PostgreSQL test database. |
| [ADR-008](008-analytics-architecture.md) | Analytics architecture | Keeps analytics calculations in the service layer, separate from HTTP and persistence concerns. |
| [ADR-009](009-recommendation-engine.md) | Recommendation engine | Isolates recommendation and prioritization logic from API routing. |
| [ADR-010](010-production-readiness.md) | Production readiness | Standardizes configuration, logging, errors, request tracing, and continuous integration. |
