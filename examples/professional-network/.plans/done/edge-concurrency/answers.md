---
role: product-owner
status: done
reasons: []
---

# Answers to the Planner (edge-concurrency)

All `answered-by-delegate`, recorded in `docs/business/decisions.md`.

- **Q1 who wins** -> D-37: unspecified; either sequential order is correct, tests check the result equals one of them (also for erase and for read against write).
- **Q2 an operation throws** -> D-38: its caller sees the same error unchanged, queued operations run normally, the failed one wrote nothing; no new rejection reason.
