---
role: reviewer
status: escalate
verdict: GO
reasons:
  - "Gauntlet green (51 tests, typecheck, harness 50/50 covered, selftest 5/5, mutation 99.3%). One major finding (decline direction undecided), under the three-major NO-GO threshold."
  - "Escalate: the diff touches the Sensitive zones (store port in application/ports.ts, infrastructure/in-memory-store.ts, index.ts, erasure): a human reviews before merge."
severity: major
open_majors:
  - "M1: after A->B is declined, B sending to A is accepted by the code; no document decides whether a decline also blocks the decliner's own request back (open point 3, stories.md). Ask it before any story relies on it."
---

# Pre-merge review — claude/bank-account-poc-1435f8, story 2 (decline-and-withdraw)

**Verdict: GO** (status `escalate`: Sensitive zones touched, human review before merge)
**Date**: 2026-10-18 · **Base**: 9f28130..1a3147a · **Scope**: examples/professional-network only, 46 files, +928/-20 (src ~160 lines, tests ~400, 28 new test-case files)
**Criticality**: critical — domain layer, public entry point (`index.ts`), data erasure, store port.
**Iteration**: n=1 (counter 0 before this review). This report is named `-story2-1` so as not to overwrite the story 1 report `claude-bank-account-poc-1435f8-2026-10-18-1.md`.

## Summary

Story 2 adds decline, withdraw, the decline block, the pair state for declined/withdrawn/several requests, `eraseMember`, and `request-id-taken`. The behavior follows the plan and D-24 to D-32; code and tests are tidy and well bounded. One consumer-visible behavior is left to the code with no decision: whether the decliner may send a request back. It is the only major, so the verdict is GO, with that point carried in `open_majors`.

## Gauntlet

| Check | Result |
|-------|--------|
| Test suite (`npm test`) | OK — 8 files, 51 tests |
| Typecheck (`npm run typecheck`) | OK — clean |
| Harness invariants (`npm run harness`) | OK — check_layers 0, check_shape 0 |
| Test-case bridge | OK — 50 test-cases, 50 covered_ok, 0 broken, 0 pending, 0 orphan |
| Harness selftest | OK — 5/5 |
| Mutation (`npm run mutation`, critical scope, 14 files) | 99.3% (138 killed / 139), no threshold set (INV-010: a human sets it). 1 survivor: `src/connections/domain/send-rules.ts:29` ConditionalExpression (`r.sender === c.sender` -> `true` in `previouslyDeclined`) |
| Test-cases touched | 28 new files under `docs/business/test-cases/connections/`; sampled/read (e.g. erase-lifts-decline-block), front-matter validated by the bridge |

The survivor is real and explained: only a test about a decliner sending back would kill it, which is open point 3 (see M1). The developer correctly neither wrote a speculative test nor excluded it in `stryker.config.mjs`. The story 1 survivor (`send-rules.ts` `r.state === "pending"` -> `true`) is gone.

## Carried-over majors (from story 1)

- **M1 (id collision silently replaces)**: handled as D-25/D-32 say. `addRequest` returns `id-taken`, send rejects with `request-id-taken`, nothing stored, existing request unchanged; business rules are checked first and the id is drawn only after (`send-request.ts`). Tests: "rejects a request whose generated id is already used…" and "reports a broken business rule before an id that is already used". Closed.
- **M2 (reads take no acting member)**: deferred by D-24 (delegate), reads unchanged, as the plan says. Handled as the decision says. Residual risk noted as m1.
- Minors: `pair-state.ts` comment added (D-12). I checked its claim (a pending request is always the latest of its pair): it holds, since R9/R10 reject any newer request while one is pending. Vitest 4.x pin untouched (human decision), mutation threshold unset (human decision).

## Findings

### Blocking
None.

### Major
- **[M1] The decline block's direction is decided by the code, not by a document** — `src/connections/domain/send-rules.ts:27-29` · angle: compliance / bugs
  After A->B is declined, `previouslyDeclined` matches "same sender" only, so B->A is accepted (and then also becomes reachable: B->A pending, A->B then yields `reverse-pending` rather than `previously-declined`; the guard precedence in `GUARDS` is likewise unsettled). The brief and stories.md (open point 3) say this is open and NOT decided; the developer and plan both flag it. A consumer can see it, no decision, document or answered question settles it, so per the rule it is a `major`. Not a defect in the delivery (the plan forbade choosing), but it must not stay silent. Recommendation: the next planner asks the Product Owner (allowed / blocks the pair / defer), then adds a test that kills the `send-rules.ts:29` survivor, and fixes guard precedence if the pair is blocked.

### Minor
- **[m1] Reads unrestricted (D-24) vs Sensitive-zone rationale** — `index.ts` (`getPairState`, `listPendingRequests`) · angle: security
  D-24, a delegate decision, leaves any caller able to read any pair state or pending list; `invariants.md` Sensitive zones describes `index.ts` as the promise "readable by connections only". The decision flags the privacy risk and defers to the sign-in layer, so it is settled (hence not major; I hesitated and kept the lower level). Recommendation: the human revisits D-24 when sign-in exists.
- **[m2] A store write on a missing id is silent** — `infrastructure/in-memory-store.ts` `replaceRequest` (`if (index !== -1)`) and `saveAccepted` · angle: bugs
  If a request is erased between `findRequest` and `replaceRequest`/`saveAccepted`, decline/withdraw report success for nothing stored and accept would still push a connection for an erased member (a trace "nothing remains" forbids). Only reachable under concurrency, which is open point 2, undecided and unplanned; a durable store will need a conflict rule. Recommendation: decide open point 2 before a real store; until then no change.
- **[m3] Human decisions still pending** — mutation threshold (INV-010) and the Vitest 4.x pin: unchanged, correctly left to a person.

## Checks not performed

No lint/format tool exists in the project beyond `tsc` and the harness shape checks. `tools/check-glossary.sh` and the repo validator are outside this project folder (not run). No behavior of the real storage product can be reviewed: only the in-memory adapter exists.

## Positive notes

- The plan's decisions (D-24 to D-32) are traced one to one in code and tests; every new rejection reason (`not-sender`, `previously-declined`, `request-id-taken`) is exercised and distinct.
- `change()` factors accept/decline/withdraw (authorization before state, D-13) within the INV-005..008 limits; the decline block is one named guard.
- The developer's note is honest about the survivor and open point 3, and did not paper over either.
