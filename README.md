# ai-harness

A reference library of AI standards, skills, agents, and workflows. Other repositories consume it by cloning it and either tracking `main` or pinning a release tag. Each consumer owns its own run records and data.

## Where to start

- [docs/explanation/layout.md](docs/explanation/layout.md): how the folders fit together
- [AGENTS.md](AGENTS.md): rules for agents working in this repository
- [CHANGELOG.md](CHANGELOG.md): breaking changes, listed for consumers

## Layout

Source lives in `src/`. See [src/README.md](src/README.md).

| Folder | Purpose |
|---|---|
| `src/agents` | Role-specified agents |
| `src/cli` | Python validate, sync, and doctor |
| `src/context` | Facts and glossary |
| `src/mcp` | MCP configuration |
| `src/powers` | Kiro-referenced functionality |
| `src/prompts` | Workflow and agent entry points |
| `src/scripts` | Shell support scripts |
| `src/shared-kernels` | Reused frameworks |
| `src/skills` | Atomic capabilities |
| `src/steering` | Standards |
| `src/workflows` | Skill combinations |

Other top-level folders: `docs/` (Diataxis with Mermaid), `tests/`, and tool configuration (`.claude/`, `.kiro/`, `.github/`, `.vscode/`). The tool folders hold generated bindings and are not edited by hand.

## Commands

```bash
make bootstrap   # install dependencies with uv
make sync        # generate bindings from src/
make validate    # check frontmatter, references, placeholders, and git rules
make doctor      # fail if a binding differs from its source
make test        # run tests
make lint        # validate, doctor, and test
```

## The contract

- `src/` is the only place to edit. Bindings are regenerated, and `doctor` fails on drift.
- Consumers may override parameters that an artifact declares, and only within its `allowed` values. Undeclared changes fail.
- A change to an id, a parameter name, or a frontmatter field is breaking. It is noted in `CHANGELOG.md` with a MAJOR bump.
