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

lint: validate doctor test
	@echo "all checks passed"

check:
	uv run ruff check src tests
	uv run yamllint .
