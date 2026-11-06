---
role: reviewer
status: escalate
verdict: GO
reasons:
  - "Gauntlet green (74 tests, typecheck, harness 0 violation / 73 test-cases covered, selftest 5/5, mutation 100.0% 161/161)."
  - "Requirements 1 to 8 covered; the blank check precedes every other rule in the seven operations; requirement 4 behaviors unchanged."
  - "Escalate: the diff touches src/connections/index.ts, a Sensitive zone (public result shapes of three operations changed); a human reviews before merge."
severity: minor
open_majors: []
---

> Translation note: the body of this report was written in French by the Reviewer, although the project is in English. The Orchestrator translated it afterwards, without changing a finding. The commit ids cite the history before the commits were grouped by stage.

# Pre-merge review, claude-bank-account-poc-1435f8, edge-ids-and-decliner (iteration 1)

**Verdict: GO** (status `escalate`: sensitive zone)
**Date**: 2026-10-18 · **Base**: 54530f6..727e21a · **Scope**: 43 files (22 test-cases, 7 sources, 9 tests/support), +762/-93
**Criticality**: critical, because the diff touches `src/connections/index.ts` (public contract, sensitive zone) and the domain (`member-id.ts`).

## Summary

A single helper `blankIdRejection` is called on the first line of the seven use cases, before any read of the store and before any other rule. Case (b) needed no production code: only tests and test-cases pin it. The return shapes of `getPairState`, `listPendingRequests` and `eraseMember` change (public contract), a decision taken by the Architect and accepted by delegation (answers.md). Nothing blocking or major.

## Gauntlet

| Check | Result |
|---|---|
| Test suite | OK, 74 tests, 9 files |
| Typecheck | OK |
| Harness invariants | OK, 0 violation (layers, shape) |
| Test-case bridge | OK, 73 test-cases covered_ok, 0 orphan, 0 broken |
| Harness selftest | OK, 5/5 |
| Mutation (critical) | 100.0 % (161 killed / 161), no survivor; threshold: none recorded (human decision, INV-010). The survivor `send-rules.ts:29` is killed. |
| Test-cases touched | 22 added, read by sampling, all aligned with their test (PRD R1 to R8) |

## Targeted checks

- **Blank before everything, seven operations.** send: both ids are tested before `requestsBetween`/`findConnection`/`decideSend`, so before `self-request`, `already-connected`, etc., and before an id is drawn (test "does not draw an id"). accept/decline/withdraw: before `findRequest`, so before `request-not-found`, `not-recipient`, `not-sender`, `not-pending` (tested on unknown, withdrawn, declined and accepted requests). getPairState: both ids, including `(blank, blank)`. listPending and erase: the id. Adversarial combinations read in the code (both ids blank, one blank and one identical to the other, a blank actor on a nonexistent request): all return `blank-member-id`. No flaw found.
- **Requirement 4 unchanged.** The old tests change only by the wrapper (`stateOf`/`pendingOf`), no assertion weakened. Kept and checked: a member's request to themselves = `none` (D-19), erase of an unknown member = `{ok:true}` (D-26), ids with whitespace around or inside are not blank (` alice `, `a b`), zero-width characters are not blank (D-33, `\p{White_Space}` and not `trim()`, a good choice for U+FEFF).
- **Case (b).** The guards in `send-rules.ts` are per direction; B to A after a refusal of A to B goes through, A to B stays `reverse-pending` (D-34), accepting connects, declining blocks both ways, the pair state gives pending, otherwise the most recent. 7 tests, mutation `r.sender === c.sender` -> `true` killed.
- **Contract `index.ts`.** `Connections`: three returns become `Result`, four rejections gain `blank-member-id`. No consumer outside the tests (ADR-0001, no other module). Documented in PRD section 6, architect.md, answers.md, RUN-NOTES.md line 52.
- **Would the tests catch a regression?** Yes: order tested per operation against every other reason, "nothing is stored/modified" checked by reading the state afterwards, id not drawn checked. Mutation 100 %.

## Findings

### Blocking
None.

### Major
None. The behaviors visible to the consumer (the name of the reason D-35, the definition of blank D-33, the reason of `send` D-34, the envelope of reads/erase via answers.md) are all settled by a document.

### Minor
- **[m1] D-19 and D-26 not amended** — `docs/business/decisions.md` (D-19 "a query does not reject", D-26 "always succeeds") · angle: compliance. These decisions are now false for a blank id, with no mention; only PRD section 6 says so. Recommendation: add an "amended by D-35 / edge-ids-and-decliner" line to D-19 and D-26.
- **[m2] `EraseResult` not re-exported by `index.ts`** — `src/connections/index.ts:6,32` · angle: debt. The type appears in the public interface but a consumer cannot name it (whereas `PairState` and `ConnectionRequest` can be named). Recommendation: export it with the other types, at the next pass over this file.
- **[m3] Non-string id at runtime** — `src/connections/domain/member-id.ts:13` · angle: bugs. `null`/`undefined` forced by a cast are converted to "null"/"undefined" by `RegExp.test` and count as non-blank. Out of scope (D-15, the `MemberId` type excludes it); to note if an untyped caller appears.

## Checks not performed

No missing reference material. The network/persistence layer does not exist (in-memory store), so there is no security point beyond input validation.

## Positive notes

- A single source of truth for the blank rule (the domain) and for the guard (the helper), seven one-line calls.
- Choosing `\p{White_Space}` rather than `trim()` avoids a false blank on U+FEFF, and a test pins it.
- The case (b) tests are checked by mutation and not only green from the start.
