# ADR-003: Use PostgreSQL as the Primary Database

## Status

Accepted

## Context

GolfIQ stores users, golfer profiles, clubs, rounds, hole scores, practice
sessions, swing thoughts, and their relationships. These records require
referential integrity, uniqueness constraints, transactions, ordered history,
and aggregate queries for analytics. Development, testing, and production should
use the same database semantics.

## Decision

Use PostgreSQL as the system of record. Model domain relationships with foreign
keys and constraints, perform writes transactionally, and use SQL queries through
SQLAlchemy for operational and analytical reads. Use a dedicated PostgreSQL
database for automated tests rather than substituting a different database
engine.

## Consequences

- Referential and transactional guarantees are enforced by the database.
- Relational joins and aggregates fit the connected golf activity data.
- PostgreSQL behavior remains consistent across local, CI, and production
  environments.
- Operating the service requires provisioning, credentials, backups, migrations,
  and monitoring for PostgreSQL.
- The application is not database-engine agnostic in practice, even though
  SQLAlchemy abstracts much of the access syntax.

## Alternatives Considered

- **SQLite:** convenient for small local applications, but differs from
  PostgreSQL in concurrency, typing, and constraint behavior and would weaken
  test fidelity.
- **MySQL:** capable relational storage, but PostgreSQL was preferred for its
  strong constraint behavior and mature analytical SQL capabilities.
- **Document database:** flexible documents do not outweigh the value of explicit
  relationships, constraints, and transactional updates in this domain.
