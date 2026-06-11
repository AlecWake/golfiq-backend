# GolfIQ Database Design Specification

## 1. Purpose of This Document

This document defines the database design for the GolfIQ backend.

GolfIQ is a FastAPI/PostgreSQL platform that helps golfers determine whether their practice habits and swing thoughts are improving on-course performance.

The database must support:

* user accounts
* golfer profiles
* clubs
* practice sessions
* swing thoughts
* rounds
* round statistics
* basic analytics
* rule-based recommendations

The main design goal is to create a clean PostgreSQL schema that is realistic for a solo student developer, strong enough for backend engineering resume value, and not overengineered for the MVP.

---

# 2. Database Design Principles

## Principle 1: User Ownership Must Be Clear

Most data in GolfIQ belongs to one user.

Examples:

* clubs
* practice sessions
* swing thoughts
* rounds
* goals
* recommendations

Every user-owned table should either directly contain `user_id` or be connected to a parent record that contains `user_id`.

This supports authorization and prevents users from accessing each other's data.

## Principle 2: MVP Should Avoid Excessive Normalization

Some normalization is good.

Too much normalization early can slow development.

For example, the MVP does not need a fully normalized table for every possible golf concept.

The first version should prioritize:

* users
* practice
* swing thoughts
* rounds
* stats
* analytics

## Principle 3: Analytics Should Be Possible Without Complex Queries

The database should make basic analytics easy:

* scoring average
* average putts
* average penalties
* fairway percentage
* GIR percentage
* practice time by category
* swing thought before/after comparison

If a table design makes these very hard, the schema should be simplified.

## Principle 4: Avoid Premature Tables

Tables for coaches, admin dashboards, audit logs, subscriptions, background reports, and advanced snapshots should be delayed until the core app works.

---

# 3. Review of Proposed Tables From Master Specification

## users

Purpose:
Stores account identity and login-related data.

MVP decision:
Keep.

Reason:
This is required for authentication, ownership, and multi-user behavior.

Notes:
This is one of the most important tables.

---

## golfer_profiles

Purpose:
Stores golf-specific user information such as handicap estimate, scoring goal, dominant miss, and experience level.

MVP decision:
Keep.

Reason:
Separating account data from golf profile data is clean and realistic.

Relationship:
One user has one golfer profile.

---

## practice_sessions

Purpose:
Stores each practice session logged by a golfer.

MVP decision:
Keep.

Reason:
This is one of the core product tables.

---

## practice_focus_areas

Purpose:
Lookup table for areas such as driver, irons, wedges, putting, chipping, bunker, and course management.

MVP decision:
Keep, but keep simple.

Reason:
This allows consistent analytics by category.

Important:
This should be a global lookup table, not user-owned.

---

## practice_session_focuses

Purpose:
Connects practice sessions to focus areas and stores minutes spent per area.

MVP decision:
Keep.

Reason:
This is important for analytics because one practice session may include multiple focus areas.

Example:
A 60-minute session could be:

* 30 minutes driver
* 20 minutes wedges
* 10 minutes putting

This is a good many-to-many design with extra fields.

---

## clubs

Purpose:
Stores clubs owned or used by a user.

MVP decision:
Keep.

Reason:
Club-specific practice tracking is useful and not too difficult.

---

## practice_session_clubs

Purpose:
Connects practice sessions to clubs used.

MVP decision:
Keep, but optional for MVP.

Reason:
This is useful but not as important as practice focus areas.

Recommendation:
Build after basic practice sessions and focus areas are working.

---

## swing_thoughts

Purpose:
Stores swing thoughts as trackable experiments.

MVP decision:
Keep.

Reason:
This is one of the unique differentiators of GolfIQ.

This table helps make the project more interesting than a regular golf stats tracker.

---

## practice_session_swing_thoughts

Purpose:
Connects swing thoughts to practice sessions.

MVP decision:
Keep.

Reason:
A user may test multiple swing thoughts in one practice session, and one swing thought may appear across many sessions.

---

## rounds

Purpose:
Stores rounds played.

MVP decision:
Keep.

Reason:
This is the main on-course performance table.

---

