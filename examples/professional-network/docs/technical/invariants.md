# Executable invariants

Architecture and shape rules made mechanically verifiable. Every invariant has an immutable ID, a script that checks it, and an actionable remediation. All start in `warn`: a rule moves to `error` only when the humans decide so, once its existing violations are at zero.

Run every check: `bash tools/harness/run_all.sh` (or `npm run harness`). Mutation is separate (slow): `npm run mutation`. Self-test of the checks: `npm run harness:selftest`. Exit codes: 0 clean, 1 error, 2 warnings only.

| ID | Statement | Severity | Status |
|----|-----------|----------|--------|
| INV-001 | The domain layer imports nothing outside its own domain folder | warn | active |
| INV-002 | The application layer imports only the domain and application of its module | warn | active |
| INV-003 | The infrastructure layer imports only infrastructure, application and domain of its module | warn | active |
| INV-004 | A module reaches another module only through its public entry point | warn | active |
| INV-005 | A function is at most 40 lines | warn | active |
| INV-006 | A function has a cyclomatic complexity of at most 10 | warn | active |
| INV-007 | A function nests control blocks at most 4 deep | warn | active |
| INV-008 | A function takes at most 5 parameters | warn | active |
| INV-009 | Every test-case points at a real test, and every test has a test-case | warn (broken reference: error) | active |
| INV-010 | The mutation score of the critical scope does not fall below its threshold | warn | active, no threshold until the first baseline |

---

## INV-001 — Domain isolation

- **Status**: active
- **Statement**: `src/<module>/domain` imports only files of `src/<module>/domain`: no package, no Node API, no other layer, no other module.
- **Source**: ADR-0001, dependency rule
- **Script**: `tools/harness/check_layers.mjs`
- **Severity**: warn
- **Remediation**: move the call that needs a package or the platform into `src/<module>/infrastructure`, and expose a port in the domain or application layer that the adapter implements.
- **Example violation**:
  ```ts
  // src/connections/domain/request.ts
  import { randomUUID } from "node:crypto";
  ```
- **Fix**:
  ```ts
  // domain/application declare `IdGenerator`; infrastructure implements it with randomUUID
  ```

## INV-002 — Application depends on the domain only

- **Status**: active
- **Statement**: `src/<module>/application` imports only `src/<module>/domain` and `src/<module>/application`: no package, no Node API, no infrastructure.
- **Source**: ADR-0001, dependency rule
- **Script**: `tools/harness/check_layers.mjs`
- **Severity**: warn
- **Remediation**: depend on a port declared in the application layer; the adapter lives in infrastructure and is wired at the edge.
- **Example violation**:
  ```ts
  // src/connections/application/send-request.ts
  import { InMemoryRequests } from "../infrastructure/in-memory-requests";
  ```
- **Fix**:
  ```ts
  import type { RequestRepository } from "./ports";
  ```

## INV-003 — Infrastructure depends inward

- **Status**: active
- **Statement**: `src/<module>/infrastructure` imports only infrastructure, application and domain of the same module (and packages: an adapter is where a dependency belongs).
- **Source**: ADR-0001, dependency rule
- **Script**: `tools/harness/check_layers.mjs`
- **Severity**: warn
- **Remediation**: an adapter must not reach into another module's folders or the module root; go through that module's public entry point (INV-004).
- **Example violation**:
  ```ts
  // src/connections/infrastructure/memory.ts
  import { thing } from "../index";
  ```
- **Fix**:
  ```ts
  import { thing } from "../application/thing";
  ```

## INV-004 — Cross-module access through the public entry point

- **Status**: active
- **Statement**: code in one module imports another module only from `src/<other>/index.ts`.
- **Source**: ADR-0001, dependency rule
- **Script**: `tools/harness/check_layers.mjs`
- **Severity**: warn
- **Remediation**: import from `src/<other>/index.ts`. If it exposes too little, ask the owner of that module to widen its public entry point; never deep-import.
- **Example violation**:
  ```ts
  // src/posts/application/feed.ts
  import { isConnected } from "../../connections/domain/connection";
  ```
