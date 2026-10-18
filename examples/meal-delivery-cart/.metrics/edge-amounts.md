---
role: orchestrator
status: done
reasons: []
---

# Metrics: edge cases, amounts (negative, too large, rate scale)

- first-review-go: yes (verdict GO at iteration 0)
- iterations: 0 NO-GO (1 review)
- failure-analyst-ran: no
- escalated: yes, by the Reviewer (the diff touches the declared money sensitive zone). A person's review is pending
- delegated-decisions: 3 in this request (D-42 to D-44, `answered-by-delegate`); human answers D-37 to D-39
- pending-decisions: 0
- sensitive-zones: declared
- open-majors: 0. Minors: the exception message is built eagerly (about 110 ns per successful addition); the plan file was not brought up to date (checkboxes, a wrong test count); no mutation baseline for a person to accept (81.3 percent raw, 61 of the 62 non-equivalent mutants killed)
- mutation: 81.3% (61/75), scope critical, no threshold; 12 of the 14 non-killed mutants are equivalent (10 null-check intrinsics, a dead inline body, a stdlib shortcut pair), one is the carried Percentage.getScale
- regression:
