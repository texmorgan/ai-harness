# AGENTS.md

This repo is the AI engineering harness.
It defines shared steering, powers, and skills
that are distributed to Claude Code, Kiro,
GitHub Copilot / Codex, and VS Code.

## Before you act
1. Read `steering/project.md` for org context.
2. Read `steering/conventions.md` for rules.
3. Read `powers/_index.yaml` to see available
   roles and what each one is allowed to do.
4. Read `skills/_registry.yaml` for atomic
   capabilities and their triggers.

## Do NOT
- Edit `.claude/`, `.kiro/`, `.github/copilot/`,
  or `.vscode/` by hand. Those are generated
  by `make sync`.
- Add a new skill or power without registering
  it in the corresponding `_index.yaml` /
  `_registry.yaml`.

## Commands
- `make sync`      regenerate all tool bindings
- `make doctor`    check bindings match source
- `make validate`  lint steering / powers / skills
- `make lint`      all of the above

## Hierarchy
steering/   →  context: where we're going,
               what the rules are
powers/     →  roles: what a given agent
               is empowered to do
skills/     →  atomic operations: the
               smallest triggerable unit

A power composes skills.
Steering constrains both.
