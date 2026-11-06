# Review reports

One report per review, as the Reviewer wrote it. By convention the roles keep `.reviews/` out of git, since it is working state; this example keeps the reports here, on purpose, so that a reader can see what a Reviewer finds: the verdict, the findings with their severity, and the checks behind them. It is an exception made for the examples, not a rule of the repository.

| Review | Verdict |
|---|---|
| [Story 1, ask and accept](01-connection-requests-story-1-ask-and-accept.md) | GO |
| [Story 2, decline and withdraw](02-connection-requests-story-2-decline-and-withdraw.md) | GO |
| [Edge case 1, blank ids and the decliner](03-edge-ids-and-decliner.md) | GO |
| [Edge case 2, simultaneous operations](04-edge-concurrency.md) | GO |
| [Bug: check of the Diagnostician's proof](05-bug-proof-check.md) | GO |
| [Bug: the fix](06-bug-fix.md) | GO |

Every review of this example that touched a sensitive zone also carries `status: escalate`, and no person reviewed those diffs.

The commit ids cited in the reports are those of the history before the commits were grouped by stage; they no longer resolve. The file and test names do.

Two reports, `03-edge-ids-and-decliner.md` and `06-bug-fix.md`, were written in French by the Reviewer and translated afterwards; the translation note at the top of each says so.
