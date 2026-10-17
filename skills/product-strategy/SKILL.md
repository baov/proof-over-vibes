---
name: product-strategy
description: >
  Product strategy from an idea or an existing product: market watch (competitors, blue or red
  ocean), vision, roadmap, story mapping, a backlog of epics and features prioritized, and a
  PRD for one chosen feature. Use as soon as the user wants to "define the product vision",
  "build a roadmap", "do a story map", "fill or prioritize the backlog", "study the market or
  the competition", "find a blue ocean", "write a PRD", or starts from an idea with no code yet
  and asks what to build first. Works at the level of epics and features, never of user
  stories. Writes under `docs/product/`, and its conclusions are hypotheses the user
  validates. Hands a chosen feature to the architecture and planning work that follows.
---

# Product strategy

Decides what is worth building and in which order, before anyone designs or codes it. It stops at the epic and the feature: user stories belong to whoever works one level down, at the moment a feature is picked.

## Initial announcement

Like `plan-driven-dev`, this skill **announces itself before applying**: state in a line or two which phase it expects to start from, and ask the user to confirm. Never write a file under `docs/product/` without agreement.

## Picking the phase

| Signal in the request | Phase |
|---|---|
| An idea, a market, "what should we build" | **1. Market watch** |
| The market is understood, "what is the product" | **2. Vision and roadmap** |
| A vision exists, "what do we build first" | **3. Story map and backlog** |
| A feature was picked, "write its PRD" | **4. PRD** |
| Ambiguous | Ask with a multiple-choice question (2 options) |

An existing product enters at the phase that matches what is missing: read `docs/product/` first, and the business documentation when the cartographer wrote it.

## The phases

Each phase has its reference. Read it **before** the phase, not all of them at once.

| # | Phase | Output | Reference |
|---|---|---|---|
| 1 | Market watch | `docs/product/research.md` | `references/market-watch.md` |
| 2 | Vision and roadmap | `docs/product/vision.md`, `docs/product/roadmap.md` | `references/vision-and-roadmap.md` |
| 3 | Story map and backlog | `docs/product/story-map.md`, `docs/product/backlog.md` | `references/story-map-and-backlog.md` |
| 4 | PRD, for one feature | `docs/product/prd/<feature>.md` | `references/prd.md` |

A PRD is written **on demand**, for the feature the user picked, never for the whole backlog: it would age before anyone read it.

## Doctrine

- **Hypotheses, not facts.** A market watch gives sourced hypotheses. Every claim carries its source, or is marked *unverified*. The user decides; the skill recommends.
- **Validation by multiple-choice question.** A vision, a positioning and a prioritization are bets. Each goes through the user (shape and degraded mode: see `clarify-with-choices`) before it is written. Questions are asked in the target project's language.
- **File-backed.** Everything lives in `docs/product/`, versioned, not in the context window.
- **Degraded mode.** Without web access, the skill says so, asks the user for their own sources (competitors, reports, interviews), and marks everything it could not check as *unverified*. It never invents a market figure.
- **Nothing is launched.** The skill ends on the backlog or the PRD. The user picks an item and starts the work: this skill creates no ticket and no request.

## Fitting into the ecosystem

- **codebase-cartographer**: consume `docs/business/` when it exists; the glossary is the vocabulary of the vision and the PRDs.
- **ddd-advisor**: a vision split into epics often suggests contexts; hand that over rather than deciding it here.
- **plan-driven-dev**: a PRD gives the objective and the acceptance criteria of the request that follows.
- **codebase-harness**: none directly; structural decisions come after the vision, not in it.

Everything written outside this repository follows the language of the target project.
