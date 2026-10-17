# Phase 3: story map and backlog

## Story map (`docs/product/story-map.md`)

1. **The backbone**: the steps a user goes through, left to right, from the first need to the outcome they want.
2. **Under each step**, the epics and features that serve it, the most essential at the top.
3. **Slices**: horizontal cuts across the backbone, each slice being a coherent release that delivers the outcome end to end, however thin. The first slice is the *walking skeleton*: the thinnest path that works.

Draw it as a Mermaid diagram or a table. Map to the level of the feature; stop there.

**On an existing product**, read the business documentation (`docs/business/`) first and place the features already built in the map with the status `done`, citing the document as the source rather than copying its details. The whole journey then shows, and the gaps with it. New epics are proposed to fill those gaps.

## Backlog (`docs/product/backlog.md`)

One line per epic and per feature, in priority order:

- the epic it belongs to, the outcome it serves,
- a one-sentence statement of the value,
- its slice and horizon,
- its status: *idea*, *shaped*, *picked*, *done* (a feature already built in the product).

No user stories, no acceptance criteria: those come at the moment a feature is picked, in its PRD.

## Prioritizing

Rank epics, then features within each epic. Pick the method with a multiple-choice question, with a recommendation:

- **Value against effort**: two axes, quick to read, coarse.
- **RICE** (reach, impact, confidence, effort): a score, useful with data, misleading without.
- **MoSCoW** (must, should, could, won't): a scope cut for a given slice.

Whatever the method, write the reasoning in the backlog, not the score alone. A prioritization is a bet the user validates.
