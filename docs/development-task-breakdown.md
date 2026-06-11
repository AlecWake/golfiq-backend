# GolfIQ Development Task Breakdown and GitHub Issues Plan

## 1. Purpose of This Document

This document breaks GolfIQ into practical development milestones and GitHub-style issues.

GolfIQ is a FastAPI/PostgreSQL backend platform that helps golfers track practice sessions, swing thoughts, rounds, analytics, and recommendations.

This plan is designed for a solo student developer working about 10 hours per week.

The goal is to finish a high-quality MVP, not to start an overly ambitious project that never gets completed.

---

# 2. GitHub Milestones

Recommended GitHub milestones:

1. Project Foundation
2. FastAPI Foundation
3. Database Foundation
4. Authentication
5. Core CRUD
6. Analytics
7. Recommendations
8. Production Readiness
9. Deployment
10. Version 2 Backlog

---

# 3. GitHub Labels

Recommended labels:

```text
documentation
backend
api
database
auth
testing
analytics
recommendation
deployment
docker
ci
refactor
bug
mvp
optional
version-2
good-first-issue
blocked
```

Priority labels:

```text
priority-high
priority-medium
priority-low
```

Difficulty labels:

```text
difficulty-low
difficulty-medium
difficulty-high
```

---

# 4. Milestone 1: Project Foundation

## Issue 1: Add initial project documentation

Status:
Required MVP

Labels:
documentation, mvp, priority-high, difficulty-low

Description:
Add the initial planning documents to the repository.

Checklist:

* Add master project specification
* Add implementation roadmap
* Add technical architecture specification
* Add database design specification
* Add API specification
* Add development task breakdown

Dependencies:
None

Estimated difficulty:
Low

Expected deliverable:
Documentation files exist in the `docs/` folder.

Learning goal:
Practice professional project documentation.

Acceptance criteria:

* All documents exist in `docs/`
* Each document has a clear title
* README links to the documents

---

## Issue 2: Create initial README

Status:
Required MVP

Labels:
documentation, mvp, priority-high, difficulty-low

Description:
Create a professional README that explains what GolfIQ is and what the planned backend stack is.

Checklist:

* Add project description
* Add MVP goals
* Add planned tech stack
* Add project status
* Add documentation links
* Add setup section placeholder

Dependencies:
Issue 1

Estimated difficulty:
Low

Expected deliverable:
Readable `README.md`.

Learning goal:
Practice writing project documentation for recruiters and developers.

Acceptance criteria:

* README explains the project in one paragraph
* README lists planned stack
* README links to docs
* README states current status

---

## Issue 3: Create project folder structure

Status:
Required MVP

Labels:
backend, mvp, priority-high, difficulty-low

Description:
Create the initial folder structure for the backend.

Checklist:

* Create `app/`
* Create `app/api/`
* Create `app/core/`
* Create `app/db/`
* Create `app/schemas/`
* Create `app/services/`
* Create `app/repositories/`
* Create `app/dependencies/`
* Create `tests/`
* Create `tests/unit/`
* Create `tests/integration/`
* Create `tests/api/`

Dependencies:
None

Estimated difficulty:
Low

Expected deliverable:
Project folder structure exists.

Learning goal:
Understand clean backend organization.

Acceptance criteria:

* Folder structure matches the technical architecture document
* Empty folders can contain placeholder `.gitkeep` files if needed

---

## Issue 4: Add Python gitignore and environment example

Status:
Required MVP

Labels:
backend, documentation, mvp, priority-high, difficulty-low

Description:
Add files needed to keep secrets and generated files out of Git.

Checklist:

* Add `.gitignore`
* Ignore virtual environments
* Ignore `.env`
* Ignore Python cache files
* Ignore pytest cache
* Add `.env.example`
* Document required environment variables

Dependencies:
None

Estimated difficulty:
Low

Expected deliverable:
`.gitignore` and `.env.example`.

