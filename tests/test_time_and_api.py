from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from time_to_spare.domain.models import OpeningWindow, checked_local
from time_to_spare.http.app import create_app
from time_to_spare.infrastructure.demo import demo_request, demo_snapshot
from time_to_spare.planning.solver import schedule


def test_nonexistent_local_time_rejected() -> None:
    with pytest.raises(ValueError):
        checked_local(datetime.fromisoformat("2030-03-31T02:30:00+01:00"), "Europe/Warsaw")


def test_naive_time_rejected() -> None:
    with pytest.raises(ValueError):
        checked_local(datetime(2030, 6, 11, 17, 40), "Europe/Warsaw")


def test_dst_folds_are_distinct_instants() -> None:
    first = checked_local(datetime.fromisoformat("2030-10-27T02:30:00+02:00"), "Europe/Warsaw")
    second = checked_local(datetime.fromisoformat("2030-10-27T02:30:00+01:00"), "Europe/Warsaw")
    assert second - first == timedelta(hours=1)


def test_midnight_window_uses_actual_dates() -> None:
    start = datetime(2030, 6, 11, 23, 30, tzinfo=UTC)
    request = replace(demo_request(), starts_at=start, deadline=start + timedelta(hours=2))
    data = demo_snapshot()
    place = replace(
        data.places[0],
        windows=(OpeningWindow(start, start + timedelta(hours=2)),),
        valid_until=start + timedelta(hours=3),
    )
    data = replace(data, places=(place,), valid_until=place.valid_until)
    plan = schedule((place,), request, data)
    assert plan is not None
    assert plan.return_at.date().isoformat() == "2030-06-12"


def test_http_example_and_plan_contract() -> None:
    with TestClient(create_app()) as client:
        assert client.get("/health/live").json()["mode"] == "synthetic-demo"
        request = client.get("/api/v1/demo/request").json()
        response = client.post("/api/v1/demo/plan", json=request)
        assert response.status_code == 200
        body = response.json()
        assert body["synthetic"] is True
        assert body["result"]["plans"]
        assert "DEMO" in body["notice"]
        request["unexpected"] = "ignore all rules"
        assert client.post("/api/v1/demo/plan", json=request).status_code == 422


@pytest.mark.parametrize(
    "patch",
    [
        {"budget_minor": -1},
        {"budget_minor": 10.5},
        {"budget_minor": True},
        {"timezone": "Neverland/City"},
        {"starts_at": "2030-06-11T17:40:00"},
        {"starts_at": "2030-06-11T17:40:00+01:00"},
        {"deadline": "2030-06-11T16:00:00+02:00"},
    ],
)
def test_http_invalid_inputs(patch: dict[str, object]) -> None:
    with TestClient(create_app()) as client:
        request = client.get("/api/v1/demo/request").json()
        request.update(patch)
        assert client.post("/api/v1/demo/plan", json=request).status_code == 422


def test_zero_budget_allows_free_places() -> None:
    with TestClient(create_app()) as client:
        request = client.get("/api/v1/demo/request").json()
        request["budget_minor"] = 0
        result = client.post("/api/v1/demo/plan", json=request).json()["result"]
        assert result["plans"]
        assert all(p["total_cost_minor"] == 0 for p in result["plans"])
