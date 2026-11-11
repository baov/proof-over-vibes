# Trim report — copro-parking test suite

**TL;DR** — "How many tests" applied to all 6 test files: 303 → 151 tests, 2 847 → 2 004 lines, mutation score unchanged, harness green, 109/109 test-cases still bridged. 

| | Before | After |
|---|---|---|
| Tests | 303 | 151 |
| Lines of tests (`tests/*.py`) | 2 847 | 2 004 |
| Mutation score (critical) | 91.3 % (188/206) | 91.3 % (188/206) |
| Harness / bridge | green / 109 ok | green / 109 ok |

## What was done (tests removed or merged)
- **Examples grouped into one parameterized test** (subtests / tables): date forms, blank values, invalid parameters, roles, unreadable files, offer/stored-check answers, etc. (~55)
- **Rules shared by several use cases tested once over a table**: role check, refusal order, blank / unknown / duplicate refusals (offer+withdraw; register, correct, remove; add+change rule), unreadable stores, "refusal leaves the file identical", "failed write" (~50)
- **Restated behavior dropped** (exercised elsewhere): domain `Register` tests duplicating use-case tests, `OfferBook.has_open_offer` unit tests (covered through the offer check), duplicated removal/renumbering offer tests (~30)
- **Pinned "how" dropped**: clock-read / load / save counts, `issubclass`, `assertIsInstance` of ports, old-signature `TypeError`, "asked once" stub counts (~15)
- Test-case front-matter repointed to the surviving tests (~45 files).

## Kept despite the doctrine
- `test_the_owner_check_states_that_a_declared_name_is_not_an_authentication`: docstring text, kept for D-46 (the limit must be written down; the test-case points to it).
- `test_the_system_clock_answers_a_date`: a type assertion, but the only test of `system_clock`.
- `assertIsInstance(..., Refusal)` / `assertNotIsInstance(..., Refusal)`: refusal vs store error is a behavior, not a hierarchy detail.
- `__cause__` / `__suppress_context__` check on the unknown-offer refusal: the test-case requires it.
- Domain return-value test in `test_register.py`: removing it dropped the score to 89.8 %.

## Ambiguities
- Rule 4 ("already exercised elsewhere") is a judgment call: mutation was the only arbiter, and it caught one over-trim (restored).
- No decision requires a call count, so every count was dropped; "withdrawal is one save" is no longer asserted.
- Some test-cases now point to a table test shared with others (e.g. blank values), so one test serves several test-cases.
