---
role: orchestrator
status: done
reasons: []
---

# Brief: S4 A space with an open offer cannot be removed or renumbered

- Type: prompt (no ticket). Story S4 of `../stories.md`; acceptance criteria are those of S4 there (including AC6, D-57). Architecture: `../architect.md` (OfferCheck port, StoredOfferCheck adapter, `remove_space` and `change_space_number` take it; two breaking signature changes) and ADR-0001..0004. Decisions: `docs/business/decisions.md` (D-45..D-68).
- Constraints: Python 3.14, stdlib `unittest`, offline; run `bash tools/harness/run_all.sh` before handing over.
- Sensitive zones: the manager-only role check, the offers write path, and the fail-closed `OfferCheck` call in `remove_space` and `change_space_number` (invariants.md). A diff touching them escalates to the human.
- Iteration counter: 0 / limit 5.
- Carried over (open majors, reviews 06 to 08):
  - M1: orphan offers (space gone from the register) reappear under another owner, or block a re-registered number. This story closes it by blocking removal and renumbering; the plan must also say what happens to orphans that already exist in a stored file (S1 to S3 allowed them), as a question if undecided.
  - M2 of review 08: an unknown offer versus an unreadable register on withdrawal (offers are read before the register) is decided by no document and pinned by no test. Plan a decision (ask the human with a recommendation) and a test, and the test-case text aligned.
  - Minors to take: `from None` on the orphan/unknown offer refusal so the cause chain does not differ (review 08 m3); the order of "blank offerer" vs "bad number" in withdrawal may go in the same decision line (m1).
