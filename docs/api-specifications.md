# GolfIQ API Specification

## 1. Purpose of This Document

This document defines the MVP API design for the GolfIQ backend.

GolfIQ is a FastAPI/PostgreSQL backend platform that helps golfers track practice sessions, swing thoughts, rounds, analytics, and recommendations.

The API should be:

* consistent
* secure
* easy to test
* easy to document
* realistic for a solo student developer
* impressive enough to discuss in backend engineering interviews

The MVP API should focus on the core product loop:

```text
User creates account
  ↓
User logs practice sessions
  ↓
User tracks swing thoughts
  ↓
User logs rounds
  ↓
System calculates analytics
  ↓
System generates recommendation
```

---

# 2. API Design Principles

## 2.1 REST Conventions

Use REST-style resource routes.

Good:

```text
GET /rounds
POST /rounds
GET /rounds/{round_id}
PATCH /rounds/{round_id}
DELETE /rounds/{round_id}
```

Avoid:

```text
POST /createRound
GET /getUserRounds
POST /deleteRound
```

## 2.2 Route Naming

Use plural nouns for resources:

```text
/users
/clubs
/practice-sessions
/swing-thoughts
/rounds
/recommendations
```

Use hyphenated route names for multi-word resources:

```text
/practice-sessions
/swing-thoughts
/round-stats
```

## 2.3 API Versioning

Use versioning from the beginning:

```text
/api/v1
```

Example:

```text
GET /api/v1/rounds
```

This makes the project look more professional and allows future versions without breaking clients.

## 2.4 Status Codes

Use standard HTTP status codes.

Common success codes:

```text
200 OK              successful GET/PATCH
201 Created         successful POST that creates a resource
204 No Content      successful DELETE
```

Common error codes:

```text
400 Bad Request        invalid business rule
401 Unauthorized       missing or invalid authentication
403 Forbidden          authenticated but not allowed
404 Not Found          resource does not exist or is not owned by user
409 Conflict           duplicate resource or conflict
422 Unprocessable      request validation error
500 Internal Error     unexpected server error
```

## 2.5 Request and Response Consistency

Use consistent JSON naming.

Recommended:

```text
snake_case
```

Example:

```json
{
  "course_name": "Eagle Ridge",
  "holes_played": 18,
  "penalty_strokes": 3
}
```

## 2.6 Error Response Format

Use one consistent error format:

```json
{
  "error": {
    "code": "ROUND_NOT_FOUND",
    "message": "Round not found.",
    "details": {}
  }
}
```

Examples of error codes:

```text
USER_ALREADY_EXISTS
INVALID_CREDENTIALS
UNAUTHORIZED
FORBIDDEN
ROUND_NOT_FOUND
CLUB_NOT_FOUND
PRACTICE_SESSION_NOT_FOUND
SWING_THOUGHT_NOT_FOUND
NOT_ENOUGH_DATA
VALIDATION_ERROR
```

FastAPI/Pydantic will provide default validation errors at first, but the long-term goal should be consistent application errors.

---

# 3. Authentication Endpoints

## 3.1 Register User

Method:

```text
POST
```

Path:

```text
/api/v1/auth/register
```

Purpose:
Create a new user account.

Auth required:
No.

Request body fields:

```text
email
password
first_name
last_name
```

Response body fields:

```text
id
email
first_name
last_name
role
created_at
```

Success status:

```text
201 Created
```

Possible errors:

```text
409 USER_ALREADY_EXISTS
422 VALIDATION_ERROR
```

Business rules:

* email must be unique
* password must be hashed before storage
* default role is golfer
* password_hash must never be returned

MVP priority:
Required.

---

## 3.2 Login

Method:

```text
POST
```

Path:

```text
/api/v1/auth/login
```

Purpose:
Authenticate user and return access token.

Auth required:
No.

Request body fields:

```text
email
password
```

Response body fields:

```text
access_token
token_type
expires_in
user
```

User object:

```text
id
email
first_name
last_name
role
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 INVALID_CREDENTIALS
422 VALIDATION_ERROR
```

Business rules:

* do not reveal whether email or password was wrong
* return generic invalid credentials message
* password hash comparison happens in auth service

MVP priority:
Required.

---

## 3.3 Get Current User

Method:

```text
GET
```

Path:

```text
/api/v1/auth/me
```

Purpose:
Return currently authenticated user.

Auth required:
Yes.

Request body:
None.

Response body fields:

