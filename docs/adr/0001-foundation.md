# ADR 0001: deterministic backend foundation

Status: accepted for this implementation stage.

The surrounding repository is a portfolio with unrelated pending changes.
This project therefore has an independent Git repository in `jeszcze-zdaze/`.
Do not add it as a submodule or stage parent-repository changes. It can later be
moved unchanged to a sibling folder and published to a dedicated remote.

Use one uv project with a src layout under apps/api, not empty microservices.
Use Ruff and strict mypy; include tests in type checking. Only add dependencies
when code actually needs them. Database/Celery/LangGraph will follow their milestones.

The synchronous `/demo/plan` endpoint is deliberately separate from the future
asynchronous `/planning-runs` contract. It has no persistence or user records.

The initial opening model uses explicit dated intervals (including exceptions)
rather than interpreting a weekly schedule at request time. A later citypack adapter
must expand schedules, holidays and DST before invoking the planner. This prevents
silently applying regular hours on an exceptional date.

Initial ranking uses preference matches, stop count, then walking time; this is a
transparent baseline, not the final calibrated scoring model. Final geometry and
provider freshness reconciliation are deferred until a real routing adapter exists.

References checked 2026-11-04:
- https://docs.astral.sh/uv/guides/projects/
- https://docs.astral.sh/ruff/configuration/
- https://mypy.readthedocs.io/en/stable/config_file.html
