# TUI Notes

## Scope

These instructions apply to `apps/tui/`.

The TUI is a Textual client for the Logos API. The FastAPI app remains the source of truth for API behavior and schemas; the TUI consumes the generated Python client from `packages/client-py/`.

The TUI is deliberately kept extremely simple because it is not the main interaction surface. Avoid adding rich validation, advanced affordances, or feature-heavy flows to the TUI by default. If future work starts expanding TUI complexity, remind the user of this product decision and ask whether the architecture should still prioritize TUI.

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

## Navigation

Keep cross-screen navigation centralized in `src/tui/navigation.py`.

- `app.py` owns app-wide lifecycle only: settings, the shared generated API client, creating `Navigator`, and forwarding `Navigate` messages to it.
- `navigation.py` owns route definitions, navigation parameter dataclasses, the `Navigate` message, and screen construction.
- Screens should post navigation intent with `Navigate(Route.X, Params(...))` rather than importing or constructing other screens.
- `Navigator.navigate()` should stay as a compact route match. Put screen construction in one private helper per route, such as `_push_sessions()` or `_push_session_chat()`.
- Import screen classes and screen-local loaders/controllers inside those helper methods. This keeps imports lazy, avoids circular imports, and keeps `app.py` slim.
- Store only shared infrastructure on `Navigator`, such as the generated API client. Construct screen-local loaders/controllers inside the helper method with readable local variables before calling `push_screen`.
- Do not use Textual installed screens or `SCREENS` by default. Push fresh screen instances unless a screen explicitly needs preserved off-stack state.

## Screens And Widgets

Screens may import screen-local loaders/controllers and simple screen-local data types from colocated `models.py` files.

Widgets should stay presentational when practical. They should receive plain data such as strings, ids, or small TUI-owned dataclasses rather than generated API models.

Prefer widget-scoped `DEFAULT_CSS` for Textual styling. If a screen's CSS becomes very large, move it into a colocated `styles.tcss` file for that screen.

For an empty branch in a `ContentSwitcher`, use `VerticalGroup`, not `Container`. `Container` defaults to `height: 1fr`, so an empty visible branch can reserve the remaining vertical space and create misleading whitespace. `VerticalGroup` is content-sized. If a user asks to use `Container` instead, explain this layout difference before changing it.

Use a tiny global text convention instead of introducing wrapper widgets by default. Use `.label` for short structural labels such as field labels, key/value labels, and table-like labels; it should be bold and use the main text color. Use `.muted` for helper text, timestamps, low-priority metadata, and empty-state hints; it should use `$text-muted` and should not add bold styling. Body text should usually have no class and use the default foreground color. Keep layout-specific classes widget-local, and combine them with these semantic classes when needed, such as `classes="field-label label"` or `classes="field-helper muted"`. Avoid generic variant-like global class names such as `.secondary`, because they can collide with Textual or widget-specific styling.

When a visible border is used as a panel boundary, give the panel a meaningful `border_title` instead of rendering an in-content heading for that same panel. Do not force border titles onto control borders, such as an input composer border, where the border is part of the control rather than a panel container.

Keep API response validation and generated-model adaptation inside loaders/controllers. Screens should receive generated models directly when they are already ergonomic for rendering and state management; otherwise loaders/controllers may adapt responses into TUI-owned models from `models.py`.

When adapting discriminated unions or dispatching across two or more concrete generated model/state classes, prefer `match` over repeated `isinstance(...)` branches. Add a `case _ as never: assert_never(never)` fallback for closed unions so adding a new branch fails loudly instead of falling through. Single `isinstance(...)` type guards are fine when there is only one branch.

When a focused widget has a built-in binding for a key, that widget binding can hide or override a screen-level binding in the Footer. For widgets like `DataTable`, prefer handling the widget event such as `RowSelected` in the screen, and override the widget binding label only when the Footer needs to show app-specific wording.

Use `can_focus` deliberately. Container widgets that exist only for layout should usually set `can_focus = False` so keyboard focus lands on meaningful controls, while interactive widgets and panes that need direct keyboard handling should remain focusable.

For screen-owned form or wizard state, prefer a single authoritative state reactive on the screen, such as `form_state`. When child widgets need to update that state, define a screen-local message subclass of `tui.shared.state.StateChanged[StateType]`, and apply its pure update callable in one screen handler such as `handle_form_state_changed`. This keeps updates race-resistant and avoids drilling the current full state through multiple widget layers. Update callables must be small, pure, and side-effect free.

Prefer uncontrolled input widgets for TUI forms. Pass initial values when the section/widget is mounted, let the Textual input own its live value while focused, and post update messages as values change. Do not globally recompose on ordinary input changes. If a parent state change significantly changes the form shape, such as switching a strategy mode that changes which fields exist, the screen or owning section should explicitly remount only that affected area.

Prefer explicit constructor props over ad hoc context helpers. Pass initial section state and read-only dependencies such as option lists through constructors, and post messages upward for mutations. Avoid child widgets mutating screen state directly; let the screen handler apply update messages so state changes stay centralized, typed, and observable.

Do not defensively catch `NoMatches` around `query_one(...)` for children that the same screen or widget always composes. If a required child is missing, let the error surface because that indicates a broken composition invariant. Only handle missing widgets when absence is a real, expected state.

Prefer `tui.shared.textual.on` over importing Textual's `on` decorator directly. The TUI wrapper stops message bubbling by default with `stop=True`; pass `stop=False` only when a handler intentionally lets the message continue upward. Decorated message handlers should use descriptive `handle_*` names, such as `handle_judge_model_changed`, instead of Textual's implicit `on_xxx` method names. Keep `on_mount`, `on_unmount`, and other lifecycle hooks as `on_xxx` methods.

When a decorated handler targets a specific widget among multiple controls, use a clear widget ID without incidental prefixes, for example `id="judge-model"` with `@on(Select.Changed, "#judge-model")`. Do not use placeholder prefixes such as `alt-`.

Prefer targeting decorated handlers with an `@on(...)` selector over subscribing broadly and filtering inside the handler with checks like `event.widget.has_class(...)`. Use handler-side filtering only when the condition depends on runtime state that a selector cannot express, such as ignoring events from inactive but still-mounted mode widgets.

Prefer Textual's `@work(...)` decorator for workers instead of calling `run_worker(...)` directly. Call the decorated method from event handlers or lifecycle hooks. Use direct `run_worker(...)` only when worker options must be computed dynamically, such as a group name derived from a runtime id. Worker methods do not need a private underscore prefix just because they are implementation details; prefer readable public-style names for decorated workers.

Organize Textual screen and widget classes in this order: `DEFAULT_CSS`, `BORDER_TITLE`, `BINDINGS`, `can_focus`, reactive state declarations, `__init__`, `compose` or `compose_content`, `on_mount`, event handlers such as decorated `handle_*` methods, `check_action`, action handlers such as `action_xxx`, workers decorated with `@work`, then other private helper methods.

## Settings

Use `pydantic-settings` for TUI settings when values come from environment variables or `.env`.

Use the `TUI_` environment prefix for TUI-specific settings. For example, `api_base_url` maps to `TUI_API_BASE_URL`.