```text
id
email
first_name
last_name
role
created_at
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
```

Business rules:

* token must be valid
* user must still exist

MVP priority:
Required.

---

## 3.4 Refresh Token

Method:

```text
POST
```

Path:

```text
/api/v1/auth/refresh
```

Purpose:
Refresh an access token.

Auth required:
Depends on refresh-token strategy.

MVP priority:
Postpone.

Reason:
Refresh tokens add complexity. For MVP, use access tokens only.

---

# 4. User and Profile Endpoints

## 4.1 Get Own User Account

Method:

```text
GET
```

Path:

```text
/api/v1/users/me
```

Purpose:
Return account information for current user.

Auth required:
Yes.

Response body fields:

```text
id
email
first_name
last_name
role
created_at
updated_at
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
```

Business rules:

* users can only retrieve themselves through MVP API

MVP priority:
Required.

---

## 4.2 Update Own User Account

Method:

```text
PATCH
```

Path:

```text
/api/v1/users/me
```

Purpose:
Update basic account fields.

Auth required:
Yes.

Request body fields:

```text
first_name
last_name
email
```

Response body fields:

```text
id
email
first_name
last_name
role
updated_at
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
409 EMAIL_ALREADY_EXISTS
422 VALIDATION_ERROR
```

Business rules:

* email must remain unique
* user cannot change role through this endpoint

MVP priority:
Useful but not first.

---

## 4.3 Get Own Golfer Profile

Method:

```text
GET
```

Path:

```text
/api/v1/users/me/profile
```

Purpose:
Return current user's golf-specific profile.

Auth required:
Yes.

Response body fields:

```text
id
user_id
current_handicap_estimate
scoring_goal
dominant_miss
experience_level
created_at
updated_at
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 PROFILE_NOT_FOUND
```

Business rules:

* profile belongs to current user
* profile may be created automatically during registration

MVP priority:
Required.

---

## 4.4 Update Own Golfer Profile

Method:

```text
PATCH
```

Path:

```text
/api/v1/users/me/profile
```

Purpose:
Update golf-specific profile data.

Auth required:
Yes.

Request body fields:

```text
current_handicap_estimate
scoring_goal
dominant_miss
experience_level
```

Response body fields:

```text
id
user_id
current_handicap_estimate
scoring_goal
dominant_miss
experience_level
updated_at
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
422 VALIDATION_ERROR
```

Business rules:

* handicap estimate can be nullable
* scoring goal can be nullable
* user cannot update another user's profile

MVP priority:
Required.

---

# 5. Club Endpoints

## 5.1 Create Club

Method:

```text
POST
```

Path:

```text
/api/v1/clubs
```

Purpose:
Create a club for the current user.

Auth required:
Yes.

Request body fields:

```text
club_type
display_name
estimated_distance
notes
```

Response body fields:

```text
id
user_id
club_type
display_name
estimated_distance
notes
created_at
updated_at
```

Success status:

```text
201 Created
```

Possible errors:

```text
401 UNAUTHORIZED
422 VALIDATION_ERROR
```

Business rules:

* club belongs to current user
* estimated_distance must be positive if provided

MVP priority:
Required, but after auth.

---

## 5.2 List Clubs

Method:

```text
GET
```

Path:

```text
/api/v1/clubs
```

Purpose:
List current user's clubs.

Auth required:
Yes.

Query parameters:

```text
club_type
limit
offset
```

Response body fields:

```text
items
total
limit
offset
```

Each item:

```text
id
club_type
display_name
estimated_distance
notes
created_at
updated_at
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
422 VALIDATION_ERROR
```

Business rules:

* only return clubs owned by current user

MVP priority:
Required.

---

## 5.3 Get Club by ID

Method:

```text
GET
```

Path:

```text
/api/v1/clubs/{club_id}
```

Purpose:
Return one club.

Auth required:
Yes.

Response body fields:

```text
id
user_id
club_type
display_name
estimated_distance
notes
created_at
updated_at
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 CLUB_NOT_FOUND
```

Business rules:

* return 404 if club does not exist or is not owned by current user

MVP priority:
Required.

---

## 5.4 Update Club

Method:

```text
PATCH
```

Path:

```text
/api/v1/clubs/{club_id}
```

Purpose:
Update a club.

Auth required:
Yes.

Request body fields:

```text
club_type
display_name
estimated_distance
notes
```

