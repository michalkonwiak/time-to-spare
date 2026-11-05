# Fixture citypack format

The current importer accepts **synthetic data only**. It is not a real-data
publishing pipeline. Start from `apps/api/src/time_to_spare/infrastructure/data/demo-citypack.json`.

Validate a local file:

```sh
uv run --locked python scripts/citypack.py path/to/pack.json
```

The command exits nonzero on invalid data. It does not persist, activate or upload
the file. API and CLI use the committed packaged fixture, not arbitrary local files.

The JSON Schema is `packages/contracts/citypack.schema.json`. Regenerate it with
`make contract`; check it with `make check`. Also regenerate the browser API types
with `npm --prefix apps/web run generate` after API schema changes.

Required top-level fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | Exactly 1 |
| `id` | Stable snapshot identifier |
| `synthetic` | Must be true |
| `timezone`, `currency` | Valid IANA zone and PLN |
| `fixture_clock`, `valid_until` | Offset-aware instants defining fixture validity |
| `return_point` | Unique entrance ID and display name |
| `places` | 1–20 candidates; distinct from the return point |
| `routes` | Explicit directed connections between known points |
| `evidence` | Unique synthetic source IDs, descriptions and validity |

Each place defines a visit duration, optional cost upper bound, optional dated
opening intervals, evidence references, categories and optional step-free status.
`null` means unknown; an empty opening list means no open interval. Unknown data
cannot silently become zero cost, all-day opening or verified accessibility.
Every visit must fit in a single interval, including last-admission restrictions.

Route durations must be positive between distinct points; zero-duration self-edges
are allowed. Opposite directions are separate records. Omitting a connection does
not create a straight-line fallback. Every route references a known evidence ID.

Evidence must be verified no later than the fixture clock and remain valid through
the snapshot's expiry. Place validity must end within the snapshot's validity.
The JSON Schema captures structural constraints; the importer additionally checks
references, duplicate records and cross-record time constraints.

Before real data: extend this format through a new schema version and adapter,
including provenance per critical field, source rights, geography, service bounds,
entrance audits, weekly schedules, date exceptions and real routing. Do not relabel
fixtures as verified places or change `synthetic` to false to bypass this gate.
