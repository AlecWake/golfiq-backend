# ADR-009: Separate Recommendation Logic from API Routing

## Status

Accepted

## Context

GolfIQ turns profile, practice, swing-thought, round, and performance data into
recommendations, ranked priorities, practice plans, and weekly schedules. The
logic includes thresholds, evidence strength, deterministic ordering, fallback
guidance, and time allocation. It is expected to evolve more frequently than the
HTTP paths that expose it.

## Decision

Keep recommendation generation and planning in dedicated service modules.
Routers define request parameters and response models, then call the appropriate
service. Recommendation services gather owned data, derive candidates, rank or
deduplicate results, and construct typed response objects. Higher-level planning
services may compose lower-level recommendation or priority services.

Keep the engine deterministic and rules-based for the current feature set. Avoid
embedding recommendation rules in routers or database models.

## Consequences

- Recommendation rules can evolve without changing endpoint definitions.
- Ranking and fallback behavior can be tested through stable API contracts.
- Practice plans and schedules can reuse established priority outputs.
- Deterministic rules are explainable and reproducible.
- Thresholds and rule interactions require deliberate maintenance as the engine
  grows.
- Service composition can repeat database work if query boundaries are not
  reviewed.
- A rules-based engine does not automatically learn from population-level data.

## Alternatives Considered

- **Rules inside route handlers:** initially direct, but mixes transport and
  decision logic and makes reuse difficult.
- **Rules on ORM models:** couples recommendations to persistence objects and
  does not fit multi-record analysis.
- **Machine-learning service:** may become appropriate with sufficient validated
  data, but currently adds training, explainability, monitoring, and deployment
  costs without demonstrated benefit.