Response body fields:
Same as club response.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 CLUB_NOT_FOUND
422 VALIDATION_ERROR
```

Business rules:

* user can only update own club
* estimated_distance must be positive if provided

MVP priority:
Required.

---

## 5.5 Delete Club

Method:

```text
DELETE
```

Path:

```text
/api/v1/clubs/{club_id}
```

Purpose:
Delete a club.

Auth required:
Yes.

Response body:
None.

Success status:

```text
204 No Content
```

Possible errors:

```text
401 UNAUTHORIZED
404 CLUB_NOT_FOUND
```

Business rules:

* user can only delete own club
* deleting a club should not delete practice sessions
* join-table references may be removed

MVP priority:
Useful.

---

# 6. Swing Thought Endpoints

## 6.1 Create Swing Thought

Method:

```text
POST
```

Path:

```text
/api/v1/swing-thoughts
```

Purpose:
Create a swing thought experiment.

Auth required:
Yes.

Request body fields:

```text
title
description
category
status
started_at
confidence_rating
notes
```

Response body fields:

```text
id
user_id
title
description
category
status
started_at
ended_at
confidence_rating
notes
created_at
updated_at
```

Success status:

```text
201 Created
```

Possible errors:

```text
401 UNAUTHORIZED
422 VALIDATION_ERROR
```

Business rules:

* swing thought belongs to current user
* default status can be testing
* confidence_rating must be between 1 and 5 if provided

MVP priority:
Required.

---

## 6.2 List Swing Thoughts

Method:

```text
GET
```

Path:

```text
/api/v1/swing-thoughts
```

Purpose:
List current user's swing thoughts.

Auth required:
Yes.

Query parameters:

```text
status
category
limit
offset
```

Response body fields:

```text
items
total
limit
offset
```

Each item:
Swing thought response object.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
422 VALIDATION_ERROR
```

Business rules:

* only return current user's swing thoughts
* support filtering by status

MVP priority:
Required.

---

## 6.3 Get Swing Thought by ID

Method:

```text
GET
```

Path:

```text
/api/v1/swing-thoughts/{swing_thought_id}
```

Purpose:
Return one swing thought.

Auth required:
Yes.

Response body fields:
Swing thought response object.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 SWING_THOUGHT_NOT_FOUND
```

Business rules:

* return 404 if not owned by current user

MVP priority:
Required.

---

## 6.4 Update Swing Thought

Method:

```text
PATCH
```

Path:

```text
/api/v1/swing-thoughts/{swing_thought_id}
```

Purpose:
Update swing thought details.

Auth required:
Yes.

Request body fields:

```text
title
description
category
status
started_at
ended_at
confidence_rating
notes
```

Response body fields:
Swing thought response object.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 SWING_THOUGHT_NOT_FOUND
422 VALIDATION_ERROR
```

Business rules:

* user can only update own swing thought
* ended_at should be after started_at
* confidence_rating must be between 1 and 5 if provided

MVP priority:
Required.

---

## 6.5 Retire Swing Thought

Method:

```text
POST
```

Path:

```text
/api/v1/swing-thoughts/{swing_thought_id}/retire
```

Purpose:
Mark swing thought as retired.

Auth required:
Yes.

Request body fields:

```text
ended_at
notes
```

Response body fields:
Swing thought response object.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 SWING_THOUGHT_NOT_FOUND
422 VALIDATION_ERROR
```

Business rules:

* status becomes retired
* ended_at is set
* do not hard delete swing thoughts by default

MVP priority:
Useful.

---

## 6.6 Delete Swing Thought

Method:

```text
DELETE
```

Path:

```text
/api/v1/swing-thoughts/{swing_thought_id}
```

MVP priority:
Postpone or avoid.

Reason:
Swing thoughts are historical experiments. Retiring is better than deleting.

---

# 7. Practice Session Endpoints

## 7.1 Create Practice Session

Method:

```text
POST
```

Path:

```text
/api/v1/practice-sessions
```

Purpose:
Create a practice session.

Auth required:
Yes.

Request body fields:

```text
date
duration_minutes
location
overall_focus
quality_rating
notes
focus_areas
club_ids
swing_thought_ids
```

Optional nested focus area item:

```text
focus_area_id
minutes_spent
intensity_rating
```

Response body fields:

```text
id
user_id
date
duration_minutes
location
overall_focus
quality_rating
notes
focus_areas
clubs
swing_thoughts
created_at
updated_at
```

Success status:

```text
201 Created
```

Possible errors:

```text
401 UNAUTHORIZED
404 CLUB_NOT_FOUND
404 SWING_THOUGHT_NOT_FOUND
422 VALIDATION_ERROR
```

Business rules:

* user can only attach own clubs
* user can only attach own swing thoughts
* duration_minutes must be positive
* quality_rating must be between 1 and 5 if provided
* focus area minutes should not exceed total duration by a large amount

MVP priority:
Required.

---

## 7.2 List Practice Sessions

Method:

```text
GET
```

Path:

```text
/api/v1/practice-sessions
```

Purpose:
List current user's practice sessions.

Auth required:
Yes.

Query parameters:

```text
start_date
end_date
focus_area_id
limit
offset
```

Response body fields:

```text
items
total
limit
offset
```

Each item:
Practice session summary.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
422 VALIDATION_ERROR
```

