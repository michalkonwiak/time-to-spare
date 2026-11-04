"""Validate the final artifact independently; never call the solver here."""

from datetime import timedelta

from time_to_spare.domain.models import Constraints, Plan, Snapshot


def validate_plan(plan: Plan, request: Constraints, data: Snapshot) -> tuple[str, ...]:
    errors: list[str] = []
    if plan.snapshot_id != data.id:
        errors.append("SNAPSHOT_MISMATCH")
    if not 1 <= len(plan.stops) <= 3:
        errors.append("INVALID_STOP_COUNT")
    if len({s.place_id for s in plan.stops}) != len(plan.stops):
        errors.append("DUPLICATE_STOP")
    places = {p.id: p for p in data.places}
    position, time = request.start_id, request.starts_at
    cost, walking = 0, 0
    route_evidence: list[str] = []
    for stop in plan.stops:
        place = places.get(stop.place_id)
        route = data.route(position, stop.place_id)
        if place is None or route is None:
            errors.append("UNKNOWN_PLACE_OR_ROUTE")
            return tuple(errors)
        seconds = request.walk_seconds(route.base_seconds)
        walking += seconds
        route_evidence.append(route.evidence_id)
        expected_arrival = time + timedelta(seconds=seconds)
        if stop.arrival != expected_arrival or stop.starts_at < stop.arrival:
            errors.append("INVALID_ARRIVAL")
        if stop.ends_at != stop.starts_at + timedelta(seconds=place.visit_seconds):
            errors.append("INVALID_VISIT_DURATION")
        if not place.windows or not any(
            window.contains(stop.starts_at, stop.ends_at) for window in place.windows
        ):
            errors.append("OUTSIDE_OPENING_WINDOW")
        if not place.active or place.valid_until < stop.ends_at:
            errors.append("PLACE_UNAVAILABLE")
        if request.avoid_stairs and (place.step_free is not True or route.step_free is not True):
            errors.append("ACCESSIBILITY_UNVERIFIED")
        if place.cost_upper_minor is None or stop.cost_minor != place.cost_upper_minor:
            errors.append("INVALID_PRICE")
        if stop.evidence_ids != place.evidence_ids:
            errors.append("INVALID_EVIDENCE")
        cost += stop.cost_minor
        position, time = stop.place_id, stop.ends_at
    back = data.route(position, request.return_id)
    if back is None:
        return (*errors, "RETURN_UNREACHABLE")
    if request.avoid_stairs and back.step_free is not True:
        errors.append("ACCESSIBILITY_UNVERIFIED")
    walking += request.walk_seconds(back.base_seconds)
    route_evidence.append(back.evidence_id)
    expected_return = time + timedelta(seconds=request.walk_seconds(back.base_seconds))
    if plan.return_at != expected_return:
        errors.append("INVALID_RETURN_TIME")
    if expected_return > request.plan_deadline:
        errors.append("DEADLINE_EXCEEDED")
    if data.valid_until < expected_return:
        errors.append("SNAPSHOT_EXPIRED")
    if walking > request.max_walk_seconds or plan.walk_seconds != walking:
        errors.append("INVALID_WALK_TOTAL")
    if cost > request.budget_minor or plan.total_cost_minor != cost:
        errors.append("INVALID_COST_TOTAL")
    slack = int((request.plan_deadline - expected_return).total_seconds())
    if plan.slack_seconds != slack:
        errors.append("INVALID_SLACK")
    if plan.route_evidence_ids != tuple(route_evidence):
        errors.append("INVALID_ROUTE_EVIDENCE")
    return tuple(dict.fromkeys(errors))
