---
role: developer
status: done
reasons: []
---

# Developer, iteration 1: what the loser of a simultaneous booking sees

Skills announced: `plan-driven-dev` (implementation steps) and `behavior-driven-testing`. The code already met the PRD, so no behavior was changed; the work is proof. Every plan step done, no deviation.

## Commits (on the shared branch, only under `examples/medical-appointments`)

1. `fda7b94` Race helper (`Race.java`, no timed wait) + tests 1 and 2 + test-cases (first one rewritten, overlapping one renamed to `simultaneous-overlapping-bookings-loser-sees-overlapping.md`).
2. `c80a3d0` Tests 3 and 4 + 2 test-cases.
3. `80b854a` Tests 5 and 6 + 2 test-cases.
4. `7d2cfe8` Tests 7, 8 and 9 + 3 test-cases.
5. `5af7e66` One Javadoc sentence on `BookingStore.atomically` (the only production change).
6. `ffffc73` Gate refinement found by the lock-removal proof (see below).

## Results

- Full `mvn -o test`: 35 tests green (9 in `BookSlotConcurrencyTest`, 16 ms, no sleep). `run_all.sh --with-mutation`: INV-001 green, INV-002 35/35 covered, 0 orphan, INV-003 critical 100 % (29/29), unchanged as expected (the Javadoc is the only production change, no baseline written: human decision).
- Flakiness with the lock: `BookSlotConcurrencyTest` run in separate Maven runs 10 (baseline) + 25 + 10 (under CPU load, 22 busy processes on 11 cores) = 45 runs, 0 failure.

## Lock-removal proof (done by hand, restored, in no commit)

- Mutation 1 (`atomically` body = `return unit.get();`): 10 runs, 7 of 9 tests fail on every run: tests 1 to 6 and test 9. Messages: "exactly one request must book; outcomes: [Booked..., Booked...]" and "no order one after the other gives Result[...]". Tests 7 and 8 stay green, as the plan said (no exclusion needed). Test 9 contains a race, so it fails too.
- Mutation 2 (also unlocked `save`): first 10 runs showed one run where test 2 passed. Cause: the gate treated any WAITING/BLOCKED thread as held back; a thread blocked for another reason (class loading) let the gate open early. Per plan step 5 this is a failing step, so I fixed the gate (commit `ffffc73`): a racer counts as held back only if the first non-JDK frame of its stack is `atomically`. Then mutation 2: 20 runs, the same 7 tests fail on every run; mutation 1 again: 10 runs, 7 fail on every run.
- Restored: `git diff HEAD -- src/main` is empty after the restore; the only production diff in the commits is the Javadoc sentence. Baseline re-run green.

## Behaviors added

None. No operation, parameter, type or error was added or changed; only a Javadoc and tests.

## Points for the reviewer

- The gate recognises a held-back racer by the name `atomically` in its stack; an adapter that blocks outside a method of that name would make a race fail with "the race never formed" after 10 s (a loud failure, not a false pass).
- Accepted limit named in the plan: test 6 flips the clock inside the winner's `save`; a clock read hoisted before the unit but after another request's save would need a third interleaving.
- Test 5's oracle replays `BookSlot` itself in sequence: it proves concurrent = sequential, not that the sequential rule is right (`BookSlotTest`).
- Plan flag, still for the human: the third party in "loser who also holds an overlap" sees `TAKEN` or `OVERLAPPING` depending on arrival.
- Minor 1 (500 ms wait) closed; minor 2 (loser pinned by no test) closed; minor 3 (no mutation baseline) untouched.
