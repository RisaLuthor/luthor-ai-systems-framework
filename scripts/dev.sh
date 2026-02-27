#!/usr/bin/env bash
set -euo pipefail

# Load .env if present (local dev)
if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

export LAF_API_TOKEN="${LAF_API_TOKEN:-dev-token}"

BASE_PORT="${PORT:-8000}"

pick_port () {
  local p="$1"
  python - "$p" <<'PY'
import socket, sys
p=int(sys.argv[1])
s=socket.socket()
try:
    s.bind(("0.0.0.0", p))
    s.close()
    print(p)
except OSError:
    print("")
PY
}

PORT_CHOSEN=""
for offset in 0 1 2 3 4 5; do
  cand=$((BASE_PORT + offset))
  ok="$(pick_port "$cand")"
  if [[ -n "$ok" ]]; then
    PORT_CHOSEN="$ok"
    break
  fi
done

if [[ -z "$PORT_CHOSEN" ]]; then
  echo "No free port found starting at ${BASE_PORT}"
  exit 1
fi

echo "Starting LAF on port ${PORT_CHOSEN} (token set)"
exec uvicorn laf.api.main:app --reload --host 0.0.0.0 --port "${PORT_CHOSEN}"
