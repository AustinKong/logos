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

Committed client extensions live in `packages/client-overrides/`. The generation flow copies these files into ignored generated client packages after OpenAPI generation. Use this for maintained behavior that OpenAPI generators do not model well, such as SSE helpers.

## Source Of Truth

The FastAPI app is the source of truth for API behavior and schemas.

For API contract changes:

1. Edit API modules under `apps/api/src/api/modules/`.
2. Run `npm run gen`.
3. Update consumers in `apps/tui/` or `apps/web/` if generated names changed.

Do not hand-edit `packages/contracts/openapi.json`. It is committed for reviewability and non-Python tooling, but it must be regenerated from the API app.

## API Organization

Use colocated feature modules under `apps/api/src/api/modules/<module>/`.

A module may contain:

- `router.py`: FastAPI endpoints and HTTP boundary.
- `schemas.py`: Pydantic request/response schemas for the API contract.
- `models.py` or `models/`: SQLAlchemy ORM models or internal persistence/domain models.
- `service.py`: main application behavior and orchestration. It must not import FastAPI.
- `repository.py`: optional database query wrapper for repeated, lengthy, or complex ORM access.
- `deps.py`: optional FastAPI dependency wiring for this module, such as constructing services or repositories with `Depends`.
- `errors.py`: optional module-specific application errors.

Top-level API files and packages:

- `main.py`: FastAPI app factory/module.
- `settings.py`: API settings.
- `deps.py`: shared/global FastAPI dependencies, such as settings and the database dependency.
- `shared/`: shared application types such as errors and exception handlers.
- `db/`: database setup, engine/sessionmaker wiring, mixins, and base model metadata.

The API must not import generated clients from `packages/client-py/`. Generated clients consume the API contract, not the other way around.

Keep `__init__.py` files empty unless there is a strong reason to expose a tiny public API. Do not use package `__init__.py` files as general export barrels.

Preferred dependency direction:

- `router.py` may import its own module's `schemas.py`, `adapters.py`, and `deps.py`.
- `router.py` should call services for behavior. A module's router should normally call its own module's service; cross-module behavior should be exposed through the owning module's service rather than importing another module's repository or internals.
- `deps.py` may import `service.py` and `repository.py`.
- `service.py` is the application boundary for its module. Other modules may call it, but should not reach through it to that module's repositories, ORM query details, or internal helpers.
- `service.py` may use SQLAlchemy ORM directly for simple persistence operations and straightforward queries. Do not create a repository only to wrap a one-line `select`, `get`, `add`, or `delete`.
- `service.py` may import `repository.py`, `models.py`, and `errors.py`.
- `repository.py` may import `models.py`.
- module `errors.py` may import `api/shared/errors.py`.

Repository guidance:

- Use repositories pragmatically, not by default. A repository should exist when it wraps repeated, lengthy, or complex query logic, or when naming the query clarifies behavior at call sites.
- Avoid one repository per domain object unless each repository removes real complexity. Small applications may be cleaner when services use the ORM directly for simple work.
- Repositories should not become a second application boundary. Services own module behavior and should enforce module-level invariants.
- Prefer clear service methods over exposing repository methods across module boundaries.

Avoid these dependency directions:

- `service.py` importing `fastapi`.
- `repository.py` importing `fastapi`.
- `models.py` importing `fastapi`.

Constructor-injected dependencies stored on classes should use private attribute names with an underscore prefix, such as `self._repository` or `self._provider_resolver`.

## API Schema Naming

FastAPI request/response schemas live in each module's `schemas.py`.

Keep API schemas focused on contract shape. Put ORM-to-API-schema conversion in a module-local `adapters.py` rather than `from_*` class methods when conversion crosses ORM inheritance or union response types; class methods do not play well with subtype-specific parameters, inherited schema classes, and discriminated unions.

Use explicit suffixes that describe how the schema is used:

- `UserCreate` for create request bodies.
- `UserUpdate` for update request bodies.
- `UserRead` for returned resource responses.
- `LoginRequest` for action request bodies.
- `LoginResponse` for action responses.

For non-CRUD endpoints, prefer action-oriented names such as `HealthCheckResponse`.

Avoid `model_config` on API request/response schemas unless it is required for runtime validation or serialization behavior. Do not use schema-level `json_schema_extra`, examples, or similar documentation-only config that pollutes generated OpenAPI response definitions. This restriction does not apply to non-contract settings models such as `BaseSettings` configuration.

Set explicit `operation_id` values on routes that are consumed by generated clients. Operation IDs become generated client function names, so keep them stable and readable:

```python
@router.get("/health", operation_id="getHealth", response_model=HealthCheckResponse)
```