Learning goal:
Learn safe project configuration practices.

Acceptance criteria:

* `.env` is ignored
* `.env.example` is committed
* Python cache files are ignored

---

# 5. Milestone 2: FastAPI Foundation

## Issue 5: Set up Python virtual environment and dependencies

Status:
Required MVP

Labels:
backend, mvp, priority-high, difficulty-low

Description:
Set up the Python environment and initial dependencies.

Checklist:

* Create virtual environment
* Install FastAPI
* Install Uvicorn
* Install pytest
* Create `requirements.txt`
* Document setup steps in README

Dependencies:
Issue 3

Estimated difficulty:
Low

Expected deliverable:
Local Python environment ready for development.

Learning goal:
Practice Python backend environment setup.

Acceptance criteria:

* Dependencies are installed
* `requirements.txt` exists
* README includes setup instructions

---

## Issue 6: Create FastAPI application entry point

Status:
Required MVP

Labels:
backend, api, mvp, priority-high, difficulty-low

Description:
Create the initial FastAPI application.

Checklist:

* Create `app/main.py`
* Create FastAPI app instance
* Add app title
* Add API version metadata
* Confirm app starts locally

Dependencies:
Issue 5

Estimated difficulty:
Low

Expected deliverable:
FastAPI app starts successfully.

Learning goal:
Understand FastAPI app initialization.

Acceptance criteria:

* App starts with Uvicorn
* OpenAPI docs are available locally
* No import errors

---

## Issue 7: Add health check endpoint

Status:
Required MVP

Labels:
backend, api, testing, mvp, priority-high, difficulty-low

Description:
Add a simple health check endpoint.

Checklist:

* Add `/api/v1/health`
* Return simple status response
* Add basic test for health endpoint

Dependencies:
Issue 6

Estimated difficulty:
Low

Expected deliverable:
Working health endpoint.

Learning goal:
Practice route creation and first API test.

Acceptance criteria:

* `GET /api/v1/health` returns 200
* Response includes status field
* Test passes

---

## Issue 8: Set up API router structure

Status:
Required MVP

Labels:
backend, api, mvp, priority-high, difficulty-low

Description:
Create the central router structure that will organize all API routes.

Checklist:

* Create `app/api/router.py`
* Create `app/api/routes/`
* Move health route into route structure
* Include router in `main.py`

Dependencies:
Issue 7

Estimated difficulty:
Low

Expected deliverable:
Clean route organization.

Learning goal:
Understand modular FastAPI routing.

Acceptance criteria:

* `main.py` stays clean
* health endpoint still works
* route files are organized under `app/api/routes/`

---

## Issue 9: Configure pytest test structure

Status:
Required MVP

Labels:
testing, mvp, priority-high, difficulty-low

Description:
Set up the testing structure for future API, unit, and integration tests.

Checklist:

* Create `tests/conftest.py`
* Create `tests/api/`
* Create `tests/unit/`
* Create `tests/integration/`
* Add first health test
* Document test command in README

Dependencies:
Issue 7

Estimated difficulty:
Low

Expected deliverable:
Testing structure exists and one test passes.

Learning goal:
Learn project-level pytest organization.

Acceptance criteria:

* Tests can be run with one command
* Health test passes
* README includes test command

---

# 6. Milestone 3: Database Foundation

## Issue 10: Add PostgreSQL with Docker Compose

Status:
Required MVP

Labels:
database, docker, mvp, priority-high, difficulty-medium

Description:
Add a local PostgreSQL database using Docker Compose.

Checklist:

* Create `docker-compose.yml`
* Add PostgreSQL service
* Add database name
* Add database user
* Add database password through environment variables
* Document startup command

Dependencies:
Issue 4

Estimated difficulty:
Medium

Expected deliverable:
PostgreSQL runs locally through Docker Compose.

Learning goal:
Learn local database infrastructure setup.

Acceptance criteria:

* Database container starts
* Database is reachable locally
* README documents how to start it

