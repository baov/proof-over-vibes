# Executable invariants

Architecture and quality rules made mechanically verifiable. Each has an immutable ID, a script that checks it, and an actionable remediation.

Run every check: `bash tools/harness/run_all.sh` (add `--with-mutation` for INV-003, which takes longer). Maven is found on the PATH, in `$MVN_CMD`, or under `~/.m2/wrapper/dists`.

| ID | Statement | Severity | Status |
|----|-----------|----------|--------|
| INV-001 | `domain` imports only the JDK; `application` depends on `domain` only; nothing in them imports `adapters` | warn | active |
| INV-002 | Every business test-case points at an automated test that exists, and every test has a test-case | warn (broken reference: error) | active |
| INV-003 | Mutation testing covers `domain` and `application`; no threshold yet | warn | active |

---

## INV-001 — Hexagonal dependency rule

- **Status**: active
- **Statement**: in the base package, `domain` depends on nothing but `java.*`, `application` depends on `domain` (and the JDK) only, and no class in `domain` or `application` depends on `adapters`.
- **Source**: ADR-0001, "Dependency rule"
- **Script**: `python3 tools/harness/check_layers.py` (runs the ArchUnit rules of `src/test/java/io/example/medical/ArchitectureTest.java` through Maven, profile `invariants`; excluded from the default `mvn test`)
- **Severity**: warn (the script exits 2). Moving it to `error` is a human decision: change `SEVERITY` in `check_layers.py` and this entry in the same commit.
- **Remediation**: when `domain` or `application` needs something from outside, define a port (an interface) in `application`, and implement it in `adapters`. Never import `adapters` from `domain` or `application`, and never import a library into `domain`.
- **Example violation**:
  ```java
  package io.example.medical.domain;
  import io.example.medical.adapters.InMemoryStore;   // domain depends on adapters
  ```
- **Fix**:
  ```java
  package io.example.medical.application;
  public interface SlotStore { /* port owned by application */ }
  // io.example.medical.adapters.InMemoryStore implements SlotStore
  ```
- **Known limit**: the base package `io.example.medical` is named in `pom.xml` (`base.package`) and in `ArchitectureTest`. On an empty codebase the rules pass vacuously; a wrong package name would keep them passing. Change both places together if the package changes.

## INV-002 — Test-case bridge

- **Status**: active
- **Statement**: each test-case under `docs/business/test-cases/` carries a front-matter (`feature`, `type`, `priority`, `automated_test`, `status`) whose `automated_test` (`src/test/java/<path>/<Class>Test.java::<method>`) exists; each test class has a test-case, except the technical tests listed in the script (`ArchitectureTest`).
- **Source**: harness block B
- **Script**: `python3 tools/harness/check_test_coverage.py`
- **Severity**: error for a broken reference or malformed front-matter (exit 1); warn for a pending test-case or an orphan test (exit 2)
- **Remediation**: fix the `automated_test` field, or set `status: pending` if the test was deleted on purpose; write the missing test-case for an orphan test.
- **Example violation**: `automated_test: src/test/java/.../BookSlotTest.java::refusesTakenSlot` while that method no longer exists.
- **Fix**: restore or rename the test, then correct the reference.
- **Known limit**: it checks that a test exists, not what it is worth (that is INV-003). Until `docs/business/test-cases/` exists the script reports it and exits 0.

## INV-003 — Mutation testing on the domain and application

- **Status**: active
- **Statement**: mutants injected into `domain` and `application` are killed by the tests; the share killed is measured, and must not regress once a threshold is set.
- **Source**: harness block D, scope approved by the human: `domain` and `application` packages
- **Scope**: `io.example.medical.domain.*` and `io.example.medical.application.*` (property `pit.targetClasses` in `pom.xml`); `diff` and `full` scopes exist in the script
- **Script**: `bash tools/harness/run_mutation.sh --scope critical|diff|full`
- **Tool**: PIT 1.20.1 with pitest-junit5-plugin 1.2.2 (pom.xml); parsable report `target/pit-reports/mutations.xml`, readable report `target/pit-reports/index.html`. Default mutators. `ArchitectureTest` is excluded.
- **Severity**: warn, once a threshold exists
- **Threshold**: none yet (human decision)
- **Baseline**: not measured (no production code yet). To record, with date and sha, after the first feature lands.
- **Remediation**: for each surviving mutant, find the unprotected behavior and add a test that states it. Never add a test whose only purpose is killing the mutant; if the mutant matches no behavior that counts, exclude it in `pom.xml` with a comment explaining why. Never lower a threshold to get back to green.
- **Not in pre-commit**: a run takes minutes at least.

---

## Sensitive zones

- `adapters` storing bookings (database, file, any persistence): personal data; the booking links a person to a health practitioner, which can reveal health information (GDPR Article 9, unverified).
- Any exposure of booking data (API, export, logs, error messages): personal data; same reason.

The domain and application of the first feature (ids only, no persistence) are not declared sensitive; the architect's note requires a return to a human before any storage or exposure request.
