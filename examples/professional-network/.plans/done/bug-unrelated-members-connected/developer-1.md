---
role: developer
status: done
reasons: []
---

# Developer, iteration 1: unrelated members shown as connected

Skills applied: `plan-driven-dev` (implementation steps, the diagnostician's proof standing in for the plan) and `behavior-driven-testing`. No plan.md, no deviation.

## Commits

- `cab6193` Connections: failing tests for member ids that look alike once joined (red; 2 tests + 2 test-case files)
- `e93ab41` Connections: key stored connections by an unambiguous pair, not a colon-joined string (green)

## What was done

- Tests (`tests/connections/colliding-member-ids.test.ts`, through the public module only):
  1. After `ann:bo`/`cy` connect, the pair state of (`ann`, `bo:cy`) is `none` in both argument orders, and `ann` can send to `bo:cy` (pending). The first pair stays connected.
  2. The open major of the proof review: both colliding pairs connected (both requests sent, then both accepted), erase `ann:bo`: (`ann:bo`, `cy`) has no state, (`ann`, `bo:cy`) stays connected.
- Red confirmed on HEAD for the right reason (`connected: true` for the unrelated pair; the erased pair still connected).
- Business test-cases: `docs/business/test-cases/connections/colliding-ids-unrelated-members.md` and `colliding-ids-erase-keeps-other-pair.md` (source: bug brief + D-15 / D-26, `automated_test` exact, `status: covered`).
- Fix, one function in `src/connections/infrastructure/in-memory-store.ts`: `pairKey` is now `JSON.stringify([a, b].sort())` instead of `[a, b].sort().join(":")`.
  - Encoding chosen: JSON array of the sorted pair. Technical choice, unobservable from outside. Unambiguous for any string (quoting and escaping make the boundary between ids explicit), keeps the O(1) lookup that commit `347911f` wanted, and is a one-line change. A different separator would not close the collision; a nested map would be a larger change for no gain; the default `sort()` is consistent for any string (UTF-16 code-unit order), so (A, B) and (B, A) still share a key.
- The second symptom (later connection overwriting the earlier one, erase leaving a pair connected) disappears with the same fix: each pair now has its own key.

## Behaviors added

None. No public behavior, error type or interface changed; ids stay unvalidated (D-15).

## Commands and results

- `npm test`: 11 files, 88 tests passed (was 86; +2).
- `npm run typecheck`: no error.
- `npm run harness`: check_layers 0, check_shape 0, check_test_coverage 87 test-cases, 87 covered_ok, 0 broken, 0 orphan; check_serialized 0.
- `npm run harness:selftest`: 6 tests, 6 pass.
- Repository: `python3 tools/validate-skills.py --root .` no violation; `tools/check-glossary.sh` OK.
- `npm run mutation` (scope critical): **90.1% (145 killed / 161 generated)**, threshold none. Unchanged by the fix.

## Mutation: where the score stands

All 16 survivors are `NoCoverage` in `src/connections/domain/connection.ts` (`connects()`, lines 12 and 14). That function is dead code since `347911f` (the store no longer calls it; no other usage in `src` or `tests`), which explains the drop to 90.1%: the 16 mutants are on code nothing runs, not on an unprotected behavior. Excluding or removing them is not done here: removing `connects` (dead code) would restore the score (145/145 of the live mutants) but is outside the diagnosis, and I did not touch `stryker.config.mjs` or write any threshold. Suggested follow-up for the human/orchestrator: delete `connects()` in a separate cleanup commit. Setting the threshold stays a human decision.
