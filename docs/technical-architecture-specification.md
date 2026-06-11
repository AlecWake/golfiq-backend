# GolfIQ Technical Architecture Specification

## 1. Purpose of This Document

This document defines the technical architecture for the GolfIQ backend before implementation begins.

GolfIQ is a FastAPI/PostgreSQL backend platform that helps golfers track practice sessions, swing thoughts, rounds, analytics, and recommendations.

The purpose of this architecture is to keep the project:

* understandable
* testable
* resume-worthy
* realistic for a solo student developer
* organized enough to discuss in backend engineering interviews

The first priority is to build a clean MVP, not an overengineered enterprise system.

---

# 2. Overall Backend Architecture

GolfIQ will use a layered backend architecture.

The main layers are:

1. API Layer
2. Schema Layer
3. Service Layer
4. Repository Layer
5. Database Model Layer
6. Core/Shared Layer

The request flow should usually look like this:

```text
Client
  ↓
FastAPI Router
  ↓
Pydantic Schema Validation
  ↓
Service Layer
  ↓
Repository Layer
  ↓
SQLAlchemy Models
  ↓
PostgreSQL Database
```

The main rule is:

```text
Routers handle HTTP.
Services handle business logic.
Repositories handle database queries.
Models define database tables.
Schemas define request/response shapes.
```

This separation matters because it keeps route files small and makes the project easier to test and explain.

---

# 3. Recommended Folder Structure

Recommended structure:

