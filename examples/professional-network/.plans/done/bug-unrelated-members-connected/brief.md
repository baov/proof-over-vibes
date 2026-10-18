# Brief: bug, two unrelated members shown as connected

- Request type: prompt (bug report below)
- Slug: bug-unrelated-members-connected
- Iteration counter: 0
- Iteration limit: 5
- Delegation: the human delegated every decision (answered-by-delegate)

## Bug report (as received)

**Title:** Two unrelated members are shown as already connected, and one can't send a request to the other.

Steps:
1. Member ids can be any string, so use `ann:bo` and `cy`, and also `ann` and `bo:cy`.
2. `ann:bo` sends a connection request to `cy`, and `cy` accepts it.
3. `ann` (an unrelated member) sends a request to `bo:cy`.
4. Query the pair state of `ann` and `bo:cy`.

Expected: `ann` and `bo:cy` have never interacted. The send in step 3 succeeds with a new pending request. The pair state is `{connected: false, requestState: "none"}`.

Actual: the send in step 3 is rejected with `already-connected`. The pair state reports `{connected: true, requestState: "none"}`, even though no request or connection exists between those two members.

## Context

Code: `src/connections/`, tests in `tests/connections/`. Earlier work: `.plans/done/`. Decisions: `docs/business/decisions.md`. The bug is not in any plan; it was reported on the code as it stands today (branch HEAD).

## Carried over

Open major of the previous request: an operation that never settles blocks the module (no timeout, undecided). Not part of this bug.