---

## Issue 11: Add SQLAlchemy database session setup

Status:
Required MVP

Labels:
database, backend, mvp, priority-high, difficulty-medium

Description:
Create database connection and session management.

Checklist:

* Add database settings
* Create engine
* Create session factory
* Add database dependency
* Confirm app can connect to database

Dependencies:
Issue 10

Estimated difficulty:
Medium

Expected deliverable:
Application can create database sessions.

Learning goal:
Understand SQLAlchemy sessions and FastAPI database dependencies.

Acceptance criteria:

* Database session dependency exists
* App starts without database import errors
* Connection can be tested

---

## Issue 12: Add Alembic migration setup

Status:
Required MVP

Labels:
database, backend, mvp, priority-high, difficulty-medium

Description:
Set up Alembic for database migrations.

Checklist:

* Install Alembic
* Initialize Alembic
* Configure Alembic database URL
* Connect Alembic to model metadata
* Document migration commands

Dependencies:
Issue 11

Estimated difficulty:
Medium

Expected deliverable:
Alembic migration system ready.

Learning goal:
Learn schema migration management.

Acceptance criteria:

* Alembic folder exists
* Alembic can create a migration
* README documents migration workflow

---

## Issue 13: Create users and golfer profiles models

Status:
Required MVP

Labels:
database, backend, auth, mvp, priority-high, difficulty-medium

Description:
Create the first database models.

Checklist:

* Create user model
* Create golfer profile model
* Add relationship between user and profile
* Add constraints
* Create migration
* Apply migration

Dependencies:
Issue 12

Estimated difficulty:
Medium

Expected deliverable:
Users and golfer profiles tables exist.

Learning goal:
Learn SQLAlchemy model relationships and Alembic migrations.

Acceptance criteria:

* Migration creates users table
* Migration creates golfer_profiles table
* Email is unique
* One user has one golfer profile

---

# 7. Milestone 4: Authentication

## Issue 14: Implement password hashing utilities

Status:
Required MVP

Labels:
auth, backend, mvp, priority-high, difficulty-medium

Description:
Add password hashing and verification utilities.

Checklist:

* Add password hashing function
* Add password verification function
* Add security configuration
* Add unit tests

Dependencies:
Issue 13

Estimated difficulty:
Medium

Expected deliverable:
Password security utilities exist and are tested.

Learning goal:
Learn secure password handling.

Acceptance criteria:

* Plain passwords are not stored
* Hash verification works
* Unit tests pass

---

## Issue 15: Implement user registration endpoint

Status:
Required MVP

Labels:
auth, api, backend, testing, mvp, priority-high, difficulty-medium

Description:
Create the register endpoint.

Checklist:

* Create auth schemas
* Create auth route
* Create auth service
* Create user repository method
* Hash password before saving
* Create golfer profile during registration
* Add API tests

Dependencies:
Issue 14

Estimated difficulty:
Medium

Expected deliverable:
`POST /api/v1/auth/register` works.

Learning goal:
Learn full route-service-repository flow.

Acceptance criteria:

* User can register
* Duplicate email fails
* Password hash is stored
* Password hash is not returned
* Golfer profile is created
* Tests pass

---

## Issue 16: Implement login endpoint

Status:
Required MVP

Labels:
auth, api, backend, testing, mvp, priority-high, difficulty-medium

Description:
Create the login endpoint.

Checklist:

* Accept email and password
* Verify credentials
* Return access token
* Return safe user object
* Add failed login test
* Add successful login test

Dependencies:
Issue 15

Estimated difficulty:
Medium

Expected deliverable:
`POST /api/v1/auth/login` works.

Learning goal:
Understand authentication flow.

Acceptance criteria:

* Valid login returns token
* Invalid login returns 401
* Error does not reveal whether email or password was wrong
* Tests pass

---

## Issue 17: Implement current user dependency and auth/me endpoint

Status:
Required MVP

