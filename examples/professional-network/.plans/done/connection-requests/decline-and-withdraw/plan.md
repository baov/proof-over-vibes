---
role: planner
status: done
reasons:
  - "Round 1 answered by delegate: D-24 to D-31. Nothing consumer-visible remains open for this story."
---

# Connection requests, story 2: decline a request, or withdraw one I sent

Announcement: I apply the `plan-driven-dev` workflow (context, goal, plan) and stop when the plan is written. Questions Q1 to Q3 and the two held points are answered (D-24 to D-31); the plan is final. Open points 1 to 3 of `../stories.md` stay open and are not planned.

## 1. Metadata
- **Type**: feature
- **Date**: 2026-10-18
- **Status**: in-progress 

## 2. Goal

The recipient declines a pending request (the two are not connected, and the same sender can no longer ask the same recipient); the sender withdraws a pending request (and may later send a new one). A non-recipient cannot decline, a non-sender cannot withdraw, and neither can act on a request that is not pending; the authorization reason comes first (D-13). The state of a pair reports declined and withdrawn. When the module is told to erase a member, nothing about them remains, which lifts any decline block that involved them. Every new rejection has its own identifiable reason.

## 3. Context

- **Built on story 1** (merged): module `src/connections` (domain, application, infrastructure, public entry point `index.ts`); `acceptRequest`, `sendRequest`, `getPairState`, `listPendingRequests`; rejections are returned `{ ok: false, reason }` (D-21); request = `{ id, sender, recipient, state }` (D-23); reasons `self-request`, `duplicate-pending`, `reverse-pending`, `already-connected`, `not-recipient`, `not-pending`, `request-not-found` (D-22); the store port (`ports.ts`) has `saveRequest` (insert or replace), `findRequest`, `requestsBetween` (oldest first), `saveAccepted`, `findConnection`, `pendingFor`.
- **Decisions to respect** (architect, not reopened): ADR-0001; cross-request rules are a pure domain function; rejections are values; the erasure operation is one public operation of the module, by hard deletion through the repository port, tested at that operation ("when the module is told to erase that member"); declined requests kept with no expiry, no clock (D-14).
- **Decision log** that settles this story: D-7 (withdraw, decline block), D-8 (not pending: distinct reason), D-11, D-12 (which request is reported), D-13 (authorization before not-pending), D-14 (no expiry, erased with the account), D-16 (unknown request id), D-17 (state answer = the two facts), D-19, D-21 to D-23.
- **Invariants**: INV-001 to INV-004 (layers; erasure touches `application/ports.ts`, `infrastructure`, `index.ts` only), INV-005 to INV-008 (function size, complexity, nesting, parameters: keep one named guard per send rule), INV-009 (test-case bridge, section 5 step 9), INV-010 (mutation on `domain` and `application`, no threshold set; recording one stays a human decision). Run `npm test`, `npm run typecheck`, `npm run harness` at every green.
- **Sensitive zones touched** (human review before merge): the store port, `infrastructure/in-memory-store.ts`, `index.ts` (erasure; the reads are unchanged, D-24).
- **Earlier lessons**: `.plans/FEEDBACK.md` does not exist.
- **Left open and NOT decided** (stories open points): member id validity (D-15, no check, nothing tested); concurrency (decline against withdraw, two sends: nothing invented); a decliner sending a request back (R14 binds the original direction in the code only because nothing else is written; no test, no claim).

### Carried over from story 1 (review 1, GO with open majors)

| Item | Plan |
|---|---|
| M1: an existing request id silently replaces the stored request | **Planned (D-25)**: send is rejected with `request-id-taken`, nothing stored, the existing request unchanged. |
| M2: any caller can read any pair state or pending list | **Deferred by decision (D-24)**: the module restricts no read; access control belongs to the sign-in layer. Reads unchanged, nothing built. Privacy risk flagged in D-24 for a person to revisit once sign-in exists. |
| Minor: `pair-state.ts` uses the last request of the pair | **Planned** (step 6): applies D-12, commented. |
| Minor: survivor `send-rules.ts:21` (`r.state === "pending"` replaced by `true`) | **Planned**: killed by the withdrawn cases W3 and W4 (a withdrawn request must block neither direction). |
| Minor: Vitest 4.x pin (commit 8a0ce23) | **Not touched**: a human decision, outside this story. Reported. |

## 4. Expected behaviors

Test boundary of every behavior: the public operations of `connections` through `src/connections/index.ts`, in-memory adapter, deterministic ids (`req-1`, `req-2`, ...). New operations: **decline** (request id, acting member), **withdraw** (request id, acting member), **erase member** (member). Changed: **send** (declined block), **state** (declined, withdrawn, several requests).
Reasons are fixed by D-27 to D-31 (section "Public interface").

