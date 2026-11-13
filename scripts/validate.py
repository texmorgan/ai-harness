"""validate.py — lint the source-of-truth files.

Usage:
    python scripts/validate.py all
    python scripts/validate.py skills
    python scripts/validate.py powers
    python scripts/validate.py steering
    python scripts/validate.py all --strict
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (
    CONVENTIONS,
    load_powers,
    load_skills,
    load_steering,
    mcp_server_exists,
    power_exists,
)

# ── individual checks ──────────────────────────────────────────


def check_skills(skills, powers, *, strict: bool) -> int:
    """Every skill must have a SKILL.md. Every required
    convention, power, and MCP server must exist."""
    errors: list[str] = []
    warnings: list[str] = []

    for skill in skills:
        # SKILL.md must exist
        if not skill.skill_md_path or not skill.skill_md_path.exists():
            errors.append(f"  skill '{skill.id}': skills/{skill.id}/SKILL.md not found")
        continue

        # required conventions
        for conv in skill.requires.get("conventions", []):
            if not (CONVENTIONS / f"{conv}.md").exists():
                msg = (
                    f"  skill '{skill.id}': "
                    f"convention '{conv}' not found in conventions/"
                )
                errors.append(msg)

        # required powers
        for pw in skill.requires.get("powers", []):
            if not power_exists(pw, powers):
                msg = (
                    f"  skill '{skill.id}': "
                    f"power '{pw}' not found in powers/_index.yaml"
                )
                errors.append(msg)

        # required MCP servers
        for mcp in skill.requires.get("mcp", []):
            if not mcp_server_exists(mcp):
                msg = f"  skill '{skill.id}': MCP server '{mcp}' not in .mcp.json"
                errors.append(msg)

        # target path safety (no ../, no absolute)
        for tool, target in skill.targets.items():
            p = target.get("path", "")
            if ".." in p or p.startswith("/"):
                errors.append(
                    f"  skill '{skill.id}': "
                    f"target path '{p}' for {tool} escapes repo root"
                )
            if p and not p.startswith("."):
                warnings.append(
                    f"  skill '{skill.id}': "
                    f"target path '{p}' for {tool} "
                    f"doesn't start with a dot-dir"
                )

        # context.md is optional
        if skill.context_md_path and not skill.context_md_path.exists():
            warnings.append(f"  skill '{skill.id}': context.md referenced but missing")

    _report("skills", errors, warnings, strict)
    return len(errors) + (len(warnings) if strict else 0)


def check_powers(powers, *, strict: bool) -> int:
    """Every power must have its .md file and must
    only compose skills that exist."""
    errors: list[str] = []
    warnings: list[str] = []
    skill_ids = {s.id for s in load_skills()}

    for power in powers:
        if not power.md_path or not power.md_path.exists():
            errors.append(f"  power '{power.id}': {power.file} not found in powers/")

        for skill_id in power.composes.get("skills", []):
            if skill_id not in skill_ids:
                errors.append(
                    f"  power '{power.id}': "
                    f"composes skill '{skill_id}' "
                    f"which is not in _registry.yaml"
                )

        for conv in power.composes.get("conventions", []):
            if not (CONVENTIONS / f"{conv}.md").exists():
                errors.append(
                    f"  power '{power.id}': "
                    f"composes convention '{conv}' "
                    f"which doesn't exist"
                )

        if not power.permissions:
            warnings.append(f"  power '{power.id}': no permissions declared")

    _report("powers", errors, warnings, strict)
    return len(errors) + (len(warnings) if strict else 0)


def check_steering(steering, *, strict: bool) -> int:
    """Every steering doc in _index.yaml must exist on disk."""
    errors: list[str] = []
    warnings: list[str] = []

    for doc in steering:
        if not doc.path.exists():
            errors.append(f"  steering '{doc.id}': {doc.file} not found in steering/")
        elif doc.path.stat().st_size == 0:
            warnings.append(f"  steering '{doc.id}': {doc.file} is empty")

    _report("steering", errors, warnings, strict)
    return len(errors) + (len(warnings) if strict else 0)


# ── helpers ────────────────────────────────────────────────────


def _report(name: str, errors: list[str], warnings: list[str], strict: bool) -> None:
    for w in warnings:
        click.secho(f"  WARN {w}", fg="yellow")
    for e in errors:
        click.secho(f"  FAIL {e}", fg="red")

    if not errors and not warnings:
        click.secho(f"  {name}: all checks passed.", fg="green")
    elif not errors:
        click.secho(
            f"  {name}: {len(warnings)} warning(s), "
            f"0 error(s)." + ("  [strict: warnings = errors]" if strict else ""),
            fg="yellow",
        )
    else:
        click.secho(
            f"  {name}: {len(errors)} error(s), {len(warnings)} warning(s).",
            fg="red",
        )


# ── click CLI ──────────────────────────────────────────────────


@click.group()
@click.option("--strict", is_flag=True, help="Treat warnings as errors.")
@click.pass_context
def cli(ctx: click.Context, strict: bool) -> None:
    """Lint the source-of-truth files."""
    ctx.ensure_object(dict)
    ctx.obj["strict"] = strict


@cli.command()
@click.pass_context
def all(ctx: click.Context) -> None:
    """Run every check."""
    skills = load_skills()
    powers = load_powers()
    steering = load_steering()
    strict = ctx.obj["strict"]

    total = 0
    total += check_skills(skills, powers, strict=strict)
    total += check_powers(powers, strict=strict)
    total += check_steering(steering, strict=strict)

    click.echo("")
    if total:
        click.secho(f"  validate: FAILED ({total} issue(s)).", fg="red")
        sys.exit(1)
    else:
        click.secho("  validate: PASSED.", fg="green")


@cli.command()
@click.pass_context
def skills(ctx: click.Context) -> None:
    """Check skills only."""
    s = load_skills()
    p = load_powers()
    check_skills(s, p, strict=ctx.obj["strict"])


@cli.command()
@click.pass_context
def powers(ctx: click.Context) -> None:
    """Check powers only."""
    p = load_powers()
    check_powers(p, strict=ctx.obj["strict"])


@cli.command()
@click.pass_context
def steering(ctx: click.Context) -> None:
    """Check steering docs only."""
    st = load_steering()
    check_steering(st, strict=ctx.obj["strict"])


if __name__ == "__main__":
    cli()
