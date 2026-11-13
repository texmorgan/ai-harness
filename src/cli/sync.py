"""Generate tool bindings from src/. Never edit the generated files by hand."""

from __future__ import annotations

import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness import REPO_ROOT, write_outputs


@click.command()
def main() -> None:
    count = write_outputs(REPO_ROOT)
    click.echo(f"ok: wrote {count} binding(s)")


if __name__ == "__main__":
    main()
