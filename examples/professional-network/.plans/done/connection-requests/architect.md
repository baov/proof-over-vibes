---
role: architect
status: done
structure: decided
reasons:
  - "ADR-0001 written: modular monolith, hexagonal modules (answered-by-delegate, option a)."
  - "Stories pass: story 2 criterion 10 (erasure ends a decline block) is covered by a member-level erasure operation of the module, not by account deletion (see Stories pass)."
  - "Retention of declined requests settled by D-14; no longer open."
---

# Architect: connection requests

## What I understood

- The project is empty (no code, no package file). Stack fixed: TypeScript, Node 22, npm, Vitest.
- The request is a small, pure domain core: a connection request between two members, with a short life cycle (pending, then accepted, declined or withdrawn) and 15 rules. No UI, no sign-in, no storage chosen, no transport.
- What follows on the roadmap: profiles (E2), connections list/removal (3.3), posts and feed limited to connections (E4), data rights (E5: erasure, export), later search, blocking, notifications.
- DDD view: the vision's differentiator is "posts readable by connections only". The **connection** is therefore the heart of the core domain; profiles, posts and the feed are separate concerns that will each read "are these two members connected?". Account access and a user directory are generic. Connection requests are not CRUD: the rules between members carry real behavior, so a domain model is justified here (not a plain table with handlers).

## Question 1: architectural style (answered)

Answered by delegate: 1a, modular monolith with hexagonal modules. Recorded in `docs/technical/adr/0001-modular-monolith-with-hexagonal-modules.md`. Options weighed: (a) modular monolith with hexagonal modules, (b) single-module hexagonal, (c) clean architecture, (d) n-tier.

## Decided now (cheap to reverse)

Applied inside whichever option is chosen; none of it needs an ADR.

- **Where the code lives.** A `connections` module (under `src/`). Its domain has the connection request as an aggregate root (a state machine: pending to accepted, declined or withdrawn) and the connection between two members as its own small concept (a pair of members, with no order). Members appear only as a member id, a value object: this module holds no member data.
- **Cross-request rules.** Rules 9, 10, 11, 14 look across requests (same direction pending, reverse pending, already connected, declined before). They live in the domain as a pure function over the relevant requests and connection, not in the repository. The application layer loads what the function needs through a port, then applies the result.
- **Rejections.** A distinct, named reason per rule (requirement 7), returned as a value (a result type with a reason code), not thrown. The caller can then branch on the reason, and a test can assert it exactly.
- **Storage.** A repository port in the application layer plus an in-memory adapter, enough for this request. **No storage product is chosen and no dependency is added**: that is a separate, costly decision for a later request. Only Vitest and TypeScript are added, as given.
- **Time and ids.** A clock port and an id generator port, so tests are deterministic. No time-based rule exists yet, but the declined-request retention question (below) will likely need the clock.
- **Tests.** Vitest, behavior first, against the public use cases with the in-memory adapter; one test per requirement of the PRD section 5.
- **Vocabulary.** The words of the PRD are the ubiquitous language for names in code: member, connection request, pending, accepted, declined, withdrawn, connected. No synonyms (no "friend", "invite", "follow", "reject").

## Technical unknowns taken up from the PRD

1. **Erasure when a member deletes their account (E5.2).** Recommended design, cheap now: the `connections` module stores only member ids, never names or other personal data, and its repository port offers one operation to remove everything involving a member id (requests and connections). Erasure by hard deletion is then one call per module. A consequence to be aware of: removing a declined request also lifts rule 14 for the counterpart, since the record that blocked a new request is gone. That is acceptable for an erased member (the counterpart cannot be blocked from a member who no longer exists), but I flag it. Who triggers the deletion across modules (a cross-module step or an event) is not decided: it is a decision for the data-rights request, with a public entry point per module as the extension point.
2. **Retention of declined requests.** Not decided by me and not a technical question alone: rule 14 *requires* keeping the declined request for as long as the block should hold, which makes a retention period a product and legal choice (how long may a decline block a new request; what the privacy notice says). **Question for `product-owner` (to relay; not decided here):** how long may a decline block a new request from the same sender, and what must the privacy notice say? This does not block this feature. For this feature the code keeps declined requests with no expiry; the retention rule can later be added through the clock port without changing the model.

## Left open in the PRD, and what the structure does about it

- **Member id validity** (empty or unknown id): no requirement; the id is a value object, so a validity rule can be added in one place when the question is answered. I decide nothing.
- **Concurrent requests** (two members requesting each other at once; accept against withdrawal): no requirement. The repository port will be written so a store can refuse a write that conflicts (a version check on the request), but the behavior is not specified and I do not invent it.
- **Decliner sends a request back:** a product question, untouched.

## Stories pass (once-per-feature, stories in hand)

D-11 to D-13 fit the structure as decided: "none" is a value returned by the state query; the pair state picks pending, else most recent; the authorization check runs before the not-pending check in the domain. Nothing to add. D-14 settles unknown 2 of the earlier pass: declined requests are kept with no expiry, so no clock is needed for this feature.

**Story 2 criterion 10 (erasure).** Account deletion is out of this feature, but the criterion is honestly coverable at the level this module owns. Decision (cheap to reverse, no ADR; it applies ADR-0001):

- The `connections` module exposes, through its public entry point, one operation: erase everything held about a member id (every request where the member is sender or recipient, and every connection involving them), by hard deletion through the repository port (the operation already planned in unknown 1).
- The criterion is tested at that operation: after a decline, a new request is rejected; after the erasure of either member, it is no longer rejected for that reason (and no trace of the pair remains).
- Out of this feature: what triggers the operation (account deletion, the future data-rights module), cross-module orchestration, the privacy-notice wording. The criterion's "when either account is erased" is therefore read as "when the module is told to erase that member"; the planner should word the test that way, and no behavior of account deletion is invented.
- The operation sits in a sensitive zone (repository port and public entry point, see invariants): a human reviews before merge.

## ADR

ADR-0001 written (accepted), with the dependency rule: domain imports nothing outside its module; application imports the domain of its module; infrastructure imports application and domain of its module; a module reaches another only through its public entry point, no deep imports. For the harness engineer.

## Debt

None: the project is empty.
