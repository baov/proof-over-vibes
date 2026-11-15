---
name: ux-redesign
description: Use when asked to redesign a product's experience end to end, rethink a journey or a key screen, or propose an art direction for any interactive product (web app, site, tool, onboarding, checkout, form-based flow). Produces a design document: diagnosis, three distinct creative directions with a recommendation, journey and screen architecture, text wireframes, components, microcopy, priorities and a validation plan. Not for implementing the UI (that is planning then implementation, as in plan-driven-dev) nor for a visual polish of one component.
---

# UX redesign

Design a complete redesign, not a refresh of colors and components: rethink the experience, the navigation, the hierarchy of content and how the core interaction is staged. The result must read as a singular, finished product, not a demo of visual effects.

The skill is product-agnostic. `references/example-palia.md` is one worked request, for a self-assessment site: read it to calibrate the expected depth and tone, never as a model of the product, its stages or its constraints.

## Initial announcement

Like `plan-driven-dev`, this skill **announces itself before applying**: state in a line or two which product and which journey it is about to inspect, and ask the user to confirm. The design document goes to `.plans/<slug>-ux.md`, or to the path the request gives.

## Cardinal rules

1. **Inspect before designing.** Walk the real product: every screen, desktop and mobile, keyboard only once. Read the documentation of its rules. A redesign built on a guessed product is a redesign of another product.
2. **Preserve the real product rules.** Never invent a business rule, a calculation, a feature, a duration or a statistic. What you cannot reach, you mark as a hypothesis, explicitly.
3. **Every important proposal says three things**: what appears on screen, how it works, why it improves the experience. An intention without these three is not a deliverable.
4. **Sophistication comes from composition, typography and interaction**, not from piling up effects. Modern is not dark mode. Creative is not complex.

## Doctrine

- **Validation by multiple-choice question.** The choice of a direction, and any doubt about a product rule, goes to the user (shape and degraded mode: see `clarify-with-choices`). Questions are asked in the target project's language.
- **File-backed.** The design document lives in the repository, not in the context window.
- **Readable.** The document opens with a TL;DR (what the redesign changes, the recommended direction, what the user must decide), and draws the journey and the screen architecture as Mermaid diagrams.
- **Degraded mode.** Without a browser, or without access to a screen (behind a login, a payment, a state you cannot reach), the skill says so, designs from the documentation and what the user shows it, and marks every point it could not check as a hypothesis.

## Phase 1 — Inspect

- Read the project documentation (glossary, rules, architecture, decisions).
- Walk the journey in a browser: entry point, each step, outcome, sharing, language switch, return visit. Note friction with the exact screen and action.
- Check accessibility on the spot: contrast, focus order and visibility, touch targets, reduced motion, error states.
- List the useful existing features that the redesign must keep.

## Phase 2 — Map the journey

Map the stages the product actually has, from the inspection, not from a template. Most interactive products have some of these; keep only the ones that exist, and add the ones that are specific to the product:

- **Discovery**: in a few seconds, what the product does, who it is for, what the user will have to do, what they will get. Make the first real action central; no long marketing page before trying. Never show a duration or a figure that is not known or measured.
- **Personalization or setup** (a profile, a goal, a context): a real step rather than an administrative form, understandable without overload, easy to confirm or change later.
- **The core interaction**: the task the product exists for. Comfortable reading, inputs easy to use by touch and keyboard, visible and reversible choices, going back without losing work, clear progress without artificial pressure, discreet transitions that support continuity. If the product collects judgments or answers, do not let the design steer them: no option looks "better" than another, no feedback that would bias what follows.
- **Outcome**: what the user leaves with (a result, a document, a decision, a purchase). Design it to be understood, not just looked at: hierarchy from summary to detail, then next actions if the data supports them. Choose the representation that compares best rather than the expected one. Be honest about what the outcome is and is not; no precision, ranking or statistic the product cannot justify.
- **Return**: what brings the user back, and what they find when they do.

## Phase 3 — Three directions

Propose three genuinely different directions, by default:

- **Editorial**: expressive typography, strong contrast, assertive composition.
- **Measuring instrument**: precision, landmarks, visualization, restraint.
- **Experimental**: a singular identity and original interactions, without sacrificing usability.

For each: concept and intended emotion; palette and color roles (with contrast ratios); type families and their use; screen composition; treatment of inputs, choices and progress; one signature interaction; trade-offs and UX risks. Then recommend one, argued against the product's goals, and say what you would borrow from the other two.

## Guardrails

- No generic template: purple gradient, cards everywhere, gratuitous glass.
- No childish gamification, arbitrary badges, systematic confetti.
- No decorative jargon.
- No mysterious navigation, custom cursor or hijacked scroll.
- No mandatory account added without need.
- Mobile is designed as an experience of its own, not a squeezed desktop.
- Accessible contrast, keyboard focus, error states and `prefers-reduced-motion` are designed, not left to implementation.
- Respect the project's technical invariants (for instance a strict CSP, no third-party resource): a direction that needs a forbidden dependency is not a valid direction.

## Deliverables

The design document holds, in this order:

1. **Diagnosis**: strengths, frictions, hypotheses to verify.
2. **Three creative directions** and the argued recommendation.
3. **User journey and screen architecture**.
4. **Text wireframes** of the key screens — at least the entry point, the core interaction and the outcome — desktop and mobile.
5. **Art direction and main components** (with their states: default, hover, focus, selected, disabled, error).
6. **Titles, CTAs and microcopy**, in the current language of the product (every language if it is multilingual).
7. **Priorities**: essential, improvement, experimentation.
8. **Validation plan**: comprehension, completion, drop-off and interpretation of the outcome — what to measure, how, and the threshold that would change the design.

## Common mistakes

| Mistake | Instead |
|---|---|
| Designing from screenshots or memory | Walk the live journey, then design |
| Reusing the stages of a past example | Stages come from this product's inspection |
| A duration or a "x % of users" figure | Only what is measured; otherwise say it is unknown |
| Three directions that differ only by palette | Differ by concept, composition and signature interaction |
| The expected chart by reflex | Choose the representation that compares best |
| Highlighting the "good" option | Neutral, equal treatment of every option |
| Intentions ("make it more fluid") | Screen, mechanism, reason |

## Fitting into the ecosystem

- **codebase-cartographer**: consume `docs/business/` when it exists; its glossary is the vocabulary of the microcopy.
- **codebase-harness**: the invariants bound the directions (see the guardrails).
- **plan-driven-dev**: the design document, once a direction is chosen, is the input of the plan that builds it.

Everything written outside this repository follows the language of the target project.
