#!/usr/bin/env bash
# Install Python dependencies with uv. Shell only; structural checks live in src/cli/.
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required: https://docs.astral.sh/uv/" >&2
  exit 1
fi

uv sync
echo "ready: run 'make lint'"
