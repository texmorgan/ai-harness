"""sync.py — fan shared source-of-truth into tool-specific bindings.

Usage:
    python scripts/sync.py all
    python scripts/sync.py claude
    python scripts/sync.py kiro
    python scripts/sync.py copilot
    python scripts/sync.py vscode

    python scripts/sync.py all --dry-run --verbose
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

# allow `python scripts/sync.py` without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (
    GENERATED_HEADER,
    GENERATED_HEADER_YAML,
    REPO_ROOT,
    Skill,
    load_skills,
    read_json,
    skill_content,
    write_generated,
    write_json,
)

# ── renderers ──────────────────────────────────────────────────

def render_claude_command(skill: Skill) -> str:
    """Claude Code: one .md file per command under .claude/commands/."""
    body = skill_content(skill)
    return f"# /{skill.id}\n\n{body}"


def render_kiro_steering(skill: Skill) -> str:
    """Kiro: one .md file per skill under .kiro/steering/."""
    body = skill_content(skill)
    return f"# Steering: {skill.id}\n\n{body}"


def render_kiro_hook(skill: Skill) -> dict:
    """Kiro: a YAML hook under .kiro/hooks/."""
    target = skill.targets.get("kiro", {})
    trigger = target.get("trigger", f"on/{skill.id}")
    return {
        "trigger": trigger,
        "action": "load",
        "skill": f"skills/{skill.id}/SKILL.md",
        "steering": [
            "steering/conventions.md",
            "steering/values.md",
        ],
    }


def render_copilot_section(skill: Skill) -> str:
    """Copilot: one section appended to copilot-instructions.md."""
    return textwrap.dedent(f"""\
    ## Skill: {skill.id}  (v{skill.version})

    **Triggers:** {', '.join(skill.triggers)}
    **Tags:** {', '.join(skill.tags)}
    **File:** `skills/{skill.id}/SKILL.md`

    {skill_content(skill).strip()}
    """)


def render_vscode_setting(skill: Skill) -> dict:
    """VS Code: a key merged into .vscode/settings.json."""
    target = skill.targets.get("vscode", {})
    key = target.get("key", f"aiHarness.skills.{skill.id}")
    return {
        key: {
            "enabled": True,
            "trigger": ", ".join(skill.triggers),
            "file": f"skills/{skill.id}/SKILL.md",
        }
    }


# ── per-tool sync functions ────────────────────────────────────

def sync_claude(skills: list[Skill], *, dry_run: bool = False,
                verbose: bool = False) -> int:
    count = 0
    for skill in skills:
        target = skill.targets.get("claude", {})
        if target.get("type") != "command":
            continue
        out_path = REPO_ROOT / target["path"]
        rendered = render_claude_command(skill)
        if verbose:
            click.echo(f"  [claude] {skill.id} → {out_path.relative_to(REPO_ROOT)}")
        if not dry_run:
            write_generated(out_path, rendered, header=GENERATED_HEADER)
        count += 1
    click.echo(f"  claude: {count} command(s) synced.")
    return count


def sync_kiro(skills: list[Skill], *, dry_run: bool = False,
              verbose: bool = False) -> int:
    count = 0
    for skill in skills:
        target = skill.targets.get("kiro", {})
        ttype = target.get("type")
        out_path = REPO_ROOT / target["path"]

        if ttype == "steering":
            rendered = render_kiro_steering(skill)
            if verbose:
                click.echo(f"  [kiro:steering] {skill.id} → "
                           f"{out_path.relative_to(REPO_ROOT)}")
            if not dry_run:
                write_generated(out_path, rendered, header=GENERATED_HEADER)
            count += 1

        elif ttype == "hook":
            hook = render_kiro_hook(skill)
            import yaml
            body = yaml.dump(hook, default_flow_style=False, sort_keys=False)
            if verbose:
                click.echo(f"  [kiro:hook] {skill.id} → "
                           f"{out_path.relative_to(REPO_ROOT)}")
            if not dry_run:
                write_generated(out_path, body, header=GENERATED_HEADER_YAML)
            count += 1

    click.echo(f"  kiro: {count} binding(s) synced.")
    return count


def sync_copilot(skills: list[Skill], *, dry_run: bool = False,
                 verbose: bool = False) -> int:
    """Copilot uses a single inline file. Collect all, concatenate, write."""
    out_path = REPO_ROOT / ".github" / "copilot-instructions.md"
    sections: list[str] = []
    count = 0

    for skill in skills:
        target = skill.targets.get("copilot", {})
        if target.get("type") != "inline":
            continue
        sections.append(render_copilot_section(skill))
        if verbose:
            click.echo(f"  [copilot:section] {skill.id}")
        count += 1

    # preface is the fixed header the user wrote in the initial file
    preface = (
        f"{GENERATED_HEADER}\n\n"
        "# AI Harness — Copilot / Codex Instructions\n\n"
        "## Context\n"
        "Read steering/project.md and steering/conventions.md "
        "before acting.\n\n"
        "## Conventions\n"
        "- Naming: kebab-case files, snake_case config, "
        "UPPER_SNAKE_CASE env vars.\n"
        "- Error handling: fail fast, structured logs, "
        "no silent swallows.\n"
        "- API: URL versioning, Bearer auth, idempotent writes.\n"
        "- Testing: 80%+ new code, 95%+ payment/auth paths.\n\n"
        "## Hard rules\n"
        "- Never deploy to prod without security-scan passing.\n"
        "- Payment / auth paths require security-auditor power "
        "+ two reviewers.\n"
        "- Do not edit .claude/, .kiro/, .github/copilot/, "
        "or .vscode/ by hand.\n\n"
    )

    body = preface + "\n".join(sections)

    if verbose:
        click.echo(f"  [copilot] {count} section(s) → "
                   f"{out_path.relative_to(REPO_ROOT)}")
    if not dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(body)
    click.echo(f"  copilot: {count} section(s) inlined.")
    return count


def sync_vscode(skills: list[Skill], *, dry_run: bool = False,
                verbose: bool = False) -> int:
    """VS Code: merge skill settings into .vscode/settings.json."""
    settings_path = REPO_ROOT / ".vscode" / "settings.json"

    # start from a minimal base; merge in any existing user keys
    if settings_path.exists():
        data = read_json(settings_path)
    else:
        data = {}

    count = 0
    for skill in skills:
        target = skill.targets.get("vscode", {})
        if target.get("type") != "setting":
            continue
        rendered = render_vscode_setting(skill)
        for key, val in rendered.items():
            data[key] = val
        if verbose:
            click.echo(f"  [vscode:setting] {skill.id} → {key}")
        count += 1

    if verbose:
        click.echo(f"  [vscode] {count} setting(s) merged into "
                   f"{settings_path.relative_to(REPO_ROOT)}")
    if not dry_run:
        write_json(settings_path, data)
    click.echo(f"  vscode: {count} setting(s) merged.")
    return count


# ── click CLI ──────────────────────────────────────────────────

@click.group()
@click.option("--dry-run", is_flag=True, help="Print actions, write nothing.")
@click.option("--verbose", "-v", is_flag=True, help="Verbose per-file output.")
@click.pass_context
def cli(ctx: click.Context, dry_run: bool, verbose: bool) -> None:
    """Fan shared source-of-truth into tool-specific bindings."""
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run
    ctx.obj["verbose"] = verbose


@cli.command()
@click.pass_context
def all(ctx: click.Context) -> None:
    """Sync every tool at once."""
    skills = load_skills()
    _ = sync_claude(skills, **ctx.obj)
    _ = sync_kiro(skills, **ctx.obj)
    _ = sync_copilot(skills, **ctx.obj)
    _ = sync_vscode(skills, **ctx.obj)
    click.echo("")
    if ctx.obj["dry_run"]:
        click.secho("  [dry-run] no files written.", fg="yellow")
    else:
        click.secho("  all bindings synced.", fg="green")


@cli.command()
@click.pass_context
def claude(ctx: click.Context) -> None:
    """Sync Claude Code bindings only."""
    skills = load_skills()
    sync_claude(skills, **ctx.obj)


@cli.command()
@click.pass_context
def kiro(ctx: click.Context) -> None:
    """Sync Kiro bindings only."""
    skills = load_skills()
    sync_kiro(skills, **ctx.obj)


@cli.command()
@click.pass_context
def copilot(ctx: click.Context) -> None:
    """Sync Copilot / Codex bindings only."""
    skills = load_skills()
    sync_copilot(skills, **ctx.obj)


@cli.command()
@click.pass_context
def vscode(ctx: click.Context) -> None:
    """Sync VS Code settings only."""
    skills = load_skills()
    sync_vscode(skills, **ctx.obj)


if __name__ == "__main__":
    cli()