Labels:
auth, api, backend, testing, mvp, priority-high, difficulty-medium

Description:
Create JWT validation and current user loading.

Checklist:

* Create JWT token creation function
* Create JWT decode function
* Create current user dependency
* Add protected `/auth/me` endpoint
* Add tests for missing token
* Add tests for valid token

Dependencies:
Issue 16

Estimated difficulty:
Medium

Expected deliverable:
Protected routes can access current user.

Learning goal:
Learn JWT auth and FastAPI dependencies.

Acceptance criteria:

* Missing token returns 401
* Invalid token returns 401
* Valid token returns current user
* Tests pass

---

# 8. Milestone 5: Core CRUD

## Issue 18: Implement clubs CRUD

Status:
Required MVP

Labels:
backend, api, database, testing, mvp, priority-high, difficulty-medium

Description:
Build CRUD endpoints for clubs.

Checklist:

* Create club model
* Create club schemas
* Create club repository
* Create club service
* Create club routes
* Add ownership checks
* Add API tests

Dependencies:
Issue 17

Estimated difficulty:
Medium

Expected deliverable:
Current user can manage their clubs.

Learning goal:
Learn user-owned CRUD pattern.

Acceptance criteria:

* User can create club
* User can list own clubs
* User can get own club
* User can update own club
* User can delete own club
* User cannot access another user's club
* Tests pass

---

## Issue 19: Implement swing thoughts CRUD

Status:
Required MVP

Labels:
backend, api, database, testing, mvp, priority-high, difficulty-medium

Description:
Build CRUD-style endpoints for swing thoughts.

Checklist:

* Create swing thought model
* Create schemas
* Create repository
* Create service
* Create routes
* Add retire endpoint
* Add tests

Dependencies:
Issue 17

Estimated difficulty:
Medium

Expected deliverable:
User can create and manage swing thoughts.

Learning goal:
Learn domain-specific CRUD with status transitions.

Acceptance criteria:

* User can create swing thought
* User can list own swing thoughts
* User can update own swing thought
* User can retire swing thought
* User cannot access another user's swing thought
* Tests pass

---

## Issue 20: Implement practice focus areas seed data

Status:
Required MVP

Labels:
database, backend, mvp, priority-medium, difficulty-low

Description:
Add initial practice focus areas.

Checklist:

* Create practice_focus_areas model
* Create migration
* Add seed data approach
* Include driver, irons, wedges, putting, chipping, bunker, course_management

Dependencies:
Issue 12

Estimated difficulty:
Low-medium

Expected deliverable:
Practice focus areas exist in database.

Learning goal:
Learn lookup/reference tables.

Acceptance criteria:

* Focus areas table exists
* Required focus areas are available
* Names are unique

---

## Issue 21: Implement practice sessions CRUD

Status:
Required MVP

Labels:
backend, api, database, testing, mvp, priority-high, difficulty-high

Description:
Build practice session endpoints with focus area support.

Checklist:

* Create practice session model
* Create practice session focus join model
* Create schemas
* Create repository
* Create service
* Create routes
* Add ownership checks
* Add tests

Dependencies:
Issues 17, 20

Estimated difficulty:
High

Expected deliverable:
User can log practice sessions and focus areas.

Learning goal:
Learn parent-child resources and many-to-many relationships with extra fields.

Acceptance criteria:

* User can create practice session
* User can attach focus areas
* User can list own sessions
* User can get own session
* User can update own session
* User can delete own session
* User cannot access another user's session
* Tests pass

---

## Issue 22: Add practice session swing thought linking

Status:
Required MVP

Labels:
backend, api, database, testing, mvp, priority-medium, difficulty-medium

Description:
Allow practice sessions to be linked to swing thoughts.

Checklist:

* Create join table
* Add schemas for linking swing thoughts
* Add service validation
* Ensure swing thoughts belong to current user
* Add tests

Dependencies:
Issues 19, 21

Estimated difficulty:
Medium

