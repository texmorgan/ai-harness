"""Validate src/ frontmatter, references, placeholders, and required paths."""

from __future__ import annotations

import subprocess  # nosec B404 - argv-list calls only, no shell
import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness import REPO_ROOT, iter_artifacts, validate_artifacts

REQUIRED_PATHS = [
    "src",
    "tests",
    "docs",
    "Makefile",
    "pyproject.toml",
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".mcp.json",
    ".claude/settings.json",
    ".github/workflows/ci.yml",
]


def check_paths(root: Path = REPO_ROOT) -> list[str]:
    """Required paths must exist and must not be hidden by .gitignore."""
    errors = []
    for p in REQUIRED_PATHS:
        if not (root / p).exists():
            errors.append(f"{p}: required path is missing")
            continue
        result = subprocess.run(
            ["git", "check-ignore", "-q", p], check=False, cwd=root, capture_output=True
        )
        if result.returncode == 0:
            errors.append(f"{p}: ignored by .gitignore, so it will not be committed")
    return errors


@click.command()
def main() -> None:
    artifacts = iter_artifacts()
    errors = validate_artifacts(artifacts) + check_paths()
    for e in errors:
        click.echo(f"ERROR {e}", err=True)
    if errors:
        sys.exit(1)
    click.echo(f"ok: {len(artifacts)} artifacts and required paths validated")


if __name__ == "__main__":
    main()
