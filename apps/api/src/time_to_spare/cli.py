"""Run the reproducible, network-free example."""

import json
from dataclasses import asdict

from time_to_spare.infrastructure.demo import DEMO_NOTICE, DEMO_START, demo_request, demo_snapshot
from time_to_spare.planning.solver import solve


def main() -> None:
    result = solve(demo_request(), demo_snapshot(), now=DEMO_START)
    print(
        json.dumps(
            {"synthetic": True, "notice": DEMO_NOTICE, "result": asdict(result)},
            default=str,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
