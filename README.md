# ai-harness

AI engineering harness.
One source of truth. Five tool bindings.

## Structure

    steering/   context  — where we're going,
                           what the rules are
    powers/     roles    — what an agent can do
    skills/     atomic   — the smallest
                           triggerable unit
    conventions/ org rules
    docs/       human-facing docs + ADRs
    mcp/        shared MCP servers

    .claude/        Claude Code binding
    .kiro/          Kiro binding
    .github/        Copilot / Codex binding
    .vscode/        VS Code binding

    scripts/      the harness (sync / validate / doctor)

## Quick start

    make sync       # generate bindings
    make doctor     # confirm no drift
    make validate   # lint source

## Adding a skill

    mkdir skills/my-skill/
    # write SKILL.md
    # add entry to skills/_registry.yaml
    make sync
    git add -A && git commit -m "feat: add my-skill"

## Adding a power

    # write powers/my-power.md
    # add entry to powers/_index.yaml
    make sync

## Hierarchy

steering  >  powers  >  skills
context   >  roles   >  operations

Steering constrains.
A power composes skills.
A skill is the smallest unit of work.
