---
role: product-owner
status: done
reasons: []
---

# Answers to the Planner (story 1)

All `answered-by-delegate`, recorded in `docs/business/decisions.md`.

- **Q1 member id validity** -> D-15: option (c), leave undefined, nothing tested. Deliberate deferral to a later edge-case request; still listed under Open points of stories.md. Drop B20 to B23 and Step 9's part for Q1.
- **Q2 unknown request id on accept** -> D-16: rejected with its own reason `request-not-found`, state unchanged. Source: PRD rule 7.
- **Q3 state shape** -> D-17: connected (yes or no) and request state only. Source: PRD rule 5, D-11.
- **Q4 pending list order** -> D-18: oldest first. Source: none in the PRD; consistent with D-12's creation order.
- **Q5 state of the same member twice** -> D-19: "none, not connected", no rejection. Source: PRD rules 5 and 8.
