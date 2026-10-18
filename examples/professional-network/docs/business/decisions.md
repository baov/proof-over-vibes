# Decision log

Append-only. Entries D-1 to D-10 were taken before any code existed, by the human's delegate.

### D-1 Positioning: focused segment, freelance translators and interpreters in the EU
- status: answered-by-delegate
- answer: focused segment, EU jurisdiction (GDPR applies)
- source: docs/product/research.md section 7
- request: product-phase

### D-2 Business model
- status: answered-by-delegate
- answer: free; no monetization, no payment feature
- source: docs/product/research.md section 7
- request: product-phase

### D-3 Sequencing of the roadmap
- status: answered-by-delegate
- answer: as drafted (Now, Next, Later horizons)
- source: docs/product/roadmap.md (status line), docs/product/backlog.md (status line)
- request: product-phase

### D-4 Prioritization method
- status: answered-by-delegate
- answer: MoSCoW per slice
- source: docs/product/backlog.md (status line and table)
- request: product-phase

### D-5 Segment fields in slice 1
- status: answered-by-delegate
- answer: language pairs and specialties are in the walking skeleton
- source: docs/product/story-map.md (status line), docs/product/backlog.md (reasoning)
- request: product-phase

### D-6 Invalid requests: self, duplicate pending, reverse pending, already connected
- status: answered-by-delegate
- answer: all rejected (PRD rules 8-11; no automatic accept on a reverse request)
- source: docs/product/prd/connection-requests.md section 5, rules 8-11
- request: connection-requests

### D-7 Withdraw and decline
- status: answered-by-delegate
- answer: sender may withdraw a pending request and send a new one; a decline blocks a new request from the same sender to the same recipient (PRD rules 12-14)
- source: docs/product/prd/connection-requests.md section 5, rules 12-14
- request: connection-requests

### D-8 Answering a request that is not pending
- status: answered-by-delegate
- answer: accept, decline or withdraw is rejected with a distinct reason; state unchanged (PRD rule 15)
- source: docs/product/prd/connection-requests.md section 5, rule 15
- request: connection-requests

### D-9 Feature picked for the first request
- status: answered-by-delegate
- answer: connection requests (backlog 3.1 + 3.2, one feature)
- source: docs/product/backlog.md (status line, row 3.1-3.2)
- request: connection-requests

### D-10 Architectural style (technical, recorded for completeness)
- status: answered-by-delegate
- answer: modular monolith, each module hexagonal (domain, application, infrastructure)
- source: docs/technical/adr/0001-modular-monolith-with-hexagonal-modules.md
- request: connection-requests

### D-11 State reported for two members who never exchanged a request
- status: answered-by-delegate
- answer: an explicit "none" state (a query always returns a state, never an absence)
- source: docs/product/prd/connection-requests.md section 5, rule 5 ("what state their request is in" asks for a state for any two members)
- request: connection-requests

### D-12 Which request is reported when a pair has several
- status: answered-by-delegate
- answer: the pending one if any, otherwise the most recent
- source: docs/product/prd/connection-requests.md section 5, rules 5, 13, 14 (after a withdrawal then a new request, the live one must show; a decline must stay visible)
- request: connection-requests

