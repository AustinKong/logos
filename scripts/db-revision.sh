#!/usr/bin/env bash
set -euo pipefail

if (($# == 0)); then
  echo 'Usage: npm run db:revision -- "describe change"' >&2
  exit 2
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_ROOT="$REPO_ROOT/apps/api"
message="$*"

cd "$API_ROOT"
PYTHONPATH=src uv run alembic revision --autogenerate -m "$message"

cd "$REPO_ROOT"
uv run ruff format apps/api/migrations/versions
uv run ruff check apps/api/migrations/versions --fix
