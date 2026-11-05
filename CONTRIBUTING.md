# Contributing

Run `make bootstrap web-bootstrap`, `make hooks`, then `make check-all`.
Install Chromium once with `npx playwright install chromium` from `apps/web`.
Use English for code, documentation, commits and pull requests.
Pre-commit checks lint, formatting and types. Pre-push includes both builds and
desktop/mobile browser tests. CI also checks clean installation.
Changes to dependencies must include `uv.lock` or `apps/web/package-lock.json`;
do not bypass checks to push. After API changes run `make contract` and
`npm --prefix apps/web run generate`, and commit both generated contracts.
Use small feature branches and descriptive commits (e.g. `feat(planner): ...`).
Name branches by purpose: `feat/`, `fix/`, or `docs/`, followed by a short description.
Explain behavior changes, tests and limitations in PRs. Add regression tests for
constraint violations. Do not weaken type checking or the validator to pass CI.

Keep documentation and PR descriptions concrete: explain the problem, behavior,
tradeoffs and verification. Avoid promotional claims and describe only capabilities
that are implemented and tested.

Synthetic fixtures must be clearly labeled. Real datasets need provenance and
redistribution rights. Do not submit secrets or personal location histories.