### Decline
- **D1 (R4, crit. 1)**: given A->B pending, when B declines, then the request is returned with state declined; state(A,B) and state(B,A) report not connected, request state declined; B's pending list no longer holds it.
- **D2 (R2, crit. 2)**: given A->B pending, when C declines, or when A (the sender) declines, then it is rejected with the authorization reason and the request is still pending.
- **D3 (R14, crit. 6)**: given A->B declined, when A sends to B, then it is rejected with the declined-block reason, nothing is stored, and the state is still declined.
- **D4 (R14, crit. 6)**: the block is for that pair only: after A->B declined, A can send to C, and C can send to B.
- **D5 (R14, D-14, crit. 10)**: the block has no expiry and survives other activity: after A->B declined, other requests between other members do not lift it.
- **D6 (crit. 10, architect)**: given A->B declined, when the module is told to erase A (or B), then A sending to B (or B... see E2) is no longer rejected for the decline: a new request is accepted and pending, and no trace of the old pair remains (state none before the new send).
- **Not planned**: a decline of B->A sent back by the decliner (open point 3).

### Withdraw
- **W1 (R12, crit. 3)**: given A->B pending, when A withdraws, then the request is returned with state withdrawn; state(A,B) reports not connected, request state withdrawn; B's pending list is empty.
- **W2 (R12, crit. 4)**: given A->B pending, when C withdraws, or when B (the recipient) withdraws, then it is rejected with the authorization reason and the request is still pending.
- **W3 (R13, crit. 5)**: given A->B withdrawn, when A sends to B, then a new request is accepted and pending (not rejected as duplicate or declined); state(A,B) reports pending (D-12); B's list holds only the new one.
- **W4 (R10, R13)**: given A->B withdrawn, when B sends to A, then it is accepted: a withdrawn request is not pending, so it blocks neither direction.
- **W5**: withdraw, resend, withdraw again, resend: each time accepted; the pending list holds at most the live one, ids all different.

### Not pending, unknown, precedence
- **N1 (R15, D-8, crit. 7)**: given a request in each non-pending state (accepted, declined, withdrawn), when the right party tries to decline it and when the right party tries to withdraw it, then each of the six is rejected with the not-pending reason and the state is unchanged (state(A,B) the same before and after). Accept on declined and withdrawn too (two more cases), same reason.
- **N2 (R15, D-8)**: twice: B declines, B declines again: not-pending, state still declined. A withdraws, A withdraws again: not-pending, state still withdrawn.
- **N3 (D-13, crit. 9)**: given a non-pending request, when a non-recipient declines it, or a non-sender withdraws it, then the reason is the authorization one, not the not-pending one (for accepted, declined and withdrawn requests).
- **N4 (D-31)**: decline or withdraw on an unknown id is rejected with the not-found reason, whoever the acting member is, and changes nothing.
- **N5 (R7, crit. 11)**: the reasons of the new rejection scenarios (declined block, non-sender withdraw, plus the existing ones) are pairwise distinct per rule.

### State query with several requests (crit. 8)
- **S1 (R5)**: after a decline: not connected, declined, from both members' side. After a withdrawal: not connected, withdrawn.
- **S2 (D-12, R13, crit. 8a)**: the state is the live request if there is one, otherwise the most recent: withdrawn then resent = pending; withdrawn, resent, withdrawn again = withdrawn; withdrawn then resent then accepted = accepted, connected.
- **S3 (D-12)**: pending and declined cannot be told apart by "first" vs "last" in one request: the case "A->B withdrawn, then A->B declined" reports declined (most recent), not withdrawn.

### Erase a member (crit. 10)
- **E1 (architect)**: given A->B pending, C->A pending, A and B connected through another request, when A is erased, then no request of A as sender or recipient remains in anyone's list, state(A,B), state(A,C) report none and not connected, and B and C are not affected otherwise (B's other relations remain).
- **E2 (crit. 10)**: erasing the recipient B of a declined request A->B lifts the block exactly as erasing the sender does; A can send to B again (a member B who exists again, as the module holds ids only).
- **E3 (crit. 10)**: erasing a third member C does not lift the block of A->B.
- **E4**: erasing a connected member ends the connection: the other member's state with them is none, and they can send a request again.
- **E5 (D-26)**: erase always returns `{ ok: true }`; erasing twice, or a member the module never saw, succeeds and changes nothing.
- **I1 (D-25, R7)**: given the id generator returns an id already used, when a member sends, then it is rejected with `request-id-taken`, nothing is stored, the existing request is unchanged (same fields, same list, same state).

## 5. Steps

Order is strict; each step ends green (`npm test`, `npm run typecheck`, `npm run harness`). Test-first inside each step: write the failing test at the stated boundary, then the code.

