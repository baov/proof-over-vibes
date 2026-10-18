#!/usr/bin/env bash
# Runs every harness check except mutation (too slow: `npm run mutation`). Exit: 1 if any error, 2 if only warnings, else 0.
# Usage: bash tools/harness/run_all.sh [--root <path>]
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_args=("$@")
worst=0
for check in check_layers check_shape check_test_coverage; do
  echo "== $check"
  node "$here/$check.mjs" ${root_args[@]+"${root_args[@]}"}
  rc=$?
  if [ "$rc" = 1 ] || { [ "$rc" = 2 ] && [ "$worst" = 0 ]; }; then worst=$rc; fi
  [ "$rc" -gt 2 ] && worst=1
done
exit "$worst"
