"""Tests for the harness: validation, overrides, and drift detection."""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "cli"))

from harness import (
    REPO_ROOT,
    HarnessError,
    drift,
    iter_artifacts,
    render,
    validate_artifacts,
    write_outputs,
)

AGENT = textwrap.dedent(
    """\
    ---
    id: demo-agent
    version: 0.1.0
    status: active
    origin: authored
    audience: agent
    description: Demo agent.
    parameters:
      driver:
        default: a
        allowed: [a, b]
    ---
    Use {{driver}}.
    """
)


def make_repo(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


def test_repository_validates():
    assert validate_artifacts(iter_artifacts(REPO_ROOT)) == []


def test_repository_bindings_are_in_sync():
    assert drift(REPO_ROOT) == []


def test_undeclared_placeholder_fails(tmp_path):
    root = make_repo(
        tmp_path, {"src/agents/demo.md": AGENT.replace("{{driver}}", "{{other}}")}
    )
    errors = validate_artifacts(iter_artifacts(root))
    assert any("{{other}}" in e for e in errors)


def test_referenced_origin_requires_source(tmp_path):
    text = AGENT.replace("origin: authored", "origin: referenced")
    root = make_repo(tmp_path, {"src/agents/demo.md": text})
    errors = validate_artifacts(iter_artifacts(root))
    assert any("requires 'source'" in e for e in errors)


def test_unknown_implements_fails(tmp_path):
    text = AGENT.replace(
        "description: Demo agent.", "description: Demo agent.\nimplements: [missing-id]"
    )
    root = make_repo(tmp_path, {"src/agents/demo.md": text})
    errors = validate_artifacts(iter_artifacts(root))
    assert any("unknown id 'missing-id'" in e for e in errors)


def test_override_outside_allowed_fails(tmp_path):
    root = make_repo(tmp_path, {"src/agents/demo.md": AGENT})
    art = iter_artifacts(root)[0]
    with pytest.raises(HarnessError):
        render(art, {"driver": "c"})


def test_undeclared_override_fails(tmp_path):
    root = make_repo(tmp_path, {"src/agents/demo.md": AGENT})
    art = iter_artifacts(root)[0]
    with pytest.raises(HarnessError):
        render(art, {"not_declared": "x"})


def test_allowed_override_renders(tmp_path):
    root = make_repo(tmp_path, {"src/agents/demo.md": AGENT})
    art = iter_artifacts(root)[0]
    out = render(art, {"driver": "b"})
    assert out.startswith("---\nname: demo-agent\n")
    assert "Use b." in out


def test_drift_detected_and_fixed(tmp_path):
    root = make_repo(tmp_path, {"src/agents/demo.md": AGENT})
    write_outputs(root)
    assert drift(root) == []

    target = root / ".claude" / "agents" / "demo-agent.md"
    target.write_text("hand edit")
    assert drift(root) == [("stale", target)]

    write_outputs(root)
    assert drift(root) == []


def test_orphan_binding_detected(tmp_path):
    root = make_repo(tmp_path, {"src/agents/demo.md": AGENT})
    write_outputs(root)
    (root / "src" / "agents" / "demo.md").unlink()
    kinds = [kind for kind, _ in drift(root)]
    assert kinds == ["orphan"]
    write_outputs(root)
    assert drift(root) == []
