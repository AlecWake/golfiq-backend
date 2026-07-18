# ADR-008: Keep Analytics Logic in the Service Layer

## Status

Accepted

## Context

GolfIQ computes round summaries, practice effectiveness, correlations,
improvement timelines, goal progress, and other derived metrics. These
calculations combine owned records, date windows, aggregation, classification,
and explanatory text. They are business capabilities rather than HTTP concerns
or persistence-model responsibilities.

## Decision

Implement analytics use cases in `app/services`. Routers validate HTTP inputs,
obtain the current user and database session, and delegate to analytics services.
Services scope queries to the authenticated user, load required relationships,
perform calculations, and return data compatible with explicit response schemas.

Share small, side-effect-free calculation helpers only when they remove clear
duplication. Keep endpoint-specific orchestration readable instead of building a
generic analytics framework.

## Consequences

- Analytics rules are reusable independently of routing.
- Route functions remain focused on the API contract.
- Database models remain representations of stored state rather than containers
  for reporting behavior.
- Analytics services can choose query and relationship-loading strategies based
  on each use case.
- Some services contain substantial calculation code and require focused review.
- Shared metric definitions must remain consistent when multiple analytics
  features use them.

## Alternatives Considered

- **Calculations in routers:** reduces file count but couples domain logic to
  FastAPI and encourages duplication.
- **Calculated properties on ORM models:** convenient for single records, but
  poorly suited to user history, windows, and cross-record aggregation.
- **Database views or stored procedures:** can optimize stable, data-intensive
  reporting, but would move current application rules into a second language and
  complicate testing and migration ownership.
