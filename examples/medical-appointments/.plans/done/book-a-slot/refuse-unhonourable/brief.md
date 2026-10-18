# Brief: book a slot, story 2 (refuse-unhonourable)

- Request type: prompt (feature "book a slot", brief.md of the parent folder)
- Story: 2 of 2, see ../stories.md ("Story 2"); its acceptance criteria are those of that section
- Depends on story 1 being merged first
- Iteration counter: 0
- Iteration limit: 5
- Delegation: middle way (cheap-to-reverse questions answered by the orchestrator with the role's recommendation, `answered-by-delegate`; product bets and costly choices go to the human)
- Decision log: docs/business/decisions.md
- PRD: docs/product/prd/book-a-slot.md
- Architecture: docs/technical/adr/0001-*, architect note ../architect.md
- Harness: docs/technical/invariants.md; tools/harness/run_all.sh before each commit; Maven at /Users/baovuong/.m2/wrapper/dists/apache-maven-3.9.11-bin/6mqf5t809d9geo83kj4ttckcbc/apache-maven-3.9.11/bin/mvn (see tools/harness/_maven.sh), run offline (-o) once dependencies are resolved
- Open and NOT decided (ask, do not choose): simultaneous booking of one slot, blank or empty identifiers; any other behavior a caller would see that neither the stories nor the decision log settle
- Carried over: none

## Answers

(none yet)

## Carried over (from story 1, review 1: GO, open_majors)

- M1: atomicity of check-and-save is built (a lock in the in-memory adapter) but proven by no test: removing the lock passes every test and every PIT mutant. The outcome of simultaneous booking is an open product question, reserved for an edge-case request: do not decide it. Plan whether a test of atomicity can be written without deciding what the loser sees, or defer by a question.
- M2: `BookSlot.book` on an unknown slot throws NoSuchElementException (no document settled it): this story's criterion 1 and D-26 replace it with Refused(UNKNOWN_SLOT).

Minor items to take along: `null` identifiers (D-22, deferred, unspecified); `findSlot` reads without the lock (a comment would keep it safe if slots become mutable); `slotIsNoLongerFreeAfterBooking` asserts only `isPresent()`; no mutation baseline is recorded (a human decision).
