---
role: orchestrator
status: done
reasons: []
---

# Metrics: bug, two unrelated members shown as connected

- first-review-go: yes (the proof: GO; the fix: GO at iteration 0)
- iterations: 0 NO-GO (1 review of the proof, 1 review of the fix)
- failure-analyst-ran: no
- escalated: yes, by the Reviewer (sensitive zone: the store). Review pending a person
- delegated-decisions: 0
- pending-decisions: 0
- sensitive-zones: declared
- open-majors: 1 carried (an operation that never settles blocks the module), not from this bug
- mutation: 90.1% (145/161). The 16 survivors are all NoCoverage on `connects()`, dead code since the regression; not changed by the fix
- regression: this bug IS a planted regression (commit 347911f, no run of the organization produced it); it is linked to no earlier merge request on purpose
