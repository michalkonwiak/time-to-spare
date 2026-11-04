# Implementation rules

Read SPEC.md and docs/STATUS.md. Work in small tested milestones.
Do not claim a production capability when only fixtures exist.
Keep the domain independent of FastAPI, Pydantic, SDKs and AI frameworks.
Do not relax hard constraints. Use UTC for arithmetic and integer minor currency units.
Unknown facts are not free prices, open venues, or accessible routes.
Run `make check` and `make build` before reporting a completed code milestone.
Update OpenAPI with `make contract` for intentional HTTP contract changes.
Do not publish, add live credentials, or enable paid integrations without authorization.
