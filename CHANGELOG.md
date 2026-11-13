# Changelog

## 0.2.0 (breaking)

- Reorganized source into `src/` with the folders listed in `src/README.md`.
- Removed the Node implementations (`scripts/*.mjs`, `package.json`). Python in `src/cli/` is the only implementation.
- Removed root-level `agents/`, `prompts/`, `skills/`, `steering/`, and `mcp/`. Their contents are now under `src/`, or were removed.
- Reset `powers/_index.yaml` to empty. The previous entries remain at commit `0c87935`.
- Removed `.mcp.json` server entries and Claude hook entries that pointed to files not in the repository.
- Removed the Python-template ignore rules that hid `scripts/` and `.python-version`.
- Added the frontmatter schema, `validate`, `sync`, and `doctor`, and declared-parameter overrides.
- Added tests and a CI workflow that runs `make lint`.
