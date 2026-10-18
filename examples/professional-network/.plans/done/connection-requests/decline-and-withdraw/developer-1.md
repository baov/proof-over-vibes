---
role: developer
status: done
reasons:
  - "Plan implemented; all acceptance criteria covered by behavior tests. One mutation survivor remains and it is tied to open point 3 (a decliner sending back): see 'Behaviors added' and 'Mutation'."
---

# Developer, iteration 1: story 2 (decline-and-withdraw)

Skills applied: `plan-driven-dev` (implementation steps) and `behavior-driven-testing`. The plan was followed as written; its checkboxes were not ticked (the plan is not mine to edit). No deviation.

## Commits (on top of 9f28130)

1. `3b21212` Reject a send whose generated request id is already used (step 1: states `declined`/`withdrawn`, store port split `addRequest`/`replaceRequest`, `request-id-taken`, I1)
2. `f9c60bb` Decline and withdraw a connection request (steps 2, 3, 4)
3. `3e6cbbb` Block a sender from asking again after a decline; allow resending after a withdrawal (steps 5, 6)
4. `f6cf3c9` State of a pair: declined, withdrawn, and the most recent of several requests (step 7)
5. `0f72327` Erase a member: hard-delete their requests and connections (step 8)
6. `1a3147a` Check that the new rejection reasons are distinct (step 10)

Step 9 (reads): nothing built, signatures unchanged (D-24). Step 11: 28 new test-case files under `docs/business/test-cases/connections/` (50 in total), each `covered` with its exact `it()` name, none pending.

## Behaviors added

All consumer-visible behavior is stated by the plan and D-24 to D-32: `declineRequest`, `withdrawRequest`, `eraseMember` (always `{ ok: true }`), reasons `not-sender`, `previously-declined`, `request-id-taken`, request states `declined`/`withdrawn`. Exported types `DeclineRejection` and `WithdrawRejection` follow from them. Beyond that:

- **Decline block direction (open point 3, not decided)**: the `previouslyDeclined` guard matches "same sender, same recipient" as the plan prescribes. So after A->B is declined, B sending to A is accepted by the code. No test and no claim, as the plan says. A consumer can see it and no document decides it: the orchestrator may relay the question to `product-owner` (should a decline also block the decliner's own request back, or not). This is the cause of the one mutation survivor.
- Internal only, not observable: `previously-declined` is the last guard; `request-id-taken` is checked only after the business rules (D-32).

## Commands and results

- Red then green at each step (new tests failed on missing operation or missing behavior, then passed). Some tests of steps 4, 5 and 7 passed immediately because the code already behaved that way (accept/reverse-pending guards, `.at(-1)`); they are kept as behavior protection.
- `npm test`: 8 files, 51 tests passed.
- `npm run typecheck`: clean.
- `npm run harness`: check_layers 0, check_shape 0, check_test_coverage 50 test-cases, 50 covered_ok, 0 broken, 0 pending, 0 orphan.
- `npm run harness:selftest`: 5 pass, 0 fail.
- `npm run mutation` (critical scope, 14 files): **99.3% (138 killed / 139)**, threshold none (baseline to record: a human decision, file not written).

## Mutation

- The story-1 survivor (`send-rules.ts` `r.state === "pending"` replaced by `true`) is killed (withdrawn cases W3/W4).
- One survivor: `src/connections/domain/send-rules.ts:29`, ConditionalExpression, `r.sender === c.sender` replaced by `true` in `previouslyDeclined`. It would only be killed by a test saying a decliner may (or may not) send back: that is open point 3, so I wrote no test for it and did not exclude it in `stryker.config.mjs`. Once the point is decided, the test kills it (or the condition changes).

## Carried over from story 1

- M1: done (`request-id-taken`, D-25). M2: deferred by D-24, reads unchanged. Pair state: `pair-state.ts` comment added (D-12). Vitest 4.x pin: untouched, still awaits a human.

## Points for the reviewer

- Sensitive zones touched: store port (`ports.ts`), `in-memory-store.ts` (`eraseMember` via a small `keepOnly` helper, `addRequest` refusing a taken id), `index.ts`.
- `change()` in `domain/connection-request.ts` is the shared helper (actor check, then state) for accept, decline, withdraw; within INV-005 to INV-008.
- Untouched as requested: docs/product, decisions.md, tools/harness, stryker.config.mjs, the plan. Nothing pushed; `.plans/in-progress` and `.reviews` not added.
