---
role: developer
status: done
reasons: []
---

# Developer, iteration 1: blank member ids and the decliner writing back

I applied `plan-driven-dev` (implementation steps) and `behavior-driven-testing`, following plan.md step by step. Every step ended green (`npm test`, `npm run typecheck`, `npm run harness`).

## Commits (examples/professional-network)

1. `daa394a` reads and erase return a result; tests read them through `stateOf` / `pendingOf` (step 1, no behavior change)
2. `6d399e3` reject a send with a blank member id before any other rule (step 2)
3. `3a6d0ef` accept, decline and withdraw by a blank member rejected before the request lookup (step 3)
4. `1629be8` state queries, pending lists and erasure rejected for a blank member id (step 4)
5. `91d996c` blank means Unicode whitespace only; zero-width characters are not blank (step 5)
6. `5cfd186` the decliner writing back pinned down by tests and test-cases only (step 6)
7. `727e21a` the blank member id reason is distinct from the others (step 7)

Test-case files (step 8) were written in the same commit as their test, because `check_test_coverage` fails on an orphan test: 23 files, all `status: covered`, none pending, the exact `it()` names of the plan.

## Final gauntlet

- `npm test`: 74 tests green. `npm run typecheck`: clean. `npm run harness`: 0 violations, 73 test-cases covered_ok, 0 orphan. `npm run harness:selftest`: 5 pass, 0 fail.
- `npm run mutation` (critical scope): **100.0% (161 killed / 161 generated), no survivors**. The `domain/send-rules.ts:29` survivor is gone: I also checked by hand that replacing `r.sender === c.sender` by `true` makes 7 decliner tests fail. No threshold written (human decision, INV-010; the run says "no threshold yet").

## Notes for the reviewer

- Case (b) (C1 to C7) was green at once without production code, as the plan expected (characterization tests); their strength is shown by the mutation above, not by a red phase.
- Deviation from a technical choice of the plan (structure only, not visible to a caller): `isBlankMemberId` uses `/^\p{White_Space}*$/u`, not `trim() === ""`. `trim()` also strips U+FEFF (zero-width no-break space), which would make that id blank against D-33 ("zero-width and invisible characters are not blank"). A test covers U+200B, U+200D, U+2060, U+FEFF.
- The blank check is one shared helper `application/blank-ids.ts` called as the first lines of the seven use cases. The domain transitions are untouched.
- Sensitive zone `src/connections/index.ts`: result shapes of `getPairState`, `listPendingRequests`, `eraseMember` changed (accepted by the orchestrator, see answers.md); human review before merge.
- `support.ts` helpers `stateOf` / `pendingOf` throw on a rejection (like `sendOrFail`).

## Behaviors added

None beyond the plan. Visible to a caller, all stated by the plan: `blank-member-id` on the seven operations; the three new result shapes; `EraseResult` type exported from `application/erase-member.ts` (used only by `index.ts`; not re-exported from the module's public surface).

## Not touched

docs/product, decisions.md, tools/harness, stryker.config.mjs, the plan.
