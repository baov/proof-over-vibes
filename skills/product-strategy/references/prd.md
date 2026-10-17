# Phase 4: the PRD

A product requirements document for **one feature**, written when the user picks it. Output: `docs/product/prd/<feature>.md`. It says what and why, never how: the structure is the architect's, the plan is the planner's.

## Contents

1. **Problem**: who has it, in which situation, and the evidence from the market watch.
2. **Goal and success**: the outcome and how it is measured.
3. **Users and use**: who uses the feature and the main path they follow.
4. **Scope**: what is in, and what is explicitly out.
5. **Requirements**: what the feature must do, each one testable. These become the acceptance criteria of the request.
6. **Risks and open questions**: the assumptions that, if false, change the feature, and the technical unknowns (real time, several users at once, sensitive data, an external dependency). Name them without answering them: the structure is not decided here.

## Rules

- Each requirement is observable from the outside; none names a technology.
- Use the vocabulary of the business glossary when it exists.
- No user stories beyond the main path: they are cut when the work is planned.
- End on a multiple-choice question for what remains open; do not guess it.
- Hand-off: the user creates the request and cites the PRD. Do not start the work.
