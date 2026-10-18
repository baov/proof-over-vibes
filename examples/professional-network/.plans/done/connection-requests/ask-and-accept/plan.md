---
role: planner
status: done
reasons:
  - "Round 1 answered by delegate: D-15 (member id validity left undefined, nothing tested), D-16 to D-19. Nothing consumer-visible remains open for this story."
---

# Connection requests, story 1: ask a colleague to connect, and be connected once they accept

Announcement: I apply the `plan-driven-dev` workflow (context, goal, plan) and stop when the plan is written. Questions Q1 to Q5 are answered (D-15 to D-19); the plan is final.

## 1. Metadata
- **Type**: feature
- **Date**: 2026-10-18
- **Status**: in-progress

## 2. Goal

A member sends a connection request to another member; the recipient accepts it, and the two are then connected, each to the other. For any two members one can tell whether they are connected and the state of their request, and a recipient can list the requests pending for them. Sending is rejected for oneself, a duplicate pending request, a pending reverse request and members already connected; accepting is rejected for a non-recipient and for a request that is not pending. Every rejection has its own identifiable reason. Declining, withdrawing and erasure are story 2. (Validation of this restatement is delegated, see the brief.)

## 3. Context

- **Project**: empty `src/` and `tests/`. TypeScript (NodeNext, strict, `noUncheckedIndexedAccess`), Node 22, Vitest (`include: tests/**/*.test.ts, src/**/*.test.ts`), npm. No dependency to add.
- **Decisions to respect** (architect, not reopened): ADR-0001, modular monolith, one module `src/connections` with `domain`, `application`, `infrastructure`. Request = aggregate root (state machine); connection = small concept, a pair of members with no order; members are only a member id value object. Cross-request rules (R9, R10, R11) are a pure domain function over the relevant requests and connection; the application layer loads them through a port. Rejections are returned values with a reason code, never thrown. Repository port in `application` plus an in-memory adapter; id generator port; no storage product. Tests go through public use cases with the in-memory adapter. The vocabulary of the PRD is the language of the code (member, connection request, pending, accepted, connected; no friend, invite, follow, reject).
- **Decision log** D-1 to D-14: D-6 (rules 8 to 11 reject), D-8 (not-pending rejection), D-11 (state "none"), D-12 (pending if any, else most recent), D-13 (authorization reason before not-pending), D-14 (declined requests kept without expiry, so no clock in this story).
- **Invariants that apply** (docs/technical/invariants.md): INV-001 (domain imports only its own domain folder: no `node:crypto`, no package), INV-002 (application imports domain and application only), INV-003 (infrastructure imports inward), INV-004 (no deep import of another module; none here), INV-005 to INV-008 (function at most 40 lines, complexity 10, nesting 4, 5 parameters: the send rules must be split into named guards, not one long function), INV-009 (test-case bridge, below), INV-010 (mutation on `domain` and `application` of `connections`; no threshold yet). All are `warn`, except a broken test-case reference (error). Run `npm run harness` and `npm run typecheck` on every move to green.
- **Sensitive zones touched** (human review before merge): the repository port in `src/connections/application`, `src/connections/infrastructure/**`, and the public entry point `src/connections/index.ts`.
- **Bridge format** (read from `tools/harness/check_test_coverage.mjs`): one `.md` per case under `docs/business/test-cases/` (any depth), starting with a YAML front-matter `---` block; keys read: `status` (`covered`, `pending` or `manual`, otherwise malformed = error), `automated_test` (`<path>::<test name>`; the path must exist, the name must appear as text in that file; empty or `pending` status = a warning), `source` (PRD requirement or D-id; without it the case is only counted). The message also names `feature`, `type`, `priority`: write them. Every `*.test.ts` file must be referenced by at least one case, otherwise a warning (orphan).
- **Earlier lessons**: `.plans/FEEDBACK.md` does not exist. Nothing to apply.
- **Left open and NOT decided** (PRD): member id validity (D-15: left undefined, not tested), concurrency (no behavior invented: the repository port is written so that a store can refuse a conflicting write, nothing more), a decliner sending a request back (no case in this story; the reverse-direction rule R10 only concerns a pending request).

## 4. Expected behaviors

Test boundary of every behavior unless stated: the public use cases of the `connections` module, called through `src/connections/index.ts`, with the in-memory adapter and a deterministic id generator. Operations (names in "Public interface"): **send** (sender, recipient), **accept** (request id, acting member), **state** (member, member), **pending list** (recipient).

