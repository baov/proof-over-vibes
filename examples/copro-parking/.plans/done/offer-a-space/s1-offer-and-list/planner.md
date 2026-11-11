---
role: planner
status: done
reasons: []
---

# Planner: S1 Offer and list

Draft plan in `plan.md` (6 steps). Q1-Q3 answered by delegate (A each): D-59, D-60, D-61. Load-time overlap check moved from S1 to S2 (technical choice, listed for the reviewer).

- Q1: A blank, missing or non-text offerer name or space number in an offer request: which refusal, at which rank?
  - A (recommended): invalid input, `BlankValueRefused` (D-12), same rank as a bad period, before unknown space and owner.
  - B: blank space is "unknown space", blank offerer is "not the owner".
- Q2: Which date forms are accepted?
  - A (recommended): a `date` (a `datetime` refused) or text `YYYY-MM-DD`, surrounding spaces ignored; anything else is an invalid date.
  - B: same without trimming text.
  - C: also other ISO forms (`20261105`).
- Q3: Number of the first offer (the number shown in the list and used later to withdraw)?
  - A (recommended): 1, then 2, 3, never reused.
  - B: 0.
