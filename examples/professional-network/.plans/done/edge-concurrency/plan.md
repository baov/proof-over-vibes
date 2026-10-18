---
role: planner
status: done
reasons:
  - "Round 1 answered by delegate: D-37 (either sequential order, nothing promised on arrival order), D-38 (a thrown error reaches its own caller unchanged, the queue goes on). Nothing consumer-visible remains open."
---

# Connection requests: simultaneous operations

Announcement: I apply the `plan-driven-dev` workflow (context, goal, plan) and stop when the plan is written. Round 1 is answered (D-37, D-38); the plan is final.

## Answers (round 1)

Q1 -> D-37 (a): unspecified, tests accept either order. Q2 -> D-38 (a): same error to its own caller, queue not blocked, no new reason. Questions kept below for the record.

## Questions (round 1, answered)

What I understood:
- The queue makes every pair of simultaneous operations behave as one of the two sequential orders (R1, ADR-0002). R6 says no priority between members or kinds of operation, but a caller does see who got the pending request (mutual sends) or whose answer is `ok`.
- Operations return rejections as values (D-21); a throw happens only when something underneath fails (e.g. the id generator). D-21 leaves thrown errors open.

1. Two operations on the same pair start on the same tick (e.g. `Promise.all([send(A,B), send(B,A)])`). Which one wins?
   a) Unspecified (R6 taken literally): either sequential order is correct. Tests accept either order, and check each outcome is the exact result of one sequential order. The same holds for erase against another operation (erase first or erase last), and for a read against a write (before or after). Recommended: the PRD refuses to specify it, and ADR-0002 says a second instance ends any arrival-order guarantee.
   b) The first call started wins (arrival order, a promise of the module). Tests assert the exact winner: the first of `[send(A,B), send(B,A)]` gets `req-1` pending, the other `reverse-pending`.
   c) Other.
2. An operation throws (a failure underneath, not a business rejection). What do the callers see?
   a) Its own caller gets the same error (the promise rejects with it, unchanged); the operations behind it run normally and get their own answers; the failed one wrote nothing. Recommended: smallest contract, nothing converted, nobody else affected.
   b) Its own caller gets a rejection value instead of a throw (a new reason, changes the result shapes).
   c) Other.

Answer with something like "1a 2a".

## 1. Metadata
- **Type**: feature
- **Date**: 2026-10-18
- **Status**: in-progress

## 2. Goal

When two operations on the same pair of members are submitted at the same moment (neither has answered when the other starts), the answers and the final state are those of the two operations run one after the other, in one of the two orders; no third outcome, no half-finished state observable (PRD requirements 1 to 6). Calls made one after the other behave exactly as before.

## 3. Context

- **Inputs**: PRD `connection-requests-edge-concurrency.md` (R1 to R6 = acceptance criteria), `architect.md`, ADR-0002 (one FIFO queue owned by the module, whole use case as the unit, five writes and two reads, one process only, store port unchanged), ADR-0001, D-1 to D-36.
- **Code**: use cases read, decide, write across awaits (`application/*.ts`); `InMemoryStore.saveAccepted` awaits between the request write and the connection write, so a read can see an accepted request without its connection (R4). `createConnections` in `src/connections/index.ts` wires the seven operations. Tests: `tests/connections/*.test.ts` + `support.ts`; test-cases `docs/business/test-cases/connections/`. Ids are drawn only after the send rules allow it (D-32): a rejected send consumes no id.
- **Invariants**: INV-011 (warn, pending): `index.ts` must import the queue from `./infrastructure/serial-queue`, create it in `createConnections`, and each returned method must use it (a local alias is accepted). INV-001 to INV-004 (the queue is plain TypeScript, imports nothing outside infrastructure; use cases untouched), INV-005 to INV-008 (a method wrapper is one line), INV-009 (a test-case per test), INV-010 (mutation scope is domain and application only; the queue is outside it, so tests cover it by behavior). Run `npm test`, `npm run typecheck`, `npm run harness` at every green.
- **Sensitive zones** (human review before merge): `src/connections/index.ts` and `infrastructure/`.
- **Earlier lessons**: `.plans/FEEDBACK.md` does not exist.
- **Public contract**: `Connections` unchanged (signatures, results). Store port unchanged. No result shape changes.

### Carried over

None major. Minor items from earlier reviews (Vitest 4.x pin, mutation threshold, `EraseResult` not re-exported by `index.ts`) are humans' or out of scope; see section 7.

## 4. Expected behaviors

