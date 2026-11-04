from dataclasses import replace
from datetime import timedelta

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from time_to_spare.domain.models import DeadlineType, OpeningWindow
from time_to_spare.infrastructure.demo import DEMO_START, demo_request, demo_snapshot
from time_to_spare.planning.solver import schedule, solve
from time_to_spare.planning.validation import validate_plan


def test_demo_has_distinct_valid_options() -> None:
    request, data = demo_request(), demo_snapshot()
    result = solve(request, data, now=DEMO_START)
    assert len(result.plans) == 3
    assert result.reason is None
    assert len({frozenset(s.place_id for s in p.stops) for p in result.plans}) == 3
    for plan in result.plans:
        assert validate_plan(plan, request, data) == ()
        assert plan.return_at <= request.plan_deadline


def test_unknown_price_is_not_free() -> None:
    data = demo_snapshot()
    data = replace(data, places=tuple(replace(p, cost_upper_minor=None) for p in data.places))
    assert solve(demo_request(), data, now=DEMO_START).reason == "NO_FEASIBLE_PLAN"


def test_unknown_and_closed_hours_are_not_open() -> None:
    data = demo_snapshot()
    for windows in (None, ()):
        changed = replace(data, places=tuple(replace(p, windows=windows) for p in data.places))
        assert not solve(demo_request(), changed, now=DEMO_START).plans


def test_no_route_is_not_straight_line_fallback() -> None:
    data = replace(demo_snapshot(), routes=())
    assert solve(demo_request(), data, now=DEMO_START).reason == "RETURN_UNREACHABLE"


def test_past_start_and_expired_snapshot() -> None:
    request, data = demo_request(), demo_snapshot()
    assert solve(request, data, now=DEMO_START + timedelta(seconds=1)).reason == "START_IN_PAST"
    data = replace(data, valid_until=DEMO_START - timedelta(seconds=1))
    assert solve(request, data, now=DEMO_START).reason == "SNAPSHOT_EXPIRED"


def test_return_buffers_and_arrive_by() -> None:
    request = demo_request()
    assert request.plan_deadline == request.deadline - timedelta(minutes=30)
    arrive = replace(request, deadline_type=DeadlineType.ARRIVE_BY)
    assert arrive.plan_deadline == request.deadline - timedelta(minutes=10)
    tight = replace(request, deadline=DEMO_START + timedelta(minutes=15))
    assert solve(tight, demo_snapshot(), now=DEMO_START).reason == "INSUFFICIENT_TIME"


def test_step_free_requires_confirmation() -> None:
    request, data = replace(demo_request(), avoid_stairs=True), demo_snapshot()
    for plan in solve(request, data, now=DEMO_START).plans:
        assert "gallery" not in {s.place_id for s in plan.stops}
    data = replace(data, routes=tuple(replace(r, step_free=None) for r in data.routes))
    assert solve(request, data, now=DEMO_START).reason == "ACCESSIBILITY_UNVERIFIED"


def test_wait_for_opening_and_entire_visit_inside_window() -> None:
    request, data = demo_request(), demo_snapshot()
    window = OpeningWindow(DEMO_START + timedelta(minutes=30), DEMO_START + timedelta(minutes=50))
    place = replace(data.places[0], windows=(window,))
    data = replace(data, places=(place,))
    plan = schedule((place,), request, data)
    assert plan is not None
    assert plan.stops[0].starts_at == window.opens_at
    short = replace(
        place, windows=(replace(window, closes_at=window.closes_at - timedelta(seconds=1)),)
    )
    assert schedule((short,), request, replace(data, places=(short,))) is None


def test_last_admission() -> None:
    request, data = demo_request(), demo_snapshot()
    place = data.places[0]
    window = OpeningWindow(DEMO_START, request.deadline, DEMO_START + timedelta(minutes=1))
    place = replace(place, windows=(window,))
    assert schedule((place,), request, replace(data, places=(place,))) is None


def test_validator_rejects_tampered_plan() -> None:
    request, data = demo_request(), demo_snapshot()
    plan = solve(request, data, now=DEMO_START).plans[0]
    assert "INVALID_COST_TOTAL" in validate_plan(replace(plan, total_cost_minor=0), request, data)
    assert "INVALID_SLACK" in validate_plan(replace(plan, slack_seconds=9999), request, data)
    assert "INVALID_RETURN_TIME" in validate_plan(
        replace(plan, return_at=plan.return_at - timedelta(minutes=10)), request, data
    )
    assert "INVALID_ROUTE_EVIDENCE" in validate_plan(
        replace(plan, route_evidence_ids=()), request, data
    )
    stop = replace(plan.stops[0], evidence_ids=("invented",))
    assert "INVALID_EVIDENCE" in validate_plan(
        replace(plan, stops=(stop, *plan.stops[1:])), request, data
    )
    assert "DEADLINE_EXCEEDED" in validate_plan(
        plan, replace(request, deadline=DEMO_START + timedelta(minutes=31)), data
    )


