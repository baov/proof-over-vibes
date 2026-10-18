# PRD: connection requests

Status: ready. The three product questions were answered by delegate (recommended options); the two remaining open questions are left for later requests. Epic E3 Connections, backlog items 3.1 and 3.2, slice 1 (walking skeleton), outcome 1 (a first connection). Hypotheses, not facts.

## 1. Problem

A freelance translator or interpreter knows colleagues but has no way to say "we know each other professionally" that the other person agrees to. Without a mutual, consented link, posts cannot be limited to connections (the positioning, see `vision.md`). The market watch shows that the established networks all rely on a connection between members (`research.md`); how well it serves this segment is *unverified*.

## 2. Goal and success

A member can ask another member to connect, and the other member can accept or decline; an accepted request makes the two members connected. Success: outcome 1 of the vision (share of new members with a connection after one week). The target is not yet set by the human.

## 3. Users and use

- **Sender**: the member who asks. **Recipient**: the member asked. Both are members already identified by an id.
- Main path: the sender sends a request; it is pending; the recipient accepts; the two are connected, each in the other's circle. Alternative: the recipient declines; no connection.

## 4. Scope

**In:** sending a request, accepting it, declining it, and the rules between them. The behavior only: no screen, no sign-in, no profile, no feed.

**Out:** listing or removing connections (3.3), notifications (Later), blocking and reporting (E7), search (E6), requests with a message. 

## 5. Requirements

Each is observable from the outside. Vocabulary: member, connection request, pending, accepted, declined, withdrawn, connected. Source of the rules 8-12: answered by delegate (human's delegate), recommended options.

1. A member can send a connection request to another member; the request is **pending**.
2. Only the recipient can accept or decline a pending request; any other member is rejected and the request is unchanged.
3. Accepting a pending request makes the sender and the recipient **connected**; the connection is mutual (each is connected to the other).
4. Declining a pending request leaves them not connected; the request is **declined**.
5. It is possible to tell, for any two members, whether they are connected, and what state their request is in.
6. A recipient can obtain the pending requests addressed to them.
7. Every rejection carries a distinct, identifiable reason for the rule that caused it.
8. A request to oneself is rejected.
9. A second request is rejected while one from the same sender to the same recipient is pending.
10. A request is rejected while one in the reverse direction is pending (no automatic accept).
11. A request between members already connected is rejected.
12. The sender can withdraw a pending request; it becomes **withdrawn**. Only the sender can; any other member is rejected and the request is unchanged.
13. After a withdrawal, the sender can send a new request to the same member.
14. After a decline, a new request from the same sender to the same recipient is rejected. (The recipient could still send one in the other direction: not covered, see open questions.)
15. Accepting, declining or withdrawing a request that is not pending is rejected with a distinct reason; the state is unchanged.

## 6. Risks and open questions

- *Assumption:* mutual, consented connections (not following) fit this segment. If false, the circle model changes.
- *Assumption:* a decline is silent to the sender (no notification exists). If the segment expects feedback, revisit with Notifications.
- *Technical unknowns, for the architect, not answered here:* what must be erased from requests when a member deletes their account (GDPR, E5); retention of declined requests.

**Open questions (not decided; to come as later edge-case requests):**

1. **Member id validity.** What happens when the sender or the recipient id is empty or unknown to the product? Not specified: no requirement covers it.
2. **Concurrent requests.** What happens when two members request each other at the same moment, or when an accept and a withdrawal arrive together? Not specified.
3. After a decline, may the recipient send a request to the former sender? Not specified.
