#!/usr/bin/env bash
# Start the Rust server and Python client, and stop both when either exits.
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! command -v cargo >/dev/null 2>&1; then
  echo "[launcher] Rust/Cargo is required but was not found in PATH." >&2
  exit 127
fi

if [[ -z "${DATABASE_PATH:-}" ]]; then
  export DATABASE_PATH="$ROOT_DIR/database"
fi
if [[ -z "${DATABASE_URL:-}" ]]; then
  export DATABASE_URL="sqlite:${DATABASE_PATH%/}/the_last_signal.db"
fi
mkdir -p "$DATABASE_PATH" || {
  echo "[launcher] Could not create DATABASE_PATH: $DATABASE_PATH" >&2
  exit 1
}

if command -v python >/dev/null 2>&1; then
  PYTHON_BIN="${PYTHON:-python}"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="${PYTHON:-python3}"
else
  echo "[launcher] Python is required but neither python nor python3 was found." >&2
  exit 127
fi

echo "[launcher] Building Rust server..."
if ! (cd "$ROOT_DIR/server_rust" && cargo build --locked); then
  echo "[launcher] Server build failed; the client was not started." >&2
  exit 1
fi

SERVER_BIN="$ROOT_DIR/server_rust/target/debug/the-last-signal-server"
if [[ ! -x "$SERVER_BIN" ]]; then
  echo "[launcher] Expected server executable was not produced: $SERVER_BIN" >&2
  exit 1
fi

CLIENT_PID=""
SERVER_PID=""

cleanup() {
  trap - EXIT INT TERM
  if [[ -n "$CLIENT_PID" ]] && kill -0 "$CLIENT_PID" 2>/dev/null; then
    kill -TERM "$CLIENT_PID" 2>/dev/null || true
  fi
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill -TERM "$SERVER_PID" 2>/dev/null || true
  fi
  if [[ -n "$CLIENT_PID" ]] && kill -0 "$CLIENT_PID" 2>/dev/null; then
    sleep 2
    kill -KILL "$CLIENT_PID" 2>/dev/null || true
  fi
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    sleep 2
    kill -KILL "$SERVER_PID" 2>/dev/null || true
  fi
  if [[ -n "$CLIENT_PID" ]]; then
    wait "$CLIENT_PID" 2>/dev/null || true
  fi
  if [[ -n "$SERVER_PID" ]]; then
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

echo "[launcher] Starting Rust server (127.0.0.1:5000)..."
"$SERVER_BIN" &
SERVER_PID=$!

READY=0
for ((attempt = 1; attempt <= 60; attempt++)); do
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    wait "$SERVER_PID"
    status=$?
    echo "[launcher] Server exited before becoming ready (exit $status)." >&2
    exit "$status"
  fi
  if command -v python3 >/dev/null 2>&1; then
    if python3 -c 'import socket; s=socket.socket(); s.settimeout(0.5); s.connect(("127.0.0.1", 5000)); s.close()' >/dev/null 2>&1; then
      READY=1
      break
    fi
  elif "$PYTHON_BIN" -c 'import socket; s=socket.socket(); s.settimeout(0.5); s.connect(("127.0.0.1", 5000)); s.close()' >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 1
done

if [[ "$READY" -ne 1 ]]; then
  echo "[launcher] Server did not listen on 127.0.0.1:5000 within 60 seconds." >&2
  exit 1
fi

echo "[launcher] Server is ready; starting Python client..."
"$PYTHON_BIN" -m client_python.main &
CLIENT_PID=$!

while :; do
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    wait "$SERVER_PID"
    status=$?
    echo "[launcher] Server stopped; shutting down the client." >&2
    exit "$status"
  fi
  if ! kill -0 "$CLIENT_PID" 2>/dev/null; then
    wait "$CLIENT_PID"
    status=$?
    echo "[launcher] Client stopped; shutting down the server."
    exit "$status"
  fi
  sleep 0.5
done
