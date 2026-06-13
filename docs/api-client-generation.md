# API And Client Generation

The FastAPI app is the source of truth for API behavior and schemas. The OpenAPI contract and generated clients are derived from it.

Generated outputs:

- `packages/contracts/openapi.json`: committed OpenAPI snapshot for review and non-Python tooling.
- `packages/client-py/`: generated Python client, ignored by Git.
- `packages/client-ts/`: generated TypeScript client, ignored by Git.

Do not hand-edit generated clients or `packages/contracts/openapi.json`.

## Generation Flow

Run:

```sh
npm run gen
```

This runs four steps:

1. `gen:openapi`: export the FastAPI OpenAPI schema to `packages/contracts/openapi.json`.
2. `gen:py`: generate `packages/client-py/` with `openapi-python-client`.
3. `gen:ts`: generate `packages/client-ts/` with Orval.
4. `gen:overrides`: apply committed project-specific client extensions.

Generator configuration lives in:

- `.openapi-python-client.yaml`
- `orval.config.ts`
- `scripts/apply-client-overrides.mjs`
- `packages/client-overrides/`

The generated Python import package is `api_client`.
The generated TypeScript package name is `api-client`.

## Changing The API Contract

For route, schema, or operation changes:

1. Edit the FastAPI module under `apps/api/src/api/modules/`.
2. Keep operation IDs explicit and stable.
3. Run `npm run gen`.
4. Review `packages/contracts/openapi.json`.
5. Update TUI or web consumers if generated function or type names changed.

Prefer fixing the API contract before adding client overrides. If generated code is awkward because the OpenAPI schema is vague, fix the FastAPI route or schema first.

## Generated Client Usage

Application code should import through the generated package for its language. Do not import generated files with relative paths from app code.

- Python consumers import from `api_client`.
- TypeScript consumers import from `api-client`.

## Client Overrides

The generated clients handle normal finite request/response endpoints. Some API shapes do not generate well. For those cases, committed source lives under:

```text
packages/client-overrides/
```

`npm run gen:overrides` copies these files into the ignored generated clients after generation.

Use overrides for generated-client gaps:

- SSE or other streaming helpers.
- Thin package exports that make generated and manual helpers importable from the same package.
- Dependency patches required by those helpers.

Do not use overrides for runtime policy:

- Generic REST error handling.
- Auth headers.
- Timeouts.
- Retries.
- Logging.

Those belong in application client setup, such as TUI or web client construction.

## Current Override Layout

Overrides are grouped by generated client language:

```text
packages/client-overrides/
```

Each language directory mirrors how that generated client is packaged:

```text
packages/client-overrides/py/
packages/client-overrides/ts/
```

When an override replaces a generated operation module, mirror the generated package path so the public import path stays the same.

```text
packages/client-overrides/<language>/<generated-package-path>/...
  -> packages/client-<language>/<generated-package-path>/...
```

Package metadata patches live beside the override files for that language. The override script applies them after generation when manual helpers need runtime dependencies that the OpenAPI generators do not know about.

Current metadata patch files:

```text
packages/client-overrides/py/pyproject.patch.json
packages/client-overrides/ts/package.patch.json
```

## Adding A Client Override

Only add an override after checking that the generator cannot produce a good client shape from a better OpenAPI contract.

1. Add the manual source file under `packages/client-overrides/<language>/`.
2. Preserve the generated import path when replacing an operation module.
3. Add any package dependency to the language-specific patch file.
4. Update `scripts/apply-client-overrides.mjs` to copy the new file or merge the new patch.
5. Run `npm run gen`.
6. Update consumers to use public package imports only.

For operation overrides, mirror the generated module path. For example, overriding:

```text
packages/client-<language>/<generated-package-path>/example_operation
```

means committing:

```text
packages/client-overrides/<language>/<generated-package-path>/example_operation
```

If a generated client uses a package-level export file, expose manual helpers through that same public package surface so consumers do not need special import paths.

## Package Metadata Patches

Overrides sometimes need dependencies that generators do not know about. The override script patches generated package metadata after generation:

- JSON metadata patches are deep-merged into the generated package metadata.
- TOML metadata patches are applied as section entries to the generated package metadata.

Keep metadata patches small and focused on dependencies required by committed overrides. If TOML patches grow beyond simple dependency additions, switch to a TOML parser instead of expanding ad hoc string editing.

After changing generated-client dependencies, update the relevant consumer lockfile. For example:

```sh
cd apps/tui
uv lock
```
