# ADR-002: Use FastAPI for the HTTP API

## Status

Accepted

## Context

GolfIQ requires a JSON API with authenticated endpoints, structured validation,
consistent error responses, and documentation that stays aligned with the
implementation. The project is implemented in Python and benefits from making
type annotations part of the runtime API contract.

## Decision

Use FastAPI as the web framework. Pydantic schemas define request and response
data, FastAPI dependencies provide database sessions and authentication context,
and route metadata produces the OpenAPI document and interactive documentation.
Synchronous route handlers and SQLAlchemy sessions are used consistently with
the current persistence approach.

## Consequences

- Request validation and response serialization are declarative.
- OpenAPI, Swagger UI, and ReDoc are generated from the application.
- Dependency injection gives request-scoped infrastructure a consistent shape.
- Python type annotations improve editor support and reviewability.
- The application depends on FastAPI, Starlette, and Pydantic conventions.
- Blocking database access must not be presented as asynchronous work.
- Framework and Pydantic upgrades require attention to validation and schema
  compatibility.

## Alternatives Considered

- **Flask:** mature and flexible, but validation, dependency patterns, and
  OpenAPI generation would require additional libraries and conventions.
- **Django REST Framework:** comprehensive, but its full-stack ORM and framework
  conventions are heavier than needed for this API-focused service.
- **Direct Starlette:** provides the underlying ASGI primitives, but would
  require rebuilding validation and API documentation features supplied by
  FastAPI.