```text
golfiq-backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── clubs.py
│   │   │   ├── practice_sessions.py
│   │   │   ├── swing_thoughts.py
│   │   │   ├── rounds.py
│   │   │   ├── analytics.py
│   │   │   └── recommendations.py
│   │   │
│   │   └── router.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── errors.py
│   │   └── constants.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   │       ├── user.py
│   │       ├── golfer_profile.py
│   │       ├── club.py
│   │       ├── practice_session.py
│   │       ├── swing_thought.py
│   │       ├── round.py
│   │       ├── round_stat.py
│   │       ├── recommendation.py
│   │       └── analytics_snapshot.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── club.py
│   │   ├── practice_session.py
│   │   ├── swing_thought.py
│   │   ├── round.py
│   │   ├── analytics.py
│   │   └── recommendation.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── club_service.py
│   │   ├── practice_session_service.py
│   │   ├── swing_thought_service.py
│   │   ├── round_service.py
│   │   ├── analytics_service.py
│   │   └── recommendation_service.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── club_repository.py
│   │   ├── practice_session_repository.py
│   │   ├── swing_thought_repository.py
│   │   ├── round_repository.py
│   │   └── recommendation_repository.py
│   │
│   └── dependencies/
│       ├── auth.py
│       ├── database.py
│       └── permissions.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── api/
│   └── conftest.py
│
├── alembic/
│
├── docs/
│   ├── master-project-specification.md
│   ├── implementation-roadmap-v1.md
│   ├── technical-architecture-specification.md
│   ├── database-design-specification.md
│   ├── api-specification.md
│   └── development-journal.md
│
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

---

# 4. Folder Responsibilities

## app/

Contains the actual backend application.

Nothing outside `app/` should be needed to run the API except configuration, tests, migrations, and docs.

## app/main.py

Responsible for:

* creating the FastAPI app
* including the main API router
* adding middleware later if needed
* registering exception handlers later if needed

It should not contain business logic.

## app/api/routes/

Contains route files.

Each route file should define HTTP endpoints for one domain area.

Examples:

* `auth.py`
* `rounds.py`
* `practice_sessions.py`
* `analytics.py`

Routes should be thin.

A route should:

* receive a request
* validate inputs through schemas
* use dependencies such as current user and database session
* call a service
* return a response

A route should not:

* directly contain complex business logic
* directly calculate analytics
* directly build large SQL queries
* directly check complicated recommendation rules

## app/api/router.py

Combines all route files into one main API router.

This keeps `main.py` clean.

## app/core/

Contains shared application-level utilities.

Examples:

* configuration
* security helpers
* shared constants
* custom error classes

This folder should not depend on feature-specific modules.

## app/db/

Contains database setup and SQLAlchemy models.

## app/db/session.py

Responsible for:

* creating database engine
* creating session factory
* providing database sessions

## app/db/base.py

Responsible for collecting model metadata for Alembic migrations.

## app/db/models/

Contains SQLAlchemy database models.

Models define:

* table names
* columns
* relationships
* constraints
* indexes when appropriate

Models should not contain business logic.

## app/schemas/

Contains Pydantic schemas.

Schemas define:

* request bodies
* response shapes
* validation rules
* serialized API output

Do not use SQLAlchemy models directly as API responses.

## app/services/

Contains business logic.

Services answer questions like:

* Can this user create this resource?
* What happens when a round is created?
* How is a recommendation generated?
* Is there enough data for analytics?
* What validation is needed beyond Pydantic field validation?

Services may call one or more repositories.

## app/repositories/

Contains database access logic.

Repositories should handle:

* finding records by ID
* filtering records
* creating records
* updating records
* deleting records
* database queries

Repositories should not decide business rules.

## app/dependencies/

Contains FastAPI dependency functions.

Examples:

* get current user
* get database session
* require authenticated user
* require resource ownership
* require admin role later

## tests/

Contains all tests.

Test structure should roughly mirror the application structure.

---

# 5. Module Boundaries

## Auth Module

Responsible for:

* user registration
* login
* password hashing
* JWT creation
* JWT verification
* current user loading

Auth owns:

* token generation
* password checking
* authentication dependencies

Auth does not own:

* golf profile logic
* practice data
* analytics
* recommendations

## Users Module

Responsible for:

* user profile data
* golfer profile data
* account-level user information

Users owns:

* `users`
* `golfer_profiles`

Users does not own:

* login token creation
* password hashing internals
* round analytics

## Clubs Module

Responsible for:

* user club setup
* club type
* club display name
* estimated distance
* notes

Clubs are user-owned.

A user should only access their own clubs.

## Practice Sessions Module

Responsible for:

* logging practice sessions
* practice duration
* practice location
* practice focus
* quality rating
* notes
* linking sessions to clubs
* linking sessions to swing thoughts

Practice sessions should be one of the core MVP modules.

## Swing Thoughts Module

Responsible for:

* creating swing thoughts
* marking swing thoughts active, retired, successful, harmful, or unknown
* tracking descriptions and notes
* connecting swing thoughts to practice sessions
* later connecting swing thoughts to analytics comparisons

Swing thoughts are important because they make GolfIQ different from a normal golf stats tracker.

## Rounds Module

Responsible for:

* logging rounds
* course name
* score
* holes played
* par
* weather
* notes
* round stats
* miss patterns later

Rounds are the main on-course performance record.

## Analytics Module

Responsible for:

* scoring averages
* putting averages
* penalty averages
* fairway percentages
* GIR percentages
* trends
* before/after swing thought comparisons
* practice-to-round summaries

Analytics should not modify user data.

Analytics should read data and return calculated results.

## Recommendations Module

Responsible for:

* generating practice recommendations
* explaining why the recommendation was made
* storing recommendation history later
* handling not-enough-data cases

The first version should use simple rule-based logic.

Do not use AI recommendations in the MVP.

## Shared/Core Utilities

Responsible for:

* configuration
* security helpers
* shared constants
* custom errors
* common pagination helpers later

Shared code should not know too much about golf-specific domain logic.

---

# 6. Responsibility Rules

## Routers

Routers should:

* define endpoint paths
* define HTTP methods
* accept request schemas
* return response schemas
* call services
* use dependencies

Routers should not:

* calculate analytics
* directly run database queries
* contain large if/else business rules
* hash passwords directly
* manually check every ownership rule if a service/dependency can handle it

## Schemas

Schemas should:

* define API request and response formats
* validate field types
* enforce simple constraints
* hide internal database fields when needed

Examples:

* `UserCreate`
* `UserResponse`
* `RoundCreate`
* `RoundResponse`
* `PracticeSessionCreate`
* `AnalyticsSummaryResponse`

Schemas should not:

* talk to the database
* contain business workflows
* replace SQLAlchemy models

## Models

Models should:

* define database tables
* define relationships
* define constraints
* support Alembic migrations

Models should not:

* be returned directly from the API
* contain service logic
* know about HTTP status codes

## Services

Services should:

* enforce business rules
* coordinate repositories
* handle ownership checks when appropriate
* prepare analytics results
* generate recommendations
* decide whether there is enough data

Services should not:

* know raw HTTP request details
* depend heavily on FastAPI-specific objects
* directly construct API responses unless simple

## Repositories

Repositories should:

* handle database queries
* create/update/delete database records
* return model instances or query results

Repositories should not:

* decide recommendation rules
* decide whether advice is useful
* handle HTTP exceptions directly unless the project intentionally chooses that style

## Dependencies

Dependencies should:

* provide database sessions
* load the current authenticated user
* enforce role requirements
* provide reusable permission checks

Dependencies should not:

* contain analytics logic
* contain recommendation logic
* contain large application workflows

## Tests

Tests should verify:

* endpoints behave correctly
* auth protects data
* users cannot access other users’ resources
* database relationships work
* analytics calculations are correct
* recommendations are explainable and not random

---

# 7. Data Flow Examples

## User Registration Flow

```text
Client sends POST /auth/register
  ↓
