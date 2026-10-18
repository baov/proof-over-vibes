---
role: product-owner
status: done
reasons: []
---

# Stories: connection requests

Source: PRD `docs/product/prd/connection-requests.md` (section 5, rules numbered R1-R15). No glossary exists yet; the PRD vocabulary applies (member, connection request, pending, accepted, declined, withdrawn, connected). Pure domain behavior: no UI, no sign-in, no profile. The PRD's three open questions stay open (see "Open points").

Two stories. Story 1 closes the journey end to end (ask, accept, be connected); story 2 adds the other two ways a request ends.

## Story 1: Ask a colleague to connect, and be connected once they accept

**Value:** a member can reach a colleague, and the colleague controls who connects: the first connection exists (outcome 1).

Acceptance criteria:

1. A member sends a connection request to another member; the request is pending. (R1)
2. The recipient accepts a pending request; sender and recipient are then connected, each to the other. (R3)
3. A member other than the recipient who tries to accept is rejected, and the request stays pending. (R2)
4. For any two members, one can tell whether they are connected and what state their request is in (pending, accepted, or none). (R5)
   - 4a. For two members who never exchanged a request, the state is "none", not an absence. (R5, D-11)
5. A recipient obtains the pending requests addressed to them. (R6)
6. Sending is rejected when the sender and the recipient are the same member. (R8)
7. Sending is rejected while a request from the same sender to the same recipient is pending. (R9)
8. Sending is rejected while a request in the reverse direction is pending; it is not accepted automatically. (R10)
9. Sending is rejected between members who are already connected. (R11)
10. Accepting a request that is not pending (already accepted) is rejected with its own reason; the state is unchanged. (R15, accept on an accepted request; declined and withdrawn are covered in story 2)
11. When a member who is not the recipient tries to accept a request that is also not pending, the rejection reason is the authorization one, not the not-pending one. (R2, R15, D-13)
12. Every rejection above carries a distinct, identifiable reason for the rule that caused it. (R7)

## Story 2: Decline a request, or withdraw one I sent

**Value:** the recipient can refuse without a connection forming, and the sender can take back a request they no longer want, so the circle stays under both members' control.

Depends on story 1.

Acceptance criteria:

1. The recipient declines a pending request; the request is declined and the two are not connected. (R4)
2. A member other than the recipient who tries to decline is rejected, and the request stays pending. (R2)
3. The sender withdraws a pending request; it becomes withdrawn. (R12)
4. A member other than the sender who tries to withdraw is rejected, and the request stays pending. (R12)
5. After a withdrawal, the sender can send a new request to the same member; it is pending. (R13)
6. After a decline, a new request from the same sender to the same recipient is rejected. (R14)
7. Accepting, declining or withdrawing a request that is not pending (declined, withdrawn, accepted) is rejected with a distinct reason; the state is unchanged. (R15)
8. The state of a request reported for two members includes declined and withdrawn. (R5)
   - 8a. When a pair has several requests, the state reported is the pending one if any, otherwise the most recent. (R5, R13, D-12; moved from story 1, not reachable before withdraw and decline exist)
9. When a member who is not the sender tries to withdraw a request that is also not pending, or a non-recipient tries to decline one, the rejection reason is the authorization one. (R12, R2, R15, D-13)
10. The decline block of criterion 6 has no expiry while both accounts exist; it ends when either account is erased. (R14, D-14; the privacy-notice wording is out of scope)
11. Each new rejection carries a distinct, identifiable reason. (R7)

## Open points

Each is for the orchestrator to relay. None is decided; no criterion depends on a choice below.

1. **Member id validity** (PRD open question 1). Deliberately deferred (D-15): no id check, nothing tested, until a later edge-case request. Sender or recipient id empty or unknown to the product. Options: (a) reject with its own reason; (b) accept any non-empty id until the profiles module exists; (c) leave undefined and defer to a later edge-case request. PRD recommends nothing.
2. **Concurrency** (PRD open question 2). Two members request each other at the same moment, or an accept and a withdrawal arrive together. Options: (a) first writer wins, the second gets a rejection per R10 or R15; (b) leave undefined and defer. Needs a product answer before the technical design chooses a mechanism.
3. **Decliner sends a request back** (PRD open question 3, related to R14). After a decline, may the recipient send a request to the former sender? Options: (a) allowed, the decline binds only the original direction; (b) rejected, a decline blocks the pair; (c) defer. No criterion covers this case.

Points 4 to 7 of the first version were settled by delegate: D-11 (none state), D-12 (which request), D-13 (reason precedence), D-14 (decline block and erasure). Points 1 to 3 stay open, reserved for later edge-case requests.
