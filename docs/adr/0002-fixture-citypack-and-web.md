# ADR 0002: fixture citypacks and the web planning flow

Status: accepted for the demo milestone.

## Data boundary

Move the hardcoded catalog into a packaged, versioned JSON citypack shared by the
API and CLI. Validate it with Pydantic at the infrastructure boundary, then create
immutable domain objects. No HTTP upload or arbitrary path endpoint is introduced.
The local importer reads at most 1 MB and rejects unknown fields, invalid windows,
missing evidence references, duplicate IDs/routes and inconsistent validity.

Version 1 accepts synthetic packs only, dated opening intervals and up to 20
candidates. It is not the full city catalog format: a real citypack needs geographic
coverage, field-level source rights/provenance, weekly schedules and exceptions,
verified entrances and candidate selection before producing a bounded snapshot.
Missing routes remain missing. Unknown price/hours/accessibility remain unknown.

A committed JSON Schema checks structural drift. Cross-record rules (references,
uniqueness, validity) are enforced by the Python importer, not JSON Schema alone.
The fixture JSON is a package resource so an installed wheel works outside the
repository. CI tests that installation explicitly.

## Browser contract

Use React, strict TypeScript and Vite, with a typed fetch client generated from
OpenAPI. Commit generated types and check drift in CI. The API returns calculated
return deadlines and buffers; the UI formats them rather than reimplementing the
planning rules. All displayed times use the response timezone, not the computer's.
The demo form deliberately fixes the date to 11 June 2030 (Warsaw UTC+02).

A text timeline is the complete demo result. No map is shown because the fixture
has no geographic geometry. Choosing an option selects a comparison preview; it
must not imply a live trip has begun. A full trip/session workflow remains M4.

Use native accessible form elements and local CSS. No component framework, CSS
framework or server-state cache is needed for one bootstrap read and one explicit
planning request. This is a scoped deviation from the proposed Tailwind/TanStack
stack, not a change to the planned React architecture. Reconsider caching when
sessions, polling and invalidation have multiple consumers.

Input changes abort in-flight planning and remove previous results. A response
belongs to a captured request; obsolete responses cannot overwrite current state.
Network failure preserves inputs and offers retry. No geolocation or third-party
font requests are made. Dates, uncertainty and fictional data are visible.

## Tooling

Use Node 24 in CI and npm with an exact lockfile. TypeScript stays at 5.9 because
openapi-typescript requires TypeScript 5; do not bypass peer dependency resolution.
ESLint 10 is used with compatible TypeScript/React plugins. Scoped minimatch
11.0.1 overrides address GHSA-g3hv-75wg-m249 in ESLint and typescript-eslint;
remove these overrides once upstream dependency ranges include the fix. Lint and
contract generation are tested with the overrides. Audit reported zero known
vulnerabilities at implementation time; this is not a permanent security guarantee.

Pre-commit runs backend and relevant web static checks. Pre-push runs backend,
frontend, schema drift, both builds and Playwright against real local API/Vite
processes. CI repeats these checks on a clean checkout. Playwright covers desktop
and mobile Chromium, keyboard interaction, network failure and stale responses;
axe adds automated accessibility checks. These do not replace manual review.

References:
- https://vite.dev/guide/
- https://playwright.dev/docs/test-webserver
- https://github.com/advisories/GHSA-g3hv-75wg-m249
