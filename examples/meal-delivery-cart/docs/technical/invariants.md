# Executable invariants

Architecture and quality rules made mechanically verifiable. Each has an immutable ID, a script that checks it, and an actionable remediation.

Run every check: `bash tools/harness/run_all.sh` (add `--with-mutation` for INV-006, which takes longer). Maven is found on the PATH, in `$MVN_CMD`, or under `~/.m2/wrapper/dists`; set `MVN_OFFLINE=1` to run it with `-o`.

| ID | Statement | Severity | Status |
|----|-----------|----------|--------|
| INV-001 | `domain` imports only the Kotlin/JDK standard library; `application` depends on `domain` only; nothing in them imports `adapters` | warn | active |
| INV-002 | Only `domain.money` rounds | warn | active |
| INV-003 | No `Double`, `Float` or `BigDecimal` in `domain` or `application` | warn | active |
| INV-004 | `domain` and `application` read no clock, randomness, environment, file or network | warn | active |
| INV-005 | Every business test-case points at an automated test that exists, and every test has a test-case | warn (broken reference: error) | active |
| INV-006 | Mutation testing covers `domain` and `application`; no threshold yet | warn | active |

INV-001 to INV-004 are ArchUnit rules in `src/test/kotlin/io/example/mealcart/ArchitectureTest.kt`, run through the Maven profile `invariants` (excluded from the default `mvn test`) and wrapped by `python3 tools/harness/check_layers.py`. The base package `io.example.mealcart` is named in `pom.xml` (`base.package`) and in `ArchitectureTest`: change both together. On an empty codebase the rules pass vacuously, and a wrong package name would keep them passing.

Moving a rule to `error` is a human decision: change `SEVERITY` in `check_layers.py` and the entry here in the same commit.

---

## INV-001 — Hexagonal dependency rule

- **Status**: active
- **Statement**: in the base package, `domain` depends on nothing but the Kotlin/JDK standard library (and the `org.jetbrains.annotations` the Kotlin compiler writes by itself) and itself; `application` depends on `domain` and the standard library only; nothing in `domain` or `application` depends on `adapters`.
- **Source**: ADR-0001, "Dependency rule"
- **Script**: `python3 tools/harness/check_layers.py`
- **Severity**: warn (exit 2)
- **Remediation**: when `domain` or `application` needs something from outside, define a port (an interface) in `application` and implement it in an adapter. Never import an adapter from `domain` or `application`, and never import a library into `domain`.
- **Example violation**:
  ```kotlin
  package io.example.mealcart.domain.pricing
  import io.example.mealcart.adapters.OrderGateway   // domain depends on an adapter
  ```
- **Fix**:
  ```kotlin
  package io.example.mealcart.application
  interface OrderHandoff { /* port owned by application */ }
  // io.example.mealcart.adapters.OrderGateway implements OrderHandoff
  ```

## INV-002 — Single rounding point

- **Status**: active
- **Statement**: no rounding API is called or used outside `io.example.mealcart.domain.money`: `Math.round/rint/floor/ceil/floorDiv/ceilDiv`, `kotlin.math` rounding (`round`, `floor`, `ceil`, `truncate`, `roundToInt`, `roundToLong`), `BigDecimal.setScale`, `RoundingMode`.
- **Source**: ADR-0001, "Dependency rule" (last line); architect note "Rounding applied identically everywhere"
- **Script**: `python3 tools/harness/check_layers.py`
- **Severity**: warn (exit 2)
- **Remediation**: call the one half-up rounding function of `domain.money`; never round at the call site.
- **Example violation**: `val discount = Math.floorDiv(2 * subtotal * rate + 100, 200)` in `domain.pricing`.
- **Fix**: `val discount = Rounding.halfUp(subtotal * rate, 100)` (the money function).
- **Known limit**: it sees API calls, not hand-written integer arithmetic that rounds (`(a + b / 2) / b` outside `domain.money` passes), and it checks the package, not that `domain.money` holds only one rounding function. A reviewer still looks at both.

## INV-003 — No floating point for money

- **Status**: active
- **Statement**: no `Double`, `Float` or `BigDecimal` as a field type, in a method signature or as the target of a call, in `domain` or `application`.
- **Source**: ADR-0002
- **Script**: `python3 tools/harness/check_layers.py`
- **Severity**: warn (exit 2)
- **Remediation**: hold an amount as `Money` (Long minor units, `Math.*Exact` for overflow) and a rate as `Percentage` (integer numerator over a power of ten).
- **Example violation**: `val rate: Double = 0.1`.
- **Fix**: `val rate = Percentage(numerator = 10, scale = 2)`.
- **Known limit**: bytecode analysis; a local `Double` that is neither passed, returned nor a call target is not seen.

