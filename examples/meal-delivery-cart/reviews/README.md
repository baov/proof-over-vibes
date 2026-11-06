# Review reports

One report per review, as the Reviewer wrote it. By convention the roles keep `.reviews/` out of git, since it is working state; this example keeps the reports here, on purpose, so that a reader can see what a Reviewer finds: the verdict, the findings with their severity, and the checks behind them. It is an exception made for the examples, not a rule of the repository.

| Review | Verdict |
|---|---|
| [Story 1, price without a promotion](01-price-a-cart-story-1.md) | GO |
| [Story 2, apply a promotion](02-price-a-cart-story-2.md) | GO |
| [Edge case 1, amounts](03-edge-amounts.md) | GO |
| [Edge case 2, blank codes and simultaneous pricing](04-edge-codes-and-concurrency.md) | GO |

Every review of this example that touched a sensitive zone also carries `status: escalate`, and no person reviewed those diffs.

The commit ids cited in the reports are those of the history before the commits were grouped by stage; they no longer resolve. The file and test names do.
