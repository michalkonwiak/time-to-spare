# Implementation status

## Implemented

- Python backend with uv lockfile, Ruff, strict mypy and pytest/Hypothesis.
- Immutable domain models, integer costs, dated opening windows and UTC arithmetic.
- Deterministic 1–3-stop planning with directed routes, buffers and hard constraints.
- Independent final-plan validator; unknown data is not treated as verified.
- Versioned synthetic citypack, bounded local importer and committed JSON Schema.
- Packaged fixture resource shared by CLI and HTTP; no network or provider keys.
- Stateless API with catalog, example input, plans and server-calculated return context.
- React/TypeScript form, up to three result timelines and comparison selection.
- Budget/pace/walking/accessibility controls, explicit synthetic labels and assumptions.
- Loading, cancellation, no-plan, validation and network-failure/retry states.
- Input changes cancel pending requests and discard old results.
- Generated OpenAPI client types and API/citypack/client drift checks.
- Responsive desktop/mobile layout, keyboard flow and automated accessibility checks.
- Combined localhost launcher; backend/frontend checks, builds and E2E in Git hooks/CI.

The M1 synthetic form-to-result flow is implemented using a text timeline instead
of a map. Choosing a preview does not begin a live trip or persist a selection.

## Not yet implemented

M0 real-data audit; real citypacks with field-level rights/provenance and geography;
weekly schedules/holiday expansion; provider routing/geometry and map;
PostgreSQL/PostGIS/pgvector; durable jobs/outbox; guest ownership and trip sessions;
replanning; RAG/LangGraph; AI evaluation datasets; deployment and a user pilot.

Fixture schema v1 intentionally rejects non-synthetic packs. Its 20-place bound
matches the current solver candidate snapshot, not a future whole-city catalog.
All evidence IDs describe fictional fixtures. No real-world navigation or SLA is claimed.

## Verification

The foundation CI passed on Python 3.12–3.14 before this increment.
For the web/citypack increment, local verification on Python 3.12 and Node 24:

- 56 Python tests pass; combined branch/line coverage 96.52%.
- 9 frontend unit tests pass, including exact budget parsing and timezone formatting.
- 14 Playwright cases pass across desktop and mobile Chromium against the real API.
- Automated axe checks report no violations in tested result states; this is not a
  complete accessibility certification. Desktop/mobile screenshots were reviewed.
- Ruff, mypy strict, ESLint, TypeScript strict and Prettier pass.
- API, citypack and generated browser contract checks pass.
- Python sdist/wheel and production web bundle build successfully.
- The installed wheel loads the citypack and runs the CLI outside the source tree.
- The combined launcher starts both services and Ctrl+C stops both.

CI also runs these checks on a clean checkout; consult the branch's Actions run
for the result associated with its exact commit.

## Next bounded increment

Prepare the real-data adapter boundary: service-area/entrance schema, provenance
per fact, source-rights registry and explicit schedule exceptions. Audit a small
supported area before adding live routing. Keep the synthetic demo independently
runnable. Do not start AI retrieval until facts and baseline comparisons are ready.