Router validates request with UserCreate schema
  ↓
Auth service checks whether email already exists
  ↓
Auth service hashes password
  ↓
User repository creates user
  ↓
User repository creates golfer profile if needed
  ↓
Service returns created user response
  ↓
Router returns response
```

Important rules:

* duplicate emails should fail
* password should never be stored directly
* password hash should not be returned
* response should not expose internal security fields

## Creating a Practice Session Flow

```text
Client sends POST /practice-sessions with JWT
  ↓
Auth dependency loads current user
  ↓
Router validates PracticeSessionCreate schema
  ↓
Practice session service checks business rules
  ↓
Repository saves practice session
  ↓
Repository links clubs/focus areas/swing thoughts if provided
  ↓
Service returns created practice session
  ↓
Router returns response
```

Important rules:

* user can only attach their own clubs
* user can only attach their own swing thoughts
* duration must be positive
* quality rating should be within allowed range
* notes are optional

## Creating a Round Flow

```text
Client sends POST /rounds with JWT
  ↓
Auth dependency loads current user
  ↓
Router validates RoundCreate schema
  ↓
Round service checks score, holes played, and ownership
  ↓
Round repository creates round
  ↓
Round stats may be created separately or nested
  ↓
Analytics cache invalidation can be added later
  ↓
Router returns created round
```

Important rules:

* score must be positive
* holes played should be 9 or 18
* user owns the round
* round stats should belong to one round

## Generating Analytics Flow

```text
Client sends GET /analytics/summary with JWT
  ↓
Auth dependency loads current user
  ↓
Analytics router calls analytics service
  ↓
Analytics service requests rounds and practice data from repositories
  ↓
Analytics service calculates summary metrics
  ↓
Service checks if enough data exists
  ↓
Router returns analytics response
```

Important rules:

* analytics should only use current user's data
* analytics should clearly say when there is not enough data
* analytics should be deterministic and testable

## Generating a Recommendation Flow

```text
Client sends POST /recommendations/generate with JWT
  ↓
Auth dependency loads current user
  ↓
Recommendation service calls analytics service
  ↓
Analytics service returns scoring weaknesses and practice patterns
  ↓
Recommendation service applies rule-based logic
  ↓
Recommendation is returned and optionally stored
```

Important rules:

* recommendations must include evidence
* recommendations must not pretend certainty
* recommendations should include confidence level
* not enough data should return a useful message, not fake advice

---

# 8. Authentication and Authorization Architecture

## Authentication

GolfIQ will use JWT-based authentication.

The basic flow:

```text
User logs in with email and password
  ↓
