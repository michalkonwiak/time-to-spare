"""Validate a local fixture citypack or export/check its JSON Schema."""

import argparse
import json
from pathlib import Path

from time_to_spare.infrastructure.citypack import CityPack, load_citypack


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, nargs="?")
    parser.add_argument("--schema", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.schema:
        path = Path(__file__).resolve().parents[1] / "packages/contracts/citypack.schema.json"
        content = json.dumps(CityPack.model_json_schema(), indent=2, sort_keys=True) + "\n"
        if args.check:
            if not path.exists() or path.read_text() != content:
                raise SystemExit("Citypack schema drift: run make contract")
        else:
            path.write_text(content)
    elif args.path:
        pack = load_citypack(args.path)
        print(f"Valid synthetic citypack: {pack.id}; {len(pack.places)} places")
    else:
        parser.error("Provide a local path or --schema")


if __name__ == "__main__":
    main()