## round_stats

Purpose:
Stores aggregate stats for a round.

MVP decision:
Keep.

Reason:
This keeps the `rounds` table clean and allows stat fields to be optional/expandable.

Alternative:
Stats could be placed directly on `rounds`, but separating them is cleaner and more realistic.

---

## round_miss_patterns

Purpose:
Stores miss types and counts for a round.

MVP decision:
Postpone to Version 2.

Reason:
This is useful but increases input complexity.

The MVP should start with basic stats before detailed miss pattern logging.

---

## goals

Purpose:
Stores user improvement goals.

MVP decision:
Postpone to Version 2.

Reason:
Goals are useful, but not required to prove the core practice-to-course transfer loop.

A simple `scoring_goal` on `golfer_profiles` is enough for MVP.

---

## recommendations

Purpose:
Stores generated practice recommendations.

MVP decision:
Keep, but simple.

Reason:
The project needs recommendations to complete the core product loop.

However, recommendation history can be basic at first.

---

## recommendation_items

Purpose:
Stores individual parts of a recommendation.

MVP decision:
Postpone to Version 2.

Reason:
For MVP, the recommendation can be stored as one record with `primary_focus`, `explanation`, and `confidence_level`.

Splitting recommendation items is better later when recommendations become more detailed.

---

## analytics_snapshots

Purpose:
Stores periodic calculated analytics.

MVP decision:
Postpone.

Reason:
MVP analytics can be calculated on demand.

Snapshots are useful later for performance, weekly reports, and historical summaries.

---

## audit_logs

Purpose:
Tracks important user/system actions.

MVP decision:
Postpone.

Reason:
Useful for production systems, but not needed before the core product exists.

---

# 4. Missing Tables

## round_swing_thoughts

The master spec connects swing thoughts to practice sessions, but not directly to rounds.

This is a missing table.

Purpose:
Tracks which swing thoughts were used during an actual round.

Why it matters:
GolfIQ needs to compare swing thought usage to on-course performance.

A swing thought may work well on the range but fail on the course.

MVP decision:
Add to MVP.

Relationship:
Many-to-many between rounds and swing thoughts.

Fields:

* round_id
* swing_thought_id
* effectiveness_rating
* notes

This table is highly valuable because it supports the unique practice-to-course transfer idea.

---

# 5. Final MVP Database Schema

The MVP should include these tables:

1. users
2. golfer_profiles
3. clubs
4. practice_focus_areas
5. practice_sessions
6. practice_session_focuses
7. practice_session_clubs
8. swing_thoughts
9. practice_session_swing_thoughts
10. rounds
11. round_stats
12. round_swing_thoughts
13. recommendations

These tables are enough to support:

* authentication
* user-owned data
* practice logging
* round logging
* swing thought tracking
* basic analytics
* basic recommendations

---

# 6. MVP Table Definitions

## 6.1 users

Purpose:
Stores account information.

Ownership:
This is the root account table.

Primary key:

* id

Important fields:

* id
* email
* password_hash
* first_name
* last_name
* role
* created_at
* updated_at

Constraints:

* email must be unique
* email must not be null
* password_hash must not be null
* role must not be null

Recommended role values:

* golfer
* admin

Future role:

* coach

Indexes:

* unique index on email
* index on role only later if admin queries require it

Deletion strategy:
Soft delete later if needed.

MVP can use hard delete during development, but production should avoid deleting users casually.

---

## 6.2 golfer_profiles

Purpose:
Stores golf-specific profile data for a user.

Ownership:
Owned by one user.

Primary key:

* id

Foreign keys:

* user_id references users.id

Important fields:

* id
* user_id
* current_handicap_estimate
* scoring_goal
* dominant_miss
* experience_level
* created_at
* updated_at

Constraints:

* user_id must be unique
* one profile per user
* handicap estimate can be nullable
* scoring goal can be nullable

Indexes:

* unique index on user_id

Relationship:
One user has one golfer profile.

Deletion strategy:
Cascade delete if user is deleted.

---

## 6.3 clubs

Purpose:
Stores clubs used by a golfer.

Ownership:
Owned by one user.

Primary key:

* id

Foreign keys:

* user_id references users.id

Important fields:

* id
* user_id
* club_type
* display_name
* estimated_distance
* notes
* created_at
* updated_at

Example club types:

* driver
* fairway_wood
* hybrid
* iron
* wedge
* putter

Constraints:

* user_id must not be null
* club_type must not be null
* display_name must not be null
* estimated_distance should be positive if provided

Indexes:

* index on user_id
* optional composite index on user_id and club_type

Deletion strategy:
Restrict delete if club is referenced in practice_session_clubs, or allow delete with cascade from join table.

Recommendation:
Allow deleting the club record and cascade delete only join-table references.

Do not delete practice sessions.

---

## 6.4 practice_focus_areas

Purpose:
Lookup table for consistent practice categories.

Ownership:
Global table, not user-owned.

Primary key:

* id

Important fields:

* id
* name
* description

Example rows:

* driver
* irons
* wedges
* putting
* chipping
* bunker
* course_management

Constraints:

* name must be unique
* name must not be null

Indexes:

* unique index on name

Deletion strategy:
Restrict delete.

Reason:
Deleting a focus area could break historical practice records.

---

## 6.5 practice_sessions

Purpose:
Stores each practice session.

Ownership:
Owned by one user.

Primary key:

* id

Foreign keys:

* user_id references users.id

Important fields:

* id
* user_id
* date
* duration_minutes
* location
* overall_focus
* quality_rating
* notes
* created_at
* updated_at

Constraints:

* user_id must not be null
* date must not be null
* duration_minutes must be positive
* quality_rating should be between 1 and 5 if provided

Indexes:

* index on user_id
* composite index on user_id and date

Deletion strategy:
Hard delete allowed in MVP with cascade delete on child join rows.

Reason:
If a user deletes a practice session, its focus links, club links, and swing thought links should also be removed.

---

## 6.6 practice_session_focuses

Purpose:
Connects practice sessions to focus areas and stores time allocation.

Ownership:
Indirectly owned through practice_sessions.

Primary key:

* id

Foreign keys:

* practice_session_id references practice_sessions.id
* focus_area_id references practice_focus_areas.id

Important fields:

* id
* practice_session_id
* focus_area_id
* minutes_spent
* intensity_rating

Constraints:

* practice_session_id must not be null
* focus_area_id must not be null
* minutes_spent must be positive
* intensity_rating should be between 1 and 5 if provided
* unique combination of practice_session_id and focus_area_id

Indexes:

* index on practice_session_id
* index on focus_area_id
* composite unique index on practice_session_id and focus_area_id

Relationship:
Many-to-many between practice sessions and focus areas with extra data.

Deletion strategy:
Cascade delete when practice session is deleted.

Restrict delete for focus areas.

---

## 6.7 practice_session_clubs

Purpose:
Connects practice sessions to clubs used.

Ownership:
Indirectly owned through practice_sessions and clubs.

Primary key:

* id

Foreign keys:

* practice_session_id references practice_sessions.id
* club_id references clubs.id

Important fields:

* id
* practice_session_id
* club_id
* balls_hit
* quality_rating
* notes

Constraints:

* practice_session_id must not be null
* club_id must not be null
* balls_hit should be positive if provided
* quality_rating should be between 1 and 5 if provided
* unique combination of practice_session_id and club_id

Indexes:

* index on practice_session_id
* index on club_id
* composite unique index on practice_session_id and club_id

Relationship:
Many-to-many between practice sessions and clubs with extra data.

Deletion strategy:
Cascade delete when practice session is deleted.

Cascade delete join row when club is deleted.

Do not delete the practice session if a club is deleted.

---

## 6.8 swing_thoughts

Purpose:
Stores swing thoughts as trackable experiments.

Ownership:
Owned by one user.

Primary key:

* id

Foreign keys:

* user_id references users.id

Important fields:

* id
* user_id
* title
* description
* category
* status
* started_at
* ended_at
* confidence_rating
* notes
* created_at
* updated_at

Recommended status values:

* active
* testing
* retired
* successful
* harmful
* unknown

Constraints:

* user_id must not be null
* title must not be null
* status must not be null
* confidence_rating should be between 1 and 5 if provided
* ended_at should be after started_at if both exist

Indexes:

* index on user_id
* composite index on user_id and status
* composite index on user_id and started_at

Deletion strategy:
Soft delete or status change is better than hard delete.

Recommendation:
For MVP, use status changes instead of deleting swing thoughts.

Reason:
Swing thoughts are historical experiments. Deleting them would weaken analytics.

---

## 6.9 practice_session_swing_thoughts

Purpose:
Connects swing thoughts to practice sessions.

Ownership:
Indirectly owned through practice_sessions and swing_thoughts.

Primary key:

* id

Foreign keys:

* practice_session_id references practice_sessions.id
* swing_thought_id references swing_thoughts.id

Important fields:

* id
* practice_session_id
* swing_thought_id
* effectiveness_rating
* notes

Constraints:

* practice_session_id must not be null
* swing_thought_id must not be null
* effectiveness_rating should be between 1 and 5 if provided
* unique combination of practice_session_id and swing_thought_id

Indexes:

* index on practice_session_id
* index on swing_thought_id
* composite unique index on practice_session_id and swing_thought_id

Relationship:
Many-to-many between practice sessions and swing thoughts.

Deletion strategy:
Cascade delete when practice session is deleted.

Do not hard delete swing thoughts if they have historical links.

---

## 6.10 rounds

Purpose:
Stores rounds played by the user.

Ownership:
Owned by one user.

Primary key:

* id

Foreign keys:

* user_id references users.id

Important fields:

* id
* user_id
* course_name
* date
* holes_played
* score
* par
* weather
* notes
* created_at
* updated_at

Constraints:

* user_id must not be null
* course_name should not be null
* date must not be null
* holes_played should be 9 or 18
* score must be positive
* par must be positive if provided
* score should be reasonable based on holes played

Recommended application-level score ranges:

* 9 holes: 20 to 90
* 18 holes: 40 to 180

Indexes:

* index on user_id
* composite index on user_id and date
* optional composite index on user_id and course_name

Deletion strategy:
Hard delete allowed in MVP with cascade delete on child records.

Child records:

* round_stats
* round_swing_thoughts
* round_miss_patterns later

---

## 6.11 round_stats

Purpose:
Stores aggregate stats for a round.

Ownership:
Indirectly owned through rounds.

Primary key:

* id

Foreign keys:

* round_id references rounds.id

Important fields:

* id
* round_id
* fairways_hit
* fairways_possible
* greens_in_regulation
* putts
* penalty_strokes
* three_putts
* up_and_down_attempts
* up_and_down_successes
* sand_saves_attempted
* sand_saves_made

Constraints:

* round_id must be unique
* one stats record per round
* fairways_hit cannot exceed fairways_possible
* up_and_down_successes cannot exceed up_and_down_attempts
* sand_saves_made cannot exceed sand_saves_attempted
* all count fields should be zero or positive

Indexes:

* unique index on round_id

Relationship:
One round has one round_stats record.

Deletion strategy:
Cascade delete when round is deleted.

---

## 6.12 round_swing_thoughts

Purpose:
Connects swing thoughts to rounds.

Ownership:
Indirectly owned through rounds and swing_thoughts.

Primary key:

* id

Foreign keys:

* round_id references rounds.id
* swing_thought_id references swing_thoughts.id

Important fields:

* id
* round_id
* swing_thought_id
* effectiveness_rating
* notes

Constraints:

* round_id must not be null
* swing_thought_id must not be null
* effectiveness_rating should be between 1 and 5 if provided
* unique combination of round_id and swing_thought_id

Indexes:

* index on round_id
* index on swing_thought_id
* composite unique index on round_id and swing_thought_id

Relationship:
Many-to-many between rounds and swing thoughts.

Deletion strategy:
Cascade delete when round is deleted.

Do not hard delete swing thoughts if they are historically linked.

---

## 6.13 recommendations

Purpose:
Stores generated practice recommendations.

Ownership:
Owned by one user.

Primary key:

* id

Foreign keys:

* user_id references users.id

Important fields:

* id
* user_id
* generated_at
* primary_focus
* explanation
* confidence_level
* status

Recommended confidence values:

* low
* medium
* high

Recommended status values:

* active
* dismissed
* completed
* archived

Constraints:

* user_id must not be null
* generated_at must not be null
* primary_focus must not be null
* explanation must not be null
* confidence_level must not be null

Indexes:

* index on user_id
* composite index on user_id and generated_at
* composite index on user_id and status

Deletion strategy:
Hard delete allowed in MVP, but archive status is better later.

---

# 7. Relationship Summary

## One-to-One Relationships

### users → golfer_profiles

One user has one golfer profile.

Reason:
Account data and golf-specific data should be separated.

### rounds → round_stats

One round has one stat record.

Reason:
Round identity and round metrics are related but separate concerns.

---

## One-to-Many Relationships

### users → clubs

One user can have many clubs.

### users → practice_sessions

One user can have many practice sessions.

### users → swing_thoughts

One user can have many swing thoughts.

### users → rounds

One user can have many rounds.

### users → recommendations

One user can have many recommendations.

Reason:
These are all user-owned resources.

---

## Many-to-Many Relationships

### practice_sessions ↔ practice_focus_areas

Implemented through:

* practice_session_focuses

Reason:
One session can include multiple focus areas, and one focus area can appear in many sessions.

### practice_sessions ↔ clubs

Implemented through:

* practice_session_clubs

Reason:
One practice session can include multiple clubs, and one club can be used in many sessions.

### practice_sessions ↔ swing_thoughts

Implemented through:

* practice_session_swing_thoughts

Reason:
One session can test multiple swing thoughts, and one swing thought can be tested across many sessions.

### rounds ↔ swing_thoughts

Implemented through:

* round_swing_thoughts

Reason:
One round can involve multiple swing thoughts, and one swing thought can be used across many rounds.

This relationship is important for measuring whether swing thoughts transfer from practice to the course.

---

# 8. Ownership Rules

## Direct Ownership

These tables directly contain `user_id`:

* golfer_profiles
* clubs
* practice_sessions
* swing_thoughts
* rounds
* recommendations

Queries for these records should include both:

* record ID
* current user ID

Example rule:

```text
Find round where id = round_id and user_id = current_user.id
```

Do not query user-owned resources by ID only.

## Indirect Ownership

These tables do not need direct `user_id` because ownership is through a parent table:

* practice_session_focuses
* practice_session_clubs
* practice_session_swing_thoughts
* round_stats
* round_swing_thoughts

When accessing these records, the service should verify ownership through the parent resource.

Example:
To access `round_stats`, first verify that the parent round belongs to the current user.

## Global Tables

These tables are not user-owned:

* practice_focus_areas

They are shared lookup/reference data.

---

# 9. Alembic Migration Order

Recommended migration order:

## Migration 1: Create users

Reason:
All user-owned tables depend on users.

## Migration 2: Create golfer_profiles

Reason:
Depends only on users.

## Migration 3: Create practice_focus_areas

Reason:
Global lookup table needed before practice_session_focuses.

## Migration 4: Create clubs

Reason:
Depends on users.

## Migration 5: Create swing_thoughts

Reason:
Depends on users.

## Migration 6: Create practice_sessions

Reason:
Depends on users.

## Migration 7: Create practice_session_focuses

Reason:
Depends on practice_sessions and practice_focus_areas.

## Migration 8: Create practice_session_clubs

Reason:
Depends on practice_sessions and clubs.

## Migration 9: Create practice_session_swing_thoughts

Reason:
Depends on practice_sessions and swing_thoughts.

## Migration 10: Create rounds

Reason:
Depends on users.

## Migration 11: Create round_stats

Reason:
Depends on rounds.

## Migration 12: Create round_swing_thoughts

Reason:
Depends on rounds and swing_thoughts.

## Migration 13: Create recommendations

Reason:
Depends on users and can be added after analytics/recommendation features start.

This order minimizes foreign key dependency issues.

---

# 10. Indexing Strategy

## Required MVP Indexes

### users.email

Reason:
Login and registration need fast email lookup.

