# ADR-005: Use JWT Bearer Authentication

## Status

Accepted

## Context

GolfIQ exposes a stateless HTTP API whose protected resources are scoped to the
authenticated golfer. Clients need an authentication credential that can be sent
with each request without relying on server-side web sessions. Passwords must
never be stored or compared in plaintext.

## Decision

Authenticate users with email and a password hash, then issue a signed,
time-limited JSON Web Token. Clients send the token using the standard
`Authorization: Bearer` header. The token subject identifies the user; protected
requests decode the token and load the current user from PostgreSQL before
executing a use case.

Keep signing configuration and expiration settings externalized. Treat invalid,
expired, incomplete, and unknown-user tokens as authentication failures with the
same public response.

## Consequences

- API instances do not need shared server-side session storage.
- Standard bearer-token tooling works across clients and generated API
  documentation.
- Loading the user on each protected request ensures the account still exists.
- Issued tokens remain usable until expiration unless a separate revocation
  mechanism is introduced.
- Signing keys require secure storage and rotation procedures.
- Token payloads are signed, not encrypted, and must not contain secrets.

## Alternatives Considered

- **Cookie-backed server sessions:** provide straightforward revocation but
  require shared session state and browser-focused CSRF controls.
- **Opaque bearer tokens:** simplify revocation semantics but require token
  persistence and a lookup on every request.
- **Third-party identity provider:** can add federation and managed account
  security, but adds external dependency and operational complexity beyond the
  current product requirements.
