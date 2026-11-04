# Time to Spare: product and engineering specification

Status: design requirements, not a statement of implemented capabilities.
Read [implementation status](docs/STATUS.md) before selecting a milestone.
The [original product brief](docs/archive/spec.pl.md) is retained in Polish as
design history. This document is the English implementation overview; the archive
retains the detailed acceptance cases and backlog. Resolve requirement conflicts
in an ADR rather than silently dropping constraints.

## Product

Help someone use a short window in a city without exceeding their time, budget
or walking constraints. Return up to three feasible outings, each with one to
three stops and an explicit route back to a chosen entrance before a deadline.

Example: “I am at Kraków Główny. My train leaves at 19:40. I have PLN 45 and
would like a meal and a short walk.” The departure time is entered by the user;
the MVP does not verify train schedules or guarantee a connection.

The initial audience is adults with 45–180 minutes near one station, travelling
on foot. Start with a small audited area in Kraków. Do not imply city-wide
coverage before verifying the data. The current backend uses fictional fixtures.

## Product validation and business scope

The first objective is useful completed outings, not repository stars. After
authorization to contact participants, interview 5–8 prospective users about
actual recent situations, then observe at least five prototype outings. Compare
against their usual maps/manual-search workflow. A preliminary investment signal
is three of five finding the result useful and two willing to use it again.
This is qualitative evidence, not proof of product-market fit.

Measure activation, time to selection, useful completed outings, repeat use at the
next opportunity, no-plan reasons, data errors and cost per accepted plan. Missing
feedback is unknown, not success. Report denominators and response rates.

Future revenue hypotheses include managed hosting, venue deployments and data
maintenance sponsorship. Payments, ads, affiliate ranking and reservations are
outside the pilot. Sponsorship must not silently change recommendations.

## User flow

1. Select a supported start and return entrance; location permission is optional.
2. Enter start time, deadline type/time, budget, pace, walking limit and interests.
3. Confirm exact dates, timezone, return point and buffers. Natural-language input
   proposes values; ambiguous or missing critical values require clarification.
4. Choose from at most three plans with stops, timing, cost, return slack and
   evidence freshness. An empty result is valid.
5. Starting an outing revalidates its time and data. Progress is user-confirmed.
6. Replanning preserves completed stops, spending and immutable previous versions.
7. “Return now” works independently of the LLM, using a confirmed current position.

Results must distinguish facts, estimates and unknowns. Render times, prices and
routes from structured domain values. Explain the station buffer and extra reserve
separately. Never say “you will definitely catch your train.”

Design explicit states for clarification, planning, ready, no feasible plan,
provider failure, outside coverage, stale plan, deadline at risk, offline and
cancelled. An offline snapshot is readable but marked as no longer updating.
Provide a text alternative to maps and keyboard/mobile access.

## Planning invariants

- Domain code is independent of HTTP, database, model SDKs and orchestration.
- Use UTC instants for arithmetic and preserve the IANA timezone for display.
  Reject nonexistent local times and ambiguous times without a selected offset.
- Costs use integer minor units. Unknown is distinct from zero and false.
- `departure` subtracts a boarding buffer; `arrive_by` does not.
- `site_deadline = deadline - boarding_buffer` for departure, otherwise deadline.
  `plan_deadline = site_deadline - reserve`. Return must be at or before it.
- Initial boarding/reserve defaults are 20/10 minutes. These are explicit product
  heuristics to validate in the pilot, not measured station guarantees.
- Walking time is rounded upward after pace and route-uncertainty multipliers.
  Initial multipliers are 1.0 standard, 1.25 relaxed and 1.15 uncertainty.
- A visit must fit wholly inside one opening interval, respecting last admission,
  exceptions, waiting and minimum dwell time. Missing holiday exceptions are unknown.
- Strict budget sums mandatory cost upper bounds. Missing mandatory prices exclude
  the visit. Optional purchases must be separated from the base plan.
- Require directed walking routes between actual entrances, including the return.
  Never substitute straight-line distance for an unavailable walking connection.
- Verify accessibility for both places and legs. Walking routes alone do not prove
  step-free access. Unknown accessibility cannot satisfy a strict requirement.
- Hard constraints cannot be changed to manufacture a feasible answer.

