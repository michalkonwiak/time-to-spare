UV ?= uv
export UV_CACHE_DIR ?= $(CURDIR)/.uv-cache

.PHONY: bootstrap check lint format typecheck test demo dev contract build hooks
bootstrap:
	$(UV) sync --locked
check: lint typecheck test
	$(UV) run --locked python scripts/export_openapi.py --check
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
	$(UV) run --locked jeszcze-zdaze
dev:
	$(UV) run --locked uvicorn jeszcze_zdaze.http.app:create_app --factory --host 127.0.0.1 --port 8000 --reload
contract:
	$(UV) run --locked python scripts/export_openapi.py
build:
	$(UV) build
hooks:
	$(UV) run --locked pre-commit install
