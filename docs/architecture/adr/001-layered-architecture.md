# ADR-001: Use a Layered Backend Architecture

## Status

Accepted

## Context

GolfIQ contains authentication, CRUD workflows, analytics, and recommendation
logic. Combining HTTP handling, validation, queries, and domain calculations in
route functions would make those responsibilities difficult to test and change
independently. The application needs clear ownership boundaries without the
overhead of a more elaborate distributed or domain-framework architecture.

## Decision

Organize the backend into a small set of explicit layers:

- Routers in `app/api` define paths, HTTP methods, response models, status codes,
  and API documentation. They obtain dependencies and delegate work.
- Services in `app/services` implement use cases, ownership checks, analytics,
  recommendations, and transaction-oriented application logic.
- The database layer in `app/db` owns SQLAlchemy models, metadata, engine, and
  session construction.
- Schemas in `app/schemas` define validated request and response boundaries
  independently from persistence models.
- Dependencies in `app/dependencies` provide request-scoped database sessions and
  authenticated users.
- Middleware in `app/middleware` handles cross-cutting HTTP concerns such as
  request IDs.
- Core modules in `app/core` own configuration, security, logging, and global
  exception handling.

Dependencies should generally flow from routers to services to database models.
Cross-cutting infrastructure may be shared through the core and dependency
modules.

## Consequences

- HTTP contracts remain visible and thin.
- Business rules can be tested without duplicating them in routers.
- Persistence models do not become public API schemas by default.
- Cross-cutting behavior is applied consistently.
- Some workflows require passing a session and current user through multiple
  layers.
- Layer boundaries require discipline; small helpers should not become
  unnecessary abstractions.

## Alternatives Considered

- **Route-centric implementation:** simpler initially, but couples HTTP,
  persistence, and business rules as the application grows.
- **Repository layer for every model:** can isolate persistence further, but
  would add indirection without enough current query complexity to justify it.
- **Microservices:** would introduce network, deployment, and data-consistency
  costs that are unnecessary for GolfIQ's current scope.