Check direct return first. Prefilter up to 20 candidates, enumerate ordered sets
of 1–3 distinct stops and reject infeasible sequences. Rank feasible plans only;
use preferences, useful visit time, diversity, walking/waiting burden and evidence
quality. Version ranking weights. Return fewer alternatives when appropriate.

Fetch final route geometries for real integrations. If directions and matrix
times differ, recalculate and validate the final artifact again. An independent
validator checks stops, timing, prices, routes, totals, expiry and evidence IDs;
it must not just call the solver again. No arbitrary confidence percentages.

For replanning use current time, confirmed location, spent budget, completed stops
and optimistic concurrency. A stale base version returns HTTP 409. A proposal
becomes active only after acceptance. If the deadline is no longer achievable,
show the estimated lateness rather than a misleading feasible status.

## Data and providers

Audit 30–50 places and station entrances before a live pilot. Every critical fact
needs provenance, verification time and validity. Keep source text, normalized
values and editorial decisions separate. A verified address does not verify hours.

Citypacks define a version, timezone, service polygon, places, return entrances,
opening schedules, prices, visit estimates and source rights. Opening schedules
include weekly intervals, date exceptions, breaks and last admission. Outdoor
locations are not assumed open all day. Prices must describe an actual option.

Adapters: place catalog, routing, maps, optional geocoding/weather, manual deadline,
LLM and embeddings. Routing and map providers remain undecided until coverage,
terms, quotas, cache and attribution requirements are checked. Public map services
must not be assumed unrestricted infrastructure. Unknown redistribution rights
block publication of a dataset. Code, data, photos and models have separate rights.

Expired critical facts cannot support a fresh feasible plan. Withdrawing a source
must remove its chunks from retrieval without waiting for a complete reindex.
Version snapshots and preserve exactly which facts produced each plan.

## Architecture

Use a modular monolith. Implement dependencies when their milestone needs them:

| Layer | Decision |
| --- | --- |
| API | Python 3.12+, FastAPI, Pydantic; uv lockfile |
| Domain | Immutable values, deterministic Python solver and separate validator |
| Storage | PostgreSQL with PostGIS and pgvector; SQLAlchemy and Alembic |
| Background work | Celery and Redis; durable job state and outbox in PostgreSQL |
| AI workflow | LangGraph in the application layer, not a replacement for the queue |
| Web | React, strict TypeScript, Vite, accessible components, TanStack Query |
| Maps | MapLibre with a separately selected data/tile provider |
| Verification | Ruff, strict mypy, pytest, Hypothesis; later Vitest and Playwright |
| Operations | Structured logs, OpenTelemetry, containers when deployment is needed |

The current synchronous fixture endpoint is a deliberate foundation exception.
Production planning runs will be asynchronous. Avoid microservices, Kubernetes
and extra databases without measured need. A LangGraph checkpoint is not evidence
that old time-sensitive data remains valid after resumption.

Persist requests, runs, immutable plan versions, stops, legs, trip sessions,
feedback and outbox events. Use owner/session authorization, unique idempotency
keys and atomic plan acceptance. WGS84 API coordinates use explicit lat/lon;
GeoJSON uses lon/lat. Embedding generations record model revision and dimensions.
Do not mix embedding spaces or add approximate indexes before measurement.

## AI and evaluation

AI may extract intent, retrieve approved places and explain validated alternatives.
It may not invent IDs, prices, hours or routes; decide feasibility; relax constraints;
execute arbitrary code; browse arbitrary URLs; or make bookings.

Workflow: parse intent → validate/clarify → retrieve → load facts/routes → solve
→ independently validate → explain with evidence → validate explanation → ready.
Allow narrow backend tools only. Retrieved content is untrusted data, including
any instructions it contains. Source fetching needs an allowlist and SSRF controls.

Start with two normal model calls: intent and explanation. Allow one schema repair
per stage, four calls maximum per run, plus a total deadline and cost budget.
Retries do not reset budgets. The form and template explanations are fallbacks.

Compare tags/full-text against hybrid lexical/vector retrieval on the same cases.
Embeddings describe places, not authoritative prices or opening hours. Filter
permissions, coverage and freshness before retrieval. Evaluate multilingual models
on Polish queries; record revision, dimensions, metric, latency and license.
Add reranking only after measuring its value.