Test boundary of every behavior: the public operations of `connections` through `createConnections`, in-memory store, ids `req-1`, `req-2`, ... Simultaneous = launched with `Promise.all` (or `Promise.allSettled`) in one tick, before any answer. Tests live in `tests/connections/concurrency.test.ts`.

**Oracle (R1)**, in `support.ts`: `bothOrders(setup, opA, opB)` runs the two operations one after the other on two fresh modules built by the same `setup`, once in each order, and returns the two sequential outcomes (the two answers, matched to their operation, plus the final pair state, pending lists and, where useful, the next id drawn). A concurrent run on a third fresh module must equal one of them. This is the assertion; no winner is asserted (D-37). Each behavior below also asserts its named outcome explicitly, so the oracle cannot hide a wrong sequential result.

- **K1 (R2, mutual sends)**: given nobody has a request, when A sends to B and B sends to A simultaneously, then exactly one is `ok` (a pending request, id `req-1`) and the other is `{ ok: false, reason: "reverse-pending" }`; not connected; the pending request is the only one (state pending from both sides, exactly one pending list entry, for the recipient of the winner only); no automatic accept (D-6); the rejected send consumed no id (the next send gets `req-2`). Which of the two wins: either order accepted (D-37).
- **K2 (R3, accept wins or withdraw wins)**: given A->B pending, when B accepts and A withdraws it simultaneously, then exactly one succeeds. Accept first: B's accept returns the accepted request, connected, state accepted from both sides, A's withdraw is `not-pending`. Withdraw first: not connected, state withdrawn, B's accept is `not-pending`. Never both `ok`, never connected with a withdrawn state (R4). Winner either order accepted (D-37).
- **K3 (R5, accept against decline)**: given A->B pending, when B accepts and B declines simultaneously, then exactly one succeeds, the other is `not-pending`; the final state is accepted and connected, or declined and not connected, and matches the winner's answer. Winner either order accepted (D-37).
- **K4 (R5, identical sends)**: given nobody has a request, when A sends to B twice simultaneously, then exactly one is `ok` (`req-1`) and the other is `duplicate-pending`; B's pending list holds exactly one request; the next send (A to C) gets `req-2`. Three identical sends at once: one `ok`, two `duplicate-pending`.
- **K5 (R1, other pairs of operations, one test each)**: each checked against the oracle and with its named outcome: (a) withdraw and decline of the same request: one succeeds, the other `not-pending`; (b) accept twice by the recipient: one `ok`, the other `not-pending`, one connection (state connected, a later send is `already-connected`).
- **K6 (R4, a read never sees half an operation)**: given A->B pending, when B accepts while the state of the pair is asked repeatedly (reads launched after 0, 1, 2, ... N microtask turns, from both sides), then every answer is `{ connected: false, requestState: "pending" }` or `{ connected: true, requestState: "accepted" }`, never accepted with `connected: false`. Same for the pending list during accept (listed before, absent after) and during withdraw. After the accept settles, the state is accepted and connected.
- **K7 (R1, erase against another operation)**: given A->B pending, when A is erased while B accepts: both orders end in state none for the pair and an empty pending list for B; B's accept is `ok` (accept first, then the erase removes everything) or `request-not-found` (erase first); the erase answers `{ ok: true }` either way. Given nobody has a request, when A is erased while A sends to B: the send is `ok` and the state is none (send first, erased after) or pending (erase first), never a request without an owner or a connection to an erased member. Erase against erase of the same member: both `{ ok: true }`. Order of outcome either order accepted (D-37) (a: either; b: erase listed first runs first).
- **K8 (independence)**: given operations on different pairs (A->B and C->D sends, simultaneous), then both are `ok` and independent: two pending requests with the ids `req-1` and `req-2` in some order. The queue does not reject or merge operations of different pairs.
- **K9 (blank, nothing, invalid)**: a simultaneous operation rejected by the rules (blank id, unknown request id) answers its own rejection (`blank-member-id`, `request-not-found`) exactly as it would alone, and changes nothing for the operation beside it: e.g. `send("", B)` with `send(A, B)` simultaneously: `blank-member-id` and `ok` `req-1`.
- **K10 (D-38, a failing operation does not block the queue)**: given an id generator that throws on its first call, when A sends to B (throws) and C sends to D and B reads are launched simultaneously, then A's call rejects with the generator's error (unchanged), the others answer normally, and A->B was not stored (state none). A call made after the failure also runs normally. Per D-38. The queue also returns, for a normal operation, exactly the value of the use case (same `ok`, same request), proved by every test above.
- **K11 (sequential behavior unchanged)**: the whole existing suite stays green with no change.

## 5. Steps

Order is strict. Each step ends with `npm test`, `npm run typecheck`, `npm run harness` as stated.