Business rules:

* only return current user's sessions
* default sort should be newest first

MVP priority:
Required.

---

## 7.3 Get Practice Session by ID

Method:

```text
GET
```

Path:

```text
/api/v1/practice-sessions/{session_id}
```

Purpose:
Return one practice session with details.

Auth required:
Yes.

Response body fields:
Full practice session response.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 PRACTICE_SESSION_NOT_FOUND
```

Business rules:

* return 404 if not owned by current user

MVP priority:
Required.

---

## 7.4 Update Practice Session

Method:

```text
PATCH
```

Path:

```text
/api/v1/practice-sessions/{session_id}
```

Purpose:
Update basic practice session fields.

Auth required:
Yes.

Request body fields:

```text
date
duration_minutes
location
overall_focus
quality_rating
notes
```

Response body fields:
Practice session response.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 PRACTICE_SESSION_NOT_FOUND
422 VALIDATION_ERROR
```

Business rules:

* user can only update own session
* updating linked clubs/focuses/swing thoughts may be separate later

MVP priority:
Required.

---

## 7.5 Delete Practice Session

Method:

```text
DELETE
```

Path:

```text
/api/v1/practice-sessions/{session_id}
```

Purpose:
Delete a practice session.

Auth required:
Yes.

Response body:
None.

Success status:

```text
204 No Content
```

Possible errors:

```text
401 UNAUTHORIZED
404 PRACTICE_SESSION_NOT_FOUND
```

Business rules:

* user can only delete own session
* child join rows should be deleted with it

MVP priority:
Useful.

---

# 8. Round Endpoints

## 8.1 Create Round

Method:

```text
POST
```

Path:

```text
/api/v1/rounds
```

Purpose:
Create a round.

Auth required:
Yes.

Request body fields:

```text
course_name
date
holes_played
score
par
weather
notes
swing_thought_ids
```

Response body fields:

```text
id
user_id
course_name
date
holes_played
score
par
weather
notes
swing_thoughts
created_at
updated_at
```

Success status:

```text
201 Created
```

Possible errors:

```text
401 UNAUTHORIZED
404 SWING_THOUGHT_NOT_FOUND
422 VALIDATION_ERROR
```

Business rules:

* user can only attach own swing thoughts
* holes_played must be 9 or 18
* score must be positive
* score should be reasonable for holes played
* par must be positive if provided

MVP priority:
Required.

---

## 8.2 List Rounds

Method:

```text
GET
```

Path:

```text
/api/v1/rounds
```

Purpose:
List current user's rounds.

Auth required:
Yes.

Query parameters:

```text
start_date
end_date
course_name
limit
offset
```

Response body fields:

```text
items
total
limit
offset
```

Each item:
Round summary.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
422 VALIDATION_ERROR
```

Business rules:

* only return current user's rounds
* default sort newest first

MVP priority:
Required.

---

## 8.3 Get Round by ID

Method:

```text
GET
```

Path:

```text
/api/v1/rounds/{round_id}
```

Purpose:
Return one round with details.

Auth required:
Yes.

Response body fields:
Full round response including stats if available.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 ROUND_NOT_FOUND
```

Business rules:

* return 404 if round is not owned by user

MVP priority:
Required.

---

## 8.4 Update Round

Method:

```text
PATCH
```

Path:

```text
/api/v1/rounds/{round_id}
```

Purpose:
Update a round.

Auth required:
Yes.

Request body fields:

```text
course_name
date
holes_played
score
par
weather
notes
```

