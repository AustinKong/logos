1. Investigate how the Fastapi model/schema convention will affect codegen, especially wrt affecting query params. Does query param need special naming convention etc.
2. Setup agent skills for commit conventions etc.
3. Migrate api/ SQLAlchemy internals to use async instead of sync
4. ~~Apply formatting rules to all screens in tui, as defined in AGENTS.md~~
5. Consider adding an endpoint to AI-generate an entire session config for the user, ~~not just participants~~.
6. Clean up plurality in folder structure and class names across the project
7. Clean up other TUI pages to follow the session_config pattern: screen chrome in `widgets/`, feature slices in colocated directories with section state, adapters, validation, and widgets.
