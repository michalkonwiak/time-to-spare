"""Framework-independent values. All arithmetic uses UTC, including across DST."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from zoneinfo import ZoneInfo


def instant(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("An explicit UTC offset is required")
    return value.astimezone(UTC)


def checked_local(value: datetime, timezone: str) -> datetime:
    utc = instant(value)
    local = utc.astimezone(ZoneInfo(timezone))
    if local.replace(tzinfo=None) != value.replace(tzinfo=None):
        raise ValueError("Timestamp does not exist or its offset conflicts with the timezone")
    if local.utcoffset() != value.utcoffset():
        raise ValueError("Offset conflicts with timezone")
    return utc


class DeadlineType(StrEnum):
    DEPARTURE = "departure"
    ARRIVE_BY = "arrive_by"


@dataclass(frozen=True)
class Constraints:
    starts_at: datetime
    deadline: datetime
    budget_minor: int
    max_walk_seconds: int = 3600
    deadline_type: DeadlineType = DeadlineType.DEPARTURE
    boarding_seconds: int = 1200
    reserve_seconds: int = 600
    pace_percent: int = 100
    uncertainty_percent: int = 115
    start_id: str = "station"
    return_id: str = "station"
    avoid_stairs: bool = False
    interests: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "starts_at", instant(self.starts_at))
        object.__setattr__(self, "deadline", instant(self.deadline))
        if self.deadline <= self.starts_at:
            raise ValueError("Deadline must be after the start")
        if (
            min(
                self.budget_minor,
                self.max_walk_seconds,
                self.boarding_seconds,
                self.reserve_seconds,
            )
            < 0
        ):
            raise ValueError("Money, duration and buffers must be nonnegative")
        if self.pace_percent < 100 or self.uncertainty_percent < 100:
            raise ValueError("Walking multipliers must not reduce provider durations")

    @property
    def site_deadline(self) -> datetime:
        buffer = self.boarding_seconds if self.deadline_type == DeadlineType.DEPARTURE else 0
        return self.deadline - timedelta(seconds=buffer)

    @property
    def plan_deadline(self) -> datetime:
        return self.site_deadline - timedelta(seconds=self.reserve_seconds)

    def walk_seconds(self, base: int) -> int:
        # Integer ceiling: no floating point drift at the deadline boundary.
        numerator = base * self.pace_percent * self.uncertainty_percent
        return (numerator + 9999) // 10000


@dataclass(frozen=True)
class OpeningWindow:
    opens_at: datetime
    closes_at: datetime
    last_admission: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "opens_at", instant(self.opens_at))
        object.__setattr__(self, "closes_at", instant(self.closes_at))
        if self.opens_at >= self.closes_at:
            raise ValueError("Opening window must have positive duration")
        if self.last_admission is not None:
            admission = instant(self.last_admission)
            object.__setattr__(self, "last_admission", admission)
            if not self.opens_at <= admission <= self.closes_at:
                raise ValueError("Last admission must be inside opening window")

    def contains(self, start: datetime, end: datetime) -> bool:
        return self.opens_at <= start < end <= self.closes_at and (
            self.last_admission is None or start <= self.last_admission
        )


@dataclass(frozen=True)
class Place:
    id: str
    name: str
    visit_seconds: int
    cost_upper_minor: int | None
    windows: tuple[OpeningWindow, ...] | None
    evidence_ids: tuple[str, ...]
    valid_until: datetime
    categories: tuple[str, ...] = ()
    step_free: bool | None = None
    active: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "valid_until", instant(self.valid_until))
        if self.visit_seconds <= 0:
            raise ValueError("Visit duration must be positive")
        if self.cost_upper_minor is not None and self.cost_upper_minor < 0:
            raise ValueError("Price cannot be negative")
        if not self.id or not self.evidence_ids:
            raise ValueError("Place and evidence IDs are required")


@dataclass(frozen=True)
class Route:
    origin: str
    destination: str
    base_seconds: int
    evidence_id: str
    step_free: bool | None = None

    def __post_init__(self) -> None:
        if self.base_seconds < 0 or (self.origin != self.destination and self.base_seconds == 0):
            raise ValueError("Route duration must be positive between distinct points")
        if not self.evidence_id:
            raise ValueError("Route evidence is required")


@dataclass(frozen=True)
class Snapshot:
    id: str
    places: tuple[Place, ...]
    routes: tuple[Route, ...]
    valid_until: datetime
    synthetic: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "valid_until", instant(self.valid_until))
        if len({p.id for p in self.places}) != len(self.places):
            raise ValueError("Duplicate place ID")
        keys = {(r.origin, r.destination) for r in self.routes}
        if len(keys) != len(self.routes):
            raise ValueError("Duplicate directed route")
        if len(self.places) > 20:
            raise ValueError("Candidate limit is 20")

    def route(self, origin: str, destination: str) -> Route | None:
        return next(
            (r for r in self.routes if r.origin == origin and r.destination == destination), None
        )


@dataclass(frozen=True)
class Stop:
    place_id: str
    arrival: datetime
    starts_at: datetime
    ends_at: datetime
    cost_minor: int
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class Plan:
    snapshot_id: str
    stops: tuple[Stop, ...]
    return_at: datetime
    total_cost_minor: int
    walk_seconds: int
    slack_seconds: int
    route_evidence_ids: tuple[str, ...]