## API Dependencies And Errors

FastAPI `Depends` is appropriate in `router.py` or module-local `deps.py`. Avoid using `Depends` inside `service.py`; services should be reusable from workers, tests, and non-HTTP entrypoints without FastAPI dependency injection.

Use `Annotated[..., Depends(...)]` directly at feature-level injection sites instead of creating module-local `XDep` type aliases such as `SessionServiceDep`. Shared dependencies that are reused across multiple modules may have aliases in top-level `api/deps.py`, such as the database session dependency.

When a module needs application errors, define module-specific errors in `apps/api/src/api/modules/<module>/errors.py`. Services should raise application errors, not `HTTPException`.

Module errors should inherit from the shared `AppError` classes in `apps/api/src/api/shared/errors.py`; `main.py` already registers the central handler.

Routers should generally not catch module errors manually. Let the central exception handler translate known `AppError` subclasses into HTTP responses. Catch errors in routers only for route-specific translation or cleanup.

## Database Models And Migrations

Use SQLAlchemy ORM models for persistence. Keep ORM models colocated under the feature module, either in `apps/api/src/api/modules/<module>/models.py` for small modules or in `apps/api/src/api/modules/<module>/models/` for larger model groups. When splitting into a `models/` package, prefer plural group filenames such as `sessions.py`, `participants.py`, and `events.py`. Shared database infrastructure belongs under `apps/api/src/api/db/`.

All ORM model files should start with:

```python
from __future__ import annotations
```

Prefer future annotations over string annotations for relationships, for example `Mapped[list[Participant]]` instead of `Mapped[list["Participant"]]`.

Use the shared database mixins from `api.db.mixins` for common columns:

- `UUIDMixin` provides the UUID `id` primary key.
- `TimestampMixin` provides `created_at` and `updated_at`.

For SQLAlchemy joined-table inheritance child IDs, define the child `id` column explicitly on each concrete subclass, for example `id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)`. Avoid clever ID mixins here; explicit declarations are repetitive but work best with SQLAlchemy and Pylance.

Use `ShortString`, `LongString`, or `Text` for SQLAlchemy string columns. `ShortString` and `LongString` live in `api.db.types`; do not hardcode ad hoc string lengths in model files.

Time helpers that are not SQLAlchemy-specific belong in `api.shared.time`; use `utc_now()` for Python-side UTC timestamps.

When adding a new ORM model module, register it in `apps/api/src/api/db/models.py` with an unused import so Alembic autogenerate can discover its table metadata. Keep `# ruff: noqa: F401` at the top of that registry file so these side-effect imports remain lint-clean.

When domain entities have genuinely different required configuration by subtype, prefer explicit SQLAlchemy joined-table inheritance over one table with many nullable subtype-specific columns.

For event timelines, start with a base event table containing `session_id`, `type`, and timestamps. Keep simple lifecycle events as rows in the base table. Add joined-table event subclasses only when an event needs distinct persisted fields.

For API contract changes, regenerate clients with `npm run gen`. For database schema changes, prompt the user to generate database migrations with Alembic.

If the user asks you to generate one for them, do it with the command:

```sh
npm run db:revision -- "describe change"
```

Review autogenerated migrations.

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

For TypeScript clients, Orval writes generated code to `packages/client-ts/src/client/generated.ts`. The public package entrypoint is overlaid from `packages/client-overrides/ts/src/client/index.ts`, which re-exports generated client code and explicitly replaces maintained overrides such as `streamSessionEvents`.

The TypeScript generated client is configured with Orval `fetch.forceSuccessResponse` so non-OK HTTP responses throw and successful calls return the success response shape. Keep TypeScript client overrides, such as SSE helpers, aligned with that behavior so TanStack Query can use thrown errors consistently.

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
```

Python linting/formatting is centralized in the root `pyproject.toml` with Ruff.
JS/TS/JSON linting and formatting is centralized in `biome.json`.

## Testing Philosophy

Do not chase 100% code coverage. Tests are optional and should only cover behavior that might realistically break, especially public contracts, meaningful edge cases, regressions, and failure modes that matter to users or generated clients.

Prefer behavior tests that remain valid through internal refactors. Avoid tests that mirror implementation details, assert trivial hardcoded behavior, or mainly verify that framework plumbing such as FastAPI exception handler registration works.

After implementing a change, agents may suggest specific tests that would be worth adding, but must not add tests autonomously without user confirmation.

When the user confirms that tests should be added, every test function must have a short docstring explaining the behavior in human-readable language. The docstring should be clearer than the function name, but no longer than necessary.

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
