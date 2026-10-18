# PRD: connection requests, edge case: blank member ids and the decliner

Status: ready. The three questions were answered by delegate (recommended options 1a 2a 3a). Extends `connection-requests.md` (same vocabulary: member, connection request, pending, accepted, declined, withdrawn, connected). Decisions already taken: `docs/business/decisions.md` D-6 to D-8, D-14, D-15, D-26, D-29.

## 1. Problem

Two situations the first PRD left open, and the built behavior answers only by accident.

- **(a) A blank member id.** A member id that is empty or only blank characters is passed to an operation. Nobody decided what the product does (the first PRD's open question 1 was deferred, D-15). Whether an id belongs to a real member stays out of scope (see section 6); a blank id is a different case, since it can never name a member, whatever the member directory contains.
- **(b) The decliner writes back.** A sent a request to B and B declined it. The first PRD (rule 14, D-29) blocks A from sending again to B. It says nothing about B sending a request to A (the first PRD's open question 3).

## 2. Goal and success

Every operation gives a predictable, identifiable answer when given a blank id, and members know whether a decline also closes the door on the decliner. Success is observable by the rules in section 5; no market outcome is attached, it protects outcome 3 of the vision (trust).

## 3. Users and use

Same users as the first PRD: sender, recipient. The caller of an operation is whoever provides the ids (another part of the product, not a person). Main paths: an operation receives a blank id; a member who declined a request sends one back to the former sender.

## 4. Scope

**In:** (a) a blank id on send (sender or recipient), accept, decline, withdraw (the acting member), state query (either member), pending list (the member), erase; (b) a request from a former decliner to the former sender.

**Out:** an id that is not blank but names no known member (no member directory exists; D-15); a blank *request* id (request ids are supplied by the caller, D-20); concurrency (see the other edge-case PRD).

## 5. Requirements

Each is observable from the outside. Source of the rules below: answered by delegate, recommended options.

**Case (a), blank member id**

1. An operation given a blank member id is rejected with one identifiable reason, distinct from every existing reason; nothing is created, changed or erased. This holds for send (either id), accept, decline, withdraw (the acting member), state query (either member), pending list and erase.
2. A member id is blank when it is empty or made only of whitespace.
3. The blank-id check comes before every other rule: a blank id is reported as such even when another rule would also reject the call.
4. A call with non-blank ids behaves exactly as before.

**Case (b), the decliner writes back**

5. When A's request to B was declined, B can send a request to A; it is pending, and the earlier declined request stays as it was.
6. In that situation A still cannot send a request to B (rule 14 of the first PRD holds, and a reverse request is pending anyway).
7. If A accepts B's request, the two are connected. If A declines it, they are not connected, and B cannot send another to A (rule 14).
8. For the pair, the state query reports the pending request when there is one, otherwise the most recent (D-12).

## 6. Risks and open questions

- *Assumption:* a blank id is always a caller fault, never a member to serve.
- *Not decided, kept for later:* ids that are non-blank but unknown (D-15), and blank request ids.
- *For the architect, not answered here:* where the check belongs; the present habit of reads never rejecting (D-19) and of erase always succeeding (D-26) changes for blank ids only.
