#!/usr/bin/env bash
set -euo pipefail

if (($# == 0)); then
  echo 'Usage: npm run db:revision -- "describe change"' >&2
  exit 2
fi

API_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../apps/api" && pwd)"
message="$*"

cd "$API_ROOT"

PYTHONPATH=src uv run alembic revision --autogenerate -m "$message"
uv run ruff format migrations/versions
uv run ruff check migrations/versions --fix
