"""Packaged fictional fixture shared by the CLI and HTTP demo."""

from datetime import timedelta
from functools import lru_cache
from importlib.resources import files

from time_to_spare.domain.models import Constraints, Snapshot
from time_to_spare.infrastructure.citypack import CityPack

DEMO_NOTICE = "DEMO: fictional places, prices and routes. Do not use for navigation."


@lru_cache(maxsize=1)
def demo_citypack() -> CityPack:
    resource = files("time_to_spare.infrastructure").joinpath("data/demo-citypack.json")
    return CityPack.model_validate_json(resource.read_bytes())


DEMO_START = demo_citypack().fixture_clock


def demo_snapshot() -> Snapshot:
    return demo_citypack().to_snapshot()


def demo_request() -> Constraints:
    return Constraints(
        DEMO_START, DEMO_START + timedelta(hours=2), 4500, interests=("food", "walk")
    )