- **Fix**:
  ```ts
  import { isConnected } from "../../connections";
  ```

## INV-005 to INV-008 — Shape thresholds

- **Status**: active
- **Statement**: per function, at most 40 lines (INV-005), complexity 10 (INV-006, 1 + `if`, loops, `case`, `catch`, `?:`, `&&`, `||`, `??`), nesting depth 4 (INV-007), 5 parameters (INV-008). Nested functions are measured on their own.
- **Source**: harness default thresholds (tangled code makes agents loop and widen their diffs); tune after two weeks of data
- **Script**: `tools/harness/check_shape.mjs`
- **Severity**: warn
- **Remediation**: extract named steps, use guard clauses, group parameters into a value object. Do not raise a threshold to silence a function.
- **Example violation**:
  ```ts
  function decide(a, b, c, d, e, f) { /* 6 parameters */ }
  ```
- **Fix**:
  ```ts
  function decide(input: DecisionInput) { /* one object */ }
  ```

## INV-009 — Test-case bridge

- **Status**: active
- **Statement**: each file under `docs/business/test-cases/` has a front-matter whose `automated_test` (`<path>::<test name>`) names an existing test, or is `pending` or `manual`; each `*.test.ts` is referenced by a test-case.
- **Source**: harness block B; one test per PRD requirement (architect's note)
- **Script**: `tools/harness/check_test_coverage.mjs`
- **Severity**: warn for pending and orphans; error for a broken reference or a malformed front-matter
- **Remediation**: fix the `automated_test` reference, write the missing test, or create the missing test-case. Test-cases that name no source are only counted (information).
- **Example violation**:
  ```
  docs/business/test-cases/connections/withdraw.md:7: [INV-009] test-case marked `covered` but the test `withdraws` is nowhere to be found in `tests/withdraw.test.ts`
  ```
- **Fix**:
  ```yaml
  automated_test: tests/withdraw.test.ts::the sender withdraws a pending request
  ```

## INV-010 — Mutation score of the critical scope

- **Status**: active (no threshold yet)
- **Statement**: the mutation score over the critical scope does not fall below the threshold recorded in `tools/harness/mutation-threshold.json`.
- **Source**: harness block D; scope approved by delegate on 2026-10-18
- **Scope**: `src/connections/domain/**` and `src/connections/application/**` (production files, tests excluded)
- **Script**: `tools/harness/run_mutation.sh --scope critical` (`--scope diff` for a branch)
- **Tool**: Stryker 10 with the Vitest runner; config `stryker.config.mjs`; machine report `reports/mutation/mutation.json`, human report `reports/mutation/mutation.html`
- **Severity**: warn (to `error` once stable)
- **Baseline**: none. No code exists yet. After the first run on real tests, record baseline, date and sha in `mutation-threshold.json` and set the threshold to the baseline rounded down.
- **Remediation**: read the surviving mutants the script lists. For each one, identify the unprotected behavior and add a test that expresses it. Never add a test whose only justification is killing a mutant; if a surviving mutant matches no behavior that counts, exclude it in `stryker.config.mjs` with a comment justifying it. Never lower the threshold to get green. Never run it in pre-commit.
- **Example violation**:
  ```
  score: 71.0% (110 killed / 155 generated)  threshold: 75%  → BELOW THRESHOLD
  src/connections/domain/request.ts:44  [EqualityOperator]  Survived
  ```
- **Fix**: a test that fails if the comparison at line 44 is off by one.

---

## Sensitive zones

Areas where a human reviews before merge (declared by delegate, option a).

- `src/*/infrastructure/**` and every repository port in `src/*/application/**`: personal data (member ids and their relationships, storage) and the erasure operation; whatever stores or removes data about a member.
- `src/data-rights/**` (future module): erasure and export of personal data.
- `src/*/index.ts`: the public entry points; what another module can read about a member's connections is the product's promise ("readable by connections only").
