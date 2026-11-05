UV ?= uv
export UV_CACHE_DIR ?= $(CURDIR)/.uv-cache

.PHONY: bootstrap check lint format typecheck test demo dev contract build hooks web-bootstrap web-check web-build web-test demo-web check-all
bootstrap:
	$(UV) sync --locked
check: lint typecheck test
	$(UV) run --locked python scripts/export_openapi.py --check
	$(UV) run --locked python scripts/citypack.py --schema --check
lint:
	$(UV) run --locked ruff check .
	$(UV) run --locked ruff format --check .
format:
	$(UV) run --locked ruff format .
	$(UV) run --locked ruff check --fix .
	$(UV) run --locked ruff format .
typecheck:
	$(UV) run --locked mypy
test:
	$(UV) run --locked pytest --cov --cov-report=term-missing
demo:
	$(UV) run --locked time-to-spare
dev:
	$(UV) run --locked uvicorn time_to_spare.http.app:create_app --factory --host 127.0.0.1 --port 8000 --reload
contract:
	$(UV) run --locked python scripts/export_openapi.py
	$(UV) run --locked python scripts/citypack.py --schema
build:
	$(UV) build
hooks:
	$(UV) run --locked pre-commit install
web-bootstrap:
	npm --prefix apps/web ci
web-check:
	npm --prefix apps/web run check
web-build:
	npm --prefix apps/web run build
web-test:
	npm --prefix apps/web run test:e2e
demo-web:
	$(UV) run --locked python scripts/dev.py
check-all: check web-check build web-build web-test
