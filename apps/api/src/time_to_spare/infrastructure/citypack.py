"""Versioned fixture import boundary. Real citypacks need a separate audited adapter."""

from pathlib import Path
from typing import Annotated, Literal, Self
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from time_to_spare.domain.models import OpeningWindow, Place, Route, Snapshot, instant

Identifier = Annotated[str, Field(pattern=r"^[a-z][a-z0-9:_-]{0,99}$")]
Nonnegative = Annotated[int, Field(strict=True, ge=0)]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Evidence(Record):
    id: Identifier
    description: Annotated[str, Field(min_length=1, max_length=500)]
    kind: Literal["synthetic"] = "synthetic"
    verified_at: AwareDatetime
    valid_until: AwareDatetime

    @model_validator(mode="after")
    def valid_interval(self) -> Self:
        if self.verified_at >= self.valid_until:
            raise ValueError("Evidence must expire after verification")
        return self


class Window(Record):
    opens_at: AwareDatetime
    closes_at: AwareDatetime
    last_admission: AwareDatetime | None = None

    @model_validator(mode="after")
    def valid_window(self) -> Self:
        self.to_domain()
        return self

    def to_domain(self) -> OpeningWindow:
        return OpeningWindow(self.opens_at, self.closes_at, self.last_admission)


class PackPlace(Record):
    id: Identifier
    name: Annotated[str, Field(min_length=1, max_length=120)]
    visit_seconds: Annotated[int, Field(strict=True, gt=0, le=10_800)]
    cost_upper_minor: Nonnegative | None
    windows: tuple[Window, ...] | None
    evidence_ids: Annotated[tuple[Identifier, ...], Field(min_length=1)]
    valid_until: AwareDatetime
    categories: tuple[Literal["walk", "food", "art"], ...] = ()
    step_free: bool | None = None
    active: bool = True

    def to_domain(self) -> Place:
        return Place(
            self.id,
            self.name,
            self.visit_seconds,
            self.cost_upper_minor,
            None if self.windows is None else tuple(w.to_domain() for w in self.windows),
            self.evidence_ids,
            self.valid_until,
            self.categories,
            self.step_free,
            self.active,
        )


class PackRoute(Record):
    origin: Identifier
    destination: Identifier
    base_seconds: Nonnegative
    evidence_id: Identifier
    step_free: bool | None = None

    @model_validator(mode="after")
    def valid_route(self) -> Self:
        self.to_domain()
        return self

    def to_domain(self) -> Route:
        return Route(
            self.origin, self.destination, self.base_seconds, self.evidence_id, self.step_free
        )


class ReturnPoint(Record):
    id: Identifier
    name: Annotated[str, Field(min_length=1, max_length=120)]


class CityPack(Record):
    schema_version: Literal[1]
    id: Identifier
    synthetic: Literal[True]
    timezone: str
    currency: Literal["PLN"]
    fixture_clock: AwareDatetime
    valid_until: AwareDatetime
    return_point: ReturnPoint
    evidence: Annotated[tuple[Evidence, ...], Field(min_length=1, max_length=500)]
    places: Annotated[tuple[PackPlace, ...], Field(min_length=1, max_length=20)]
    routes: Annotated[tuple[PackRoute, ...], Field(max_length=441)]

    @model_validator(mode="after")
    def validate_references(self) -> Self:
        # The fixture format contains dated instants, not weekly wall-clock schedules.
        try:
            ZoneInfo(self.timezone)
        except (KeyError, ValueError) as error:
            raise ValueError("Unknown IANA timezone") from error
        if self.fixture_clock >= self.valid_until:
            raise ValueError("Snapshot must expire after its fixture clock")
        evidence = {e.id: e for e in self.evidence}
        if len(evidence) != len(self.evidence):
            raise ValueError("Duplicate evidence ID")
        ids = {p.id for p in self.places}
        if self.return_point.id in ids:
            raise ValueError("Return point must be distinct from places")
        ids.add(self.return_point.id)
        for item in self.evidence:
            if item.verified_at > self.fixture_clock:
                raise ValueError("Evidence cannot come from after the fixture clock")
            if item.valid_until < self.valid_until:
                raise ValueError("Snapshot validity exceeds evidence validity")
        for place in self.places:
            if not self.fixture_clock < place.valid_until <= self.valid_until:
                raise ValueError("Place validity must be inside snapshot validity")
            if len(set(place.evidence_ids)) != len(place.evidence_ids):
                raise ValueError("Duplicate place evidence reference")
            if any(ref not in evidence for ref in place.evidence_ids):
                raise ValueError("Unknown place evidence reference")
        for route in self.routes:
            if route.origin not in ids or route.destination not in ids:
                raise ValueError("Route references an unknown point")
            if route.evidence_id not in evidence:
                raise ValueError("Unknown route evidence reference")
        self.to_snapshot()  # Also enforce domain uniqueness and directed route invariants.
        return self

    def to_snapshot(self) -> Snapshot:
        return Snapshot(
            self.id,
            tuple(p.to_domain() for p in self.places),
            tuple(r.to_domain() for r in self.routes),
            instant(self.valid_until),
            self.synthetic,
        )


def load_citypack(path: Path) -> CityPack:
    """Read a local, bounded JSON file; never fetch a URL or trust a user-supplied path."""
    with path.open("rb") as stream:
        payload = stream.read(1_000_001)
    if len(payload) > 1_000_000:
        raise ValueError("Citypack exceeds the 1 MB import limit")
    return CityPack.model_validate_json(payload)
