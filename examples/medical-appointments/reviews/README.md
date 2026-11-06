# Review reports

One report per review, as the Reviewer wrote it. By convention the roles keep `.reviews/` out of git, since it is working state; this example keeps the reports here, on purpose, so that a reader can see what a Reviewer finds: the verdict, the findings with their severity, and the checks behind them. It is an exception made for the examples, not a rule of the repository.

| Review | Verdict |
|---|---|
| [Story 1, book and never double-book](01-book-a-slot-story-1.md) | GO |
| [Story 2, refuse what cannot be honoured](02-book-a-slot-story-2.md) | GO |
| [Edge case 1, blank identifiers](03-edge-blank-ids.md) | GO |
| [Edge case 2, simultaneous bookings](04-edge-simultaneous.md) | GO |

Every review of this example that touched a sensitive zone also carries `status: escalate`, and no person reviewed those diffs.

The commit ids cited in the reports are those of the history before the commits were grouped by stage; they no longer resolve. The file and test names do.