- [ ] Step 1 — Support only. In `tests/connections/support.ts` add `bothOrders` (oracle, above) and a `startSimultaneous` helper if needed to launch operations in one tick. No production code. Suite green.
- [ ] Step 2 — Red tests, no queue yet. Create `tests/connections/concurrency.test.ts` with K1 to K9 and K10. Run `npx vitest run tests/connections/concurrency.test.ts` on the unchanged production code and keep the output as the red proof (see Risks, "Red first"). Expected red: K1 (both sends `ok`), K2, K3, K4 (two requests created, no rejection), K5a and K5b, K6 (an `accepted` read with `connected: false`), K7 send variant (see below). Expected green already: K8, K9, K7 accept variant and erase twice (no race in single steps). Every test that is green now is named in the Developer's report with the reason; none may be kept unless it protects a behavior the queue must not break. Write nothing else until the red run exists.
- [ ] Step 3 — The queue: create `src/connections/infrastructure/serial-queue.ts` (a plain promise chain: `createSerialQueue()` returns a function `run(operation)` that starts the operation after every earlier one has settled, resolves or rejects with the operation's own outcome, and is not poisoned by an earlier rejection). No dependency, no import outside infrastructure.
- [ ] Step 4 — Wire it in `src/connections/index.ts`: import from `./infrastructure/serial-queue`, create one queue per `createConnections` call, wrap each of the seven methods in it (one line each). Run the whole suite: K1 to K9 green, the existing suite unchanged. Run `npm run harness`: INV-011 is now active and must be clean (no new warning).
- [ ] Step 5 — Failure isolation (K10): with the queue in, make the test pass. Then check it guards the behavior: temporarily replace the queue with `tail = tail.then(op)` (no isolation), see K10 red, restore.
- [ ] Step 6 — Test-case files (INV-009), one per case below, same front-matter as the existing ones; `status: pending` before the test exists, `covered` at the end, none left pending.
- [ ] Step 7 — Closing gauntlet: `npm test`, `npm run typecheck`, `npm run harness` (INV-011 active, no warning), `npm run harness:selftest`, `npm run mutation` (queue out of scope, expected no change in score; do not set the threshold, human, INV-010). Re-run the red proof: remove the queue wrapper of one method at a time (temporarily) and check that a concurrency test goes red each time (guards the "each method uses it" rule beyond the structural check); restore.

### Test-cases (step 6)

`automated_test` is written `tests/connections/concurrency.test.ts::<exact it() name>`; the table shortens it. Source column is the front-matter `source`.

| Test-case file (`docs/business/test-cases/connections/`) | Source | `it()` name |
|---|---|---|
| `concurrency-mutual-sends-one-pending.md` | PRD R2, D-6 | `creates one pending request and rejects the other as reverse-pending when two members send to each other at once, without connecting them` |
| `concurrency-mutual-send-consumes-one-id.md` | PRD R2, D-32 | `draws a request id only for the send that wins a mutual send` |
| `concurrency-accept-withdraw-one-wins.md` | PRD R3, R4 | `lets exactly one of accept and withdraw succeed on the same request, and the state matches the winner` |
| `concurrency-accept-decline-one-wins.md` | PRD R5 | `lets exactly one of accept and decline succeed on the same request, the other is not-pending` |
| `concurrency-identical-sends-one-request.md` | PRD R5 | `creates one request and rejects the others as duplicate-pending when the same send is made at once` |
| `concurrency-withdraw-decline-one-wins.md` | PRD R1 | `lets exactly one of withdraw and decline succeed on the same request` |
| `concurrency-accept-twice-one-connection.md` | PRD R1 | `connects the pair once when the recipient accepts twice at once` |
| `concurrency-read-never-half-done.md` | PRD R4 | `never shows a request accepted without its connection to a read made during the accept` |
| `concurrency-erase-with-operation.md` | PRD R1, ADR-0002 | `gives the outcome of erase first or erase last when a member is erased during another operation` |
| `concurrency-different-pairs-independent.md` | PRD R1 | `lets simultaneous operations on different pairs all succeed` |
| `concurrency-rejection-beside-success.md` | PRD R1, D-13 | `gives a rejected operation its own reason and leaves the simultaneous valid one untouched` |
| `concurrency-failure-does-not-block.md` | D-38 | `lets the operations behind a failing one run normally and gives its caller the original error` |

## 6. Risks & edge cases

D = decided by a document, Q = depends on a question, T = technical (not observable).

| Operation | Twice | Nothing | Invalid | Edge | Order |
|---|---|---|---|---|---|
| send (simultaneous) | identical: one `ok`, rest `duplicate-pending` (D R5, K4); mutual: one `ok`, other `reverse-pending` (D R2, K1) | n/a (no new parameter) | blank id: its own rejection, neighbor untouched (K9) | three at once (K4); after a decline the same race follows D-34 (current state first) | who wins: unspecified (D-37); rejected send draws no id (D-32) |
| accept / decline / withdraw | accept twice: one `ok` (K5b); withdraw vs decline: one wins (K5a) | n/a | unknown request id: `request-not-found` as alone (K9) | accept vs withdraw: D R3; accept vs decline: D R5 | who wins: unspecified (D-37); answers and final state match the winner (D R4) |
| eraseMember | erase twice or with itself: `{ ok: true }` both (D-26) | n/a | blank: `blank-member-id` as alone (D-36) | erase during accept or send: erase first or last, no third state (ADR-0002, K7) | unspecified (D-37) |
| getPairState / listPendingRequests | n/a (read) | n/a | blank as alone | read during accept or withdraw: before or after, never between (D R4, K6) | before or after the write (D-37) |
| queue (internal, observable through all) | failing op then next: D-38 | n/a | n/a | an operation that never settles would block everyone: not tested, out of scope (no timeout in the module) | FIFO by call order (T, not a promise: D-37) |

Other risks:
- **Red first (the tests must fail without the queue).** The interleaving is deterministic: every store method is `async` and each use case awaits between its read and its write, so two `Promise.all` calls interleave at the same microtask turns, without timers. Proof of red: step 2 runs the new file on the untouched code and records which tests fail and why (K1 both sends `ok`; K2 and K3 two `ok`; K4 two requests; K6 an accepted state with no connection). Step 7 repeats it per method by removing one wrapper. K6 depends on exact microtask turns: the reads are launched after 0 to N turns precisely so that one lands between `replaceRequest` and the connection write; if no read hits it without the queue, that is a deviation to stop on (the test is not proving R4), not a test to weaken. K10, K8, K9 and the erase accept variant pass without the queue by nature: they guard against a queue that breaks something, not against its absence, and K10 is red-checked in step 5.
- **Mutation**: the queue is outside the scope (domain and application only), so a mutant of the queue is not scored. K10, step 7 and the explicit named outcomes of each test are what protect it.
- **Single process**: the guarantee holds for one `createConnections` instance. Two instances over one store do not exist (the store is created inside `createConnections`); ADR-0002 states the limit.
- **Time**: if a test needs a sleep or a timer to reproduce a race, the design is wrong; use microtask turns only.
- **INV-005 to INV-008**: each wrapper is one line.

### Technical choices (for the reviewer to challenge)

- The queue is a closure from `createSerialQueue()` in `infrastructure/serial-queue.ts`, a plain promise chain with the tail kept after settlement (rejection swallowed on the tail, not on the caller's promise).
- Applied in `index.ts` only; use cases and store unchanged. Reads go through it too, per ADR-0002.
- One queue per `createConnections` instance, not a module-level singleton, so two instances in one test file do not serialize each other.
- All the new tests in one new file `concurrency.test.ts` (they cross use cases); oracle in `support.ts`.
- No new test of the queue as a unit: it is covered through the public operations (behavior, not class).

## 7. Out of scope

- Speed and throughput (PRD 4, ADR-0002).
- More than one process or instance, a shared store, conditional writes in the store port (new ADR first, ADR-0002).
- Non-blank unknown ids (D-15).
- A lock per pair, a timeout on a stuck operation, a retry of a failed operation.
- Recording the mutation threshold (INV-010, human), the Vitest 4.x pin, the `EraseResult` re-export.
- Any change of the public contract or the result shapes.

## 8. Deviations

- **K6 cannot be red-first (Developer finding, Planner decision: option a).** With the in-memory store both gaps are one microtask turn, so no read lands between the request write and the connection write; K6 is green without the queue. The plan's "if K6 does not go red, stop" clause is thus resolved here, not by weakening anything. Decision: keep K6 as a guard that is green by nature (it still fails if a future store or use case opens a real gap), mark it so in the test name's comment, and drop K6 and the read wrappers from the step 7 "remove one wrapper, expect red" check. The `getPairState` and `listPendingRequests` wrappers are protected only by INV-011 (structural). Rejected: option b, an injectable store in `createConnections` (public API change, consumer-visible, out of the architect's decision, and the in-memory store is the only store). The write wrappers stay red-checked by K1 to K5 and K7. Nothing consumer-visible changes; the reviewer should read this residual risk.

## 9. Self-review

(empty)

## 10. Follow-up actions

(empty)
