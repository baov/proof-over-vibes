# PRD: connection requests, edge case: simultaneous operations

Status: ready. The two questions were answered by delegate (recommended options 4a 5a). Extends `connection-requests.md` (same vocabulary). Decisions already taken: `docs/business/decisions.md` D-6 (no automatic accept on a reverse request), D-8, D-13, D-30.

## 1. Problem

The rules of the first PRD assume operations arrive one after the other. Two members can act at the same moment.

- **(c) Mutual requests.** A sends a request to B while B sends a request to A, at the same moment. Rule 10 rejects a request when the reverse one is pending, but neither is pending yet when both are submitted.
- **(d) Accept and withdraw together.** The recipient accepts a pending request while its sender withdraws it, at the same moment. Accepting makes them connected; withdrawing says they never should be.

## 2. Goal and success

No simultaneous action leaves the product in a state that no sequence of single actions could produce. Success: for every pair of simultaneous operations, the observable result equals what one of the two orders would give. It protects outcome 3 (trust) of the vision.

## 3. Users and use

Sender and recipient of the same pair, acting independently. The "same moment" means that neither operation has returned its answer when the other starts.

## 4. Scope

**In:** (c) and (d) above, and by the same principle any two operations on the same pair of members (accept against decline, two identical sends, and so on).

**Out:** the speed of the product, and how simultaneous calls are made safe (the architect's).

## 5. Requirements

Each is observable from the outside; source: answered by delegate, recommended options.

1. For any two simultaneous operations on the same pair of members, the final state and both answers are those of the two operations run one after the other, in one of the two orders. No third outcome exists.
2. (c) When A and B send each other a request at the same moment, exactly one request is created and pending; the other is rejected with the reason of rule 10 (a reverse request is pending). The two members are not connected, and no automatic accept happens (D-6).
3. (d) When the recipient accepts and the sender withdraws the same request at the same moment, exactly one succeeds. If the accept wins, the two are connected, the request is accepted, and the withdraw is rejected as not pending. If the withdraw wins, they are not connected, the request is withdrawn, and the accept is rejected as not pending.
4. It is never possible to observe a request that is both connected and withdrawn, nor two pending requests for one pair.
5. Accept and decline of the same request at the same moment: exactly one succeeds, the other is rejected as not pending. Two identical sends at the same moment: exactly one request is created, the other is rejected as a duplicate pending request.
6. Which of the two simultaneous operations wins is not specified beyond rule 1: no priority between members or between kinds of operation.

## 6. Risks and open questions

- *Assumption:* simultaneity is rare in a network this size, but it has a visible cost when it fails (a connection the sender withdrew).
- *Technical unknowns, for the architect, not answered here:* how simultaneous operations are serialized; whether the module may run in more than one process; the scope of what must be atomic; an erase during an operation (not specified).
