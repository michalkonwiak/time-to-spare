"""Generate or check the committed contract without starting a server."""

import argparse
import json
from pathlib import Path

from time_to_spare.http.app import create_app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = Path(__file__).resolve().parents[1] / "packages/contracts/openapi.json"
    content = (
        json.dumps(create_app().openapi(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    )
    if args.check:
        if not path.exists() or path.read_text() != content:
            raise SystemExit("OpenAPI drift: run make contract and commit the result")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


if __name__ == "__main__":
    main()
