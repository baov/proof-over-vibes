---
role: harness-engineer
status: done
reasons:
  - "Blocks A, B, D installed; every invariant starts in warn. No hook or CI file written (the example lives inside a parent repository)."
---

# Harness engineer: connection requests

Answers applied (all by delegate, recommended options): blocks A + B + D; custom checks on the TypeScript compiler, no new dependency; sensitive zones declared; Stryker as mutation tool (core + vitest-runner); no hook or CI file, only npm scripts; `AGENTS.md` Harness section and one-line `CLAUDE.md` written.

## What exists now

- `package.json`, `tsconfig.json`, `vitest.config.ts` (no test yet: passes with no test), `package-lock.json`. Dev dependencies: `typescript` (~6), `vitest`, `@stryker-mutator/core`, `@stryker-mutator/vitest-runner`. Nothing else.
- `docs/technical/invariants.md`: INV-001 to INV-004 (ADR-0001 dependency rule), INV-005 to INV-008 (function lines 40, complexity 10, nesting 4, parameters 5), INV-009 (test-case bridge), INV-010 (mutation score, no threshold yet). All `warn`, except a broken test-case reference, which is `error`. Section `Sensitive zones` declared: infrastructure and repository ports (personal data, erasure), the future `data-rights` module, the public entry points `src/*/index.ts`.
- `tools/harness/`: `check_layers.mjs`, `check_shape.mjs`, `check_test_coverage.mjs`, `run_mutation.sh` + `mutation_report.mjs` + `mutation-threshold.json`, `run_all.sh`, `lib.mjs`, `selftest.test.mjs`. Each check honors `--explain`, `--root`, the `path:line: [INV-NNN] message — remediation` format and exit codes 0/1/2.
- `stryker.config.mjs`: scope `src/connections/domain` and `application`, default mutators, no blocking threshold, incremental on.
- `AGENTS.md` (Harness section) and `CLAUDE.md` (`@AGENTS.md`).
- npm scripts: `npm run harness`, `harness:selftest`, `mutation`, `mutation:diff`, `test`, `typecheck`.

## Verified

- `npm run harness:selftest`: 5 tests pass (clean module passes; each ADR-0001 branch is caught with its id; the four shape thresholds fire and clean code passes; the bridge sorts ok/broken/pending/orphan; mutation score, threshold and exit codes). Fixtures are throwaway files in the OS temp folder, never project code.
- `run_all.sh` on the empty project: exit 0.
- The mutation wrapper ran end to end with real Stryker on a scratch project outside the repository (a domain file and its test): it produced the report, the normalised output and the surviving mutants.

## Not verified

- The `--scope diff` run: it stopped at "No tests were executed" because the only changed file had no test; the wrapper reports that clearly, but the nominal diff run is not proven.
- No mutation baseline exists (no code): `mutation-threshold.json` holds `null`. First run, after the first tests: record baseline, date and sha, and set the threshold to the baseline rounded down (a human decision).
- No false-positive check on real feature code (there is none). Expect to tune the layer and shape checks at the first real run; a false positive is a bug in the check, not in the code.
- Stryker on this exact project tree (no source yet) and `tsc --noEmit` (no input yet).

## Needs a decision

- Settled: test-cases live in `docs/business/test-cases/` (constant kept).
- TypeScript is pinned to `~6` on purpose: version 7 (native compiler) only offers an unstable API, and the checks use the compiler API. Moving to 7 later is a harness change.
- Settled: ADR-0001 now carries "Associated executable invariants: INV-001 to INV-004".
- Nothing to add to `.gitignore`: `node_modules/`, `reports/`, `.stryker-tmp/` are already ignored. Commit `package-lock.json`.

## For the implementer

The checks start in `warn` and flag nothing today. Run `npm run harness` before each commit. `@types/node` is not installed and `tsconfig` has `types: []`: the domain needs no Node API, and an infrastructure adapter that does must raise it as a dependency question.

I fixed no code, wrote no production code, and made no commit.
