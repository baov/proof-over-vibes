---
role: harness-engineer
status: done
reasons: []
---

# Harness engineer note: book a slot

Blocks installed: A (INV-001), B (INV-002), D (INV-003). Block C (doc-gardening) not enabled. Everything runs on an empty codebase and passes vacuously; the checks were exercised on throwaway fixtures only.

## Written

- `pom.xml`: ArchUnit 1.4.1 (test), PIT 1.20.1 + pitest-junit5-plugin 1.2.2 (downloaded from Central through Maven, as approved, nothing else), property `base.package` (`io.example.medical`, a placeholder the planner can change together with `ArchitectureTest`), profile `invariants`.
- `src/test/java/io/example/medical/ArchitectureTest.java`: the three ADR-0001 rules (test code, not feature code). Excluded from the default `mvn test` and from PIT; run by the harness.
- `tools/harness/`: `check_layers.py` (INV-001, severity `warn`, exit 2), `check_test_coverage.py` (INV-002, starter adapted to the Maven layout, `ArchitectureTest` excluded as a technical test), `run_mutation.sh` + `_pit_report.py` (INV-003, scopes critical/diff/full, normalized output), `run_all.sh` (`--with-mutation`), `_maven.sh`.
- `docs/technical/invariants.md` (3 invariants + `Sensitive zones`: storage adapters; any exposure of booking data), `AGENTS.md` (Harness section), `CLAUDE.md` (`@AGENTS.md`), line "Associated executable invariants: INV-001" in ADR-0001.
- No pre-commit or CI file (decision: this example sits inside a parent repository).

## Verified (on throwaway fixtures in the scratchpad, never in the project)

- Fixture with a domain class importing `adapters` and `javax.swing`, and an application class importing `adapters`: INV-001 reports each with file:line and remediation, exit 2; clean fixture exit 0; a compile error is reported as "could not run", exit 1, never as a pass.
- Fixture test-cases: covered_ok, covered_broken (exit 1), pending and orphan (exit 2); `ArchitectureTest` not counted as orphan.
- PIT on a fixture class with a deliberately weak test: score 60% (3/5), two survivors listed; scopes critical, full and diff (diff picks only changed domain/application classes); report with a threshold below/above gives exit 2 or 1 / 0.
- On the real (empty) project: `run_all.sh --with-mutation` exits 0, also with `MVN_OFFLINE=1`.

## Not verified / limits

- Real business behavior: no production code exists, so nothing real was checked and no mutation baseline exists.
- INV-001 passes vacuously until code exists; a wrong base package would not be noticed (documented in invariants.md).
- Block B reports a missing `docs/business/test-cases/` and exits 0; the cartographer must create the folder and front-matter.
- INV-001 stays `warn` per the role file: no one has decided to promote it to `error`; neither CI nor pre-commit runs it.
- Shape thresholds skipped (no Checkstyle/PMD). Not run: PIT `diff` against a real `origin/main` (tested against a local merge-base only).

## Open for humans

- Mutation threshold (after the first baseline), promotion of INV-001 to `error`, and whether to wire a CI job.
