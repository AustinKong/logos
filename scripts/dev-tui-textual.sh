#!/usr/bin/env bash
set -euo pipefail

TUI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../apps/tui" && pwd)"
cd "$TUI_ROOT"

export TUI_API_BASE_URL="${TUI_API_BASE_URL:-http://127.0.0.1:8000}"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
TEXTUAL_DEVTOOLS_HOST="${TEXTUAL_DEVTOOLS_HOST:-127.0.0.1}"
TEXTUAL_DEVTOOLS_PORT="${TEXTUAL_DEVTOOLS_PORT:-8081}"
TEXTUAL_CONSOLE_EXCLUDE="${TEXTUAL_CONSOLE_EXCLUDE-EVENT,DEBUG,SYSTEM,WORKER}"

console_exclude_args() {
  local groups=()
  local args=()
  IFS="," read -r -a groups <<<"$TEXTUAL_CONSOLE_EXCLUDE"

  for group in "${groups[@]}"; do
    group="${group//[[:space:]]/}"
    if [[ -n "$group" ]]; then
      args+=("--exclude" "$group")
    fi
  done

  if ((${#args[@]} > 0)); then
    printf "%q " "${args[@]}"
  fi
}

open_console() {
  local console_cmd
  local exclude_args
  exclude_args="$(console_exclude_args)"
  printf -v console_cmd "cd %q && uv run textual console --port %q %s; exec bash" "$TUI_ROOT" "$TEXTUAL_DEVTOOLS_PORT" "$exclude_args"

  if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal --title="Logos TUI Console" -- bash -lc "$console_cmd" >/dev/null 2>&1 &
    return 0
  fi

  if command -v x-terminal-emulator >/dev/null 2>&1; then
    x-terminal-emulator -e bash -lc "$console_cmd" >/dev/null 2>&1 &
    return 0
  fi

  if command -v konsole >/dev/null 2>&1; then
    konsole --new-tab -p tabtitle="Logos TUI Console" -e bash -lc "$console_cmd" >/dev/null 2>&1 &
    return 0
  fi

  if command -v kitty >/dev/null 2>&1; then
    kitty --title "Logos TUI Console" bash -lc "$console_cmd" >/dev/null 2>&1 &
    return 0
  fi

  if command -v wezterm >/dev/null 2>&1; then
    wezterm start -- bash -lc "$console_cmd" >/dev/null 2>&1 &
    return 0
  fi

  return 1
}

wait_for_console() {
  for _ in {1..50}; do
    if bash -c ":</dev/tcp/$TEXTUAL_DEVTOOLS_HOST/$TEXTUAL_DEVTOOLS_PORT" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.1
  done

  return 1
}

if ! open_console; then
  echo "Could not open a second terminal for Textual console."
  echo "Run this in another terminal for dev logs: cd apps/tui && uv run textual console --port $TEXTUAL_DEVTOOLS_PORT $(console_exclude_args)"
elif ! wait_for_console; then
  echo "Textual console did not become ready on $TEXTUAL_DEVTOOLS_HOST:$TEXTUAL_DEVTOOLS_PORT."
  echo "Starting the app anyway; restart it after the console is ready if devtools does not connect."
fi

exec uv run textual run --dev --host "$TEXTUAL_DEVTOOLS_HOST" --port "$TEXTUAL_DEVTOOLS_PORT" tui.app:TuiApp
