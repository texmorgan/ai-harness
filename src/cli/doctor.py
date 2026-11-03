#!/usr/bin/env python3
"""Detect generated bindings that drifted from src/. Exit 1 on drift unless --fix."""

from __future__ import annotations

import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness import REPO_ROOT, drift, write_outputs  # noqa: E402


@click.command()
@click.option("--fix", is_flag=True, help="Regenerate bindings instead of failing.")
def main(fix: bool) -> None:
    problems = drift(REPO_ROOT)
    if not problems:
        click.echo("ok: bindings match src/")
        return
    if fix:
        write_outputs(REPO_ROOT)
        click.echo(f"fixed {len(problems)} binding problem(s)")
        return
    for kind, path in problems:
        click.echo(f"DRIFT {kind}: {path.relative_to(REPO_ROOT)}", err=True)
    click.echo("run 'make sync' to regenerate", err=True)
    sys.exit(1)


if __name__ == "__main__":
    main()
