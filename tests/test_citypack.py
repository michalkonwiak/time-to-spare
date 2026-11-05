import json
from copy import deepcopy
from importlib.resources import files
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from time_to_spare.http.app import create_app
from time_to_spare.infrastructure.citypack import CityPack, load_citypack
from time_to_spare.infrastructure.demo import demo_citypack, demo_snapshot


@pytest.fixture
def payload() -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads(
            files("time_to_spare.infrastructure").joinpath("data/demo-citypack.json").read_text()
        ),
    )


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("schema_version",), 2),
        (("synthetic",), False),
        (("timezone",), "Not/AZone"),
        (("fixture_clock",), "2030-06-11T17:40:00"),
        (("fixture_clock",), "2040-06-11T17:40:00Z"),
        (("places", 0, "cost_upper_minor"), -1),
        (("places", 0, "cost_upper_minor"), True),
        (("places", 0, "evidence_ids"), ["missing"]),
        (("places", 0, "evidence_ids"), ["fixture:garden:v1", "fixture:garden:v1"]),
        (("places", 0, "valid_until"), "2040-01-01T00:00:00Z"),
        (("places", 0, "windows", 0, "closes_at"), "2000-01-01T00:00:00Z"),
        (("places", 0, "windows", 0, "last_admission"), "2040-01-01T00:00:00Z"),
        (("return_point", "id"), "garden"),
        (("routes", 0, "destination"), "unknown-place"),
        (("routes", 0, "evidence_id"), "unknown-source"),
        (("routes", 1, "base_seconds"), 0),
        (("evidence", 0, "verified_at"), "2040-01-01T00:00:00Z"),
        (("evidence", 0, "valid_until"), "2030-06-11T16:00:00Z"),
        (("evidence", 0, "verified_at"), "2030-06-11T16:00:00Z"),
    ],
)
def test_rejects_invalid_imports(
    payload: dict[str, Any], path: tuple[str | int, ...], value: object
) -> None:
    target: Any = payload
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValidationError):
        CityPack.model_validate(payload)


@pytest.mark.parametrize("field", ["places", "routes", "evidence"])
def test_rejects_duplicate_records(payload: dict[str, Any], field: str) -> None:
    payload[field].append(deepcopy(payload[field][0]))
    with pytest.raises(ValidationError, match="Duplicate"):
        CityPack.model_validate(payload)


def test_unknowns_survive_import_and_absent_routes_are_not_invented(
    payload: dict[str, Any],
) -> None:
    payload["places"][0].update(cost_upper_minor=None, windows=None, step_free=None)
    payload["routes"] = []
    snapshot = CityPack.model_validate(payload).to_snapshot()
    assert snapshot.places[0].cost_upper_minor is None
    assert snapshot.places[0].windows is None
    assert snapshot.places[0].step_free is None
    assert snapshot.route("station", "garden") is None


def test_local_import_and_size_limit(tmp_path: Path, payload: dict[str, Any]) -> None:
    path = tmp_path / "pack.json"
    path.write_text(json.dumps(payload))
    assert load_citypack(path).to_snapshot() == demo_snapshot()
    path.write_bytes(b" " * 1_000_001)
    with pytest.raises(ValueError, match="1 MB"):
        load_citypack(path)


def test_schema_and_catalog_keep_synthetic_identity() -> None:
    assert CityPack.model_json_schema()["properties"]["synthetic"]["const"] is True
    with TestClient(create_app()) as client:
        body = client.get("/api/v1/demo/catalog").json()
        assert CityPack.model_validate(body) == demo_citypack()
        assert body["synthetic"] is True
        assert body["return_point"]["id"] == "station"


def test_response_exposes_server_computed_buffers() -> None:
    with TestClient(create_app()) as client:
        for kind, boarding, plan_deadline in [
            ("departure", 1200, "2030-06-11T17:10:00Z"),
            ("arrive_by", 0, "2030-06-11T17:30:00Z"),
        ]:
            response = client.post("/api/v1/demo/plan", json={"deadline_type": kind})
            assert response.status_code == 200
            context = response.json()["context"]
            assert context["boarding_seconds"] == boarding
            assert context["reserve_seconds"] == 600
            assert context["plan_deadline"] == plan_deadline