Server verifies password
  ↓
Server creates access token
  ↓
Client sends token with future requests
  ↓
Server validates token and loads current user
```

## Password Hashing

Passwords must never be stored in plain text.

The backend should store:

```text
password_hash
```

not:

```text
password
```

The password hashing logic belongs in:

```text
app/core/security.py
```

## Current User Dependency

Protected routes should use a reusable dependency that:

1. reads the token
2. validates the token
3. extracts the user ID
4. loads the user from the database
5. returns the current user

This prevents repeating auth logic in every route.

## Ownership Checks

Most resources are user-owned.

Examples:

* clubs
* rounds
* practice sessions
* swing thoughts
* goals
* recommendations

A user should not be able to access another user's data.

Ownership checks can happen in the service layer or through reusable dependency helpers.

The key rule:

```text
Every user-owned query must include user_id.
```

Bad pattern:

```text
Find round by round_id only.
```

Better pattern:

```text
Find round by round_id and current_user.id.
```

This avoids accidental data leaks.

## Role Checks

Initial roles:

```text
golfer
admin
```

Future roles:

```text
coach
```

The MVP should not fully build coach functionality, but the user model can include a role field to make future expansion easier.

Role checks should be centralized.

Do not scatter role checking logic across route files.

---

# 9. Error Handling Strategy

GolfIQ should use consistent API errors.

## Common Error Types

### Validation Errors

Used when request data is invalid.

Examples:

* missing required field
* invalid email
* score is not a number
* quality rating outside allowed range

Usually handled by FastAPI/Pydantic.

### Not Found Errors

Used when a requested resource does not exist.

Examples:

* round not found
* practice session not found
* club not found

Important: for user-owned resources, it is usually okay to return 404 if the resource does not belong to the current user. This avoids revealing that another user's resource exists.

### Unauthorized Errors

Used when the user is not logged in or token is invalid.

Example:

```text
401 Unauthorized
```

### Forbidden Errors

Used when the user is logged in but does not have permission.

Example:

```text
403 Forbidden
```

This can be used later for coach/admin restrictions.

### Business Rule Errors

Used when the request is technically valid but violates a domain rule.

Examples:

* trying to attach another user's club to a practice session
* trying to create stats for a round that already has stats
* trying to generate a recommendation with not enough data

## Consistent Error Format

Recommended error shape:

```text
{
  "error": {
    "code": "ROUND_NOT_FOUND",
    "message": "Round not found.",
    "details": {}
  }
}
```

Benefits:

* easier frontend handling later
* easier debugging
* more professional API design
* easier to explain in interviews

---

# 10. Configuration Strategy

Configuration should come from environment variables.

Do not hardcode secrets or database URLs.

## Important Environment Variables

Examples:

```text
APP_ENV
DATABASE_URL
TEST_DATABASE_URL
SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES
ALGORITHM
```

## Local Development

Local development should use:

```text
.env
```

But `.env` should not be committed.

The repo should include:

```text
.env.example
```

This shows required variables without exposing secrets.

## Test Environment

Tests should use a separate test database.

Do not run tests against the development database.

## Production Environment

Production should use environment variables from the deployment provider.

Production secrets should never be committed to GitHub.

---

# 11. Testing Architecture

Testing is a major part of making this project resume-worthy.

## Test Categories

### Unit Tests

Unit tests should test isolated business logic.

Best targets:

* analytics calculations
* recommendation rules
* helper functions
* validation helpers

Unit tests should be fast and not require the full API.

### Integration Tests

Integration tests should verify that the app works with the database.

Best targets:

* repository methods
* database relationships
* ownership queries
* migrations later

### API Tests

API tests should call actual endpoints.

Best targets:

* auth endpoints
* CRUD endpoints
* protected routes
* analytics endpoints
* recommendation endpoints

## Test Database Strategy

Use a separate test database.

Recommended approach:

```text
Development database:
golfiq_dev