## INV-004 — Purity of the core

- **Status**: active
- **Statement**: `domain` and `application` depend on no `java.time`, `java.io`, `java.nio`, `java.net`, `java.sql`, `java.util.concurrent`, `kotlin.random`, `kotlin.io`, `kotlin.time`, nor on `System`, `Thread`, `Runtime`, `Random`, `Date`, `Calendar`.
- **Source**: architect note "Purity and determinism (R3, R5)"; PRD requirements R3 and R5 (same input, same result)
- **Script**: `python3 tools/harness/check_layers.py`
- **Severity**: warn (exit 2)
- **Remediation**: take the value as an argument. If the core really needs the clock or I/O, define a port in `application`; that is an ADR-level change, ask the architect.
- **Example violation**: `Instant.now()` in `domain.pricing`.
- **Fix**: the caller passes the instant, or the rule is a parameter of `PricingRules`.

## INV-005 — Test-case bridge

- **Status**: active
- **Statement**: each test-case under `docs/business/test-cases/` carries a front-matter (`feature`, `type`, `priority`, `automated_test`, `status`) whose `automated_test` (`src/test/kotlin/<path>/<Class>Test.kt::<test name>`) exists; each test class has a test-case, except the technical tests listed in the script (`ArchitectureTest`). Each test-case names its source (a `source` key, a `## Source` section or a `Source:` line); a missing source is counted, never failed.
- **Source**: harness block B, approved by the human; convention shared with `examples/medical-appointments`
- **Script**: `python3 tools/harness/check_test_coverage.py`
- **Severity**: error for a broken reference or malformed front-matter (exit 1); warn for a pending test-case or an orphan test (exit 2)
- **Remediation**: fix the `automated_test` field, or set `status: pending` if the test was deleted on purpose; write the missing test-case for an orphan test.
- **Example violation**: `automated_test: src/test/kotlin/.../PriceTest.kt::applies the promotion` while that test no longer exists.
- **Fix**: restore or rename the test, then correct the reference.
- **Known limit**: it checks that a test exists (the name appears in the file, backticked Kotlin names included), not what it is worth (that is INV-006). Until `docs/business/test-cases/` exists the script reports it and exits 0.

## INV-006 — Mutation testing on the domain and application

- **Status**: active
- **Statement**: mutants injected into `domain` and `application` are killed by the tests; the share killed is measured, and must not regress once a threshold is set.
- **Source**: harness block D, scope approved by the human's delegate: `domain` and `application` packages
- **Scope**: `io.example.mealcart.domain.*` and `io.example.mealcart.application.*` (property `pit.targetClasses` in `pom.xml`); `critical`, `diff` and `full` scopes exist in the script
- **Script**: `bash tools/harness/run_mutation.sh --scope critical|diff|full`
- **Tool**: PIT 1.20.1 with pitest-junit5-plugin 1.2.2 (`pom.xml`); parsable report `target/pit-reports/mutations.xml`, readable report `target/pit-reports/index.html`. Default mutators. `ArchitectureTest` is excluded.
- **Severity**: warn, once a threshold exists
- **Threshold**: none yet (human decision)
- **Baseline**: not measured (no production code yet). To record, with date and sha, after the first feature lands.
- **Kotlin bytecode**: on a throwaway fixture (a data class, an object and a few functions) PIT generated no mutant on the compiler's null-check intrinsics and no unviable one; the survivors were real gaps (getters of a data class that no test reads, a `require` boundary). Re-check on the real code: inline functions, `when` over sealed types and `copy`/`componentN` of data classes are where noise is expected. Exclude a class or mutator in `pom.xml` only with a comment saying why.
- **Remediation**: for each surviving mutant, find the unprotected behavior and add a test that states it. Never add a test whose only purpose is killing the mutant; if the mutant matches no behavior that counts, exclude it in `pom.xml` with a comment explaining why. Never lower a threshold to get back to green.
- **Not in pre-commit**: a run takes minutes at least.

---

## Sensitive zones

- Money computation and rounding: `src/main/kotlin/io/example/mealcart/domain/money/` and `src/main/kotlin/io/example/mealcart/domain/pricing/`, and their tests under `src/test/kotlin/io/example/mealcart/domain/money/` and `src/test/kotlin/io/example/mealcart/domain/pricing/`. Reason: money. A rounding or overflow error here is a wrong price shown to a customer; a change needs a human decision.
