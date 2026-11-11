#!/usr/bin/env bash
# Runs every harness check. Worst exit code wins (1 error > 2 warn > 0).
cd "$(dirname "$0")/../.." || exit 1
worst=0
for s in check_layers.py check_clock.py check_shape.py check_test_coverage.py; do
  python3 tools/harness/$s --root . ; rc=$?
  if [ $rc -eq 1 ] || { [ $rc -eq 2 ] && [ $worst -eq 0 ]; }; then worst=$rc; fi
done
exit $worst
