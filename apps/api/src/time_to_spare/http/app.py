"""Stateless, fixture-only API. Production planning-runs API is intentionally not exposed."""

from datetime import datetime
from typing import Annotated, Literal, Self
from zoneinfo import ZoneInfoNotFoundError

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, model_validator

from time_to_spare.domain.models import Constraints, DeadlineType, checked_local
from time_to_spare.infrastructure.demo import DEMO_NOTICE, DEMO_START, demo_snapshot
from time_to_spare.planning.solver import PlanningResult, solve


class DemoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    starts_at: datetime = datetime.fromisoformat("2030-06-11T17:40:00+02:00")
    deadline: datetime = datetime.fromisoformat("2030-06-11T19:40:00+02:00")
    timezone: str = "Europe/Warsaw"
    deadline_type: DeadlineType = DeadlineType.DEPARTURE
    budget_minor: Annotated[int, Field(strict=True, ge=0, le=100_000)] = 4500
    max_walk_minutes: Annotated[int, Field(strict=True, ge=0, le=180)] = 60
    pace: Literal["standard", "relaxed"] = "standard"
    avoid_stairs: bool = False
    interests: list[Literal["food", "walk", "art"]] = Field(default_factory=list, max_length=3)

    @model_validator(mode="after")
    def validate_times(self) -> Self:
        try:
            checked_local(self.starts_at, self.timezone)
            checked_local(self.deadline, self.timezone)
        except ZoneInfoNotFoundError as error:
            raise ValueError("Unknown IANA timezone") from error
        if self.deadline <= self.starts_at:
            raise ValueError("Deadline must follow start")
        return self

    def to_domain(self) -> Constraints:
        return Constraints(
            starts_at=self.starts_at,
            deadline=self.deadline,
            budget_minor=self.budget_minor,
            max_walk_seconds=self.max_walk_minutes * 60,
            deadline_type=self.deadline_type,
            pace_percent=125 if self.pace == "relaxed" else 100,
            avoid_stairs=self.avoid_stairs,
            interests=tuple(self.interests),
        )


class DemoResponse(BaseModel):
    synthetic: Literal[True] = True
    notice: str = DEMO_NOTICE
    fixture_clock: datetime = DEMO_START
    result: PlanningResult


def create_app() -> FastAPI:
    app = FastAPI(title="Time to Spare — synthetic demo", version="0.1.0", description=DEMO_NOTICE)

    @app.get("/health/live")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "synthetic-demo"}

    @app.get("/api/v1/demo/request", response_model=DemoRequest)
    def example() -> DemoRequest:
        return DemoRequest(starts_at=datetime.fromisoformat("2030-06-11T17:40:00+02:00"))

    @app.post("/api/v1/demo/plan", response_model=DemoResponse)
    def plan(request: DemoRequest) -> DemoResponse:
        result = solve(request.to_domain(), demo_snapshot(), now=DEMO_START)
        return DemoResponse(result=result)

    return app
