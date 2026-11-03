# CLAUDE.md

You are operating inside the AI engineering harness.

## Read first
- steering/project.md
- steering/conventions.md
- steering/values.md

## Powers available
See powers/_index.yaml.
Invoke a power by name, e.g.
  /architect, /reviewer, /incident-commander

## Skills
See skills/_registry.yaml.
On /review   →  skills/code-review/SKILL.md
On /incident →  skills/incident-response/SKILL.md

## Hard rules
- Never deploy to prod without
  skills/security-scan passing.
- Never edit the .claude/, .kiro/,
  .github/copilot/, or .vscode/ dirs
  by hand.
- Payment or auth paths require the
  security-auditor power + two reviewers.
- All output must respect
  steering/conventions.md.
