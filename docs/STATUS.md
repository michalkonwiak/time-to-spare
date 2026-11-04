# Implementation status

## Implemented

- Isolated Python project; uv lockfile, Ruff, strict mypy, pytest/Hypothesis.
- Immutable domain models, exact integer cost arithmetic, explicit opening intervals.
- Deterministic enumeration of 1–3 stops, distinct variant sets, bounded candidates.
- Directed routes, explicit buffers, unknown-data exclusion, step-free constraints.
- Independent final-artifact validation, including totals and evidence identifiers.
- Stateless synthetic FastAPI demo, CLI, OpenAPI generation/drift detection.
- CI configuration and optional local Git hooks.

## Not yet implemented

M0 real-data audit; M1 React UI; citypack ingestion/weekly schedule expansion;
provider routing/geometry; PostgreSQL/PostGIS/pgvector; jobs/outbox; sessions;
replanning; RAG/LangGraph; real AI evaluation dataset; deployment and user pilot.

The fixture routes contain no geographic geometry. All evidence IDs refer to
synthetic fixtures, not public sources. No SLA or real-world accuracy is claimed.

## Next bounded increment

Build the citypack schema and importer plus the thin React form/result flow using
the demo contract. Then audit one real supported area before adding live routing.
Keep production jobs/session endpoints distinct from the stateless demo endpoints.

## Foundation verification

Locally verified on Python 3.12: Ruff, strict mypy, all 30 tests, and committed
OpenAPI contract drift detection pass. Combined branch/line coverage is 94.07%.
The wheel and source distribution build successfully. The wheel was also installed
with locked runtime dependencies into a clean environment; its CLI and API import
work outside the repository. CI is configured for Python 3.12–3.14; GitHub CI has
not run yet.