Also required for uniqueness.

### user_id indexes on user-owned tables

Tables:

* clubs
* practice_sessions
* swing_thoughts
* rounds
* recommendations

Reason:
Most queries filter by current user.

### user_id + date indexes

Tables:

* practice_sessions
* rounds

Reason:
Analytics often asks for user data ordered by date.

### user_id + status indexes

Tables:

* swing_thoughts
* recommendations

Reason:
Common queries include active swing thoughts and latest active recommendation.

### round_stats.round_id unique index

Reason:
One stats record per round.

### join table indexes

Tables:

* practice_session_focuses
* practice_session_clubs
* practice_session_swing_thoughts
* round_swing_thoughts

Reason:
Joins need indexes on foreign keys.

## Indexes to Delay

Delay until needed:

* course_name search index
* weather index
* full-text notes search
* analytics snapshot indexes
* coach/player relationship indexes

Reason:
Do not add indexes for queries that do not exist yet.

---

# 11. Data Integrity Rules

## Database-Level Rules

Enforce at database level:

* unique email
* non-null required foreign keys
* non-null required fields
* positive duration_minutes
* holes_played must be 9 or 18
* score must be positive
* quality ratings between 1 and 5
* count stats must be zero or positive
* one round_stats per round
* unique pairs in join tables

Database-level constraints protect data even if application logic has a bug.

## Application-Level Rules

Enforce at application level:

* score is reasonable for holes played
* ended_at must be after started_at
* user cannot attach another user's club to practice
* user cannot attach another user's swing thought to round
* recommendation should not generate if there is not enough data
* fairways_hit cannot exceed fairways_possible
* GIR should not exceed holes played
* putts should be reasonable based on holes played

Some of these can also be database constraints, but application-level validation provides better error messages.

---

# 12. Deletion Strategy

## users

MVP:
Do not focus on deleting users.

Future:
Use soft delete.

Reason:
Deleting a user can remove a large amount of data and complicate analytics.

## golfer_profiles

Cascade delete with user.

Reason:
Profile has no meaning without the user.

## clubs

Allow delete, but only remove join-table references.

Do not delete practice sessions.

Reason:
Historical practice sessions still matter even if the user removes a club from their bag.

## practice_sessions

Allow hard delete in MVP.

Cascade delete:

* practice_session_focuses
* practice_session_clubs
* practice_session_swing_thoughts

Reason:
Child rows have no meaning without the session.

## swing_thoughts

Prefer status change over hard delete.

Reason:
Swing thoughts are historical experiments.

Recommended approach:
Use status values such as retired, harmful, successful, or unknown.

## rounds

Allow hard delete in MVP.

Cascade delete:

* round_stats
* round_swing_thoughts

Reason:
Stats and round swing thoughts have no meaning without the round.

## recommendations

Use status later.

MVP can hard delete or simply keep history.

Recommended:
Use status such as active, dismissed, completed, archived.

---

# 13. Analytics Implications

## Scoring Average

Depends on:

* rounds

Query needs:

* filter by user_id
* average score
* date range optional

Performance concern:
Low for MVP.

Useful index:

* user_id + date

## Last 3 vs Previous 3 Rounds

Depends on:

* rounds

Query needs:

* latest rounds ordered by date
* compare two windows

Performance concern:
Low for MVP.

Useful index:

* user_id + date

## Average Putts

Depends on:

* rounds
* round_stats

Query needs:

* join rounds to round_stats
* filter by user_id
* average putts

Performance concern:
Low for MVP.

Useful index:

* rounds.user_id + rounds.date
* round_stats.round_id

## Average Penalties

Depends on:

* rounds
* round_stats

Query needs:

* join rounds to round_stats
* filter by user_id
* average penalty_strokes

Performance concern:
Low for MVP.

## Fairway Percentage

Depends on:

* rounds
* round_stats

Formula:
fairways_hit / fairways_possible

Need to handle:

* fairways_possible = 0
* missing stats

## GIR Percentage

Depends on:

* rounds
* round_stats

Formula:
greens_in_regulation / holes_played

Need to handle:

* missing stats
* 9-hole vs 18-hole rounds

