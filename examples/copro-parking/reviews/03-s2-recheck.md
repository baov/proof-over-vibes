---
role: reviewer
status: escalate
verdict: GO
reasons:
  - gauntlet green; M1 (natural_key raw ValueError on digit-like characters) closed, verified by own probes; D-20/D-22 ordering unchanged; no blocking or major finding left
  - escalate: S2 as a whole touches the sensitive zones (manager-only check, JSON read path, listing sort); the human confirms
severity: minor
open_majors: []
---

# Review 2: S2 recheck after the M1 fix (iteration 1)

Skill `premerge-review`, criticality critical. Scope: the iteration-2 change (`domain/text.py`, new test `SuperscriptDigits`) on top of the S2 changes already reviewed in review-1. Nothing committed, working tree reviewed.

## Gauntlet (run by me)
- `python3 -m unittest discover -s tests`: 54 OK.
- `bash tools/harness/run_all.sh`: exit 0, 22/22 test-cases covered, 0 orphan tests.
- Mutation `--scope critical`: 89.1% (41/46); the 5 survivors are the known equivalents from review-1 (`frozen=True` x4, `indent=2`).

## M1 probe (own scripts, real JSON repository)
- The fix: digit runs are now the odd positions of `re.split(r"(\d+)")`, so the split alone decides what is a number; `isdigit()` is gone.
- Register, correct and list with identifiers, numbers and owners `²`, `P1²`, `①`, `P①`, `½`, `P¹0`, Arabic-Indic `٣`/`P٣`/`P٢`, Tamil `௧`, fullwidth `P１２`: no error, listing returned, text stored as typed.
- Hand-written stores holding `²`, `P1²`, `٣`, `P٣` as lot identifier: `list_register` reads and lists them.
- Arabic-Indic and fullwidth digits are matched by `\d` and compared as numbers (`int` accepts them): consistent, no crash.

## Regression D-20/D-22
- Lots `A12, a2, B1, a10, A02` list as `a2, A02, a10, A12, B1` (ties in registration order); spaces `P10, P9, p2, P02, p1` list as `p1, p2, P02, P9, P10`; after `P9 -> P100` the order follows. Duplicates (`a2 `, `P2 `) still refused. Unchanged.

## Findings
- **minor m4** `domain/text.py:23` · angle: bugs. A digit run longer than 4300 digits (Python's int-string limit, 3.11+; probed on 3.14.7) still raises a raw `ValueError` from `int(p)`: `register_lot` with 5000 digits and `register_space` with `P` + 4301 digits crash in `save`, and a hand-written store holding one would crash `list_register`. Same class as M1 but only reachable by an absurd input; I rate it minor for that reason (hesitating with major, lower level kept). Recommendation: compare digit runs without `int` (e.g. `(len(p.lstrip("0")), p.lstrip("0"))`) or bound the length; the next planner may fold it into a decision on maximum length.
- m1, m2, m3 of review-1 stand unchanged (history not verifiable, `StoreUnreadable` naming, `OSError` on read not converted).

## Compliance
ADR layers untouched (domain only, harness green); no new behavior, no test-case change needed.

Verdict: GO (no blocking, no major left), status `escalate`: S2 as a whole touches sensitive zones, the human confirms.