Expected deliverable:
Practice sessions can record swing thoughts used.

Learning goal:
Learn many-to-many user-owned relationship validation.

Acceptance criteria:

* User can attach own swing thoughts to practice session
* User cannot attach another user's swing thought
* Duplicate links are prevented
* Tests pass

---

## Issue 23: Implement rounds CRUD

Status:
Required MVP

Labels:
backend, api, database, testing, mvp, priority-high, difficulty-medium

Description:
Build round endpoints.

Checklist:

* Create round model
* Create schemas
* Create repository
* Create service
* Create routes
* Add ownership checks
* Add tests

Dependencies:
Issue 17

Estimated difficulty:
Medium

Expected deliverable:
User can log rounds.

Learning goal:
Learn another user-owned resource and validation rules.

Acceptance criteria:

* User can create round
* User can list own rounds
* User can get own round
* User can update own round
* User can delete own round
* User cannot access another user's round
* Tests pass

---

## Issue 24: Implement round stats endpoints

Status:
Required MVP

Labels:
backend, api, database, testing, mvp, priority-high, difficulty-medium

Description:
Allow users to add stats to rounds.

Checklist:

* Create round stats model
* Create schemas
* Create repository methods
* Create service logic
* Add nested round stats routes
* Add tests

Dependencies:
Issue 23

Estimated difficulty:
Medium

Expected deliverable:
Rounds can have stats.

Learning goal:
Learn one-to-one child resources and validation.

Acceptance criteria:

* User can create stats for own round
* User cannot create stats for another user's round
* User cannot create duplicate stats for same round
* Invalid stats fail validation
* Tests pass

---

## Issue 25: Add round swing thought linking

Status:
Required MVP

Labels:
backend, api, database, testing, mvp, priority-medium, difficulty-medium

Description:
Allow rounds to be linked to swing thoughts used on course.

Checklist:

* Create round_swing_thoughts join table
* Add schema support
* Validate swing thought ownership
* Add tests

Dependencies:
Issues 19, 23

Estimated difficulty:
Medium

Expected deliverable:
Rounds can record swing thoughts used.

Learning goal:
Support practice-to-course transfer analytics.

Acceptance criteria:

* User can attach own swing thoughts to round
* User cannot attach another user's swing thought
* Duplicate links are prevented
* Tests pass

---

# 9. Milestone 6: Analytics

## Issue 26: Implement analytics summary endpoint

Status:
Required MVP

Labels:
analytics, api, backend, testing, mvp, priority-high, difficulty-high

Description:
Create high-level analytics summary.

Checklist:

* Create analytics service
* Calculate scoring average
* Calculate best/worst score
* Calculate average putts
* Calculate average penalties
* Calculate fairway percentage
* Calculate GIR percentage
* Return not_enough_data when appropriate
* Add unit tests
* Add API tests

Dependencies:
Issues 21, 24

Estimated difficulty:
High

Expected deliverable:
`GET /api/v1/analytics/summary` works.

Learning goal:
Learn business logic and aggregation.

Acceptance criteria:

* Summary only uses current user's data
* Correct averages are calculated
* No-data case is handled
* Tests pass

---

## Issue 27: Implement practice breakdown analytics

Status:
Required MVP

Labels:
analytics, api, backend, testing, mvp, priority-high, difficulty-medium

Description:
Show how the user spends practice time.

Checklist:

* Sum practice minutes by focus area
* Calculate percentages
* Support date filters
* Add tests

Dependencies:
Issue 21

Estimated difficulty:
Medium

Expected deliverable:
Practice breakdown endpoint works.

Learning goal:
Learn grouping and aggregation queries.

Acceptance criteria:

* Total practice minutes are correct
* Focus area percentages are correct
* Empty data response works
* Tests pass

---

## Issue 28: Implement trends analytics

Status:
Required MVP

Labels:
analytics, api, backend, testing, mvp, priority-high, difficulty-high