## Practice Time by Category

Depends on:

* practice_sessions
* practice_session_focuses
* practice_focus_areas

Query needs:

* join sessions to focuses
* group by focus area
* sum minutes_spent
* filter by user_id and date

Useful indexes:

* practice_sessions.user_id + date
* practice_session_focuses.practice_session_id
* practice_session_focuses.focus_area_id

## Swing Thought Before/After

Depends on:

* swing_thoughts
* rounds
* round_swing_thoughts
* practice_session_swing_thoughts

Basic MVP approach:
Compare average score before and after `swing_thought.started_at`.

Better Version 2 approach:
Compare rounds where the swing thought was actually used vs rounds where it was not used.

Performance concern:
Moderate later, low for MVP.

## Recommendation Generation

Depends on:

* rounds
* round_stats
* practice_sessions
* practice_session_focuses
* practice_focus_areas
* swing_thoughts
* round_swing_thoughts

Basic rules:

* high penalties -> tee shot/control practice
* high putts -> putting
* low GIR with low penalties -> approach/irons
* high practice but no improvement -> change drill or focus
* not enough data -> collect more data

---

# 14. Critical Schema Review

## Overengineered for MVP

Postpone:

* audit_logs
* analytics_snapshots
* recommendation_items
* coach/player relationship tables
* admin-specific tables
* subscriptions
* weekly reports
* detailed report tables

These are not needed until the core product is working.

## Underengineered in Original Spec

Missing:

* round_swing_thoughts

Reason:
To evaluate practice-to-course transfer, the system should know which swing thoughts were used during actual rounds.

## Tables That Should Merge for MVP

Recommendation items should merge into recommendations for MVP.

Instead of:

* recommendations
* recommendation_items

Use one `recommendations` table first.

Split later if recommendations become multi-part.

## Tables That Should Split

Round data and round stats should stay split.

Reason:
This keeps the round identity separate from performance metrics.

## Fields to Add

Add to rounds:

* par

Reason:
Score is more useful when compared to par.

Add to round_swing_thoughts:

* effectiveness_rating

Reason:
The user can rate whether a swing thought felt helpful during the round.

Add to practice_session_swing_thoughts:

* effectiveness_rating

Reason:
This helps compare range effectiveness to course effectiveness.

## Fields to Delay

Delay:

* weather
* sand save stats
* up-and-down stats
* detailed miss patterns

These can be included later, but they increase data entry burden.

For MVP, keep them optional if included.

---

# 15. Final MVP Database Recommendation

## Exact MVP Tables

Build these first:

1. users
2. golfer_profiles
3. clubs
4. practice_focus_areas
5. practice_sessions
6. practice_session_focuses
7. swing_thoughts
8. practice_session_swing_thoughts
9. rounds
10. round_stats
11. round_swing_thoughts
12. recommendations

Optional MVP table:
13. practice_session_clubs

Recommendation:
Include `practice_session_clubs` if time allows. It adds useful learning value but is not as important as focus areas and swing thoughts.

## Version 2 Tables

Add later:

* round_miss_patterns
* goals
* recommendation_items
* analytics_snapshots

Version 2 should focus on better analytics.

## Version 3 Tables

Add much later:

* coach_player_relationships
* assigned_drills
* coach_comments
* audit_logs
* weekly_reports
* subscriptions

Version 3 should focus on collaboration, production operations, and SaaS-style features.

---

# 16. Final Database Summary

The GolfIQ MVP database should focus on the core loop:

```text
User
  ↓
Practice Sessions
  ↓
Swing Thoughts
  ↓
Rounds
  ↓
Stats
  ↓
Analytics
  ↓
Recommendations
```

The schema should be relational, but not bloated.

The most important design choices are:

1. Every user-owned table must include clear ownership.
2. Practice sessions and rounds should both connect to swing thoughts.
3. Focus areas should be normalized for analytics.
4. Round stats should be separate from round identity.
5. Recommendation history should be simple in MVP.
6. Analytics snapshots, audit logs, and coach features should be delayed.
7. Indexes should support user/date queries first.
8. Data integrity should be enforced at both the database and application levels.