# ADR-010: Standardize Production-Readiness Concerns

## Status

Accepted

## Context

A feature-complete API must be diagnosable, consistently configured, safe to
operate, and protected against accidental regressions. Ad hoc logging and error
formats make incidents harder to trace, while configuration embedded in code
creates deployment risk. Release confidence also depends on repeatable automated
checks.

## Decision

Adopt the following application-wide conventions:

- Load database, JWT, expiration, and log-level settings from validated
  environment-based configuration.
- Configure application logging centrally and avoid adding duplicate handlers.
- Attach or accept a valid request ID for each request, return it in the
  `X-Request-ID` header, and make it available to error handling.
- Convert HTTP, validation, and unexpected exceptions into a standardized error
  envelope containing a stable code, message, optional details, and request ID.
- Log unexpected exceptions once at the global boundary with request context,
  while returning a non-sensitive public message.
- Run compilation, migrations, and the complete pytest suite in GitHub Actions
  for relevant pushes and pull requests.
- Use container health checks and a migration-before-startup sequence.

## Consequences

- Clients receive predictable errors and can report request IDs during support.
- Operators can correlate failures without exposing internal exception details.
- Environment-specific values stay outside source code.
- CI blocks many syntax, migration, and behavioral regressions before merge.
- Consistency depends on new code using the shared handlers and configuration.
- Request IDs improve correlation but do not replace centralized log collection,
  metrics, or distributed tracing.
- Production still requires external secret management, backups, TLS, monitoring,
  and operational alerting appropriate to its deployment environment.

## Alternatives Considered

- **Per-route exception handling and logging:** offers local control but produces
  duplicated logs and inconsistent responses.
- **Framework-default errors only:** requires less code but does not provide a
  stable application error contract or request correlation.
- **Manual release verification:** useful as a supplement, but slower and less
  repeatable than CI-enforced checks.
