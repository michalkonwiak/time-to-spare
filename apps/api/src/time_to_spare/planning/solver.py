"""Bounded exhaustive search over a small, already filtered candidate set."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import permutations

from time_to_spare.domain.models import Constraints, Place, Plan, Snapshot, Stop, instant
from time_to_spare.planning.validation import validate_plan


@dataclass(frozen=True)
class PlanningResult:
    plans: tuple[Plan, ...]
    reason: str | None = None


def schedule(sequence: tuple[Place, ...], request: Constraints, data: Snapshot) -> Plan | None:
    position, time = request.start_id, request.starts_at
    stops: list[Stop] = []
    evidence: list[str] = []
    cost, walking = 0, 0
    for place in sequence:
        route = data.route(position, place.id)
        if route is None or place.windows is None or place.cost_upper_minor is None:
            return None
        if request.avoid_stairs and (route.step_free is not True or place.step_free is not True):
            return None
        seconds = request.walk_seconds(route.base_seconds)
        walking += seconds
        arrival = time + timedelta(seconds=seconds)
        duration = timedelta(seconds=place.visit_seconds)
        starts = [
            max(arrival, window.opens_at)
            for window in place.windows
            if window.contains(
                max(arrival, window.opens_at), max(arrival, window.opens_at) + duration
            )
        ]
        if not starts:
            return None
        start = min(starts)
        end = start + duration
        cost += place.cost_upper_minor
        if cost > request.budget_minor or walking > request.max_walk_seconds:
            return None
        if end > request.plan_deadline or end > place.valid_until or not place.active:
            return None
        stops.append(
            Stop(place.id, arrival, start, end, place.cost_upper_minor, place.evidence_ids)
        )
        evidence.append(route.evidence_id)
        position, time = place.id, end
    route = data.route(position, request.return_id)
    if route is None or (request.avoid_stairs and route.step_free is not True):
        return None
    walking += request.walk_seconds(route.base_seconds)
    returned = time + timedelta(seconds=request.walk_seconds(route.base_seconds))
    if returned > request.plan_deadline or walking > request.max_walk_seconds:
        return None
    evidence.append(route.evidence_id)
    plan = Plan(
        data.id,
        tuple(stops),
        returned,
        cost,
        walking,
        int((request.plan_deadline - returned).total_seconds()),
        tuple(evidence),
    )
    # Fail closed even if a future solver change introduces a bug.
    return None if validate_plan(plan, request, data) else plan


def solve(request: Constraints, data: Snapshot, *, now: datetime) -> PlanningResult:
    current = instant(now)
    if request.starts_at < current:
        return PlanningResult((), "START_IN_PAST")
    if data.valid_until < request.starts_at:
        return PlanningResult((), "SNAPSHOT_EXPIRED")
    direct = data.route(request.start_id, request.return_id)
    if direct is None:
        return PlanningResult((), "RETURN_UNREACHABLE")
    if request.avoid_stairs and direct.step_free is not True:
        return PlanningResult((), "ACCESSIBILITY_UNVERIFIED")
    if (
        request.starts_at + timedelta(seconds=request.walk_seconds(direct.base_seconds))
        > request.plan_deadline
    ):
        return PlanningResult((), "INSUFFICIENT_TIME")
    candidates = sorted(data.places, key=lambda place: place.id)
    plans: list[Plan] = []
    for length in range(1, min(3, len(candidates)) + 1):
        for sequence in permutations(candidates, length):
            plan = schedule(sequence, request, data)
            if plan is not None:
                plans.append(plan)
    categories = {p.id: p.categories for p in candidates}

    def rank(plan: Plan) -> tuple[int, int, int, tuple[str, ...]]:
        matched = sum(len(set(categories[s.place_id]) & set(request.interests)) for s in plan.stops)
        return (
            -matched,
            -len(plan.stops),
            plan.walk_seconds,
            tuple(s.place_id for s in plan.stops),
        )

    # Different ordering of the same places is not a genuinely different option.
    selected: list[Plan] = []
    seen: set[frozenset[str]] = set()
    for plan in sorted(plans, key=rank):
        key = frozenset(s.place_id for s in plan.stops)
        if key not in seen:
            selected.append(plan)
            seen.add(key)
        if len(selected) == 3:
            break
    return PlanningResult(tuple(selected), None if selected else "NO_FEASIBLE_PLAN")
