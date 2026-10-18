---
role: planner
status: done
reasons:
  - "Round 1 answered by delegate: D-33 (whitespace), D-34 (current state wins), D-35 (reason name). Nothing consumer-visible remains open."
---

# Connection requests: blank member ids and the decliner writing back

Announcement: I apply the `plan-driven-dev` workflow (context, goal, plan) and stop when the plan is written. Round 1 is answered (D-33, D-34, D-35); the plan is final.

## 1. Metadata
- **Type**: feature
- **Date**: 2026-10-18
- **Status**: in-progress

## 2. Goal

Every operation of the `connections` module given a blank member id (empty or only whitespace) is rejected with one identifiable reason, `blank-member-id`, before any other rule, and creates, changes or erases nothing. Calls with non-blank ids behave exactly as before. When A's request to B was declined, B can send a request to A; A still cannot send to B; accepting or declining B's request ends as the PRD says (requirements 5 to 8).

## 3. Context

- **Inputs**: PRD `docs/product/prd/connection-requests-edge-ids-and-decliner.md` (requirements 1 to 8 = acceptance criteria), `architect.md` (decided: check in the module, rejection reasons and result shapes below), D-1 to D-32.
- **Code**: `src/connections/{index.ts, domain, application, infrastructure}`; tests `tests/connections/*.test.ts` + `support.ts`; test-cases `docs/business/test-cases/connections/`. Rejections are returned values (D-21); one test file per use case; test boundary = the public operations through `src/connections/index.ts`, in-memory store, deterministic ids (`req-1`, ...).
- **Present behavior that matters**: `decideSend` guards are per direction (`previouslyDeclined` looks at `r.sender === c.sender`), so B->A after a declined A->B is accepted today by the code; nothing tests it. The ids of a send are drawn only after the rules allow it. `pairState` takes the last request of the pair (a pending request is always the latest of its pair).
- **Invariants**: INV-001/002 (`isBlankMemberId` in `domain/member-id.ts`, imports nothing; use cases import the domain only), INV-004 (nothing outside the module imports it), INV-005 to INV-008 (guard clauses, `[sender, recipient].some(...)`, no function grows), INV-009 (a test-case and a test per case), INV-010 (mutation on domain and application, no threshold set: recording one stays a human decision). Run `npm test`, `npm run typecheck`, `npm run harness` at every green.
- **Sensitive zones touched** (human review before merge): `src/connections/index.ts` (result shapes of three operations change), and the use cases around the store port (no change to the port or the store itself).
- **Earlier lessons**: `.plans/FEEDBACK.md` does not exist.

### Carried over

| Item | Plan |
|---|---|
| After A->B declined, B->A is accepted by the code; no document decided it | **Planned**: requirements 5 to 8, behaviors C1 to C6; no code change expected in `send-rules.ts`. |
| Survivor `domain/send-rules.ts:29` (`r.sender === c.sender` replaced by `true`) | **Planned**: killed by C1 (B->A must be accepted after a declined A->B); confirmed by the mutation run (step 9). |
| Reads unrestricted (D-24) | **Deferred by decision (D-24)**; not part of this request. |

## 4. Expected behaviors

Test boundary of every behavior: the public operations of `connections` through `index.ts`. Blank ids are built with `memberId("")`, `memberId("   ")`, etc. (the constructor does not validate and does not throw, architect).

### Public interface (changed)