Explanation claims carry fact and evidence IDs from the selected snapshot. The
renderer inserts numeric values. Citation existence alone is not support: audit
entailment and use neutral templates when explanation grounding fails.

Pilot evaluation targets: 100 intent cases, 50 labeled retrieval queries and 100
planning scenarios. Separate development from frozen holdout, including paraphrase
groups; add geographic/temporal holdouts as coverage grows. Store labels, snapshot,
reviewer, split, rights and limitations. No future-source leakage.

Critical acceptance: zero hard-constraint violations and silent constraint reversals
in the acceptance suite; at least 95% correct critical intent fields or appropriate
clarification. Report retrieval Recall@5/nDCG@5 against baseline, grounding audits,
correct/excessive refusals, latency and cost. Targets are not achieved results.
No model training or personalization claims without a suitable consented dataset.

## API, privacy and reliability

Use versioned JSON REST and generated OpenAPI. Production endpoints cover cities,
return points, guest sessions, intent parsing, planning runs, plan versions, trips,
progress, replanning, acceptance, return routes, feedback and session deletion.
Long operations return 202/run ID; polling uses backoff. Retries require idempotency.

Guest access still requires ownership checks. Use secure session cookies, CSRF
protection where applicable, bounded inputs, rate limits, explicit CORS and SSRF
defenses. Never log session secrets, complete private prompts or precise location
history by default. Location is opt-in and foreground-only. Define retention and
deletion before storing user data; share links are scoped, expiring and revocable.

Workers may retry or crash: the database/outbox is authoritative, not Redis.
Version run inputs, algorithm, prompts/models, source snapshot and buffer policy.
Keep run budgets across retries. Implement provider timeouts and explicit degraded
states; never silently replace missing real data with synthetic output.

## Delivery and acceptance

| Milestone | Deliverable and gate |
| --- | --- |
| M0 | Audit area/providers/rights and 10 initial places; authorize live-data use |
| M1 | Form → fixture catalog → planner → map/list; deterministic checks pass |
| M2 | Real routing and 30–50 audited places; geometry/time and provenance verified |
| M3 | Intent, retrieval, bounded workflow and explanations; holdout/baseline report |
| M4 | Guest sessions, progress, immutable replans and AI-independent return |
| M5 | Staging and five observed outings; fix critical failures and measure cost |
| M6 | Public-beta documentation, licenses, moderation, restore/rollback and release |

Test DST, midnight, holidays, opening breaks, last admission, unknown prices,
unreachable return, stale evidence, delayed start, accessibility, inconsistent
matrix/geometry, concurrent replans, spent budget, worker crash and lost responses.
Test hallucinations, source injection, budget exhaustion, IDOR and model outages.
Use property tests and deliberately corrupted plans to verify the independent
validator. Tests do not require paid providers or live internet.

CI runs lint, formatting, typing, tests, contract checks and packaging. Add actual
database migration/integration, frontend accessibility/E2E, offline AI evaluation
and image/security checks with their corresponding features. Untrusted PRs must
not receive provider credentials. Paid evaluation is separately authorized/budgeted.

Before live operation: TLS, backups, restore exercise, compatible migrations,
rollback, provider/data kill switches and incident runbooks. Initial pilot recovery
targets are RPO 24 hours and RTO 4 hours, not promises until measured. Redis must
be reconstructable; deletion rules must survive database restores.

Publishing source does not certify readiness for a live pilot or public beta.
Keep the README and status accurate. Apache-2.0 is the proposed code license, still
pending an explicit license decision. Keep third-party data rights separate.

## Later work

Group outings from different cities are a separate optimization problem. Verify
each person's round trip and intersect availability after transport buffers.
Respect individual budgets and privacy; one participant cannot relax another's
constraints. GTFS support alone does not imply operator coverage, fare data or
realtime reliability. Do not extend an outing automatically because a train is
reported late. Start with user-entered travel windows before transport integrations.

Current open decisions: real routing/map providers, citypack rights, station
entrances, hosting, model/embedding choice, cost caps, privacy policy, reporting
channel and maintenance ownership. None prevents a clearly labeled fixture demo.
