---
role: developer
status: done
reasons: []
---

# Developer, iteration 2: fix M1 (natural_key crash on "²")

- Cause: `natural_key` split on `\d+` but tested `p.isdigit()`; "²" is `isdigit()` but not `\d`, so `int("²")` raised a raw `ValueError`.
- Red first: new test `tests/test_use_cases.py::SuperscriptDigits` (register lots "P1²", "²", "P2" and spaces "S1²", "S1", then list) failed with `ValueError: invalid literal for int() with base 10: '²'`.
- Fix (`domain/text.py`): digit runs are the odd positions of the `re.split` result, so the split alone decides what is a number. Green; D-20 and D-22 behavior unchanged (stable sort, same keys for ordinary text).
- Results: 54 unit tests green; `run_all.sh` exit 0, 22/22 test-cases covered (no test-case change needed); mutation critical 89.1% (41/46), same 5 equivalent survivors as before.
- Behaviors added: none. Nothing else touched; no git.
