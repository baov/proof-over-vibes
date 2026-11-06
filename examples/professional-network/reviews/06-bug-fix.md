---
role: reviewer
status: escalate
verdict: GO
reasons:
  - "Gauntlet green (88 tests, typecheck, harness 0 violation / 87 test-cases covered, selftest 6/6, mutation 90.1% with no threshold)."
  - "The root cause is removed (ambiguous pair key), not the symptom; the two tests fail without the fix (checked in a copy outside the repository)."
  - "Escalate: the diff touches src/connections/infrastructure/in-memory-store.ts, a sensitive zone (storage of a member's relationships, erasure); a human reviews before merge."
severity: minor
open_majors:
  - "Carried over from the previous request, not in this diff: an operation that never settles blocks the module (no timeout, undecided)."
---

> Translation note: the Reviewer wrote this report in French, although the project is in English. The Orchestrator translated it afterwards, without changing a finding. The commit ids cite the history before the commits were grouped by stage.

# Pre-merge review, claude-bank-account-poc-1435f8, bug-unrelated-members-connected (iteration 1)

**Verdict: GO** (status `escalate`: sensitive zone)
**Date**: 2026-10-18 · **Base**: 347911f..e93ab41 · **Scope**: 4 files (1 source, 1 test, 2 test-cases), +75/-1
**Criticality**: critical, because the diff touches the infrastructure of the connections module (sensitive zone: personal data, erasure).

## Summary

The fix is one line: `pairKey` goes from `[a, b].sort().join(":")` to `JSON.stringify([a, b].sort())`. Joining with `:` was ambiguous for free ids (D-15); JSON quotes and escapes each id, so the boundary between the two is explicit. The two proven symptoms (false connection / rejected send, overwrite then erasure D-26) are covered and the diff stays in scope.

## Gauntlet

| Check | Result |
|-------|----------|
| Test suite | OK: 11 files, 88 tests (86 + 2) |
| Typecheck | OK, no error |
| Harness invariants | OK: check_layers 0, check_shape 0, check_serialized 0 |
| Test-case bridge | OK: 87 test-cases, 87 covered_ok, 0 broken, 0 orphan |
| Harness selftest | OK: 6/6 |
| Mutation (scope critical) | 90.1% (145/161), threshold: none (INV-010 has no baseline); 16 survivors, all `NoCoverage` in `domain/connection.ts` (`connects()`) |
| Test-cases touched | 2 read: `colliding-ids-unrelated-members.md`, `colliding-ids-erase-keeps-other-pair.md` |

No check at `error`: the four-angle review took place.

## Judgment

- **Root cause, not symptom.** The only place where a pair is composed into a string was `pairKey` (the proof and my check of the proof both verified it). The fix makes the key injective on unordered pairs: `JSON.stringify` of an array of two strings is injective, including for quotes, backslashes and lone surrogate halves (escaped by `JSON.stringify`). The default sort stays consistent for any string, so (A, B) and (B, A) share the key. The O(1) cost wanted by 347911f is kept. A mere change of separator would not have closed the defect; that is not what was done.
- **The new tests fail without the fix.** Copy of the project outside the repository (scratchpad), `pairKey` put back to the `join(":")` version: the 2 new tests fail, 86 pass; with the fix, 88 pass. The repository was not modified by this check (`git status` clean).
- **All the symptoms are covered.** Test 1: the state for both argument orders, a send that succeeds as `pending`, the original pair still connected. Test 2: both pairs connected (the second `set` no longer overwrites the first), erasure of `ann:bo`, `(ann:bo, cy)` with no state, `(ann, bo:cy)` still connected. This is the `open_major` of the proof review; it is closed. The tests go through the module's public API: behavior, not structure.
- **Scope.** One line of source plus a comment, one test file, two test-cases. No change of public behavior, error type or interface; no id validation added (D-15 unchanged). Neither `stryker.config.mjs` nor the threshold touched.
- **ADR / invariants.** ADR-0001: the fix stays in the infrastructure, no dependency added. ADR-0002: no operation added outside the queue, `check_serialized` at 0. The two test-cases match D-15 and D-26 and invent no term absent from the glossary.
- **Visible behavior not settled.** None new: for a consumer, the correction brings back the behavior already decided (D-15, D-26: free ids, an erasure leaves nothing of the member). No `major` open from me.

## Findings

### Blocking
None.

### Major
None.

### Minor
- **[m1] Dead code `connects()`** — `src/connections/domain/connection.ts:12-15` · angle: debt
  No caller left in `src` or `tests` since 347911f (checked by search). Real maintenance cost (code that nothing runs, so unverified) and the only cause of the mutation score. Recommendation: delete it in a separate cleanup commit, outside this bug fix (outside the scope of the diagnosis; deleting it in the same commit would mix two intents).
- **[m2] Mutation score 90.1% against 100% before the regression** — `reports/mutation` · angle: debt
  The 16 survivors are all `NoCoverage` on `connects()` (L12 and L14), so on dead code, not on an unprotected behavior: no live behavior has a surviving mutant (145/145 of the live mutants killed). The fix did not change the score (90.1% before and after). Recommendation: after `connects()` is deleted the score should go back to 100%; check it at the next pass. The threshold stays a human decision (`mutation-threshold.json` is `null`, severity `warn`): nothing is written here, and a threshold must not be set on 90.1%, which is an artifact of the dead code.
- **[m3] The `pairKey` comment is a little long** — `in-memory-store.ts:53` · angle: debt
  Useful (it says why), no change required. One reservation: it could cite the trap (`ann:bo`/`cy` against `ann`/`bo:cy`), already in the test.

## Decision on the mutation score and the dead code

Leaving it as is is acceptable for a GO, and it is a `minor` finding, not a `major`. Reasons: (1) the score drops because of code nothing calls, not because a behavior lost its protection; (2) the fix does not make it worse and is not its cause (the dead code comes from 347911f); (3) no threshold is set, so INV-010 is not violated; (4) setting the threshold, excluding mutants or widening the fix to a deletion are for the human or a separate request. The finding stays visible so that the cleanup gets done.

## Checks not performed

No missing check: ADR, invariants, test-cases and decisions are present. The test of real persistence does not exist (in-memory store only).

## Positive notes

- Minimal fix, at the cause, with the encoding choice justified (separator, nested map and revert rejected for good reasons).
- Red confirmed before green (tests commit `cab6193` then `e93ab41`), and the second symptom reported by the proof review is tested.
- The Developer's note is honest about the mutation: the observation, the cause, and the threshold left to the human.