def test_reproducible_and_no_mutation() -> None:
    request, data = demo_request(), demo_snapshot()
    assert solve(request, data, now=DEMO_START) == solve(request, data, now=DEMO_START)


@given(
    budget=st.integers(0, 8000),
    minutes=st.integers(1, 180),
    walk=st.integers(0, 10800),
    pace=st.integers(100, 160),
)
@settings(max_examples=100, deadline=None)
def test_all_generated_options_respect_constraints(
    budget: int, minutes: int, walk: int, pace: int
) -> None:
    request = replace(
        demo_request(),
        budget_minor=budget,
        deadline=DEMO_START + timedelta(minutes=minutes),
        max_walk_seconds=walk,
        pace_percent=pace,
    )
    data = demo_snapshot()
    for plan in solve(request, data, now=DEMO_START).plans:
        assert not validate_plan(plan, request, data)
        assert plan.total_cost_minor <= budget
        assert plan.walk_seconds <= walk
        assert plan.return_at <= request.plan_deadline


@given(minutes=st.integers(31, 180), extra=st.integers(1, 30))
def test_tighter_deadline_cannot_make_same_sequence_feasible(minutes: int, extra: int) -> None:
    request = replace(demo_request(), deadline=DEMO_START + timedelta(minutes=minutes))
    data = demo_snapshot()
    sequence = data.places[:2]
    tighter = replace(request, reserve_seconds=request.reserve_seconds + extra * 60)
    if schedule(sequence, request, data) is None:
        assert schedule(sequence, tighter, data) is None


def test_snapshot_rejects_duplicate_routes_and_oversized_catalog() -> None:
    data = demo_snapshot()
    with pytest.raises(ValueError, match="Duplicate directed"):
        replace(data, routes=(*data.routes, data.routes[0]))
    with pytest.raises(ValueError, match="Candidate limit"):
        replace(data, places=tuple(replace(data.places[0], id=str(i)) for i in range(21)))


def test_validator_checks_schedule_and_source_even_when_totals_look_valid() -> None:
    request, data = demo_request(), demo_snapshot()
    plan = solve(request, data, now=DEMO_START).plans[0]
    first = plan.stops[0]
    altered_stops = (
        (replace(first, arrival=first.arrival - timedelta(seconds=1)), "INVALID_ARRIVAL"),
        (replace(first, ends_at=first.ends_at + timedelta(seconds=1)), "INVALID_VISIT_DURATION"),
        (replace(first, cost_minor=-500), "INVALID_PRICE"),
        (replace(first, place_id="invented"), "UNKNOWN_PLACE_OR_ROUTE"),
    )
    for stop, expected in altered_stops:
        tampered = replace(plan, stops=(stop, *plan.stops[1:]))
        assert expected in validate_plan(tampered, request, data)
    assert "SNAPSHOT_MISMATCH" in validate_plan(replace(plan, snapshot_id="other"), request, data)
    assert "INVALID_STOP_COUNT" in validate_plan(replace(plan, stops=()), request, data)
    assert "DUPLICATE_STOP" in validate_plan(replace(plan, stops=(first, first)), request, data)
    assert "INVALID_WALK_TOTAL" in validate_plan(replace(plan, walk_seconds=0), request, data)
    stale = replace(data, valid_until=DEMO_START)
    assert "SNAPSHOT_EXPIRED" in validate_plan(plan, request, stale)
    changed_places = tuple(
        replace(p, active=False, windows=(), cost_upper_minor=None) for p in data.places
    )
    invalid = validate_plan(plan, request, replace(data, places=changed_places))
    assert {"PLACE_UNAVAILABLE", "OUTSIDE_OPENING_WINDOW", "INVALID_PRICE"} <= set(invalid)


def test_validation_detects_changed_route_accessibility_and_missing_return() -> None:
    request, data = demo_request(), demo_snapshot()
    plan = solve(request, data, now=DEMO_START).plans[0]
    unknown = replace(data, routes=tuple(replace(r, step_free=None) for r in data.routes))
    assert "ACCESSIBILITY_UNVERIFIED" in validate_plan(
        plan, replace(request, avoid_stairs=True), unknown
    )
    no_return = replace(data, routes=tuple(r for r in data.routes if r.destination != "station"))
    assert "RETURN_UNREACHABLE" in validate_plan(plan, request, no_return)