Response body fields:
Round response.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 ROUND_NOT_FOUND
422 VALIDATION_ERROR
```

Business rules:

* user can only update own round
* score must stay valid
* changing holes played may affect stats validation

MVP priority:
Required.

---

## 8.5 Delete Round

Method:

```text
DELETE
```

Path:

```text
/api/v1/rounds/{round_id}
```

Purpose:
Delete a round.

Auth required:
Yes.

Response body:
None.

Success status:

```text
204 No Content
```

Possible errors:

```text
401 UNAUTHORIZED
404 ROUND_NOT_FOUND
```

Business rules:

* user can only delete own round
* round stats and round swing thought links should be deleted with it

MVP priority:
Useful.

---

# 9. Round Stats Endpoints

## 9.1 Create Round Stats

Method:

```text
POST
```

Path:

```text
/api/v1/rounds/{round_id}/stats
```

Purpose:
Create stats for an existing round.

Auth required:
Yes.

Request body fields:

```text
fairways_hit
fairways_possible
greens_in_regulation
putts
penalty_strokes
three_putts
up_and_down_attempts
up_and_down_successes
sand_saves_attempted
sand_saves_made
```

Response body fields:

```text
id
round_id
fairways_hit
fairways_possible
greens_in_regulation
putts
penalty_strokes
three_putts
up_and_down_attempts
up_and_down_successes
sand_saves_attempted
sand_saves_made
```

Success status:

```text
201 Created
```

Possible errors:

```text
401 UNAUTHORIZED
404 ROUND_NOT_FOUND
409 ROUND_STATS_ALREADY_EXIST
422 VALIDATION_ERROR
```

Business rules:

* round must belong to current user
* one stats record per round
* fairways_hit cannot exceed fairways_possible
* GIR cannot exceed holes_played
* putts must be nonnegative
* penalties must be nonnegative

MVP priority:
Required.

---

## 9.2 Update Round Stats

Method:

```text
PATCH
```

Path:

```text
/api/v1/rounds/{round_id}/stats
```

Purpose:
Update stats for a round.

Auth required:
Yes.

Request body fields:
Same as create stats, all optional.

Response body fields:
Round stats response.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 ROUND_NOT_FOUND
404 ROUND_STATS_NOT_FOUND
422 VALIDATION_ERROR
```

Business rules:

* round must belong to current user
* stat values must remain valid

MVP priority:
Required.

---

## 9.3 Get Round Stats

Method:

```text
GET
```

Path:

```text
/api/v1/rounds/{round_id}/stats
```

Purpose:
Return stats for a round.

Auth required:
Yes.