The list "twice / nothing / invalid / edge / order" for each operation is in the table of section 6; every cell is decided by a document.

### Send
- **B1 (R1)**: given two distinct members with no request, when A sends to B, then a request exists in state pending with A as sender and B as recipient. Test boundary: send, then pending list of B.
- **B2 (R8)**: given a member, when they send to themselves, then it is rejected with the self-request reason and nothing is stored (B's pending list and state unchanged).
- **B3 (R9)**: given A->B pending, when A sends to B again, then it is rejected with the duplicate-pending reason and the pending list still holds one request.
- **B4 (R10)**: given A->B pending, when B sends to A, then it is rejected with the reverse-pending reason, A->B is still pending and the two are not connected (no automatic accept).
- **B5 (R11, both directions)**: given A and B connected (A->B accepted), when A sends to B, then it is rejected with the already-connected reason; and when B sends to A, same reason (not the reverse-pending reason, since nothing is pending).
- **B6 (R7)**: given the five rejection scenarios (B2, B3, B4, B5, plus the accept rejections B9, B10, B20), when their reasons are collected, then they are pairwise distinct.
- **B7 (R1, multiple recipients)**: given A->B pending, when A sends to C, then it is accepted (the duplicate rule is per pair).

### Accept
- **B8 (R3)**: given A->B pending, when B accepts it, then the request is accepted and state(A,B) and state(B,A) report connected, with request state accepted; the pending list of B is empty.
- **B9 (R2)**: given A->B pending, when a third member C accepts it, then it is rejected with the authorization reason and the request is still pending. The sender A accepting their own request is rejected the same way (A is not the recipient).
- **B10 (R15)**: given A->B accepted, when B accepts again, then it is rejected with the not-pending reason, and the state is unchanged (connected, accepted). Declined and withdrawn belong to story 2.
- **B11 (R2, R15, D-13)**: given A->B accepted, when C (not the recipient) accepts, then the reason is the authorization one, not the not-pending one.
- **B12 (R3 after R11)**: given A->B accepted, state(A,B) is the same when asked as state(B,A) (symmetry: connected is mutual).

### State
- **B13 (R5, D-11)**: given two members who never exchanged a request, when their state is asked, then it is connected = no and request state "none" (an explicit value, not an absence); same when asked in the other order (D-17: the answer holds these two facts only).
- **B13b (D-19)**: given a member, when the state of that member with themselves is asked, then it is not connected, request state none; the query does not reject.
- **B14 (R5)**: given A->B pending, then state(A,B) and state(B,A) report not connected, request state pending.
- **B15 (R5)**: given A->B accepted, then both report connected, request state accepted.
- **B16 (R5)**: given a pair with one request, the state reported is that request's. The selection rule "pending if any, otherwise the most recent" (D-12) moves to story 2 (stories.md), where a pair can hold several requests; nothing of it is built here.

### Pending list
- **B17 (R6, D-18)**: given A->B, then C->B pending, and D->E pending, when B asks for the requests pending for them, then they get exactly the two addressed to B, oldest first (A->B, then C->B); not D->E, not requests B sent.
- **B18 (R6)**: given B with no request, then the list is empty (an empty list, not an error). After B accepts one of two, only the other remains.
- **B19 (R6)**: given A->B pending, the sender A's own pending list does not contain it (it is addressed to B).

### Answered points
- **B20 (D-16)**: given no request has this id, when a member accepts it, then it is rejected with the not-found reason and nothing changes.
- **B21 (D-16, D-13)**: given a request id that does not exist, the not-found reason holds whoever the acting member is.
- Member id validity (D-15): left undefined on purpose, no id check and no test; reserved for a later edge-case request.
- **Not planned, not decided**: concurrency (two simultaneous sends, accept against a withdrawal); a decliner sending a request back.

## 5. Steps

Order is strict; each step ends green (`npm test`, `npm run typecheck`, `npm run harness`). Test-first inside each step: write the failing test at the stated boundary, then the code.

- [ ] Step 1 — Skeleton. Create `src/connections/{domain,application,infrastructure}/`, the public entry point `src/connections/index.ts` (exports the factory that wires the use cases to an in-memory store, plus the public types: member id, request id, reasons, states), and `tests/connections/support.ts` (builder of a fresh module with a deterministic id generator, helper `request(a,b)`). No behavior yet.
- [ ] Step 2 — Send, nominal (B1): test `tests/connections/send-request.test.ts`; create `domain/member-id.ts` (value object), `domain/connection-request.ts` (state pending, sender, recipient, id), `application/ports.ts` (request store port, id generator port; no clock), `application/send-request.ts`, `infrastructure/in-memory-store.ts`.
- [ ] Step 3 — Pending list (B17, B18, B19): test `tests/connections/pending-requests.test.ts`; add `application/pending-requests.ts` and the store query by recipient, returned in creation order (oldest first, D-18).
- [ ] Step 4 — Send rules, one at a time, each red then green (B2, B3, B4, B7), then (B5) once accept exists: create `domain/send-rules.ts`, a pure function `decideSend(sender, recipient, requestsBetween, connection)` returning allowed or one reason; one named guard per rule so INV-005 to INV-008 hold; define the reason codes in `domain/reasons.ts`. Tests in `send-request.test.ts`.
- [ ] Step 5 — Accept, nominal and connection (B8): test `tests/connections/accept-request.test.ts`; create `domain/connection.ts` (unordered pair), the `accept` transition on the request, `application/accept-request.ts`, store methods to save the connection and read it by pair.
- [ ] Step 6 — Accept rejections in the order of D-13 (B20, B21, B9, B11 then B10): authorization check first, then pending check, in `domain/connection-request.ts`. Then finish B5 (already connected, both directions) and B12.
- [ ] Step 7 — State query (B13, B13b, B14, B15, B16): test `tests/connections/pair-state.test.ts`; create `domain/pair-state.ts` (the single request of the pair, or none) and `application/pair-state.ts`. Answer: connected yes/no and request state (D-17); the same member twice gives none, not connected (D-19).
- [ ] Step 8 — Distinct reasons (B6): test in `tests/connections/rejection-reasons.test.ts` collecting the reasons of all rejection scenarios and asserting they are pairwise distinct.
- [ ] Step 9 — Pending list order (B17) and unknown request (B20, B21) are already in steps 3 and 6; nothing is built for member id validity (D-15).
- [ ] Step 10 — Test-case files (INV-009). For each test, one file `docs/business/test-cases/connections/<name>.md`, front-matter then a few lines: given, when, then.
  Format:
  ```
  ---
  feature: connection-requests
  type: functional
  priority: high
  source: PRD R1
  automated_test: tests/connections/send-request.test.ts::<exact it() name>
  status: covered
  ---
  ```
  Written as `status: pending` with no `automated_test` when the case is listed before its test, switched to `covered` once the test exists; at the end of the story no case is pending. List (each names its source; the test file and the exact `it()` name is the Developer's, the name must appear verbatim in the file):
  | Case | Source | Test file |
  |---|---|---|
  | A member sends a request, it is pending | PRD R1 (story 1 criterion 1) | send-request.test.ts |
  | The recipient accepts, the two are connected both ways | PRD R3 | accept-request.test.ts |
  | A non-recipient cannot accept, the request stays pending | PRD R2 | accept-request.test.ts |
  | The sender cannot accept their own request | PRD R2 | accept-request.test.ts |
  | State of a pair: connected and request state, pending then accepted | PRD R5 | pair-state.test.ts |
  | State of a pair with no request is "none" | D-11 | pair-state.test.ts |
  | State of a pair with the same member twice is none, not connected | D-19 | pair-state.test.ts |
  | Accept on an unknown request is rejected with its own reason | D-16 | accept-request.test.ts |
  | Pending requests of a recipient, only theirs, oldest first, empty when none | PRD R6, D-18 | pending-requests.test.ts |
  | Sending to oneself is rejected | PRD R8 | send-request.test.ts |
  | Duplicate pending request is rejected | PRD R9 | send-request.test.ts |
  | Reverse pending request is rejected, no automatic accept | PRD R10, D-6 | send-request.test.ts |
  | Request between connected members rejected, both directions | PRD R11, D-6 | send-request.test.ts |
  | A request to a third member stays allowed | PRD R9 (per pair) | send-request.test.ts |
  | Accept on an accepted request rejected, state unchanged | PRD R15, D-8 | accept-request.test.ts |
  | Non-recipient on a non-pending request gets the authorization reason | D-13 | accept-request.test.ts |
  | Each rejection has a distinct reason | PRD R7 | rejection-reasons.test.ts |
- [ ] Step 11 — Closing gauntlet: `npm test`, `npm run typecheck`, `npm run harness` (all invariants, then the bridge), `npm run harness:selftest`; then `npm run mutation` on the critical scope. Read the surviving mutants; add a behavior test per unprotected behavior, or exclude one with a justification in `stryker.config.mjs`. Do not set the mutation threshold: recording the baseline is a human decision (INV-010).

## 6. Risks & edge cases

Every public operation against "twice, nothing, invalid, edge, order". D = decided by a document, Q = question, T = technical (not observable).

| Operation | Twice | Nothing | Invalid | Edge | Order |
|---|---|---|---|---|---|
| send | D: R9 pending, R11 once accepted (B3, B5) | D-15 (undefined, not tested) | D-15; self = D R8 | per pair, other recipient allowed (B7) | reverse = D R10 (B4); both directions after accept = D R11 (B5) |
| accept | D: R15 (B10) | D-15 | non-recipient = D R2; unknown request id = D-16 (B20, B21); empty/unknown acting id = D-15 | sender accepting own = D R2 (B9) | authorization before not-pending = D D-13 (B11) |
| state | T: read only, repeatable | D-15 | D-15 | same member twice = D-19 (B13b); no request = D D-11 | (A,B) equals (B,A): D R3/R5 mutual (B12) |
| pending list | T: read only, repeatable | none pending = empty list, D R6 reading (B18); D-15 | D-15 | request sent by the member is not in their list (B19) | oldest first, D-18 (B17) |

- Member id validity is deliberately undefined (D-15): any id, empty or unknown, behaves however the code happens to; do not add a check and do not test it.
- Criterion 4b (pending if any, else most recent) moved to story 2 (stories.md); story 1 reports the pair's single request. Store the creation order anyway (the pending list needs it, D-18), so story 2 can rely on it.
- Accept writes two things (the request and the connection): the store port must persist both together (one port method), or a crash leaves an accepted request with no connection. In-memory it is trivial; the port signature must not forbid atomicity.
- Concurrency stays unspecified: two simultaneous sends or accept against another action are not handled and not tested; do not invent a behavior.
- Mutation: tests that only check "a reason is returned" let comparison mutants survive; assert exact reason and unchanged state after each rejection.
- Function size: the send decision has four rules; keep one guard per rule to stay under INV-006 and INV-005.
- Domain purity (INV-001): no `crypto`, no `Date` in `domain`; ids come from the port, order from the store.

## 7. Out of scope

- Decline, withdraw, the decline block (R14), the decline's authorization, erasure of a member's data (story 2).
- Listing or removing connections, notifications, blocking, search, messages on a request.
- UI, sign-in, profiles, feed, any transport (HTTP, CLI) and any storage product; no dependency added.
- A clock port (D-14: no time rule). Concurrency behavior, a decliner sending back (PRD open questions 2 and 3).
- Setting the mutation threshold (human decision), changing a harness script or invariant.

## 8. Deviations

(empty)

## 9. Self-review

(empty)

## 10. Follow-up actions

(empty)

---

## Public interface (named after the PRD vocabulary; the behavior is fixed by the sections above)

- Operations: `sendRequest(sender, recipient)`, `acceptRequest(requestId, actingMember)`, `getPairState(memberA, memberB)`, `listPendingRequests(recipient)`, exposed by one factory in `src/connections/index.ts`.
- Success returns the request; the pending list returns for each request its id, sender, recipient and state (the recipient needs the id to accept). The state query returns connected and request state only (D-17).
- Rejections are returned, not thrown (architect): `{ ok: false, reason }` with reasons `self-request` (R8), `duplicate-pending` (R9), `reverse-pending` (R10), `already-connected` (R11), `not-recipient` (R2), `not-pending` (R15), `request-not-found` (D-16).

## Technical choices (for the reviewer to challenge)

Structure only; none of it is visible to a caller.
- One store port in `application` (find a request by id, save a request, requests between two members, pending for a recipient, save a connection, find a connection by pair), one in-memory adapter; accept saves the request and the connection in a single method so a real store can make it atomic. No erasure method (story 2).
- Cross-request send rules are one pure function `decideSend` in `domain/send-rules.ts`, one named guard per rule (INV-005 to INV-008); the connection is an unordered pair value in `domain/connection.ts`.
- Creation order is the store's insertion sequence; no timestamp, no clock port (D-14).
- Ids come from an id generator port; tests use a deterministic one.
- Tests: one file per use case under `tests/connections/`, one shared support module for the builder.