### D-13 Precedence of rejection reasons
- status: answered-by-delegate
- answer: the authorization reason (rules 2 and 12) comes before the not-pending reason (rule 15)
- source: docs/product/prd/connection-requests.md section 5, rules 2, 12, 15 (a member who is not a party must not learn the request's state)
- request: connection-requests

### D-14 How long a decline blocks a new request, and erasure (Architect's question)
- status: answered-by-delegate
- answer: no expiry while both accounts exist; erased with the account; the privacy-notice wording is out of scope of this feature
- source: docs/product/prd/connection-requests.md section 5, rule 14, and section 6 (retention of declined requests)
- request: connection-requests

### D-15 Member id validity: deliberate deferral (PRD open question 1)
- status: answered-by-delegate
- answer: option (c), leave undefined: no id check, nothing tested; reserved for a later edge-case request written by the product manager. The question stays open in stories.md.
- source: docs/product/prd/connection-requests.md section 6, open question 1; relayed delegation
- request: ask-and-accept

### D-16 Accept on an unknown request id
- status: answered-by-delegate
- answer: rejected with its own reason (`request-not-found`), state unchanged
- source: docs/product/prd/connection-requests.md section 5, rule 7 (a distinct reason per rule; "does not exist" is a different cause from "not pending", rule 15)
- request: ask-and-accept

### D-17 Shape of the state query answer
- status: answered-by-delegate
- answer: the two facts only: connected (yes or no) and request state (none, pending, accepted; later declined, withdrawn)
- source: docs/product/prd/connection-requests.md section 5, rule 5; D-11
- request: ask-and-accept

### D-18 Order of the pending list
- status: answered-by-delegate
- answer: oldest first (creation order)
- source: none (PRD silent); chosen for consistency with "most recent = creation order" in D-12. Product preference, to be revisited by a person.
- request: ask-and-accept

### D-19 State query with the same member twice
- status: answered-by-delegate
- answer: reports "none, not connected"; a query does not reject
- source: docs/product/prd/connection-requests.md section 5, rules 5 and 8 (a self-request can never exist, so the state is none)
- request: ask-and-accept

### D-20 Request ids: who supplies them
- status: answered-by-delegate
- answer: (a) the caller supplies ids, as built; no change to the code
- source: none (PRD and decisions silent; a technical-interface point). Lowest-impact option, a preference for a person to revisit.
- request: ask-and-accept

### D-21 Result shape of operations
- status: answered-by-delegate
- answer: (a) asynchronous operations returning `{ ok: false, reason }` for a rejection, as built; no change to the code
- source: PRD section 5, rule 7 (a rejection carries an identifiable reason; a returned reason satisfies it). Sync vs async and thrown errors: PRD silent, lowest-impact option kept, a preference for a person to revisit.
- request: ask-and-accept

### D-22 Names of the rejection reasons
- status: answered-by-delegate
- answer: accepted as built: self-request, duplicate-pending, reverse-pending, already-connected, not-recipient, not-pending, request-not-found; no change to the code
- source: PRD section 5, rule 7 (distinct, identifiable); names themselves: PRD silent, they follow the PRD vocabulary (pending, connected, recipient). A preference for a person to revisit.
- request: ask-and-accept

### D-23 Fields of a request as seen by a caller
- status: answered-by-delegate
- answer: { id, sender, recipient, state } accepted, no field added or removed; no change to the code
- source: PRD section 5, rules 1, 5, 6 (sender, recipient and state are what the rules observe; the id is needed to accept); no timestamp, as D-14 sets no time rule. Otherwise PRD silent, a preference for a person to revisit.
- request: ask-and-accept

### D-24 Who may read a pair's state and a pending list
- status: answered-by-delegate
- answer: the module does not restrict reads: any caller may ask. Restricting who may ask belongs to the layer that knows who is signed in, outside this module. Keep the reads as built.
- source: PRD section 5, rules 5 ("any two members") and 6; PRD section 4 (no sign-in in scope); ADR-0001 (other modules, such as posts, must ask "are these two connected"). Risk to carry: vision.md anti-goal "collecting data the member did not choose to give" and audience privacy; a person should revisit when sign-in exists.
- request: decline-and-withdraw

### D-25 Send with a request id that already exists
- status: answered-by-delegate
- answer: rejected with its own reason (`request-id-taken`), nothing stored, the existing request unchanged; never a silent overwrite
- source: PRD section 5, rule 7 (distinct reason per rejection); D-20 (caller supplies ids), D-21 (rejections returned). Reason name: preference for a person to revisit.
- request: decline-and-withdraw

### D-26 Erase a member: result, second call, unknown member
- status: answered-by-delegate
- answer: always succeeds with `{ ok: true }`; a second call and a call for a member the module never saw are no-ops that also succeed (nothing remains either way)
- source: D-14 (declined requests erased with the account); D-15 (no member id check, so an unknown member is not an error). Result shape per D-21.
- request: decline-and-withdraw

### D-27 Decline by a non-recipient
- status: answered-by-delegate
- answer: reuses `not-recipient`, the reason of accept by a non-recipient
- source: PRD section 5, rule 2 (same rule for accept and decline); D-22
- request: decline-and-withdraw

### D-28 Withdraw by a non-sender
- status: answered-by-delegate
- answer: new reason `not-sender`; the recipient withdrawing is also `not-sender`
- source: PRD section 5, rule 12 (a distinct rule from rule 2), rule 7; D-22 vocabulary
- request: decline-and-withdraw

### D-29 Send after a decline
- status: answered-by-delegate
- answer: new reason `previously-declined`
- source: PRD section 5, rules 14 and 7; D-22 vocabulary
- request: decline-and-withdraw

### D-30 Acting on a request that is not pending
- status: answered-by-delegate
- answer: one shared `not-pending` for accepted, declined and withdrawn, on accept, decline and withdraw
- source: PRD section 5, rule 15 (one rule, one distinct reason; the state is readable through rule 5); D-8, D-13
- request: decline-and-withdraw

### D-31 Decline or withdraw on an unknown request id
- status: answered-by-delegate
- answer: `request-not-found`, state unchanged, checked before authorization and state
- source: D-16 extended to the two new operations; PRD section 5, rule 7
- request: decline-and-withdraw

### D-32 Send that breaks a business rule and whose id is already used
- status: answered-by-delegate
- answer: (a) business rules first: the caller gets the business reason (`self-request`, `duplicate-pending`, ...); `request-id-taken` only when the rules allow the send
- source: PRD section 5, rules 8-11 and 7 (the business rule is what the member can act on; an id clash is a technical fault); D-13 (reason precedence follows the same logic: the member-facing cause first); D-25. Preference for a person to revisit.
- request: decline-and-withdraw

### D-33 What "whitespace" covers in a blank member id
- status: answered-by-delegate
- answer: (a) standard Unicode whitespace (space, tab, line breaks, no-break space, ideographic space); zero-width and invisible characters are not blank
- source: docs/product/prd/connection-requests-edge-ids-and-decliner.md section 5, rule 2 ("whitespace", taken literally; a zero-width character is not whitespace, and an id made of one is a non-blank id, left to D-15)
- request: edge-ids-and-decliner

### D-34 Send reason when the decline block and a current-state rule both apply
- status: answered-by-delegate
- answer: (a) the current-state rule wins: `reverse-pending` when the reverse request is pending, `already-connected` when connected; `previously-declined` otherwise. Today's guard order, no code change.
- source: docs/product/prd/connection-requests-edge-ids-and-decliner.md section 5, rule 6 ("a reverse request is pending anyway"); D-13 (the cause that describes the present state first); D-29
- request: edge-ids-and-decliner

### D-35 Name of the blank-id reason
- status: answered-by-delegate
- answer: `blank-member-id`, the same on every operation and for either id
- source: docs/product/prd/connection-requests-edge-ids-and-decliner.md section 5, rule 1 (one reason, distinct from every existing one); D-22 (PRD vocabulary). Name: preference for a person to revisit.
- request: edge-ids-and-decliner

### D-36 Amendment of D-19 and D-26 for blank member ids
- status: answered-by-delegate
- answer: supersedes D-19 and D-26 for a blank member id only: the state query, the pending list and erase reject it with `blank-member-id` (D-35) instead of answering or succeeding. For every non-blank id D-19 and D-26 hold unchanged.
- source: docs/product/prd/connection-requests-edge-ids-and-decliner.md section 5, rule 1; section 6 (reads never rejecting and erase always succeeding change for blank ids only)
- request: edge-ids-and-decliner
