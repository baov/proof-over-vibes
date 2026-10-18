---
role: architect
status: done
structure: decided
reasons:
  - "Blank-id check placed in the module (domain rule, applied first in every use case); no ADR, ADR-0001 holds."
  - "Reads and erase now return a Result: a break of their result shape, but cheap to reverse today (no consumer outside the module's own tests); decided, flagged for the reviewer."
  - "Case (b) needs no structural decision: the existing send guards are per direction."
---

# Architect: blank member ids and the decliner writing back

## Decided (cheap to reverse, no ADR)

**Where the blank-id check belongs.**
- The rule "blank = empty or only whitespace" (requirement 2) is a domain rule: one pure function `isBlankMemberId` in `domain/member-id.ts`, next to the type. Nothing else knows what blank means.
- It is applied at the top of each use case in `application/`, before any store read and before every other rule (requirement 3). One shared rejection reason, `blank-member-id`, distinct from every existing reason (requirement 1).
- Why not in `memberId()`: the constructor is public and typed `MemberId`; making it throw would put an exception in a module that returns rejections as values, and `MemberId` can still be cast. Why not in `createConnections` (the public entry): the rules would sit outside the use cases, and the entry point is a sensitive zone that should stay a wiring file.
- Order inside a use case: check every member id given (send: both; accept/decline/withdraw: the acting member, before the request lookup; state query: both; pending list: the member; erase: the member), then the existing flow.

**Change of habit: reads never reject (D-19, D-24 untouched), erase always succeeds (D-26).**
- Both now reject for a blank id only. Non-blank ids behave exactly as before (requirement 4), including a query with the same member twice and an erase of an unknown member.
- New result shapes in `index.ts` (the planner names them):
  - `getPairState` returns `Result<PairState, "blank-member-id">`;
  - `listPendingRequests` returns `Result<readonly ConnectionRequest[], "blank-member-id">`;
  - `eraseMember` returns `{ ok: true }` or `{ ok: false, reason: "blank-member-id" }`;
  - `SendRejection`, `AcceptRejection`, `DeclineRejection`, `WithdrawRejection` each gain `"blank-member-id"`.
- Rejected alternatives: throwing on reads (contradicts the Result convention of the module); adding an "invalid" value to `PairState` (works for the state query only, not for the list); a second set of methods beside the old ones (two contracts for one operation).

**Is that a break of the public contract, and is it costly to reverse?**
- Yes for the type: the success values of three operations are now wrapped (`PairState` becomes `Result<PairState, ...>`, same for the list), so any caller must change. The contract of the other four operations only gains a reason.
- Not costly today: the only callers are the module's own tests (no other module imports `connections`; `profiles`, `posts`, `data-rights` do not exist). Every caller to update is in `tests/connections/` and `tests/connections/support.ts`. The same change after another module reads the pair state would touch that module too, so this is the cheapest moment. I therefore decide it myself rather than escalate; if the reviewer reads "breaking a public contract" strictly, it is one line to relay to the human.
- `src/connections/index.ts` is a sensitive zone: a human reviews before merge.

**Case (b), the decliner writes back.** No structural decision. In `domain/send-rules.ts` the guards `previouslyDeclined`, `duplicatePending` and `reversePending` already compare the direction of each request (`r.sender === c.sender`), so B to A after A to B was declined is accepted by the present code; the planner adds the tests for requirements 5 to 8 and they cover the survivor at `send-rules.ts:29` (a declined request from the other direction must not block). Pair state already picks pending, else most recent (D-12). The guard list keeps its order; nothing to move.

## Invariants and harness

- No new invariant. `isBlankMemberId` lives in `domain` and imports nothing (INV-001); the use cases import it from the domain of their module (INV-002). INV-005 to INV-008: use the guard clause (`if (isBlankMemberId(x)) return rejected("blank-member-id")`), at most two calls for send, so no function grows past its thresholds.
- INV-009: one test-case and one test per requirement 1 to 8; the blank-id test-cases should name the operation they cover.

## Debt

None flagged. D-15 (non-blank unknown ids) and blank request ids stay out of scope; if a member directory arrives, an id check would join `isBlankMemberId` in the same place.