Description:
Compare recent rounds to previous rounds.

Checklist:

* Add window_size parameter
* Compare last N rounds to previous N rounds
* Calculate score change
* Calculate putts change if stats exist
* Calculate penalties change if stats exist
* Handle not enough data
* Add tests

Dependencies:
Issue 24

Estimated difficulty:
High

Expected deliverable:
Trend endpoint works.

Learning goal:
Learn time-window analysis and edge-case handling.

Acceptance criteria:

* Last 3 vs previous 3 works
* Not enough data is handled
* Current user isolation is enforced
* Tests pass

---

## Issue 29: Implement swing thought analytics

Status:
Required MVP

Labels:
analytics, api, backend, testing, mvp, priority-medium, difficulty-high

Description:
Analyze performance around a swing thought.

Checklist:

* Load swing thought owned by current user
* Compare rounds before and after started_at
* Include round usage data if available
* Calculate average score before/after
* Include not enough data handling
* Add tests

Dependencies:
Issues 19, 23, 25

Estimated difficulty:
High

Expected deliverable:
Swing thought analytics endpoint works.

Learning goal:
Learn domain-specific analytics.

Acceptance criteria:

* User can analyze own swing thought
* User cannot analyze another user's swing thought
* Before/after calculation is correct
* Not enough data is handled
* Tests pass

---

# 10. Milestone 7: Recommendations

## Issue 30: Implement recommendation generation service

Status:
Required MVP

Labels:
recommendation, analytics, backend, testing, mvp, priority-high, difficulty-high

Description:
Create rule-based recommendation logic.

Checklist:

* Use analytics summary
* Identify main issue
* Handle high penalties
* Handle high putts
* Handle low GIR
* Handle practice mismatch
* Handle not enough data
* Return explanation and confidence
* Add unit tests

Dependencies:
Issues 26, 27, 28

Estimated difficulty:
High

Expected deliverable:
Recommendation service can generate explainable advice.

Learning goal:
Learn rule-based business logic.

Acceptance criteria:

* High penalties recommend tee shot/control practice
* High putts recommend putting
* Low GIR recommends approach practice
* Not enough data returns honest message
* Explanations include evidence
* Tests pass

---

## Issue 31: Implement recommendation endpoints

Status:
Required MVP

Labels:
recommendation, api, backend, testing, mvp, priority-high, difficulty-medium

Description:
Expose recommendation generation through the API.

Checklist:

* Create recommendation model
* Create schemas
* Create repository
* Create routes
* Add generate endpoint
* Add latest endpoint
* Add list endpoint
* Add tests

Dependencies:
Issue 30

Estimated difficulty:
Medium-high

Expected deliverable:
Recommendation API works.

Learning goal:
Connect analytics-driven business logic to REST API.

Acceptance criteria:

* User can generate recommendation
* Latest recommendation can be retrieved
* Recommendation history can be listed
* Only current user's recommendations are returned
* Tests pass

---

# 11. Milestone 8: Production Readiness

## Issue 32: Add Dockerfile for API

Status:
Required MVP

Labels:
docker, deployment, backend, mvp, priority-medium, difficulty-medium

Description:
Containerize the FastAPI application.

Checklist:

* Add Dockerfile
* Install dependencies
* Run app in container
* Document build/run commands

Dependencies:
Issue 31

Estimated difficulty:
Medium

Expected deliverable:
API can run inside Docker.

Learning goal:
Learn application containerization.

Acceptance criteria:

* Docker image builds
* Container starts
* Health endpoint works from container

---

## Issue 33: Improve Docker Compose for full local stack

Status:
Required MVP

Labels:
docker, database, deployment, mvp, priority-medium, difficulty-medium

Description:
Update Docker Compose to run API and PostgreSQL together.

Checklist:

* Add API service
* Add database service
* Configure environment variables
* Confirm API connects to DB
* Document startup command

Dependencies:
Issue 32