- [ ] Step 1 — Request states and store port split. Add `declined` and `withdrawn` to `RequestState`; split `saveRequest` into `addRequest` (refuses an existing id, D-25) and `replaceRequest` (state change of an existing one); update accept and send accordingly. Tests: the existing suite stays green; I1 gets its own test (M1), with a test id generator that repeats an id.
- [ ] Step 2 — Decline (D1, D2, N4 for decline): test `tests/connections/decline-request.test.ts`; `decline` transition in `domain/connection-request.ts` (authorization before state, D-13); `application/decline-request.ts`; public operation in `index.ts`.
- [ ] Step 3 — Withdraw (W1, W2, N4 for withdraw): test `tests/connections/withdraw-request.test.ts`; `withdraw` transition, `application/withdraw-request.ts`, public operation. Factor the shared "who may act, then is it pending" in the domain only if it stays under INV-005 to INV-008.
- [ ] Step 4 — Not pending and precedence (N1, N2, N3): extend the three test files (accept on declined and withdrawn too); no new code expected, otherwise fix the transitions.
- [ ] Step 5 — Resending (W3, W4, W5): tests in `send-request.test.ts`. Kills the line 21 survivor of story 1; fix `send-rules.ts` only if a test fails.
- [ ] Step 6 — Decline block (D3, D4, D5): a named guard `previouslyDeclined` in `domain/send-rules.ts` (same sender, same recipient, state declined); inserted in the guard list. Tests in `send-request.test.ts`.
- [ ] Step 7 — State of a pair (S1, S2, S3): tests in `pair-state.test.ts`; `domain/pair-state.ts` reports the most recent request of the pair, with a comment: a pending request is always the latest of its pair (R9, R10 reject any newer one), so "the pending one if any, otherwise the most recent" (D-12) is this single rule.
- [ ] Step 8 — Erase a member (E1 to E5, D6): test `tests/connections/erase-member.test.ts`; store port method `eraseMember(member)` (requests where the member is sender or recipient, connections involving them); `application/erase-member.ts`; public operation in `index.ts`. Returns `{ ok: true }` always (D-26).
- [ ] Step 9 — Reads: nothing to build (D-24); the signatures stay as built. Only check they still compile and pass.
- [ ] Step 10 — Distinct reasons (N5): extend `rejection-reasons.test.ts` with the new scenarios.
- [ ] Step 11 — Test-case files (INV-009), one file per case under `docs/business/test-cases/connections/`, same front-matter as story 1 (`feature: connection-requests`, `type: functional`, `priority: high`, `source`, `automated_test: <path>::<exact it() name>`, `status: covered`; written `pending` before their test exists, none left pending at the end).

  | Case | Source | Test file |
  |---|---|---|
  | The recipient declines a pending request; not connected, state declined | PRD R4 | decline-request.test.ts |
  | A non-recipient or the sender cannot decline, request stays pending | PRD R2 | decline-request.test.ts |
  | After a decline, a new request from the same sender is rejected | PRD R14, D-7 | send-request.test.ts |
  | The decline block is for the pair only | PRD R14 | send-request.test.ts |
  | The decline block has no expiry and survives other activity | D-14 | send-request.test.ts |
  | Erasing either member of a declined pair lifts the block | PRD R14, D-14, architect | erase-member.test.ts |
  | Erasing a third member does not lift the block | D-14 | erase-member.test.ts |
  | Erasing a member leaves no trace of them (requests, connection, lists) | architect, D-14 | erase-member.test.ts |
  | Erasing a connected member ends the connection | architect | erase-member.test.ts |
  | Erasing twice, or an unknown member, succeeds | D-26 | erase-member.test.ts |
  | The sender withdraws a pending request; state withdrawn | PRD R12 | withdraw-request.test.ts |
  | A non-sender or the recipient cannot withdraw, request stays pending | PRD R12 | withdraw-request.test.ts |
  | After a withdrawal, the sender can send again | PRD R13 | send-request.test.ts |
  | A withdrawn request blocks neither direction | PRD R10, R13 | send-request.test.ts |
  | Decline, withdraw and accept on a non-pending request are rejected, state unchanged | PRD R15, D-8 | decline-request.test.ts, withdraw-request.test.ts, accept-request.test.ts |
  | Acting twice (decline twice, withdraw twice) is rejected as not pending | PRD R15 | decline-request.test.ts, withdraw-request.test.ts |
  | Non-party on a non-pending request gets the authorization reason | D-13 | decline-request.test.ts, withdraw-request.test.ts |
  | Decline or withdraw on an unknown request is rejected, whoever acts | D-16 | decline-request.test.ts, withdraw-request.test.ts |
  | State reports declined and withdrawn | PRD R5 | pair-state.test.ts |
  | With several requests the state is the live one, else the most recent | D-12 | pair-state.test.ts |
  | Each new rejection has a distinct reason | PRD R7 | rejection-reasons.test.ts |
  | An id already in use is rejected, nothing overwritten | D-25, PRD R7 | send-request.test.ts |
  
