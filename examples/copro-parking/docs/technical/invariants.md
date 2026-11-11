# Executable invariants

Rules made mechanically verifiable. Run everything: `bash tools/harness/run_all.sh` (exit 1 = an `error` violation, 2 = `warn` only). Self-tests of the scripts: `python3 -m unittest discover -s tools/harness/selftest`.

| ID | Statement | Severity | Status |
|----|-----------|----------|--------|
| INV-001 | Imports point inward only (ADR-0001) | warn | active |
| INV-002 | Every test-case points at a real test, every test has a test-case | warn | active |
| INV-003 | A function has at most 40 lines | warn | active |
| INV-004 | A function has a cyclomatic complexity of at most 10 | warn | active |
| INV-005 | A function nests at most 4 levels deep | warn | active |
| INV-006 | A function has at most 5 parameters | warn | active |
| INV-007 | The mutation score of the critical scope does not regress | 90 (warn) | active |

All start in `warn`: they move to `error` only when the humans decide.

## INV-001 — Dependency rule

- **Status**: active
- **Statement**: `domain` imports only the standard library and no I/O module; `application` imports `domain` and the standard library; `infrastructure` may import both; `tests` are free.
- **Source**: ADR-0001
- **Script**: `tools/harness/check_layers.py` (`--explain`)
- **Severity**: warn
- **Remediation**: define the need as a port (abstract interface) in `application`, implement it in `infrastructure`.
- **Example violation**: `src/copro_parking/domain/register.py`: `import json`
- **Fix**: move the file access to `infrastructure/json_repository.py` behind the repository port.

## INV-002 — Test-case bridge

- **Status**: active
- **Statement**: each `docs/business/test-cases/**/*.md` carries a front-matter whose `automated_test` names an existing test; no test file lacks a test-case.
- **Source**: harness block B
- **Script**: `tools/harness/check_test_coverage.py`
- **Severity**: warn
- **Remediation**: write the test and fill `automated_test` (`tests/test_x.py::TestClass.test_name`), or set `status: pending` / `manual`.
- **Limit**: checks that a test exists, not what it is worth (see INV-007).

## INV-003 to INV-006 — Function shape

- **Status**: active
- **Statement**: functions under `src/` stay within 40 lines, complexity 10, nesting depth 4, 5 parameters (`self`/`cls` excluded).
- **Source**: harness block A, shape thresholds (tangled code costs agents repeated passes)
- **Script**: `tools/harness/check_shape.py`
- **Severity**: warn
- **Remediation**: extract helpers, use guard clauses, group parameters in a value object.

## INV-007 — Mutation score (critical scope)

- **Status**: active
- **Statement**: the mutation score of `domain`, `application` and `infrastructure` does not fall below the baseline.
- **Source**: harness block D
- **Scope**: `src/copro_parking/{domain,application,infrastructure}`
- **Script**: `python3 tools/harness/run_mutation.py --scope critical [--threshold N]` (`--scope diff` before a merge)
- **Tool**: home-made, standard library only (`ast` mutations + `unittest`). `--explain` lists what it can and cannot see: equivalent mutants count as survivors; removed statements, messages and crash-in-the-middle atomicity are invisible.
- **Severity**: none for now
- **Baseline**: 90.6% after S3 (critical scope, 5 equivalent survivors). Threshold set to 90, as `warn`, by the human.
- **Remediation**: for each survivor, add a test expressing the unprotected behavior; never a test written only to kill it, never a lowered threshold.

## Sensitive zones

- `application` role check on every write use case (manager only, ADR-0003): security, a missed check lets any role edit the register.
- `infrastructure` JSON repository write path (temp file + `os.replace`, ADR-0002): data, a non-atomic write corrupts or half-applies the only copy of the register.
