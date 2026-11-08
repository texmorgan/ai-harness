.PHONY: bootstrap sync validate doctor test lint check

PY ?= uv run python

bootstrap:
	bash src/scripts/bootstrap.sh

sync:
	$(PY) src/cli/sync.py

validate:
	$(PY) src/cli/validate.py

doctor:
	$(PY) src/cli/doctor.py

test:
	uv run pytest -q

coverage:
	uv run pytest --cov=src --cov-report=term-missing

check: validate doctor lint security
	@echo "all checks passed"

lint:
	uv run ruff format
	uv run ruff check --fix src tests
	uv run yamllint .

security:
	uv run bandit -r src
