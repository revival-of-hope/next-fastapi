#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "==> Running Ruff lint..."
uv run ruff check .

echo "==> Checking Ruff formatting..."
uv run ruff format --check .

echo "==> Running mypy..."
uv run mypy .

echo "==> All checks passed."