- [ ] Step 12 — Closing gauntlet: `npm test`, `npm run typecheck`, `npm run harness`, `npm run harness:selftest`, then `npm run mutation` on the critical scope. Read the survivors; add a behavior test per unprotected behavior or exclude one with a justification in `stryker.config.mjs`. Do not set the threshold (human, INV-010). Fill the story metrics as for story 1.

## 6. Risks & edge cases

D = decided by a document, T = technical (not observable).

| Operation | Twice | Nothing | Invalid | Edge | Order |
|---|---|---|---|---|---|
| decline | D: R15 not-pending, state unchanged (N2) | D-15 (undefined, not tested) | non-recipient = D R2 (D2); unknown id = D-31 (N4); empty or unknown member = D-15 | decline of accepted, withdrawn = D R15 (N1) | authorization before not-pending: D-13 (N3); unknown id before both: D-31 |
| withdraw | D: R15 (N2) | D-15 | non-sender incl. the recipient = D R12 (W2); unknown id = D-31 | withdraw then resend then withdraw: D R13 (W5) | as decline (N3) |
| send (changed) | D: R9 while pending; after withdraw allowed (W3); after decline rejected (D3) | D-15 | self = D R8 | pair-only block (D4); other direction after withdrawal (W4); after decline, reverse direction = open point 3, undecided | which reason when two apply: only reachable via open point 3 (decline block cannot coexist with pending or connected for the same direction); not observable, no test |
| state (changed) | T: read only | D-15 | D-24: no restriction, not tested | several requests = D-12 (S2, S3); same member twice = D-19 | (A,B) equals (B,A): D R5 |
| pending list (changed) | T | empty = D R6 | D-24 | withdrawn and declined are not listed (D1, W1) | oldest first, D-18 |
| erase member | D: D-26 always ok (E5) | D-15 | unknown member = D-26 (E5) | erasing a third member leaves the block (E3); both members of a pair, one after the other: second is a no-op, D-26 | erase then send, or send then erase, give the same final state (T) |
| send, id collision | | | existing id = D-25 (I1) | | the id is drawn only once the send rules allow it, so a business rejection comes first (nothing is drawn) |

- Unknown id for decline and withdraw: D-31, checked before authorization and state.
- Mutation: assert exact reasons and unchanged state after each rejection; the old survivor at `send-rules.ts:21` is killed by W3 and W4 together (W3 for the same-direction guard, W4 for the reverse guard).
- Concurrency (decline against withdraw, accept against withdraw) is open point 2: not planned, the store is not given a conflict rule.
- Time: no clock (D-14).

## 7. Out of scope

- The three open points of `../stories.md`: member id validity, concurrency, a decliner sending back.
- What triggers the erasure (account deletion, data-rights module), cross-module orchestration, the privacy-notice wording.
- Listing or removing connections, notifications, blocking, UI, sign-in, storage product, new dependency.
- Setting the mutation threshold and the Vitest pin (human decisions).

## 8. Deviations

(empty)

## 9. Self-review

(empty)

## 10. Follow-up actions

(empty)

---

## Public interface (behavior is fixed by section 4 and D-24 to D-31)

- `declineRequest(requestId, actingMember)` and `withdrawRequest(requestId, actingMember)`: success returns the request with its new state (D-21, D-23); rejections returned.
- `eraseMember(member)`: always `{ ok: true }` (D-26).
- Reasons: reused `not-recipient` (decline, D-27), `not-pending` (one for accepted, declined, withdrawn, D-30), `request-not-found` (D-31); new: `not-sender` (withdraw by anyone but the sender, recipient included, D-28), `previously-declined` (D-29), `request-id-taken` (send, D-25).
- `RequestState` becomes `pending | accepted | declined | withdrawn`; `PairState.requestState` adds the same two values (D-17: still two facts only).
- Reads (`getPairState`, `listPendingRequests`): unchanged (D-24).

## Technical choices (for the reviewer to challenge)

Structure only; none is visible to a caller.
- Store port: `addRequest` refuses an existing id and `replaceRequest` updates one, instead of one insert-or-replace; accept keeps its single atomic `saveAccepted`.
- `eraseMember` is one store method (hard delete of requests and connections involving the member); no domain concept.
- The decline block is one more named guard in `send-rules.ts`, with the existing guards untouched.
- `pairState` takes the last request of `requestsBetween` (creation order); the pending-first branch of D-12 is not written because it cannot be observed (a pending request is always the latest of its pair).
- Decline and withdraw share one domain helper (actor check, then state check) only if the functions stay within INV-005 to INV-008; otherwise two small transitions.
- One test file per use case, as in story 1; `support.ts` unchanged except for helpers if needed.
