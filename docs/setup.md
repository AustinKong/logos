# Developer Setup

This repo is a small monorepo with a FastAPI API, a Textual TUI, a Vite web app, and generated API clients.

## Prerequisites

Install these tools before setting up the repo:

- Python 3.12+
- `uv`
- Node.js and npm

## Fresh Clone Bootstrap

Run the bootstrap command from the repo root:

```sh
npm run bootstrap
```

This installs root tooling, installs Git hooks, syncs the Python apps, generates the OpenAPI contract and clients, then installs the web app.

For VS Code, open the multi-root workspace so each Python app uses its own virtual environment:

```sh
code logos.code-workspace
```

## Running The Apps

Run the API and web app together:

```sh
npm run dev
```

This starts:

- API: `http://127.0.0.1:8000`
- Web: `http://127.0.0.1:5173`

Run the TUI in a separate terminal because Textual needs full terminal control:

```sh
npm run dev:tui
```

## Code Generation

When API routes or schemas change, regenerate the contract and clients:

```sh
npm run gen
```

Do not edit generated client files directly:

- `packages/client-py/`
- `packages/client-ts/`

Do not hand-edit `packages/contracts/openapi.json`; regenerate it from the API app.

## Database

The API uses SQLAlchemy with Alembic migrations. By default, local development uses SQLite at `apps/api/logos.db`.

To change the database URL, copy the API env template and edit `DATABASE_URL`:

```sh
cp apps/api/.env.example apps/api/.env
```

Database URLs must use an async SQLAlchemy driver. PostgreSQL requires adding `asyncpg` and using a `postgresql+asyncpg://...` URL.

Create a migration after changing ORM models:

```sh
npm run db:revision -- "create users"
```

When adding a new ORM model module, import it in `apps/api/src/api/db/models.py` so Alembic autogenerate can see its table metadata.

Apply migrations:

```sh
npm run db:migrate
```

## Checks

Run repo-wide formatting and linting:

```sh
npm run format
npm run lint
```

Run tests:

```sh
npm run test
```