Estimated difficulty:
Medium

Expected deliverable:
Full local stack runs with Docker Compose.

Learning goal:
Learn multi-service local development.

Acceptance criteria:

* One command starts API and database
* Health endpoint works
* Database connection works

---

## Issue 34: Add GitHub Actions test workflow

Status:
Required MVP

Labels:
ci, testing, deployment, mvp, priority-medium, difficulty-medium

Description:
Run tests automatically on push and pull request.

Checklist:

* Create GitHub Actions workflow
* Install dependencies
* Run tests
* Add status badge later if desired

Dependencies:
Issue 31

Estimated difficulty:
Medium

Expected deliverable:
CI test workflow.

Learning goal:
Learn basic CI/CD.

Acceptance criteria:

* Workflow runs on push
* Workflow runs tests
* Failed tests fail the workflow

---

## Issue 35: Add structured logging

Status:
Optional MVP

Labels:
backend, deployment, optional, priority-low, difficulty-medium

Description:
Add basic logging for important API events and errors.

Checklist:

* Configure logger
* Log startup
* Log important service errors
* Avoid logging secrets
* Document logging strategy

Dependencies:
Issue 31

Estimated difficulty:
Medium

Expected deliverable:
Basic application logging.

Learning goal:
Learn production observability basics.

Acceptance criteria:

* Logs are readable
* Secrets are not logged
* Errors are easier to debug

---

## Issue 36: Polish README for portfolio use

Status:
Required MVP

Labels:
documentation, mvp, priority-high, difficulty-low

Description:
Improve README so it is recruiter-friendly.

Checklist:

* Add project overview
* Add architecture summary
* Add tech stack
* Add API examples
* Add setup instructions
* Add test instructions
* Add deployment link later
* Add project status

Dependencies:
Issue 31

Estimated difficulty:
Low-medium

Expected deliverable:
Professional README.

Learning goal:
Learn how to present a technical project.

Acceptance criteria:

* README explains why the project matters
* README shows backend skills
* README includes setup/test instructions

---

# 12. Milestone 9: Deployment

## Issue 37: Choose deployment platform

Status:
Required MVP

Labels:
deployment, documentation, mvp, priority-medium, difficulty-low

Description:
Choose where to deploy the backend.

Checklist:

* Compare Render, Railway, Fly.io, and AWS
* Choose initial platform
* Document decision
* Explain tradeoffs

Dependencies:
Issue 33

Estimated difficulty:
Low

Expected deliverable:
Deployment platform decision.

Learning goal:
Learn deployment tradeoffs.

Acceptance criteria:

* One platform is selected
* Decision is documented
* Rationale is clear

---

## Issue 38: Deploy API and database

Status:
Required MVP

Labels:
deployment, backend, database, mvp, priority-high, difficulty-high

Description:
Deploy the GolfIQ backend.

Checklist:

* Configure production environment variables
* Deploy API
* Connect production database
* Run migrations
* Test health endpoint
* Test auth endpoint
* Document deployment process

Dependencies:
Issue 37

Estimated difficulty:
High

Expected deliverable:
Live backend API.

Learning goal:
Learn real deployment and production configuration.

Acceptance criteria:

* API is reachable online
* Database connection works
* Health endpoint works
* README includes deployment link

---

# 13. Version 2 Backlog Issues

These should not block the MVP.

## V2 Issue: Add goals module

Status:
Postponed Version 2

Reason:
Useful, but not needed for the core MVP.

## V2 Issue: Add round miss patterns

Status:
Postponed Version 2

Reason:
Useful for deeper analytics, but increases data entry complexity.

## V2 Issue: Add recommendation items table

Status:
Postponed Version 2

Reason:
Needed when recommendations become multi-part.

## V2 Issue: Add analytics snapshots

Status:
Postponed Version 2

Reason:
Useful for performance and weekly reports, but on-demand analytics is fine for MVP.

## V2 Issue: Add Redis caching