Response body fields:
Round stats response.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 ROUND_NOT_FOUND
404 ROUND_STATS_NOT_FOUND
```

Business rules:

* round must belong to current user

MVP priority:
Required.

---

# 10. Analytics Endpoints

## 10.1 Analytics Summary

Method:

```text
GET
```

Path:

```text
/api/v1/analytics/summary
```

Purpose:
Return high-level performance summary for current user.

Auth required:
Yes.

Query parameters:

```text
start_date
end_date
```

Response body fields:

```text
round_count
practice_session_count
scoring_average
best_score
worst_score
average_putts
average_penalties
fairway_percentage
gir_percentage
total_practice_minutes
not_enough_data
message
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
422 VALIDATION_ERROR
```

Business rules:

* only use current user's data
* handle users with no rounds
* clearly return not_enough_data when needed

MVP priority:
Required.

---

## 10.2 Trends

Method:

```text
GET
```

Path:

```text
/api/v1/analytics/trends
```

Purpose:
Return trend comparison such as last 3 rounds vs previous 3.

Auth required:
Yes.

Query parameters:

```text
window_size
```

Response body fields:

```text
current_window
previous_window
score_change
putts_change
penalties_change
trend_summary
not_enough_data
message
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
422 VALIDATION_ERROR
```

Business rules:

* default window_size can be 3
* if not enough rounds exist, return not_enough_data
* do not fake trend analysis with too little data

MVP priority:
Required.

---

## 10.3 Practice Breakdown

Method:

```text
GET
```

Path:

```text
/api/v1/analytics/practice-breakdown
```

Purpose:
Show how practice time is distributed.

Auth required:
Yes.

Query parameters:

```text
start_date
end_date
```

Response body fields:

```text
total_minutes
focus_area_breakdown
```

Focus area item:

```text
focus_area
minutes
percentage
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
422 VALIDATION_ERROR
```

Business rules:

* only current user's practice sessions
* include zero-data response when no practice exists

MVP priority:
Required.

---

## 10.4 Swing Thought Analytics

Method:

```text
GET
```

Path:

```text
/api/v1/analytics/swing-thoughts/{swing_thought_id}
```

Purpose:
Show basic performance before/after a swing thought.

Auth required:
Yes.

Response body fields:

```text
swing_thought_id
title
started_at
rounds_before
rounds_after
average_score_before
average_score_after
average_penalties_before
average_penalties_after
user_effectiveness_average
not_enough_data
message
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 SWING_THOUGHT_NOT_FOUND
422 VALIDATION_ERROR
```

Business rules:

* swing thought must belong to current user
* return not_enough_data if comparison is not meaningful

MVP priority:
High, but after basic analytics.

---

# 11. Recommendation Endpoints

## 11.1 Generate Recommendation

Method:

```text
POST
```

Path:

```text
/api/v1/recommendations/generate
```

Purpose:
Generate a practice recommendation based on current user's data.

Auth required:
Yes.

Request body fields:
None required for MVP.

Optional fields later:

```text
goal
date_range
```

Response body fields:

```text
id
generated_at
primary_focus
explanation
confidence_level
status
evidence
not_enough_data
message
```

Evidence fields:

```text
round_count
average_score
average_putts
average_penalties
practice_breakdown
main_issue
```

Success status:

```text
201 Created
```

Possible errors:

```text
401 UNAUTHORIZED
422 VALIDATION_ERROR
```

Business rules:

* only use current user's data
* recommendation must include evidence
* if not enough data, return useful message
* do not generate fake certainty

MVP priority:
Required after analytics.

---

## 11.2 Get Latest Recommendation

Method:

```text
GET
```

Path:

```text
/api/v1/recommendations/latest
```

Purpose:
Return most recent recommendation.

Auth required:
Yes.

Response body fields:
Recommendation response.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 RECOMMENDATION_NOT_FOUND
```

Business rules:

* only return current user's recommendation

MVP priority:
Useful.

---

## 11.3 List Recommendation History

Method:

```text
GET
```

Path:

```text
/api/v1/recommendations
```

Purpose:
List prior recommendations.

Auth required:
Yes.

Query parameters:

```text
status
limit
offset
```

Response body fields:

```text
items
total
limit
offset
```

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
422 VALIDATION_ERROR
```

Business rules:

* only current user's recommendations
* newest first

MVP priority:
Useful but can be after generate/latest.

---

## 11.4 Update Recommendation Status

Method:

```text
PATCH
```

Path:

```text
/api/v1/recommendations/{recommendation_id}/status
```

Purpose:
Update recommendation status.

Auth required:
Yes.

Request body fields:

```text
status
```

Response body fields:
Recommendation response.

Success status:

```text
200 OK
```

Possible errors:

```text
401 UNAUTHORIZED
404 RECOMMENDATION_NOT_FOUND
422 VALIDATION_ERROR
```

Business rules:

* status must be valid
* recommendation must belong to current user

MVP priority:
Postpone.

---

# 12. Pagination and Filtering Strategy

## Pagination Format

Use `limit` and `offset` for MVP.

Example:

```text
GET /api/v1/rounds?limit=20&offset=0
```

Response:

```json
{
  "items": [],
  "total": 0,
  "limit": 20,
  "offset": 0
}
```

## Default Values

Recommended defaults:

```text
limit = 20
offset = 0
max_limit = 100
```

## Filtering

Support filtering where it directly helps the MVP.

Rounds:

```text
start_date
end_date
course_name
```

Practice sessions:

```text
start_date
end_date
focus_area_id
```

Swing thoughts:

```text
status
category
```

Clubs:

```text
club_type
```

Recommendations:

```text
status
```

Do not build advanced search in MVP.

---

# 13. Ownership and Authorization Rules

## Global Rule

Every protected endpoint must load the current user from the JWT.

## User-Owned Resources

These resources must always be filtered by current user:

```text
clubs
practice_sessions
swing_thoughts
rounds
recommendations
```

## Parent-Owned Resources

These resources require parent ownership checks:

```text
round_stats
practice_session_focuses
practice_session_clubs
practice_session_swing_thoughts
round_swing_thoughts
```

Example:

Before creating stats for a round:

```text
Verify round_id belongs to current user.
Then create stats.
```

## 404 vs 403

For user-owned resources, prefer `404 Not Found` when the resource does not belong to the current user.

Reason:
This avoids revealing that another user's resource exists.

Use `403 Forbidden` mainly for role-based restrictions later.

---

# 14. Validation Rules

## Account Validation

* email must be valid
* password must meet minimum length
* first_name and last_name should not be empty

## Club Validation

* estimated_distance must be positive if provided
* club_type should be one of supported values

## Practice Session Validation

* duration_minutes must be positive
* quality_rating must be 1 through 5 if provided
* date must be valid
* focus area minutes should be positive

## Swing Thought Validation

* title is required
* status must be valid
* confidence_rating must be 1 through 5 if provided
* ended_at must be after started_at if both provided

## Round Validation

* holes_played must be 9 or 18
* score must be positive
* par must be positive if provided
* score should be reasonable for number of holes

## Round Stats Validation

* counts must be zero or positive
* fairways_hit cannot exceed fairways_possible
* GIR cannot exceed holes_played
* three_putts cannot exceed holes_played
* up_and_down_successes cannot exceed attempts
* sand_saves_made cannot exceed attempted

## Recommendation Validation

* status must be valid
* confidence level must be valid
* generated recommendation must include explanation

---

# 15. Endpoints to Postpone

## Postpone to Version 2

```text
/goals
/round-miss-patterns
/recommendation-items
/analytics/weaknesses
/analytics/goals/{goal_id}
/reports
```

Reason:
Useful, but not needed for the first working product.

## Postpone to Version 3

```text
/coach/players
/coach/drills
/coach/comments
/admin/users
/admin/audit-logs
/admin/system-health
/subscriptions
/billing
```

Reason:
These require more roles, permissions, and product complexity.

---

# 16. Final MVP Endpoint Build Order

Build in this order.

## Stage 1: Health and Auth

```text
GET  /api/v1/health
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

