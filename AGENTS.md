# AGENTS.md

This repository is a reference library. Source lives in `src/`. Consumers clone it and use the artifacts they enable.

## Before you act

1. Read `docs/explanation/layout.md`.
2. Read `src/steering/naming.md` and `src/context/glossary.md`.
3. For an agent, read its file in `src/agents/` and check its declared parameters.

## Do not

- Edit `.claude/agents/`, `.kiro/`, `.github/copilot/`, or `.vscode/` by hand. Run `make sync`.
- Add a placeholder to an artifact unless it is declared in `parameters`.
- Add a referenced source without a `source` field and a row in `SOURCES.md`.
- Reproduce long passages from books. Summarize them and cite them.
- Add a top-level file or folder outside the layout in `README.md`. Propose it in a PR instead.
- Commit personal, employer, or client data. Use the gitignored `private/` directory.

## Commands

`make sync`, `make validate`, `make doctor`, `make test`, `make lint`.
