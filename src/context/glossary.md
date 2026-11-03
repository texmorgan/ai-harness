---
id: glossary
version: 0.1.0
status: active
origin: authored
audience: both
implements: []
owner: TBD
---
# Glossary

- **Harness:** this repository. A library of standards, skills, agents, and workflows.
- **Consumer:** a repository that clones the harness and enables some of its artifacts.
- **Artifact:** any markdown file under `src/` with frontmatter.
- **Skill:** one atomic, triggerable capability, defined in `src/skills/`.
- **Workflow:** an ordered set of skills with declared inputs and outputs, defined in `src/workflows/`.
- **Agent:** a role with permissions, the skills and workflows it may run, and the steering it must follow.
- **Steering:** standards that constrain how work is done.
- **Context:** facts about the world the work operates in.
- **Shared kernel:** a named framework or model reused by many artifacts. Referenced, not copied.
- **Binding:** a generated file for one tool, such as `.claude/agents/`. Never hand-edited.
- **Origin:** `authored` (written here) or `referenced` (external, summarized and cited).
- **Parameter:** a declared, bounded value that a consumer may override. Undeclared changes fail.
