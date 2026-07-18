# ADR-007: Favor API Integration Tests with Database Isolation

## Status

Accepted

## Context

GolfIQ's highest-risk behavior spans routing, validation, authentication,
services, SQLAlchemy mappings, and PostgreSQL constraints. Tests that mock every
boundary can pass while the assembled API fails. At the same time, deterministic
helpers and security functions benefit from focused unit tests.

## Decision

Use pytest as the test runner. Make API integration tests the primary confidence
layer by exercising the FastAPI application through its test client and executing
real service and persistence code. Run these tests against a dedicated
`golfiq_test` PostgreSQL database. Create the schema for a test and remove it
afterward so state does not leak between cases. Override only the request-scoped
database dependency to bind the application to the test session.

Use unit tests selectively for behavior that is valuable to verify without HTTP
or database setup, such as token handling and test database safety checks.

## Consequences

- Tests cover validation, serialization, dependencies, business logic, and real
  PostgreSQL behavior together.
- The suite detects integration failures that isolated mocks may miss.
- Dedicated database validation reduces the risk of destructive tests targeting
  development data.
- Integration tests are slower than pure unit tests and require PostgreSQL.
- Fixture cleanup must remain reliable.
- Failures may span multiple layers and require diagnosis below the API surface.

## Alternatives Considered

- **Primarily mocked unit tests:** faster, but provide less confidence in database
  mappings and assembled request behavior.
- **SQLite test database:** simpler to provision, but does not reproduce
  PostgreSQL constraints and SQL semantics closely enough.
- **Shared persistent test data:** can speed setup, but introduces ordering,
  cleanup, and reproducibility problems.