Test database:
golfiq_test
```

Tests should not depend on existing manual data.

Tests should create their own data and clean up after themselves.

## What to Mock

Mocking should be minimal.

Mock:

* external email services later
* third-party APIs later
* background job dispatching later

Do not mock:

* your own service layer in API tests
* your own repository layer in integration tests
* analytics calculations in analytics tests

For this project, real database-backed tests will be more valuable than excessive mocking.

---

# 12. Development Rules

## Naming Conventions

Use clear, boring names.

Good:

```text
practice_sessions.py
round_service.py
swing_thought_repository.py
RoundCreate
RoundResponse
```

Bad:

```text
helpers.py
stuff.py
manager.py
golf_logic.py
```

## Route File Rule

A route function should be short.

If a route starts becoming long, move logic to the service layer.

## Service Layer Rule

Business decisions belong in services.

Examples:

* deciding if there is enough data
* deciding which recommendation to generate
* checking whether a user can attach a club
* calculating scoring averages

## Repository Rule

Database access belongs in repositories.

Do not spread SQLAlchemy queries everywhere.

## Import Rules

General direction:

```text
routes import services
services import repositories
repositories import models
schemas are used by routes/services
core can be used across the app
```

Avoid circular imports.

## Interview Rule

For every major design decision, you should be able to answer:

```text
Why did I structure it this way?
```

Example answer:

```text
I separated routers, services, and repositories so HTTP handling, business logic, and database access stayed independent and testable.
```

That is the kind of explanation that helps in interviews.

---

# 13. MVP Architecture Choices

The MVP should include:

* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* JWT authentication
* Pydantic schemas
* pytest tests
* Docker Compose for local database

The MVP should not include yet:

* Redis
* background jobs
* weekly emails
* coach dashboards
* admin dashboard
* AI recommendations
* subscriptions
* mobile app
* complex frontend

These are valuable later, but they should not block the first working backend.

---

# 14. Future Architecture Extensions

## Redis Caching

Redis can later cache:

* analytics summaries
* latest recommendations
* dashboard data

Cache invalidation should happen when a user creates, updates, or deletes:

* round
* round stats
* practice session
* swing thought

Redis should not be added until analytics endpoints exist and are slow enough to justify caching.

## Background Jobs

Background jobs can later handle:

* weekly summaries
* analytics snapshots
* email reports
* scheduled recommendation generation

Possible future tools:

* Celery
* RQ
* FastAPI background tasks for simple cases

Do not add background jobs in the MVP.

## Weekly Reports

Weekly reports can use:

* analytics service
* recommendation service
* background job system
* email provider

This should be a later feature.

## Coach Accounts

Future coach support may require:

* coach role
* player role
* coach-player relationship table
* invitation/approval system
* shared analytics permissions

Do not build coach accounts until the solo golfer experience works.

## Admin Functionality

Admin features may include:

* viewing system health
* viewing audit logs
* debugging user issues

Admin users should not casually edit user golf data.

Admin functionality is not needed for MVP.

## Deployment

Deployment should be added after:

* core CRUD works
* auth works
* analytics v1 works
* tests exist

Production architecture can later include:

```text
FastAPI app
PostgreSQL database
environment variables
health check endpoint
structured logs
CI pipeline
```

---

# 15. Architecture Summary

GolfIQ should be built as a clean, layered FastAPI backend.

The most important design principles are:

1. Keep routers thin.
2. Put business logic in services.
3. Put database queries in repositories.
4. Use schemas for API input/output.
5. Use SQLAlchemy models for database tables.
6. Protect every user-owned resource with ownership checks.
7. Make analytics and recommendations testable.
8. Avoid overengineering the MVP.
9. Add Redis, background jobs, and coach features later.
10. Keep the project easy to explain in interviews.

The goal is not to build the biggest possible app.

The goal is to build a backend project that proves real software engineering ability.