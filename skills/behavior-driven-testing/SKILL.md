---
name: behavior-driven-testing
description: >
  Test strategy driven by behaviors rather than "one test per class". Use as soon as tests are
  written, designed or reviewed, when test strategy, coverage, mutation testing, mutation score
  or TDD come up, when someone asks "how do I test this", or complains about brittle tests. Use
  it also when someone proposes a "1 test ↔ 1 class" mapping, sets a numeric coverage target as
  the goal, or wonders whether their tests are worth anything — that is the reflex this skill
  corrects.
---

# Testing behaviors, not classes

## The core idea

A test checks that an **observable behavior** is correct: an input produces the expected output, a use case plays out as intended, a business rule holds. It does not exist to "cover a class".

The false belief to correct: "testing properly means a test suite dedicated to every class". That is wrong, and it produces bulky, brittle suites that test internal machinery rather than what matters.

Why, mechanically: coverage measures **which lines run**, not how many classes have their own test file. Yet a single behavior test often runs through N classes, which are covered without a direct test of their own. The "1 test ↔ 1 class" mapping is imposed by no tool; it is a discipline we inflict on ourselves.

## The coverage trap

This skill **does not aim** for "100% coverage". Coverage measures execution, not the quality of the assertions: you can run 100% of the lines without ever checking the right result. High coverage is a *consequence* of good tests, never the goal.

In practice: never add a test whose only justification is pushing the percentage up. An uncovered area is a diagnostic signal ("did I forget a use case?"), not a box to tick. If the user sets a numeric target, briefly explain the distinction, then refocus on the behaviors that need covering.

## The metric that measures what coverage cannot

The complaint made about coverage — it measures execution, not the worth of the assertions — raises a fair question: is there a metric that does measure that worth? Yes: **mutation testing**.

The principle: the tool mechanically alters the code (flipping a condition, swapping an operator, removing a call, returning null), re-runs the tests, and watches whether they fail. A *killed* mutant means the tests really do protect that behavior. A *surviving* mutant means that line can be broken without a single test noticing — a test can be green, cover 100% of the lines, and assert nothing useful.

It is the natural counterpart to working from behaviors: a surviving mutant reads as a question — "which behavior is left unprotected here?" — and the answer is a test to write, shaped by the rules of the previous section.

Three warnings, following directly from the coverage trap:

- **Mutation score is not a numeric target in disguise.** It diagnoses; it is not aimed at. A CI threshold is there to stop a regression, never to push a number up.
- **Never write a test whose only justification is killing a mutant.** Same failing as the test written to push coverage up, in more flattering clothes. If a surviving mutant matches no behavior that matters, exclude it in configuration, with a comment justifying the exclusion.
- **Equivalent mutants exist.** Some alterations are semantically neutral, and therefore unkillable. A score of 100% is neither reachable nor desirable.

The runtime cost is real — a run takes tens of minutes. In practice, restrict it to the scope that carries the business rules. Operational setup (scope, thresholds, CI integration) belongs to `codebase-harness`, block D.

## Approach

1. **Identify the unit of behavior, not the unit of code.** Before writing a test, ask: "which use case or which rule am I validating?". The subject is a behavior ("an empty cart refuses payment"), not a class ("`CartValidator`").

2. **Test at the right boundary.** Prefer testing through a stable interface — the entry point of a use case, a module API, an application port — rather than class by class. The internal classes it runs through are covered as a matter of course.

   *Exception:* test a class in isolation only when it carries complex logic that is hard to exercise from the boundary, or to drive a delicate algorithm.

3. **Name tests after behaviors.** The name describes the intent and the result ("rejects an order beyond available stock"), not the method called ("test_checkStock").

4. **Assert on the observable result**, not on implementation details. Over-checking internal calls (mocking everything) makes tests brittle. A good behavior test survives refactoring as long as the behavior does not change.

## How many tests

The unit of a suite is the **business rule**, not the input. "An offer is open until its end date included" is one rule; the last day, the day after and a one-day offer are three examples of it. The examples are the cases of one test, not three tests.

1. **One test per rule, its examples inside it.** Variants that share one assertion shape (same call, same kind of outcome, different inputs) go in a single parameterized test (subtests, a table, `test.each`), named after the rule. Two different rules never share a test: a failure must name one rule.
2. **One example per distinct outcome.** Three invalid values that give the same refusal are one example of that refusal; a fourth that gives another refusal is another rule. Do not test what the language or the types already forbid (an old call without the new argument raising a type error).
3. **A rule shared by several use cases is tested once.** The role check, the order in which refusals are reported, the handling of an unreadable store: one test over a table of the use cases, not one copy per use case. A use case gets a test of its own for such a rule only to add an example the others lack.
4. **A behavior already exercised by an example elsewhere needs no test of its own.** Deciding a behavior (in a document, a plan, an answered question) is not a reason to test it again. A test is justified when the behavior could regress without another test noticing.
5. **Do not pin how the result is obtained.** The number of reads, writes or clock calls, the class hierarchy, a type, the wording of a docstring: none of these is a behavior. The one exception is a count that a decision or the plan requires ("one save, so one atomic write"); the test then names that decision.

The mutation score cannot tell enough from too many: it stays flat as tests are added. Never use it to justify a number of tests; use it to check that a trimmed suite still protects what it protected. To trim a suite that already grew, group the examples of each rule first, then drop what another test restates, and run the mutation on the same scope before and after: the score must not fall.

## Adapting to the project's stack

Before writing tests, infer the context (language, framework, architecture) by inspecting the repository: manifests (`pom.xml`, `build.gradle`, `package.json`, `pyproject.toml`, `*.csproj`, `go.mod`…), existing test folders, naming conventions. Respect the framework and the style already in place.

If the project follows a layered / hexagonal / DDD architecture, the natural test boundary is the application use case or the port — that is where the tests go, covering the domain behind them. If a test strategy document already exists (e.g. under `docs/`), conform to it and extend it.

## Signs of a wrong turn

- A test file created "because the class exists", with no clear behavior to validate.
- A mock for every dependency, to the point where the test mirrors the implementation line by line.
- A test that breaks on every rename or method extraction, with no change of behavior.
- A goal stated as a coverage percentage rather than as use cases covered.
- Several tests that differ only by their inputs, or one rule tested again for each use case.
- An assertion on a number of calls, a type or a docstring that no decision requires.

In those cases, refocus: "which behavior does this test protect?". With no clear answer, the test is to be deleted or reworded.

## Example of a reframe

**Request:** "I need a test for `OrderValidator`, `PriceCalculator` and `StockChecker` to cover the order module."

**Behavior-driven answer:** write tests on the "place an order" use case — nominal case, insufficient stock, promotional price — which naturally run through all three classes. The three are covered, the tests describe real business rules, and they survive an internal refactoring.