## Stage 2: User Profile

```text
GET   /api/v1/users/me
PATCH /api/v1/users/me
GET   /api/v1/users/me/profile
PATCH /api/v1/users/me/profile
```

## Stage 3: Clubs

```text
POST   /api/v1/clubs
GET    /api/v1/clubs
GET    /api/v1/clubs/{club_id}
PATCH  /api/v1/clubs/{club_id}
DELETE /api/v1/clubs/{club_id}
```

## Stage 4: Swing Thoughts

```text
POST  /api/v1/swing-thoughts
GET   /api/v1/swing-thoughts
GET   /api/v1/swing-thoughts/{swing_thought_id}
PATCH /api/v1/swing-thoughts/{swing_thought_id}
POST  /api/v1/swing-thoughts/{swing_thought_id}/retire
```

## Stage 5: Practice Sessions

```text
POST   /api/v1/practice-sessions
GET    /api/v1/practice-sessions
GET    /api/v1/practice-sessions/{session_id}
PATCH  /api/v1/practice-sessions/{session_id}
DELETE /api/v1/practice-sessions/{session_id}
```

## Stage 6: Rounds and Stats

```text
POST   /api/v1/rounds
GET    /api/v1/rounds
GET    /api/v1/rounds/{round_id}
PATCH  /api/v1/rounds/{round_id}
DELETE /api/v1/rounds/{round_id}

POST  /api/v1/rounds/{round_id}/stats
GET   /api/v1/rounds/{round_id}/stats
PATCH /api/v1/rounds/{round_id}/stats
```

## Stage 7: Analytics

```text
GET /api/v1/analytics/summary
GET /api/v1/analytics/trends
GET /api/v1/analytics/practice-breakdown
GET /api/v1/analytics/swing-thoughts/{swing_thought_id}
```

## Stage 8: Recommendations

```text
POST /api/v1/recommendations/generate
GET  /api/v1/recommendations/latest
GET  /api/v1/recommendations
```

---

# 17. API Summary

The GolfIQ API should be built around a simple, secure, user-owned resource model.

The MVP API should prove:

1. A user can create an account.
2. A user can log practice sessions.
3. A user can track swing thoughts.
4. A user can log rounds and stats.
5. The system can calculate trends.
6. The system can generate an explainable recommendation.

The API should avoid unnecessary coach, admin, subscription, and report endpoints until the core golfer workflow is working.

The most important backend engineering value comes from:

* clean REST design
* JWT authentication
* ownership-based authorization
* validation
* relational data modeling
* analytics endpoints
* explainable recommendation endpoint
* consistent tests
* clear documentation