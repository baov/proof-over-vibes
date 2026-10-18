# Decision log

Append only. `answered` = a person read and answered (source: human). `answered-by-delegate` = the orchestrator relayed a role's recommendation, nobody read it; a person who later reads it supersedes it with an `answered` entry.

### D-1 Positioning
- status: answered
- answer: narrow and simple
- source: human; docs/product/research.md
- request: product

### D-2 Country / regulatory frame
- status: answered
- answer: EU, GDPR
- source: human; stated by the human
- request: product

### D-3 Purpose and price model
- status: answered
- answer: learning example; price model out of scope
- source: human; stated by the human
- request: product

### D-4 Vision success measures
- status: answered
- answer: the three proposed
- source: human; docs/product/vision.md
- request: product

### D-5 First slice
- status: answered
- answer: see / book / cancel for one practitioner, availability preloaded
- source: human; docs/product/story-map.md, slice 1
- request: product

### D-6 Roadmap horizons
- status: answered
- answer: Now = skeleton + practitioner availability; Next = data protection + reminders; Later = rescheduling (the human did not take the Product Manager's recommendation)
- source: human; docs/product/roadmap.md
- request: product

### D-7 Prioritization method
- status: answered
- answer: MoSCoW
- source: human; docs/product/backlog.md
- request: product

### D-8 Backlog items picked
- status: answered
- answer: F2.1 + F2.2, the feature "book a slot"
- source: human; docs/product/backlog.md
- request: book-a-slot

### D-9 Booking a slot in the past
- status: answered
- answer: refused
- source: human; docs/product/prd/book-a-slot.md, req 7
- request: book-a-slot

### D-10 Several bookings per patient
- status: answered
- answer: allowed, but no overlap in time (the human did not take the Product Manager's recommendation)
- source: human; docs/product/prd/book-a-slot.md, req 8-9
- request: book-a-slot

### D-11 Booking a slot the patient already holds
- status: answered
- answer: refused like any taken slot
- source: human; docs/product/prd/book-a-slot.md, req 11
- request: book-a-slot

### D-12 Architectural style
- status: answered
- answer: hexagonal
- source: human; docs/technical/adr/0001-architectural-style.md
- request: book-a-slot

### D-13 Harness blocks
- status: answered
- answer: A + B + D with PIT; download of pitest approved
- source: human; docs/technical/invariants.md
- request: book-a-slot

### D-14 Way to check the dependency rule
- status: answered
- answer: ArchUnit 1.4.1
- source: human; docs/technical/invariants.md, INV-001
- request: book-a-slot

### D-15 Sensitive zones
- status: answered
- answer: storage adapters and any exposure of booking data
- source: human; docs/technical/adr/0001-architectural-style.md
- request: book-a-slot

### D-16 Severity of the new invariant
- status: answered-by-delegate
- answer: starts in warn
- source: docs/technical/invariants.md, INV-001
- request: book-a-slot

### D-17 Pre-commit / CI file
- status: answered-by-delegate
- answer: none for this example
- source: none (role recommendation relayed)
- request: book-a-slot

### D-18 Shape thresholds
- status: answered-by-delegate
- answer: skipped (no Checkstyle download)
- source: none (role recommendation relayed)
- request: book-a-slot

### D-19 Slot starting exactly now can be booked
- status: answered-by-delegate
- answer: yes (stated by the Product Manager, not read by a person)
- source: docs/product/prd/book-a-slot.md, req 7
- request: book-a-slot

### D-20 Back-to-back slots do not overlap
- status: answered-by-delegate
- answer: confirmed (stated by the Product Manager, not read by a person)
- source: docs/product/prd/book-a-slot.md, req 10
- request: book-a-slot

### D-21 Which refusal is reported when a booking breaks several rules
- status: answered-by-delegate
- answer: single order unknown slot > past > taken (own-held included) > overlap
- source: docs/product/prd/book-a-slot.md, req 6, 7, 3, 11, 9 (the PRD gives no order; this one checks the slot alone first, then its state, then the patient's other bookings; req 11 makes an own-held slot "taken", so taken precedes overlap)
- request: book-a-slot

### D-22 Empty, blank or absent patient or slot identifiers (story 1)
- status: answered-by-delegate
- answer: deferred to a later request: no check, no test, behavior unspecified, listed out of scope
- source: docs/product/prd/book-a-slot.md, section 6 (reserved for later edge-case requests); stories.md open point 2 stays open
- request: book-a-slot

### D-23 How a caller learns a booking was refused (typed result or exception)
- status: human-needed
- answer: pending
- source: none (the PRD names the refusals, req 3, 6, 7, 9, not their form; a technical design choice)
- recommended: none from the Product Owner; to be settled by the Planner/architect in the plan
- request: book-a-slot

### D-24 Public names of the refusal reasons
- status: human-needed
- answer: pending
- source: none (the PRD names four refusal cases: taken, unknown, past, overlapping; no identifiers; a technical design choice)
- recommended: none from the Product Owner; the plan decides
- request: book-a-slot

### D-25 How a caller learns a booking was refused (supersedes D-23)
- status: answered-by-delegate
- answer: a typed result: booked (with the booking) or refused (with one reason)
- source: .plans/in-progress/book-a-slot/architect.md, 'Stories pass' lean; the Planner's recommendation (relayed by the orchestrator, nobody read it)
- request: book-a-slot

### D-26 Public names of the refusal reasons (supersedes D-24)
- status: answered-by-delegate
- answer: UNKNOWN_SLOT, PAST, TAKEN, OVERLAPPING (names fixed now; story 1 produces only TAKEN)
- source: .plans/in-progress/book-a-slot/architect.md, 'Stories pass' lean; the Planner's recommendation (relayed by the orchestrator, nobody read it)
- request: book-a-slot
