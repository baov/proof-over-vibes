---
role: product-owner
status: done
reasons: []
---

# Answers to the Planner (story 1)

- **Q1 How a caller learns a booking was refused** (D-23): escalate. The PRD says what is refused (req 3, 6, 7, 9) and that a refusal changes nothing (req 12), not its form. This is a technical design choice, for the plan or the architect, not for the Product Owner.
- **Q2 Public names of the reasons** (D-24): escalate, same reason. Only the business cases are sourced: taken (req 3, 11), unknown (req 6), past (req 7), overlapping (req 9). Story 1 itself only needs "taken".
- **Q3 Empty, blank or absent identifiers** (D-22, answered-by-delegate): option (a). Deferred to a later request: no check, no test, behavior unspecified, out of scope. Source: PRD section 6. It stays under Open points of stories.md (point 2).

## Update (orchestrator relay)

- **Q1, D-25 (answered-by-delegate, supersedes D-23):** a typed result, booked (with the booking) or refused (with one reason). Source: architect.md 'Stories pass' lean and the Planner's recommendation.
- **Q2, D-26 (answered-by-delegate, supersedes D-24):** UNKNOWN_SLOT, PAST, TAKEN, OVERLAPPING; names fixed now, story 1 produces only TAKEN. Same source.
