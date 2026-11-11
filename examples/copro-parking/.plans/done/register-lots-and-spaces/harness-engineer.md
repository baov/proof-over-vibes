---
role: harness-engineer
status: done
reasons: []
---

# Harness engineer: register lots and spaces

Skill `codebase-harness` applied to an empty project. Python 3.14.7 checked; stdlib only. Everything below starts in `warn` (exit 2); nothing is wired into pre-commit or CI (proposal only, no hook exists).

## Delivered (`tools/harness/`)
- `check_layers.py` (INV-001): ADR-0001 dependency rule via `ast`, including imports inside functions and relative imports; domain bans I/O modules and non-stdlib, application bans infrastructure.
- `check_shape.py` (INV-003..006): lines 40, complexity 10, nesting 4, parameters 5.
- `check_test_coverage.py` (INV-002): block B starter, narrowed to `tests/**/test_*.py`. No test-case exists yet, so it passes with a note; the front-matter (`feature`, `type`, `priority`, `automated_test`, `status`) is for the planner/developer to write with each test-case.
- `run_mutation.py` (INV-007): stdlib mutation script (operators flipped, `and/or`, `not`, booleans, `+/-`, int constants, `return None`, `if` negated). Scopes `critical` (domain, application, infrastructure) / `diff` / `full`. Its `--explain` states its blind spots: equivalent mutants count as survivors; removed statements, messages, and crash-mid-write atomicity are invisible. No baseline until code exists.
- `run_all.sh`, and `selftest/test_harness.py` (10 tests, passing, incl. a weak suite leaving survivors and a strong one killing all).
- `docs/technical/invariants.md` with `Sensitive zones`: the role check on writes (ADR-0003) and the JSON store's atomic write (ADR-0002). `AGENTS.md` got a short Harness section.

## Answered myself (cheap to reverse)
- Blocks A, B, D enabled; C (doc-gardening) not set up (no scheduler, nothing to garden yet).
- Severity `warn` everywhere (skill default); shape thresholds are the skill's defaults.
- Mutation scope `critical` as above; no threshold until a baseline is measured.
- Manager-only check has no script (no code to scan yet): it is guarded by sensitive-zone review and mutation testing. A future invariant could assert that every write use case takes a role, once names exist.

## Open
No question blocks the work. For the product owner, later: when to move INV-001 to `error` (suggest once the first story merges with zero violations).
