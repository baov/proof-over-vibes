# Report template

The structure stays as below; headings and content go in the target project's language. The verdict comes first and the TL;DR next, so the reader knows the outcome before the detail.

```markdown
# Acceptance proof - <feature>
**Verdict: GO | NO-GO**

## Summary
<Two to four lines: what was run, how many criteria are PROVEN / DISPROVEN / UNPROVEN, and what the reader has to decide.>

## Environment
- Application: <address or command> | version or commit: <id>
- Surface: <web | mobile | desktop | CLI | API>
- Test data: <what was created for the run>
- Criteria source: <brief | test cases | stated by the user>

## Criteria
| # | Criterion | Proof mark | Evidence |
|---|-----------|------------|----------|
| C1 | <Given / When / Then> | PROVEN | `screenshots/01-c1-after-add.png` |
| C2 | <Given / When / Then> | DISPROVEN | `screenshots/02-c2-after-remove.png` |
| C3 | <Given / When / Then> | UNPROVEN - <reason> | - |

## Raw log
- C1 step 1: expected <X> | observed <Y> | `01-c1-start.png`
- C1 step 2: expected <X> | observed <Y> | `02-c1-after-add.png`
- C2 step 2: expected <X> | observed <Y> | `03-c2-after-remove.png`

## Checks not performed
- <criterion or surface left out, and why> (or: none)

## Hand-off
- DISPROVEN: <criterion> -> `systematic-debugging`, symptom = the raw log line above
- UNPROVEN: <criterion> -> what is needed to reach the state

## Replay
1. <how to start the app and load the test data>
2. <steps of C1>
3. <steps of C2>
Automated version, if any: `<script file in this folder>`
```

A short run needs no diagram. When a feature has a flow worth seeing (several screens, a sequence of calls), add a Mermaid diagram of it under the Environment section, labeled in the project's language.
