#!/usr/bin/env bash
# INV-010 — mutation testing wrapper (block D). Never writes a test, never edits the config or the threshold.
# Usage: run_mutation.sh [--scope critical|diff|full] [--explain] [--root <path>]
# Exit: 0 OK, 1 below an `error` threshold, 2 below a `warn` threshold (or run problem: see stderr).
set -euo pipefail

scope="critical"; root="$(pwd)"; explain=0
while [ $# -gt 0 ]; do
  case "$1" in
    --scope) scope="$2"; shift 2 ;;
    --root) root="$(cd "$2" && pwd)"; shift 2 ;;
    --explain) explain=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [ "$explain" = 1 ]; then
  cat <<'TXT'
[INV-010] Mutation score of the critical scope
Tool: Stryker (vitest runner), config: stryker.config.mjs. Report: reports/mutation/mutation.json (gitignored).
Scopes: critical = src/connections/domain + application (default); diff = critical files changed against
the merge base of main; full = same as critical until other modules hold domain rules.
Threshold: tools/harness/mutation-threshold.json (null until the first baseline; then baseline rounded down).
Severity: warn. Never in pre-commit: a run takes minutes. A surviving mutant means an unprotected behavior:
write a test that expresses the behavior, never one that only kills the mutant.
TXT
  exit 0
fi

cd "$root"
critical_globs=("src/connections/domain" "src/connections/application")
files=()
for d in "${critical_globs[@]}"; do
  [ -d "$d" ] && while IFS= read -r f; do files+=("$f"); done < <(find "$d" -name '*.ts' ! -name '*.test.ts' ! -name '*.d.ts' | sort)
done

if [ "$scope" = "diff" ]; then
  base="$(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main 2>/dev/null || true)"
  if [ -z "$base" ]; then echo "no merge base with main: cannot compute the diff scope" >&2; exit 1; fi
  changed="$(git diff --name-only "$base" -- "${critical_globs[@]}")"
  picked=()
  for f in ${files[@]+"${files[@]}"}; do grep -qxF "$f" <<<"$changed" && picked+=("$f"); done
  files=(${picked[@]+"${picked[@]}"})
elif [ "$scope" != "critical" ] && [ "$scope" != "full" ]; then
  echo "unknown scope: $scope" >&2; exit 1
fi

if [ "${#files[@]}" -eq 0 ]; then
  echo "MUTATION — scope: $scope · nothing to mutate (no production file in scope yet)"
  exit 0
fi

mutate="$(IFS=,; echo "${files[*]}")"
err="$(mktemp)"; trap 'rm -f "$err"' EXIT
mkdir -p reports/mutation; rm -f reports/mutation/mutation.json
set +e
npx stryker run --mutate "$mutate" >/dev/null 2>"$err"
rc=$?
set -e
if [ ! -f reports/mutation/mutation.json ]; then
  echo "stryker produced no report (exit $rc). If it says \"No tests were executed\", a file in scope has no test importing it: that is itself an unprotected behavior." >&2
  cat "$err" >&2; exit 1
fi
node tools/harness/mutation_report.mjs --root "$root" --label "$scope (${#files[@]} files)"
