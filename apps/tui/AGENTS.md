# TUI Notes

## Scope

These instructions apply to `apps/tui/`.

The TUI is a Textual client for the Logos API. The FastAPI app remains the source of truth for API behavior and schemas; the TUI consumes the generated Python client from `packages/client-py/`.

## Layout

Use the Python `src` layout:

- `src/tui/main.py`: thin CLI entrypoint.
- `src/tui/app.py`: Textual `App` class, app-wide setup, and long-lived infrastructure such as the shared generated API client.
- `src/tui/settings.py`: TUI settings. Keep it at the package root, mirroring `api/settings.py`.
- `src/tui/screens/`: Textual screens.
- `src/tui/widgets/`: reusable Textual widgets.

For screens that need API calls or nontrivial orchestration, prefer a screen package:

```text
src/tui/screens/<screen_name>/
  __init__.py
  screen.py
  loaders.py
  controllers.py
  models.py
  widgets/
    __init__.py
    <screen-specific-widget>.py
```

- `screen.py` owns Textual composition, event handlers, and UI state.
- `loaders.py` owns read/query API calls for that screen.
- `controllers.py` owns command/mutation API calls for that screen.
- `models.py` owns screen-specific data shapes, when the screen needs a shape that differs from generated API models.
- `widgets/` owns widgets that are specific to that screen.

Colocation is key. Each screen package should have a `widgets/` directory for screen-specific widgets. Keep only reusable, cross-screen widgets in `src/tui/widgets/`.

Keep `__init__.py` files empty unless there is a strong reason to expose a tiny public API.

## API Client Usage

Do not edit generated client files under `packages/client-py/`.

The generated Python client exposes module-level endpoint functions, not methods such as `client.create_session(...)`. Import those generated endpoint functions only from loader/controller files.

Screens and widgets should not import generated endpoint functions from `api_client.api.*`.

Loaders and controllers should not recreate generated client exposed types unless the screen or widgets need data in a different shape. When a different shape is needed, define that shape in a colocated `models.py`, not directly inside `loaders.py` or `controllers.py`.

Avoid a broad `services/` layer by default. The TUI should not duplicate backend domain services. For this app, prefer colocated screen-level `loaders.py` and `controllers.py`.

If a loader or controller becomes reused across multiple screens, move it to:

- `src/tui/loaders.py` or `src/tui/loaders/`
- `src/tui/controllers.py` or `src/tui/controllers/`

Use one shared generated `api_client.Client` for the app lifetime. Create it in `app.py`, enter it when the app mounts, and close it when the app unmounts. Pass that client into loaders/controllers so polling and repeated requests reuse connections.

## Screens And Widgets

Screens may import screen-local loaders/controllers and simple screen-local data types from colocated `models.py` files.

Widgets should stay presentational when practical. They should receive plain data such as strings, ids, or small TUI-owned dataclasses rather than generated API models.

Prefer widget-scoped `DEFAULT_CSS` for Textual styling. If a screen's CSS becomes very large, move it into a colocated `styles.tcss` file for that screen.

Keep API response validation and generated-model adaptation inside loaders/controllers. Screens should receive generated models directly when they are already ergonomic for rendering and state management; otherwise loaders/controllers may adapt responses into TUI-owned models from `models.py`.

## Settings

Use `pydantic-settings` for TUI settings when values come from environment variables or `.env`.

Use the `TUI_` environment prefix for TUI-specific settings. For example, `api_base_url` maps to `TUI_API_BASE_URL`.
