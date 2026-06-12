# Repository Notes

## Project Layout

This repo is a small monorepo with three apps and generated API clients:

- `apps/api/`: FastAPI app. Owns API routes, settings, and Pydantic schemas.
- `apps/tui/`: Textual app. Calls the API through the generated Python client.
- `apps/web/`: Vite React app. Calls the API through the generated TypeScript client.
- `packages/contracts/openapi.json`: committed OpenAPI snapshot exported from the FastAPI app.
- `packages/client-py/`: generated Python client. Ignored by Git.
- `packages/client-ts/`: generated TypeScript client. Ignored by Git.

Generated clients are build artifacts. Do not edit generated client files directly.

## Source Of Truth

The FastAPI app is the source of truth for API behavior and schemas.

For API contract changes:

1. Edit API routes/schemas under `apps/api/src/api/`.
2. Run `npm run gen`.
3. Update consumers in `apps/tui/` or `apps/web/` if generated names changed.

Do not hand-edit `packages/contracts/openapi.json`. It is committed for reviewability and non-Python tooling, but it must be regenerated from the API app.

## API Organization

Use this split in `apps/api/src/api/`:

- `routes/`: FastAPI routers and endpoint functions.
- `schemas/`: Pydantic request/response schemas used in route contracts.
- `models/`: SQLAlchemy models or domain models. This package may be empty until needed.
- `settings.py`: API settings.
- `main.py`: FastAPI app factory/module.

The API must not import generated clients from `packages/client-py/`. Generated clients consume the API contract, not the other way around.

## API Schema Naming

FastAPI request/response schemas live under `apps/api/src/api/schemas/`.

Use explicit suffixes that describe how the schema is used:

- `UserCreate` for create request bodies.
- `UserUpdate` for update request bodies.
- `UserRead` for returned resource responses.
- `LoginRequest` for action request bodies.
- `LoginResponse` for action responses.

For non-CRUD endpoints, prefer action-oriented names such as `HealthCheckResponse`.

Set explicit `operation_id` values on routes that are consumed by generated clients. Operation IDs become generated client function names, so keep them stable and readable:

```python
@router.get("/health", operation_id="getHealth", response_model=HealthCheckResponse)
```

## Code Generation

Run all OpenAPI/client generation with:

```sh
npm run gen
```

This does three things:

1. Exports OpenAPI from FastAPI to `packages/contracts/openapi.json`.
2. Generates the Python client into `packages/client-py/`.
3. Generates the TypeScript client into `packages/client-ts/`.

Generator config lives in:

- `.openapi-python-client.yaml` for Python client package settings.
- `orval.config.ts` for TypeScript client settings.
- root `package.json` for generation scripts.

The generated Python import package is `api_client`.
The generated TypeScript package name is `api-client`.

## Consumer Rules

TUI code should import the generated Python client package:

```python
from api_client import Client
from api_client.api.health import get_health
```

Web code should import the generated TypeScript package:

```ts
import { getHealth } from "api-client";
```

Do not bypass package imports by directly importing generated files with relative paths.

## Tooling

Use the root bootstrap command for fresh setup:

```sh
npm run bootstrap
```

The repo intentionally does not use npm workspaces. Root npm dependencies are for repo tooling, while `apps/web/` manages its own npm install after the generated TypeScript client exists.

Use `code logos.code-workspace` as the canonical VS Code entrypoint. It keeps root, API, and TUI Python interpreters separate so the root Python environment remains tooling-only.

Git hooks are managed with `pre-commit` and installed by `npm run bootstrap`. Hooks regenerate the OpenAPI contract, run format/fix tooling, then run lint. Tests are intentionally not part of the pre-commit hook.

Use root commands:

```sh
npm run lint
npm run fix
npm run format
npm run test
```

Python linting/formatting is centralized in the root `pyproject.toml` with Ruff.
JS/TS/JSON linting and formatting is centralized in `biome.json`.

Run app tests from their app directories:

```sh
cd apps/api && uv run pytest
cd apps/tui && uv run pytest
```

## Development

Run API and web together:

```sh
npm run dev
```

Run the TUI in a separate terminal because Textual needs full terminal control:

```sh
npm run dev:tui
```

The web app proxies `/api/*` to the FastAPI dev server and strips the `/api` prefix before forwarding.

## Git Hygiene

Keep these generated/build artifacts out of commits:

- `packages/client-py/`
- `packages/client-ts/`
- `.venv/`
- `node_modules/`
- `dist/`
- caches such as `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`

Commit `packages/contracts/openapi.json` when API contracts change.
