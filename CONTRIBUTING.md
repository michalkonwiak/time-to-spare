# Contributing

Run `make bootstrap`, optionally `make hooks`, then `make check` and `make build`.
Use small feature branches and descriptive commits (e.g. `feat(planner): ...`).
Explain behavior changes, tests and limitations in PRs. Add regression tests for
constraint violations. Do not weaken type checking or the validator to pass CI.
Synthetic fixtures must be clearly labeled. Real datasets need provenance and
redistribution rights. Do not submit secrets or personal location histories.
