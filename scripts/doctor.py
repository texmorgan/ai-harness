"""doctor.py — detect and optionally fix binding drift.

Usage:
    python scripts/doctor.py all
    python scripts/doctor.py claude --fix
    python scripts/doctor.py all --report --report-out drift.json

Designed to run in CI on every PR.
Exit 1 if any binding is stale and --fix is not set.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (
    GENERATED_HEADER,
    GENERATED_HEADER_YAML,
    REPO_ROOT,
    load_skills,
    read_json,
    write_generated,
    write_json,
)

# import the renderers from sync so there's one source of truth
from sync import (
    render_claude_command,
    render_copilot_section,
    render_kiro_hook,
    render_kiro_steering,
    render_vscode_setting,
)

# ── drift check per tool ───────────────────────────────────────


def check_claude(skills, *, fix: bool) -> list[dict]:
    drifts = []
    for skill in skills:
        target = skill.targets.get("claude", {})
        if target.get("type") != "command":
            continue
        out_path = REPO_ROOT / target["path"]
        expected = f"{GENERATED_HEADER}\n\n{render_claude_command(skill)}"

        if out_path.exists():
            actual = out_path.read_text()
        else:
            actual = ""

        if actual != expected:
            entry = {
                "tool": "claude",
                "skill": skill.id,
                "path": str(out_path.relative_to(REPO_ROOT)),
                "status": "stale" if out_path.exists() else "missing",
            }
            if fix:
                write_generated(
                    out_path, render_claude_command(skill), header=GENERATED_HEADER
                )
                entry["status"] = "fixed"
                click.secho(f"  [claude] fixed  {entry['path']}", fg="green")
            else:
                click.secho(
                    f"  [claude] DRIFT  {entry['path']} ({entry['status']})", fg="red"
                )
            drifts.append(entry)
    return drifts


def check_kiro(skills, *, fix: bool) -> list[dict]:
    import yaml as _yaml

    drifts = []
    for skill in skills:
        target = skill.targets.get("kiro", {})
        ttype = target.get("type")
        out_path = REPO_ROOT / target["path"]

        if ttype == "steering":
            body = render_kiro_steering(skill)
            expected = f"{GENERATED_HEADER}\n\n{body}"
            if out_path.exists():
                actual = out_path.read_text()
            else:
                actual = ""
            if actual != expected:
                entry = {
                    "tool": "kiro",
                    "skill": skill.id,
                    "path": str(out_path.relative_to(REPO_ROOT)),
                    "status": "stale" if out_path.exists() else "missing",
                }
                if fix:
                    write_generated(out_path, body, header=GENERATED_HEADER)
                    entry["status"] = "fixed"
                    click.secho(f"  [kiro] fixed   {entry['path']}", fg="green")
                else:
                    click.secho(
                        f"  [kiro] DRIFT   {entry['path']} ({entry['status']})",
                        fg="red",
                    )
                drifts.append(entry)

        elif ttype == "hook":
            hook = render_kiro_hook(skill)
            expected = f"{GENERATED_HEADER_YAML}\n\n" + _yaml.dump(
                hook, default_flow_style=False, sort_keys=False
            )
            if out_path.exists():
                actual = out_path.read_text()
            else:
                actual = ""
            if actual != expected:
                entry = {
                    "tool": "kiro",
                    "skill": skill.id,
                    "path": str(out_path.relative_to(REPO_ROOT)),
                    "status": "stale" if out_path.exists() else "missing",
                }
                if fix:
                    write_generated(
                        out_path,
                        _yaml.dump(hook, default_flow_style=False, sort_keys=False),
                        header=GENERATED_HEADER_YAML,
                    )
                    entry["status"] = "fixed"
                    click.secho(f"  [kiro] fixed   {entry['path']}", fg="green")
                else:
                    click.secho(
                        f"  [kiro] DRIFT   {entry['path']} ({entry['status']})",
                        fg="red",
                    )
                drifts.append(entry)
    return drifts


def check_copilot(skills, *, fix: bool) -> list[dict]:
    out_path = REPO_ROOT / ".github" / "copilot-instructions.md"

    # rebuild the full expected file the same way sync.py does
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
    sections = []
    for skill in skills:
        if skill.targets.get("copilot", {}).get("type") == "inline":
            sections.append(render_copilot_section(skill))
    expected = preface + "\n".join(sections)

    if out_path.exists():
        actual = out_path.read_text()
    else:
        actual = ""

    if actual != expected:
        entry = {
            "tool": "copilot",
            "path": str(out_path.relative_to(REPO_ROOT)),
            "status": "stale" if out_path.exists() else "missing",
        }
        if fix:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(expected)
            entry["status"] = "fixed"
            click.secho(f"  [copilot] fixed   {entry['path']}", fg="green")
        else:
            click.secho(
                f"  [copilot] DRIFT   {entry['path']} ({entry['status']})", fg="red"
            )
        return [entry]
    return []


def check_vscode(skills, *, fix: bool) -> list[dict]:
    settings_path = REPO_ROOT / ".vscode" / "settings.json"

    # build expected settings
    expected: dict = {}
    if settings_path.exists():
        expected = read_json(settings_path)

    for skill in skills:
        target = skill.targets.get("vscode", {})
        if target.get("type") != "setting":
            continue
        rendered = render_vscode_setting(skill)
        for key, val in rendered.items():
            expected[key] = val

    actual = read_json(settings_path) if settings_path.exists() else {}

    # compare only the aiHarness.* keys we own
    drift_keys = []
    for key, val in expected.items():
        if not key.startswith("aiHarness."):
            continue
        if actual.get(key) != val:
            drift_keys.append(key)

    if drift_keys:
        entry = {
            "tool": "vscode",
            "path": str(settings_path.relative_to(REPO_ROOT)),
            "status": "stale",
            "drift_keys": drift_keys,
        }
        if fix:
            write_json(settings_path, expected)
            entry["status"] = "fixed"
            click.secho(
                f"  [vscode] fixed   {entry['path']} ({len(drift_keys)} key(s))",
                fg="green",
            )
        else:
            click.secho(
                f"  [vscode] DRIFT   {entry['path']} "
                f"({len(drift_keys)} key(s)): "
                f"{', '.join(drift_keys)}",
                fg="red",
            )
        return [entry]
    return []


# ── click CLI ──────────────────────────────────────────────────


@click.group()
@click.option(
    "--fix", is_flag=True, help="Re-write stale bindings instead of just reporting."
)
@click.option("--report", is_flag=True, help="Emit a JSON report to stdout.")
@click.option(
    "--report-out",
    type=click.Path(),
    default=None,
    help="Write JSON report to this path.",
)
@click.pass_context
def cli(ctx: click.Context, fix: bool, report: bool, report_out: str | None) -> None:
    """Detect and optionally fix binding drift."""
    ctx.ensure_object(dict)
    ctx.obj.update(fix=fix, report=report, report_out=report_out)


def _run(checks: dict, ctx_obj: dict) -> None:
    all_drifts: list[dict] = []
    for fn in checks.values():
        skills = load_skills()
        drifts = fn(skills, fix=ctx_obj["fix"])
        all_drifts.extend(drifts)

    # report
    if ctx_obj["report"] or ctx_obj["report_out"]:
        payload = {
            "drift_count": len(all_drifts),
            "drifts": all_drifts,
        }
        text = json.dumps(payload, indent=2)
        if ctx_obj["report_out"]:
            Path(ctx_obj["report_out"]).write_text(text)
            click.echo(f"  report → {ctx_obj['report_out']}")
        else:
            click.echo(text)

    click.echo("")
    if all_drifts:
        stale = [d for d in all_drifts if d["status"] in ("stale", "missing")]
        fixed = [d for d in all_drifts if d["status"] == "fixed"]
        if fixed and not stale:
            click.secho(f"  doctor: {len(fixed)} binding(s) fixed.", fg="green")
        elif stale:
            click.secho(
                f"  doctor: FAILED — "
                f"{len(stale)} binding(s) still stale. "
                f"Run with --fix to repair.",
                fg="red",
            )
            sys.exit(1)
    else:
        click.secho("  doctor: all bindings in sync.", fg="green")


@cli.command()
@click.pass_context
def all(ctx: click.Context) -> None:
    """Check every tool."""
    _run(
        {
            "claude": check_claude,
            "kiro": check_kiro,
            "copilot": check_copilot,
            "vscode": check_vscode,
        },
        ctx.obj,
    )


@cli.command()
@click.pass_context
def claude(ctx: click.Context) -> None:
    """Check Claude Code bindings only."""
    _run({"claude": check_claude}, ctx.obj)


@cli.command()
@click.pass_context
def kiro(ctx: click.Context) -> None:
    """Check Kiro bindings only."""
    _run({"kiro": check_kiro}, ctx.obj)


@cli.command()
@click.pass_context
def copilot(ctx: click.Context) -> None:
    """Check Copilot / Codex bindings only."""
    _run({"copilot": check_copilot}, ctx.obj)


@cli.command()
@click.pass_context
def vscode(ctx: click.Context) -> None:
    """Check VS Code settings only."""
    _run({"vscode": check_vscode}, ctx.obj)


if __name__ == "__main__":
    cli()
