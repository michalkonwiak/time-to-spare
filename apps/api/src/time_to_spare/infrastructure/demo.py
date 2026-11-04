"""Entirely fictional points and directed walking durations; not navigation data."""

from datetime import UTC, datetime, timedelta

from time_to_spare.domain.models import Constraints, OpeningWindow, Place, Route, Snapshot

DEMO_NOTICE = "DEMO: fictional places, prices and routes. Do not use for navigation."
DEMO_START = datetime(2030, 6, 11, 15, 40, tzinfo=UTC)


def demo_snapshot() -> Snapshot:
    opened = OpeningWindow(DEMO_START - timedelta(hours=2), DEMO_START + timedelta(hours=4))
    expires = DEMO_START + timedelta(hours=5)
    places = (
        Place(
            "garden",
            "Demo garden",
            1200,
            0,
            (opened,),
            ("fixture:garden:v1",),
            expires,
            ("walk",),
            True,
        ),
        Place(
            "cafe",
            "Demo cafe",
            1500,
            2500,
            (opened,),
            ("fixture:cafe:v1",),
            expires,
            ("food",),
            True,
        ),
        Place(
            "gallery",
            "Demo gallery",
            1800,
            3000,
            (opened,),
            ("fixture:gallery:v1",),
            expires,
            ("art",),
            None,
        ),
    )
    # Explicit fixture matrix; never inferred from coordinate distance.
    durations = ((0, 600, 900, 1200), (660, 0, 420, 720), (960, 480, 0, 600), (1260, 780, 660, 0))
    ids = ("station", "garden", "cafe", "gallery")
    routes = tuple(
        Route(origin, destination, durations[i][j], f"fixture:route:{origin}:{destination}", True)
        for i, origin in enumerate(ids)
        for j, destination in enumerate(ids)
    )
    return Snapshot("synthetic-city-v1", places, routes, expires)


def demo_request() -> Constraints:
    return Constraints(
        DEMO_START, DEMO_START + timedelta(hours=2), 4500, interests=("food", "walk")
    )
