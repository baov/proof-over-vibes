# Phase 0: brief framing

## Goal

Turn a brief into the few decisions that must be made before anything else is written. The output is `docs/product/framing.md`: what the brief leaves open, and the questions that settle it. No solution, no architecture, no market claim yet.

## When

The request comes with a brief (a paragraph, a document, a ticket) and the next phase cannot start without guessing. If the brief already settles the problem, the users and the delivery stage, skip this phase and say so.

## What to write

1. **Ambiguities.** Terms or statements the brief leaves open, each with the readings it allows.
2. **Assumptions.** What the brief takes for granted without saying so. Mark each *stated* or *inferred*.
3. **Contradictions.** Two statements of the brief that cannot both hold, quoted.
4. **Missing information.** What a later phase needs and the brief does not give.
5. **Questions.** The most decisive ones, ranked by how much they change the product. **At most 10**: fewer when the brief has fewer real gaps, never padded to reach a number. Each question states:
   - the **decision** it allows;
   - the **risk** if it stays unanswered;
   - the **default**: the answer you would take for the delivery stage in view, offered as a recommendation, never as a decision.

## The delivery stage

Settle first which stage the work aims at: a proof of concept, a first version, a next increment of an existing product. The stage sets the default of every other question. When the brief does not say, it is the first question. On an existing product, read `docs/product/` and `docs/business/` before asking: what they already settle is not asked again.

## Rules

- Questions go to the human, never to `product-owner`: a scope, a target user and a priority are bets.
- A default is a recommendation to confirm. Nothing written in a later phase relies on it until the human has answered.
- No solution, no technology, no structure. A technical unknown is listed in the missing information, for `architect` to take up.
- Ask the questions as multiple-choice questions, the default being the recommended option, then record the answers in `framing.md`.
- Hand-off: the answers feed the phase the request calls for. This phase starts nothing.
