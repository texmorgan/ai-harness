.PHONY: sync validate doctor lint clean

PYTHON ?= python3

sync:
	@echo "→ syncing shared → bindings"
	$(PYTHON) scripts/sync.py all

validate:
	@echo "→ validating source files"
	$(PYTHON) scripts/validate.py all

doctor:
	@echo "→ checking binding drift"
	$(PYTHON) scripts/doctor.py all

lint: validate doctor
	@echo "→ all checks passed"

clean:
	@echo "→ removing generated bindings"
	rm -f .claude/commands/*.md
	rm -f .kiro/steering/skill-*.md
	rm -f .kiro/hooks/on-*.yaml
	@echo "(run 'make sync' to regenerate)"

sync-dry:
	@echo "→ dry-run sync (no writes)"
	$(PYTHON) scripts/sync.py all --dry-run --verbose

doctor-fix:
	@echo "→ re-syncing stale bindings"
	$(PYTHON) scripts/doctor.py all --fix

check:
	@echo "→ checking for formatting"
	uv run ruff check --fix .
	uv run yamllint .