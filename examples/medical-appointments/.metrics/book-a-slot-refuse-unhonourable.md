---
role: orchestrator
status: done
reasons: []
---

# Metrics: book a slot, story 2 (refuse-unhonourable)

- first-review-go: yes (verdict GO at iteration 0)
- iterations: 0 NO-GO (1 review)
- failure-analyst-ran: no
- escalated: yes, by the Reviewer (the diff touches the bookings storage adapter, a declared sensitive zone). Acknowledgment pending a person
- delegated-decisions: D-29 in this story (`answered-by-delegate`); human answers D-27 and D-28
- pending-decisions: 0
- sensitive-zones: declared
- open-majors: 0 (the two majors carried over from story 1 are closed: atomicity proven by a test that fails without the lock, unknown slot now a refusal)
- mutation: 100.0% (18/18), scope critical, no threshold; the lock lives in `adapters`, outside the mutation scope, and is covered by the behavior tests only
- regression:
