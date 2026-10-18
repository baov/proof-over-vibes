---
role: harness-engineer
status: done
reasons: []
---

# Harness engineer note: price a cart

Skill applied: `codebase-harness`, blocks A, B and D (human: A+B+D; delegate: ArchUnit in profile `invariants`, all `warn`, no shape thresholds, PIT on `domain`+`application` without threshold, AGENTS.md + one-line CLAUDE.md, no pre-commit/CI file).

## Written

- `pom.xml`: Kotlin 2.2.0 / JDK 21, kotlin-stdlib, kotlin-test, junit-jupiter 5.12.2, ArchUnit 1.4.1, PIT 1.20.1 (not bound to the lifecycle), profile `invariants`. Base package `io.example.mealcart` (`base.package`), a choice of the harness: the architect did not name one.
- `src/test/kotlin/io/example/mealcart/ArchitectureTest.kt`: INV-001 to INV-004.
- `tools/harness/`: `check_layers.py` (INV-001..004), `check_test_coverage.py` (INV-005, Kotlin layout), `run_mutation.sh` + `_pit_report.py` (INV-006), `run_all.sh`, `_maven.sh`. Adapted from the Java sibling, which is untouched.
- `docs/technical/invariants.md` (six invariants, all `warn` except a broken test-case reference, and the `Sensitive zones` section: money computation and rounding, `domain.money` and `domain.pricing` with their tests).
- `AGENTS.md` (Harness section), `CLAUDE.md` (`@AGENTS.md`).
- "Associated executable invariants" line appended to ADR-0001 and ADR-0002.

## Verified (offline, on a throwaway fixture in the scratchpad, never in the project)

- Empty project: INV-001..004 pass vacuously, `run_all.sh` exits 0.
- Fixture with violations: every rule fires with `path:line: [INV-NNN] message -- remediation` (adapter import, `Math.round`/`floor` outside money, `Double`/`BigDecimal`, `Instant.now`, `System.getenv`), exit 2. A clean fixture (rounding via `floorDiv` inside `domain.money`) passes, exit 0.
- `mvn test` (default build) compiles Kotlin and runs JUnit tests; `ArchitectureTest` excluded.
- INV-005: ok / broken reference (exit 1, message) on fixture test-cases.
- INV-006: `critical` and `diff` scopes run and report a score and the survivors.
- Kotlin bytecode noise in PIT: on the small fixture, none seen (no null-check intrinsic mutants, none unviable); survivors were real gaps. To re-check on the real code (inline functions, data-class `copy`, `when` on sealed types).

## Could not verify / limits

- Not exercised on real code (none exists). Mutation threshold and baseline are unset (human decision).
- INV-002 sees API calls only, not hand-written integer rounding outside `domain.money`; it checks the package, not "one function". INV-003 misses a `Double` local that is never passed or called. Both documented in `invariants.md`.
- Stale classes: after deleting a Kotlin source, run `mvn clean` once, else `target/classes` keeps the old class and the rules still see it.
- No `.pre-commit-config.yaml`/CI file written (parent repository). `docs/business/test-cases/` does not exist yet; INV-005 reports it and exits 0.
- B: test-cases are written by whoever documents the behavior (planner/cartographer), with `source` and `automated_test`.
