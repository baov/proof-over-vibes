#!/usr/bin/env bash
# Runs the harness checks: INV-001 (layers), INV-002 (test-case bridge). Mutation (INV-003) is slow and runs on its own:
#   bash tools/harness/run_all.sh --with-mutation   adds `run_mutation.sh --scope critical`
#   --root <path>                                   project root (default: current directory)
# Exit: 1 if any check failed at `error` severity (or could not run), else 2 if only `warn` violations, else 0.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$PWD"; MUTATION=0
while [ $# -gt 0 ]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --with-mutation) MUTATION=1; shift ;;
    --explain) echo "Runs check_layers.py (INV-001), check_test_coverage.py (INV-002) and, with --with-mutation, run_mutation.sh (INV-003). Worst exit code wins: 1 over 2 over 0."; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done
worst=0
record() { local c=$1; if [ "$c" = 1 ]; then worst=1; elif [ "$c" = 2 ] && [ "$worst" = 0 ]; then worst=2; elif [ "$c" -gt 2 ]; then worst=1; fi; }

echo "== INV-001 layers"; python3 "$HERE/check_layers.py" --root "$ROOT"; code=$?; record $code; echo "-> exit $code"
echo "== INV-002 test-case bridge"; python3 "$HERE/check_test_coverage.py" --root "$ROOT"; code=$?; record $code; echo "-> exit $code"
if [ "$MUTATION" = 1 ]; then
  echo "== INV-003 mutation (critical)"; bash "$HERE/run_mutation.sh" --scope critical --root "$ROOT"; code=$?; record $code; echo "-> exit $code"
fi
echo "== harness exit $worst"
exit $worst