Status:
Postponed Version 2

Reason:
Only needed after analytics endpoints become expensive.

## V2 Issue: Add weekly reports

Status:
Postponed Version 2

Reason:
Requires background jobs and email.

## V2 Issue: Add coach/player relationships

Status:
Postponed Version 3

Reason:
Requires role-based sharing and permissions.

---

# 14. First 15 GitHub Issues to Add Immediately

Add these first:

1. Add initial project documentation
2. Create initial README
3. Create project folder structure
4. Add Python gitignore and environment example
5. Set up Python virtual environment and dependencies
6. Create FastAPI application entry point
7. Add health check endpoint
8. Set up API router structure
9. Configure pytest test structure
10. Add PostgreSQL with Docker Compose
11. Add SQLAlchemy database session setup
12. Add Alembic migration setup
13. Create users and golfer profiles models
14. Implement password hashing utilities
15. Implement user registration endpoint

Do not create all 38 issues immediately if it feels overwhelming.

Recommended approach:

* Add the first 15 now.
* Add the next batch after authentication is complete.
* Keep Version 2 issues in a backlog.

---

# 15. Recommended First Commit Sequence

## Commit 1

Message:

```text
Add initial project documentation structure
```

Includes:

* docs folder
* planning documents
* README
* .gitignore
* empty app/tests folders

## Commit 2

Message:

```text
Set up FastAPI project foundation
```

Includes:

* app/main.py
* basic app setup
* requirements.txt

## Commit 3

Message:

```text
Add health check endpoint and initial tests
```

Includes:

* health route
* test setup
* first API test

## Commit 4

Message:

```text
Add local PostgreSQL Docker Compose setup
```

Includes:

* docker-compose.yml
* .env.example update
* README setup instructions

## Commit 5

Message:

```text
Configure SQLAlchemy and Alembic
```

Includes:

* DB session setup
* Alembic setup
* migration docs

This commit sequence creates a clean history that shows professional development progress.

---

# 16. Practical 10-Hours-Per-Week Schedule: First 4 Weeks

## Week 1: Documentation and Repo Setup

Target hours:
10

Tasks:

* Finish docs folder
* Add README
* Add `.gitignore`
* Add `.env.example`
* Create initial folder structure
* Make first commit
* Add first 15 GitHub issues

Goal:
Project foundation is complete and organized.

Deliverable:
Repo looks professional before code starts.

---

## Week 2: FastAPI Foundation

Target hours:
10

Tasks:

* Set up Python virtual environment
* Install FastAPI, Uvicorn, pytest
* Create FastAPI app entry point
* Add health endpoint
* Add router structure
* Add first test

Goal:
The backend app runs locally.

Deliverable:
`GET /api/v1/health` works and is tested.

---

## Week 3: Database Local Setup

Target hours:
10

Tasks:

* Add Docker Compose PostgreSQL
* Add `.env.example`
* Configure database URL
* Install SQLAlchemy
* Create database session setup
* Confirm app can connect to database

Goal:
Local database infrastructure is working.

Deliverable:
FastAPI app can connect to PostgreSQL.

---

## Week 4: Alembic and First Models

Target hours:
10

Tasks:

* Install Alembic
* Configure Alembic
* Create users model
* Create golfer_profiles model
* Create first migration
* Apply migration
* Document migration commands

Goal:
The first real database tables exist.

Deliverable:
Users and golfer_profiles tables created through Alembic.

---

# 17. Final Recommendation

The best next action is not to code randomly.

The best next action is:

1. Create `docs/development-task-breakdown.md`
2. Paste this plan into it
3. Commit all documentation
4. Add the first 15 GitHub issues
5. Start Issue 5: Set up Python virtual environment and dependencies

Once Issue 5 begins, the project officially moves from planning into implementation.

The main rule going forward:

```text
One GitHub issue at a time.
One small commit at a time.
Keep the project always runnable.
Keep tests growing with the code.
```