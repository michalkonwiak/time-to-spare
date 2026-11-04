# Jeszcze zdążę

Deterministic short-trip planning with explicit return buffers and evidence.

**Status: foundation + synthetic backend demo. Not a live travel service.**
All places, prices and routes are fictional. Do not use the output for navigation.
No LLM calls, paid APIs, accounts, database, or background tracking are enabled.

## Run locally

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.12.

```sh
make bootstrap
make demo
make check
make dev
```

Open http://127.0.0.1:8000/docs for the interactive API. First try
`GET /api/v1/demo/request`, then submit the example to `POST /api/v1/demo/plan`.
The fixture clock is 2030-06-11 17:40 Europe/Warsaw; changing its date is not
requesting a real itinerary. Both endpoints are stateless and fixture-only.

```sh
curl -s http://127.0.0.1:8000/api/v1/demo/request > /tmp/zdaze-request.json
curl -s http://127.0.0.1:8000/api/v1/demo/plan \
  -H 'Content-Type: application/json' --data-binary @/tmp/zdaze-request.json
```

## Quality gates

- uv + committed `uv.lock`; `uv sync --locked` in development and CI.
- Ruff lint/format, strict mypy (including tests), pytest and Hypothesis.
- Independent final-plan validation, negative/tampering tests, UTC arithmetic.
- Committed OpenAPI contract with a drift check.
- `make hooks` installs local pre-commit checks; CI is authoritative.
- `make build` builds a typed installable package, including its demo CLI.

`make check` runs lint, formatting checks, type checks, coverage and contract checks.
`make format` applies formatting fixes. Use feature branches under `feat/` and
small commits; never commit `.env`, API keys, caches or `.venv`.

## Architecture

`apps/api/src/jeszcze_zdaze/domain` contains immutable standard-library values.
`planning/solver.py` enumerates up to three stops from a maximum of 20 candidates.
`planning/validation.py` independently checks the final artifact.
`infrastructure/demo.py` supplies an explicit directed synthetic route matrix.
`http/app.py` is the FastAPI adapter; no web-framework types leak into the domain.

Constraints are hard. Unknown prices/opening windows and unverified accessibility
are not treated as success. The API uses integer grosze, offset-aware timestamps
and validates consistency with an IANA timezone. Arithmetic runs in UTC.

## Scope and next milestones

See [SPEC.md](SPEC.md) for the product specification and
[implementation status](docs/STATUS.md) for implemented and missing capabilities.
This is **not completion of M1 or P0**: frontend, real city data, routing APIs,
persistent jobs, user sessions, replan and AI are still pending.

## Polski

Projekt jest na etapie fundamentu backendu. `make demo` pokazuje policzone warianty
na fikcyjnych danych, a `make dev` uruchamia API z interaktywną dokumentacją.
Kwoty podajemy w groszach; wynik uwzględnia oddzielny bufor dworcowy i rezerwę.
Nie potwierdzamy rozkładów kolejowych ani rzeczywistych godzin otwarcia.

## License

The specification proposes Apache-2.0. The final license decision is pending;
this checkout is not yet published as a licensed open-source release.
