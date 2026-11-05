# Time to Spare

Deterministic short-trip planning with explicit return buffers and evidence.

**Status: working web demo with synthetic data. Not a live travel service.**
All places, prices and routes are fictional. Do not use the output for navigation.
No LLM calls, paid APIs, accounts, database, or background tracking are enabled.

## Run locally

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), Python 3.12
and Node 24 (npm included). The combined launcher supports macOS and Linux.

```sh
make bootstrap web-bootstrap
make hooks
make demo-web
```

Open http://127.0.0.1:5173. Set your time window, budget, walking limit and interests,
then compare up to three outings. The timeline shows visits, costs, return time,
station buffer and extra reserve. Selecting a preview does not start a live trip.
Editing inputs cancels pending work and removes outdated results.

The launcher starts the API and web server together. Stop both with Ctrl+C. If
port 8000 is already occupied, use `TTS_API_PORT=8002 make demo-web`; the web proxy
follows this setting. `TTS_WEB_PORT` changes the web port. Both bind to localhost.

For the CLI use `make demo`; for the API alone use `make dev`.
Open http://127.0.0.1:8000/docs for the interactive API. First try
`GET /api/v1/demo/request`, then submit the example to `POST /api/v1/demo/plan`.
The fixture clock is 2030-06-11 17:40 Europe/Warsaw; changing its date is not
requesting a real itinerary. Endpoints are stateless and fixture-only.
The browser intentionally fixes the date to 11 June 2030, in Warsaw time.

```sh
curl -s http://127.0.0.1:8000/api/v1/demo/request > /tmp/time-to-spare-request.json
curl -s http://127.0.0.1:8000/api/v1/demo/plan \
  -H 'Content-Type: application/json' --data-binary @/tmp/time-to-spare-request.json
```

## Quality gates

- uv + committed `uv.lock`; `uv sync --locked` in development and CI.
- Ruff lint/format, strict mypy (including tests), pytest and Hypothesis.
- Independent final-plan validation, negative/tampering tests, UTC arithmetic.
- Committed OpenAPI contract with a drift check.
- React, strict TypeScript, generated API client types, ESLint and Prettier.
- Citypack JSON Schema, referential validation and packaged fixture resources.
- Playwright desktop/mobile flows with axe accessibility checks.
- `make hooks` installs pre-commit checks and a pre-push test/build gate.
- `make build` builds a typed installable package, including its demo CLI.

`make check` runs lint, formatting checks, type checks, coverage and contract checks.
`make format` applies formatting fixes. Use feature branches under `feat/` and
small commits; never commit `.env`, API keys, caches or `.venv`.

Install the test browser once, then run the full verification suite:

```sh
cd apps/web
npx playwright install chromium
cd ../..
make check-all
```

`make web-check web-build` runs frontend checks and builds without launching a
browser. `make web-test` starts isolated API/web processes on ports 8001/5174 and
tests against the actual API. On Linux, Playwright may also need OS dependencies:
`npx playwright install --with-deps chromium` from `apps/web`.

## Architecture

`apps/api/src/time_to_spare/domain` contains immutable standard-library values.
`planning/solver.py` enumerates up to three stops from a maximum of 20 candidates.
`planning/validation.py` independently checks the final artifact.
`infrastructure/citypack.py` validates the fixture import boundary;
`infrastructure/demo.py` loads the packaged JSON and creates domain snapshots.
`http/app.py` is the FastAPI adapter; no web-framework types leak into the domain.

Constraints are hard. Unknown prices/opening windows and unverified accessibility
are not treated as success. The API uses integer grosze, offset-aware timestamps
and validates consistency with an IANA timezone. Arithmetic runs in UTC.

## Scope and next milestones

See [SPEC.md](SPEC.md) for the product specification and
[implementation status](docs/STATUS.md) for implemented and missing capabilities.
The M1 fixture form-to-result flow is implemented with a text timeline. Real city
data, geographic routes/maps, persistent jobs, user sessions, replan and AI are
still pending. This is not a live pilot. See the [citypack guide](docs/CITYPACK.md)
and [web/data ADR](docs/adr/0002-fixture-citypack-and-web.md) for boundaries.

## Development workflow

Write code, documentation, commit messages and pull requests in English.
Run `make check-all` before submitting changes. CI repeats backend
checks on Python 3.12, 3.13 and 3.14 and smoke-tests the installed wheel outside
the source tree. A Node 24 job checks/builds the web app and runs browser tests.
It runs on pushes and pull requests with read-only permissions.
Hook installation is local to each checkout; CI is the shared quality gate.

The original Polish product brief is preserved in
[the design archive](docs/archive/spec.pl.md). It documents the initial context;
[SPEC.md](SPEC.md) describes the current product requirements in English.

## License

The specification proposes Apache-2.0. The final license decision is pending;
this checkout is not yet published as a licensed open-source release.
