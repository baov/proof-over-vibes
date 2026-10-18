#!/usr/bin/env bash
# INV-003 -- mutation testing (block D), PIT through Maven.
#   --scope critical|diff|full   (default critical)
#   --explain                    describe scope, tool and threshold; run nothing
#   --root <path>                project root (default: current directory)
# Exit: 0 OK (or no threshold set yet), 1 below an `error` threshold or the run failed, 2 below a `warn` threshold.
# Never writes a test, never edits the PIT config (pom.xml) or the threshold (a human decision, see invariants.md).
# Never in pre-commit: a run takes minutes at least.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_maven.sh
. "$HERE/_maven.sh"

SCOPE=critical
ROOT="$PWD"
EXPLAIN=0
THRESHOLD=""            # percent; empty = none yet (INV-003: set after the first baseline, by a human)
THRESHOLD_SEVERITY=warn # warn | error

while [ $# -gt 0 ]; do
  case "$1" in
    --scope) SCOPE="$2"; shift 2 ;;
    --root) ROOT="$2"; shift 2 ;;
    --explain) EXPLAIN=1; shift ;;
    *) echo "unknown argument: $1 (usage: run_mutation.sh [--scope critical|diff|full] [--explain] [--root <path>])" >&2; exit 1 ;;
  esac
done

case "$SCOPE" in critical|diff|full) ;; *) echo "invalid scope: $SCOPE" >&2; exit 1 ;; esac
ROOT="$(cd "$ROOT" && pwd)"

if [ "$EXPLAIN" = 1 ]; then
  cat <<TXT
[INV-003] Mutation testing -- tool: PIT (pitest-maven + pitest-junit5-plugin), report: target/pit-reports/mutations.xml
  critical  (default) packages <base>.domain and <base>.application, as set in pom.xml (pit.targetClasses)
  diff      only the classes of domain/application changed against the merge-base with main
  full      the whole base package (including adapters); slow, for a scheduled run
  threshold: ${THRESHOLD:-none yet} (a human sets it from the first baseline, rounded down; then it only prevents regression)
A surviving mutant is a question: which behavior is unprotected? Answer with a test that states the behavior, never with
a test written to kill the mutant. If the mutant matches no behavior that counts, exclude it in pom.xml with a comment.
TXT
  exit 0
fi

MVN="$(resolve_mvn)" || { echo "pom.xml:1: [INV-003] Maven not found -- put mvn on the PATH or set MVN_CMD" >&2; exit 1; }
cd "$ROOT"
BASE_PKG="$(sed -n 's:.*<base.package>\(.*\)</base.package>.*:\1:p' pom.xml | head -n 1)"
ARGS=()
case "$SCOPE" in
  critical) ;;
  full) ARGS+=("-Dpit.targetClasses=${BASE_PKG}.*") ;;
  diff)
    BASE_REF="$(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main 2>/dev/null || true)"
    if [ -z "$BASE_REF" ]; then echo "pom.xml:1: [INV-003] no merge-base with main found -- use --scope critical" >&2; exit 1; fi
    TOP="$(git rev-parse --show-toplevel)"
    PREFIX="$(python3 -c 'import os,sys;print(os.path.relpath(sys.argv[1],sys.argv[2]))' "$ROOT" "$TOP")"
    [ "$PREFIX" = "." ] && PREFIX_RE="" || PREFIX_RE="${PREFIX}/"
    CLASSES="$(git diff --name-only "$BASE_REF" -- "$ROOT" \
      | sed -n -E "s#^${PREFIX_RE}src/main/java/(.*/(domain|application)/.*)\.java\$#\1#p" | tr '/' '.' | sed 's/$/*/' | paste -sd, -)"
    if [ -z "$CLASSES" ]; then echo "MUTATION -- scope: diff: no domain/application class changed, nothing to mutate"; exit 0; fi
    ARGS+=("-Dpit.targetClasses=${CLASSES}")
    ;;
esac

OFFLINE=(); [ "${MVN_OFFLINE:-0}" = 1 ] && OFFLINE=(-o)
rm -rf target/pit-reports
LOG="$(mktemp)"
if ! "$MVN" -B ${OFFLINE[@]+"${OFFLINE[@]}"} test-compile org.pitest:pitest-maven:mutationCoverage ${ARGS[@]+"${ARGS[@]}"} >"$LOG" 2>&1; then
  tail -n 25 "$LOG" >&2
  echo "pom.xml:1: [INV-003] the mutation run failed (see above) -- the suite must be green before mutating" >&2
  exit 1
fi

python3 "$HERE/_pit_report.py" --report target/pit-reports/mutations.xml --scope "$SCOPE" \
  --threshold "${THRESHOLD}" --severity "$THRESHOLD_SEVERITY"