- `sendRequest`, `acceptRequest`, `declineRequest`, `withdrawRequest`: same signatures; their rejection unions each gain `"blank-member-id"`.
- `getPairState(a, b)`: now `Promise<Result<PairState, "blank-member-id">>`; success = `{ ok: true, value: { connected, requestState } }` (value identical to today's answer, R4).
- `listPendingRequests(recipient)`: now `Promise<Result<readonly ConnectionRequest[], "blank-member-id">>`; success value identical to today's list.
- `eraseMember(member)`: now `Promise<{ ok: true } | { ok: false, reason: "blank-member-id" }>`; `{ ok: true }` for every non-blank member as today (D-26).
- The reason is the same string, `blank-member-id`, on every operation and for either id (R1), distinct from the 9 existing reasons.
- Test helpers (`support.ts`): `stateOf(module, a, b)` and `pendingOf(module, member)` return the success value and throw on a rejection (like `sendOrFail`), so the existing tests change one call each.

### Case (a): blank member id

- **A1 (R1, send)**: given a blank sender, or a blank recipient (separately), when the member sends, then `{ ok: false, reason: "blank-member-id" }`; nothing stored (pending lists empty, state none) and no request id consumed (the next valid send gets `req-1`). Tested for each blank form of A5.
- **A2 (R1, R3, send, both blank)**: given both ids blank (identical, e.g. `""` and `""`; and different, e.g. `""` and `"  "`), when the member sends, then `blank-member-id`, never `self-request`.
- **A3 (R1, accept/decline/withdraw)**: given A->B pending, when a blank member accepts, declines, or withdraws it, then `blank-member-id` and the request is still pending (state(A,B) pending, B's list unchanged). One test per operation.
- **A4 (R3, order on acting operations)**: the blank check comes before every other rule. A blank acting member gets `blank-member-id` (not `request-not-found`) on an unknown request id, on accept, decline and withdraw; (not `not-recipient`/`not-sender`) on an existing request; (not `not-pending`) on a request that is accepted, declined or withdrawn.
- **A5 (R2, what blank is)**: empty string, spaces, tab, line break are blank, each rejected. D-33: standard Unicode whitespace is blank (non-breaking space, ideographic space, other Unicode spaces too); zero-width and invisible characters are NOT blank (an id made of one is non-blank, left to D-15) and a test says so.
- **A6 (R2, R4, not blank)**: an id with a blank inside or around real characters (`"a b"`, `" alice "`) is not blank: the send is accepted, the id is kept as is (not trimmed: state(`" alice "`, bob) is pending while state(alice, bob) is none).
- **A7 (R1, state query)**: given either member blank (separately), or both blank, when the state is asked, then `blank-member-id`, also for the same blank id twice (the "same member twice reports none" answer of D-19 holds for non-blank ids only).
- **A8 (R1, pending list)**: given a blank member, when the pending list is asked, then `blank-member-id`, even when other members have pending requests.
- **A9 (R1, erase)**: given A->B pending, when a blank member is erased, then `{ ok: false, reason: "blank-member-id" }` and nothing is erased (state(A,B) still pending, the list of B unchanged). Twice: rejected both times. Erase of a non-blank unknown member still `{ ok: true }` (D-26).
- **A10 (R4)**: non-blank ids behave exactly as before: the whole existing suite stays green after the call-site change of `stateOf` and `pendingOf`; A6 covers the edge.
- **A11 (R1)**: the reason differs from every existing reason (distinct-reasons test extended).

### Case (b): the decliner writes back

Setup: A sends to B (`req-1`), B declines it.

- **C1 (R5)**: when B sends to A, then it is accepted: `{ id: "req-2", sender: B, recipient: A, state: "pending" }`; A's pending list holds it; the earlier request is unchanged (B cannot accept it again: `not-pending`; A's pending list shows only `req-2`). Kills the `send-rules.ts:29` survivor.
- **C2 (R6)**: while B's request is pending, when A sends to B, then it is rejected (`reverse-pending`, D-34), nothing stored, state pending. Twice: rejected again with the same reason.
- **C3 (twice, order)**: while B's request is pending, when B sends to A again, then `duplicate-pending`.
- **C4 (R7, accept)**: when A accepts `req-2`, then A and B are connected, request state accepted from both sides; the earlier request stays declined (not acted on again: `not-pending`).
- **C5 (R7, decline)**: when A declines `req-2`, then they are not connected, state declined from both sides; B sends to A: `previously-declined`; A sends to B: `previously-declined`. Nothing else changes.
- **C6 (R6/R7 with a connection, D-34)**: after C4, when A or B sends to the other, then `already-connected` (D-34); nothing stored.
- **C7 (R8)**: state of the pair, seen from both members: A->B declined = declined; B->A sent = pending (not the earlier declined); after A declines it = declined; after A accepts it (separate run) = accepted and connected.

## 5. Steps

Order is strict; each step ends green (`npm test`, `npm run typecheck`, `npm run harness`). Test-first inside each step: write the failing test at the stated boundary, then the code.

- [ ] Step 1 — Result shapes, no behavior change. In `tests/connections/support.ts` add `stateOf` and `pendingOf`; replace every `getPairState(` / `listPendingRequests(` call in the existing tests with them (files `accept-request`, `decline-request`, `withdraw-request`, `send-request`, `pair-state`, `pending-requests`, `erase-member`, `rejection-reasons` tests). Then change `application/pair-state.ts`, `application/pending-requests.ts`, `application/erase-member.ts` and the `Connections` interface in `index.ts` to return `Result<..., "blank-member-id">` (always `ok: true` for now). Suite green before any blank logic.
- [ ] Step 2 — Blank check on send (A1, A2, A5 for empty/space/tab/line break). New test file `tests/connections/blank-member-id.test.ts` (all case (a) tests live there, one `describe` per operation). Add `isBlankMemberId` to `domain/member-id.ts` and the helper `application/blank-ids.ts` (rejection from a list of ids); call it first in `application/send-request.ts`; add `"blank-member-id"` to `SendRejection` there and in `index.ts`.
- [ ] Step 3 — Acting operations (A3, A4): the check first in `accept-request.ts`, `decline-request.ts`, `withdraw-request.ts`, before the request lookup; add the reason to the three rejection unions.
- [ ] Step 4 — Reads and erase (A7, A8, A9): the check first in `pair-state.ts` (both members), `pending-requests.ts`, `erase-member.ts`.
- [ ] Step 5 — Edge of "blank" (A5 rest per D-33, A6, A10): `isBlankMemberId` uses `trim()` (Unicode whitespace); a zero-width space id must stay non-blank; A6 must pass without trimming ids.
- [ ] Step 6 — Decliner writes back (C1 to C7): tests in `send-request.test.ts` (C1 to C3, C5, C6), `accept-request.test.ts` (C4), `pair-state.test.ts` (C7). Expected: green without code change; if a test fails, stop (deviation). D-34 keeps today's guard order: no code change.
- [ ] Step 7 — Distinct reasons (A11): extend `tests/connections/rejection-reasons.test.ts` with the `blank-member-id` scenario and the exact string.
- [ ] Step 8 — Test-case files (INV-009), one file per case under `docs/business/test-cases/connections/`, same front-matter as the existing ones (`feature: connection-requests`, `type: functional`, `priority: high`, `source`, `automated_test: <path>::<exact it() name>`, `status: covered`; `pending` before their test exists, none left pending at the end). Exact `it()` names are fixed in the table below.
- [ ] Step 9 — Closing gauntlet: `npm test`, `npm run typecheck`, `npm run harness`, `npm run harness:selftest`, then `npm run mutation` on the critical scope. Check that the `send-rules.ts:29` survivor is gone. Read other survivors; add a behavior test per unprotected behavior, or exclude one with a justification in `stryker.config.mjs`. Do not set the threshold (human, INV-010).

### Test-cases (step 8)

In the front-matter, `automated_test` is written with the full path `tests/connections/<file>::<it name>`, as in the existing test-cases; the table shortens it. The test file for case (a) is `blank-member-id.test.ts`.

| Test-case file (`docs/business/test-cases/connections/`) | Source | `automated_test` (file::it name) |
|---|---|---|
| `blank-send-sender-rejected.md` | PRD R1 | `blank-member-id.test.ts::rejects a send whose sender is blank, and stores nothing` |
| `blank-send-recipient-rejected.md` | PRD R1 | `blank-member-id.test.ts::rejects a send whose recipient is blank, and stores nothing` |
| `blank-send-both-before-self-request.md` | PRD R3 | `blank-member-id.test.ts::reports a send with both ids blank as blank-member-id, not as a request to oneself` |
| `blank-send-consumes-no-id.md` | PRD R1 | `blank-member-id.test.ts::does not draw a request id for a rejected blank send` |
| `blank-accept-rejected.md` | PRD R1 | `blank-member-id.test.ts::rejects an accept by a blank member and leaves the request pending` |
| `blank-decline-rejected.md` | PRD R1 | `blank-member-id.test.ts::rejects a decline by a blank member and leaves the request pending` |
| `blank-withdraw-rejected.md` | PRD R1 | `blank-member-id.test.ts::rejects a withdrawal by a blank member and leaves the request pending` |
| `blank-before-request-not-found.md` | PRD R3 | `blank-member-id.test.ts::reports a blank acting member before an unknown request id, on accept, decline and withdraw` |
| `blank-before-authorization-and-state.md` | PRD R3, D-13 | `blank-member-id.test.ts::reports a blank acting member before the not-recipient, not-sender and not-pending reasons` |
| `blank-state-query-rejected.md` | PRD R1, R3, D-19 | `blank-member-id.test.ts::rejects a state query with a blank member on either side, also the same blank twice` |
| `blank-pending-list-rejected.md` | PRD R1 | `blank-member-id.test.ts::rejects a pending list for a blank member` |
| `blank-erase-rejected.md` | PRD R1, D-26 | `blank-member-id.test.ts::rejects the erasure of a blank member and erases nothing` |
| `blank-forms-empty-and-spaces.md` | PRD R2 | `blank-member-id.test.ts::treats an empty id, spaces, tabs and line breaks as blank` |
| `blank-forms-unicode.md` | PRD R2, D-33 | `blank-member-id.test.ts::treats non-breaking and ideographic spaces as blank, and zero-width characters as not blank` |
| `blank-not-for-padded-ids.md` | PRD R2, R4 | `blank-member-id.test.ts::keeps an id with blanks around or inside real characters as it is` |
| `rejection-reasons-blank-distinct.md` | PRD R1 | `rejection-reasons.test.ts::gives the blank member id rejection its own reason, distinct from the others` |
| `decliner-sends-back-pending.md` | PRD R5 | `send-request.test.ts::lets the decliner send a request back, pending, and keeps the declined request as it was` |
| `decliner-sender-blocked-while-pending.md` | PRD R6, D-34 | `send-request.test.ts::still rejects the original sender while the decliner's request is pending` |
| `decliner-second-send-duplicate-pending.md` | PRD R9 | `send-request.test.ts::rejects a second request of the decliner while the first is pending` |
| `decliner-accepted-connects.md` | PRD R7 | `accept-request.test.ts::connects the two when the original sender accepts the decliner's request` |
| `decliner-declined-blocks-both.md` | PRD R7, R14 | `send-request.test.ts::blocks both members once the original sender declines the decliner's request` |
| `decliner-connected-send-reason.md` | D-34 | `send-request.test.ts::rejects a send between members connected through the decliner's request as already-connected` |
| `decliner-pair-state.md` | PRD R8, D-12 | `pair-state.test.ts::reports the decliner's pending request over the earlier declined one, else the most recent` |

The "existing suite unchanged" case (R4) is the green run of every existing test after step 1 and has no test-case of its own beyond `blank-not-for-padded-ids.md`.

## 6. Risks & edge cases

D = decided by a document, T = technical (not observable).

| Operation | Twice | Nothing | Invalid | Edge | Order |
|---|---|---|---|---|---|
| send (changed) | blank twice: rejected twice, same reason, no id drawn (D: R1) | empty string = blank (D: R2) | blank sender, recipient or both: D R1 | forms of whitespace: D (space, tab, line break), D-33; padded id not blank and not trimmed: D R4 (A6) | blank first, so `blank-member-id` beats `self-request` (D R3, A2); both blank, same or different: one reason, nothing to order; id drawn only after all rules (A1, precedent D-32) |
| accept / decline / withdraw (changed) | blank twice: same rejection, request unchanged (D R1) | empty acting member = blank (D R2) | blank acting member: D R1 | request id blank: out of scope (PRD 4) | blank before `request-not-found`, authorization and `not-pending` (D R3, A4); request id is looked up only after |
| getPairState (changed) | T: read only | empty = blank (D R2) | blank on either side: D R1 | same blank twice: blank wins over D-19 (D R3, A7) | (A,B) vs (B,A): both reject if either is blank |
| listPendingRequests (changed) | T | empty = blank | blank: D R1 | a blank member with other pending requests around: D R1 | n/a |
| eraseMember (changed) | blank twice: rejected twice, nothing erased (D R1); non-blank twice still ok (D-26) | empty = blank | blank: D R1 | non-blank unknown member still `{ ok: true }` (D R4, D-26) | a rejected erase changes nothing, so a later valid erase gives the same final state (T) |
| send, decliner side (C1 to C7) | decliner sends twice while pending: `duplicate-pending` (D R9) ; original sender twice: `reverse-pending` again (D-34) | n/a | n/a | declined, then decliner accepted/declined (D R7); connected after decline: `already-connected` (D-34) | when two reasons apply (decline block with reverse-pending or already-connected): current state wins, D-34 |

Other risks:
- **Public break of three result shapes**: accepted by the orchestrator (delegate), recorded in the run notes; all call sites sit in `tests/connections/`. Step 1 isolates it from the behavior change.
- **Non-string input**: the types say `string`; a JavaScript caller passing `undefined` or `null` would make `trim` throw. The plan says nothing about it (no document, not reachable from typed code, PRD speaks of "empty or only whitespace"); not tested.
- **Mutation**: assert the exact reason and the unchanged state after each rejection; test each whitespace class and a padded id so that `trim`/`=== ""` mutants die.
- **INV-005 to INV-008**: no function gets longer than a guard clause; `sendRequest` stays under 40 lines.

### Technical choices (for the reviewer to challenge)

Structure only; none is visible to a caller.
- `isBlankMemberId(id)` in `domain/member-id.ts` as `id.trim() === ""` (D-33); `memberId()` untouched.
- One application helper `application/blank-ids.ts` returns the `blank-member-id` rejection for a list of ids, so the seven use cases share one line each; the reason string lives in one place.
- The new reason is added to the application-layer rejection unions only; domain transitions (`accept`, `decline`, `withdraw`, `decideSend`) are untouched.
- Case (b) adds no production code ; tests only (D-34 keeps the guard order).
- Support helpers `stateOf` / `pendingOf` keep the existing tests readable instead of unwrapping `.value` in each.
- New file `blank-member-id.test.ts` for case (a); case (b) tests sit with the use case they exercise.

## 7. Out of scope

- A non-blank id that names no known member (D-15), a blank request id, concurrency (another request), who may read a pair state or a list (D-24).
- Non-string member ids at runtime (types say `string`; confirmed out of scope).
- A normalization of ids (trimming, case): ids are kept exactly as given.
- Changing the privacy-notice wording or the retention of declined requests (D-14).
- Erasure behavior beyond what the existing tests cover.
- Recording the mutation threshold (INV-010, human).

## 8. Deviations

(empty)

## 9. Self-review

(empty)

## 10. Follow-up actions

(empty)
