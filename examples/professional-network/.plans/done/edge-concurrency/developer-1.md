---
role: developer
status: blocked
reasons:
  - "Deviation from the plan, to be decided: K6 (a read never sees half an operation) cannot be red-first with this store. It passes on the unchanged code, for every offset I tried. The plan said to stop on this. Everything else is implemented, committed and green."
  - "Related gap, same cause: removing the queue from getPairState or listPendingRequests turns no test red. Only INV-011 (structural) guards those two wrappers."
---

# Developer, iteration 1: edge-concurrency

Announcement: I applied `plan-driven-dev` (implementation steps) and `behavior-driven-testing`, following plan.md step by step. No multiple-choice question was answered.

## Question for the orchestrator / planner (reason for `blocked`)

K6 is green without the queue, so the plan's red-first rule is not met for it. Why: `InMemoryStore.saveAccepted` writes the request, then the connection one microtask turn later. `getPairState` samples requests then connection, also one turn apart. Both gaps are one turn, so a read can never land between the two writes. I probed reads launched 0 to 12 turns after the accept, before and after it, on both sides, with the accept itself delayed 0 to 6 turns: only `pending/not connected` and `accepted/connected` ever appear. Nothing in the public API can expose the half state with this store.

Options (planner's call, nothing consumer-visible, so not for the product-owner):
a) Keep K6 as a guard that is green by nature (it protects R4 if the store or the use cases change), and accept that the three wrappers `eraseMember`, `getPairState`, `listPendingRequests` are proven by INV-011 only for the two reads. This is what I did.
b) Change the plan: for example inject a store into `createConnections` for tests (a public API change, so it needs its own decision).

I did not weaken or remove K6, and I added nothing to make it fake-red.

## Commits (on the shared branch, only under `examples/professional-network`)

1. `9bfc0f2` Connections: test oracle for simultaneous operations (both sequential orders): `bothOrders`, `simultaneously` and the `Scenario` type in `tests/connections/support.ts`.
2. `2fab4d7` Connections: serialize every operation through one queue (ADR-0002), with concurrency tests: `src/connections/infrastructure/serial-queue.ts`, the seven wrappers in `src/connections/index.ts`, `tests/connections/concurrency.test.ts` (12 tests).
3. `ecfa4ac` Connections: business test-cases for simultaneous operations: the 12 `concurrency-*.md` files of the plan.

Order note: the red run was done before the queue existed, but the tests and the queue are in one commit (2), so that no commit on the branch has a red suite.

## Red-first evidence (new tests on the unchanged production code, run before and re-run after the final test file)

`npx vitest run tests/connections/concurrency.test.ts`: 8 failed, 4 passed. Each failure is the oracle: the concurrent outcome is neither sequential order.

- mutual sends: both sends `ok` (`req-1` and `req-2`), two pending requests, one for each member (expected one `ok` and one `reverse-pending`).
- mutual send id: both won, the next id is `req-3` instead of `req-2`.
- accept vs withdraw: both `ok`; final state `connected: true` with request `withdrawn`.
- accept vs decline: both `ok`; final `connected: true` with request `declined`.
- identical sends: both `ok` (`req-1`, `req-2`), two pending requests in B's list.
- withdraw vs decline: both `ok`, final `declined`.
- accept twice: both `ok` (instead of one `not-pending`).
- erase: accept started first, then erase, ends with `connected: true` and request state `none` (a connection to an erased member).

Green without the queue, and why:
- K6 read during accept and withdraw: see the question above. It still guards R4; kept.
- K8 different pairs, K9 rejection beside a success, K10 failure isolation: they guard a queue that breaks something, not its absence, as the plan said. K10 was checked in step 5: with `tail = outcome` (no isolation, rejection kept on the tail) it goes red (the send behind the failing one is rejected); restored.
- The erase test fails on its accept-then-erase variant, so its send variants were not reached individually in the unchanged run: I cannot say they are red alone.

Per-method check of step 7 (remove one wrapper at a time, run the concurrency file, restore):
- `sendRequest`: red (3 tests: mutual sends, mutual id, identical sends).
- `acceptRequest`: red (accept twice, erase).
- `declineRequest`: red (accept vs decline, withdraw vs decline).
- `withdrawRequest`: red (accept vs withdraw).
- `eraseMember`: red only after I added to the erase test an erase launched 0 to 8 turns after an accept in flight (the plan's variants alone stayed green: an unqueued erase is just "erase first").
- `getPairState`, `listPendingRequests`: no test red (see the question). Only INV-011 catches these two.

## Final gauntlet

- `npm test`: 10 files, 86 tests pass (74 before plus 12 new). The existing 74 are unchanged.
- `npm run typecheck`: clean.
- `npm run harness`: 0 violation on layers, shape, serialization; INV-011 active and clean; INV-009: 85 test-cases, all covered, 0 orphan.
- `npm run harness:selftest`: 6 pass, 0 fail.
- Root `validate-skills.py` and `check-glossary.sh`: clean.
- `npm run mutation`: 100.0% (161 killed, 161 generated), threshold none. Previous score 100%, same count. The queue is outside the mutation scope (domain and application only, INV-010), so a mutant of the queue is not scored; it is protected by the behavior tests, K10 and the per-method check above. I did not touch `stryker.config.mjs` and wrote no threshold.

## Behaviors added

None of the public contract. `Connections` signatures, results and the store port are unchanged. The queue (`createSerialQueue`, `SerialQueue`) is internal to `infrastructure`, not exported by `index.ts`. Observable consequences already decided: a thrown error reaches its own caller unchanged and the queue goes on (D-38); which of two simultaneous operations wins is unspecified (D-37). Calls made in sequence behave as before; each call now settles after the ones queued before it.

## Deviations from the plan

- K6 not red-first (above).
- The erase test has an extra loop (erase launched after 0 to 8 turns) not in the plan, to make the `eraseMember` wrapper observable. Same test, same test-case, no new behavior.
- The queue is a function (`queue(() => ...)`), not an object with `run`: the plan said "a function `run(operation)`", INV-011 accepts a local alias or call.
- K1 is covered by two tests as the plan's table lists them; K7 is a single test (all its variants) and K6 a single test (accept and withdraw), as the table lists one name each.

## Notes for the reviewer

- Sensitive zones touched: `src/connections/index.ts`, `infrastructure/serial-queue.ts`.
- No sleep or timer in the tests: only microtask turns.
- Open minor items untouched: Vitest 4.x pin, mutation threshold (human), `EraseResult` re-export.
