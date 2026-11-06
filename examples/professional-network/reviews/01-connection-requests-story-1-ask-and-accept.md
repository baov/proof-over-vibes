---
role: reviewer
status: escalate
verdict: GO
reasons:
  - "Gauntlet green (22 tests, typecheck, harness 0 warnings, selftest 5/5, mutation 98.9%). No blocking finding, two major findings (below the NO-GO threshold of three)."
  - "Escalate: the diff touches the Sensitive zones of docs/technical/invariants.md (repository port src/connections/application/ports.ts, src/connections/infrastructure/in-memory-store.ts, public entry point src/connections/index.ts). A human reviews those before merge."
severity: major
open_majors:
  - "M1: an id from the id generator that already exists silently replaces the stored request (saveRequest overwrites); no decision says what a collision must do."
  - "M2: any caller can read any member's pending list and any pair's state; no document says who may ask, and neither query takes the acting member (the sensitive-zone promise is 'readable by connections only')."
---

# Pre-merge review: claude/bank-account-poc-1435f8 (connection requests, story 1, ask-and-accept)

**Verdict: GO** (escalated: sensitive zones touched)
**Date**: 2026-10-18 · **Base**: 2b01a1c..b280db0 · **Scope**: 44 files under examples/professional-network, +1146/-52 (11 source files, 5 test files + support, 22 test-case files, decisions.md, package.json/lock)
**Criticality**: critical (domain layer, public entry point, shared contract). Iteration n=1.

## Summary

The diff builds story 1: send, accept, pair state and pending list in one hexagonal `connections` module, with seven distinct returned rejection reasons, matching the plan and decisions D-1 to D-23. The gauntlet is fully green and the code follows ADR-0001 and the layer invariants. Two behaviors a consumer would see are settled by no document (id collision, who may query), hence two major findings; that is below the NO-GO threshold, so the verdict is GO, escalated to a human because sensitive zones are touched.

## Gauntlet

| Check | Result |
|-------|--------|
| Test suite (`npm test`) | OK: 5 files, 22 tests |
| Typecheck (`npm run typecheck`) | OK, clean |
| Harness invariants (`npm run harness`) | OK: check_layers 0, check_shape 0 |
| Test-case bridge | OK: 22 cases, 22 covered_ok, 0 pending, 0 orphan |
| Harness selftest | OK: 5 pass, 0 fail |
| Mutation (`npm run mutation`, critical scope, 11 files) | 98.9% (88 killed / 89), no threshold set (baseline, not a gate). 1 survivor: `src/connections/domain/send-rules.ts:21` ConditionalExpression (`r.state === "pending"` replaced by `true`) |
| Test-cases touched | 22 new, skimmed (source and automated_test checked by the bridge); those on rejection reasons and pending list read in full against the tests |

The survivor is an equivalent mutant in story 1: the only non-pending request is an accepted one, and `already-connected` is decided first. It becomes killable once declined and withdrawn exist (story 2). Not a defect now; see m3.

## Findings

### Blocking
None.

### Major
- **[M1] Request id collision overwrites an existing request** — `src/connections/infrastructure/in-memory-store.ts:12-16`, `src/connections/application/ports.ts:11`, `src/connections/application/send-request.ts:21-22` · angle: bugs
  `sendRequest` takes `deps.ids.next()` and calls `saveRequest`, which replaces any stored request with the same id. A generator that repeats an id (D-20: the caller supplies ids) overwrites another pair's request, including an accepted one, with a fresh pending one, while the connection stays: the pair then reports connected with request state pending, and the earlier request is gone. D-20 settles who supplies ids, not what a duplicate does. Consumer-visible and undecided: ask the product owner (reject with its own reason, or state that uniqueness is the generator's contract). Recommendation: separate a create-only store method from the replace needed by accept.
- **[M2] Who may read a pair's state or a member's pending list is undecided** — `src/connections/index.ts:23-25`, `src/connections/application/pending-requests.ts:5-9`, `src/connections/application/pair-state.ts:6-14` · angle: security
  `listPendingRequests(recipient)` and `getPairState(a, b)` answer for any members asked, with no acting member (unlike `acceptRequest`). Whoever can call the module learns who asked whom and who is connected to whom, the data the product promises to show "to connections only" (sensitive zone for `src/*/index.ts`). PRD R5 and R6 say what is returned, not to whom; sign-in is out of scope, so authorization may legitimately live above the module, but no document says so. Ask: is the module a trusted internal API (write that down in an ADR or the decision log), or must these queries take the asking member?

### Minor
- **[m1] Returned requests are the stored objects** — `in-memory-store.ts:28-39`. `readonly` is compile-time only; a caller can mutate `state` on a returned request and alter the store. Return copies or freeze. Hesitated with major (in-memory adapter only); kept minor.
- **[m2] Toolchain change outside the plan** — `package.json`, `package-lock.json` (commit 8a0ce23). Vitest moved from `^5.0.5` to `^4.1.12` because Stryker 10's runner does not activate mutants under Vitest 5. Documented by the developer and the mutation run confirms it works, but the plan said "no dependency to add" and the lock churn is large (238 lines). A person should confirm the downgrade at merge.
- **[m3] Plan sections 8 to 10 are still empty** — `plan.md`. Deviations exist: `domain/reasons.ts` not created (reasons are inline per module), step 1 folded into step 2, the Vitest pin. Record them, and track the survivor at `send-rules.ts:21` as a follow-up for story 2 (today only the developer note carries it).
- **[m4] Pair state assumes one request per pair** — `src/connections/domain/pair-state.ts:15` takes `between.at(-1)`. Correct for story 1; story 2 must apply D-12 (pending if any, else most recent). A one-line comment pointing at D-12 would prevent a silent wrong answer.

## Angles, in brief

1. Bugs and regressions: authorization before not-pending (D-13), not-found for any actor (D-16), duplicate and reverse rules per pair, both directions after accept, symmetric state, "none" for unknown pairs: correct and asserted with exact reason and unchanged state. Only M1 found.
2. Security: no secrets, no injection surface, no source dependency added; unauthenticated reads (M2).
3. ADR and architecture: layering respected (harness green), rejections returned, domain pure (no Date, no crypto), request as state machine, bridge complete, PRD vocabulary respected (no friend, invite, reject). The test-cases match the plan and D-11 to D-19; no vocabulary drift.
4. Debt and readability: small functions, one named guard per send rule, comments explain why. Nothing beyond the minors.

## Checks not performed

No glossary exists (PRD vocabulary used instead). Concurrency, member id validity (D-15) and a decliner sending back are deliberately open per the brief, so not judged. Persistence beyond the in-memory adapter is not verified; atomicity of `saveAccepted` is only a port contract.

## Positive notes

- Tests go through the public entry point and assert exact reasons and unchanged state after every rejection; the 98.9% mutation score confirms they protect behavior, and the developer left the single survivor honestly unexcluded.
- The accept port method writes request and connection together, anticipating a real store.
- The developer note is candid about the Vitest pin and the missing default id generator.
