# Example map

Before any code, the acceptance criteria are turned into examples someone can observe. The map finds what a criterion leaves open while it is still cheap to ask, and becomes, after the code, the plan of the proof.

It is example mapping done in writing: no meeting, several passes on one file. Each pass may add examples and questions; only the person or the role who owns the business rules adds a business rule.

## Shape

One file per request, `example-map.md`, with one section per story. Headings and content follow the target project's language.

```markdown
# Example map - <feature>

## Story <id> - <title>

### B1 <business rule: one acceptance criterion, as written, with its source>
- E1 <Given / When / Then, with the visible state expected> - source: <criterion, decision id, or "proposed">
- E2 ...

### B2 ...

### Questions
- Q1 <question> - options: A) ... B) ... - why it matters: <what a consumer would see differently>
```

## How to fill it

1. **One business rule per acceptance criterion**, copied with its source. Do not rewrite it, do not merge two.
2. **Examples that someone can observe**: a starting state, an action, a visible result. Cover the plain path, then the edges a consumer would meet: nothing, one, many, a repeat, an invalid value, a limit, an order.
3. **An example no source settles is proposed, not confirmed**: mark it `source: proposed`. A proposed example is never proved later as if it were a criterion.
4. **A question, not a guess**, whenever two readings would show a consumer two different behaviors. Write it as a multiple-choice question (shape: see `clarify-with-choices`). An example that reveals a missing business rule is a question too: only the owner of the business rules adds one.
5. **Signals to stop**:
   - a story whose questions outnumber its examples is not ready: send the questions, do not plan it;
   - business rules that fall into groups which could ship apart mean the story should be cut again: say so as a question.

## After the code

The proof plan of `acceptance-proof` starts from the map. Each confirmed example is a criterion to prove; a proposed example stays out of the proof until a decision confirms it.
