#!/usr/bin/env bash
# usage: run.sh current   -> code as it stands (HEAD)
#        run.sh before    -> same code with the in-memory store as of 347911f^ (toggle: pair index neutralized)
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(git rev-parse --show-toplevel)
PN=examples/professional-network
if [ "${1:-current}" = before ]; then
  T=$(mktemp -d); cp -R "$ROOT/$PN/src/connections" "$T/connections"
  git show 347911f^:$PN/src/connections/infrastructure/in-memory-store.ts > "$T/connections/infrastructure/in-memory-store.ts"
  export CONNECTIONS_SRC="$T/connections/index.ts"
fi
cd repro && ../../../../node_modules/.bin/vitest run --config vitest.config.ts 2>&1 | grep -E "send:|✓|✗|×|FAIL|Tests|expected|Expected|Received" || true
