---
role: product-owner
status: done
reasons: []
---

# Answers to the Planner (story 2)

All `answered-by-delegate`, recorded in `docs/business/decisions.md`. Where the sources are silent the lowest-impact option is kept and flagged for a person to revisit.

- **Q1 who may read** -> D-24: no restriction in the module; access control belongs to the sign-in layer. Flagged privacy risk.
- **Q2 id collision on send** -> D-25: rejected with `request-id-taken`, no overwrite.
- **Q3 erase a member** -> D-26: always `{ ok: true }`; second call and unknown member are successful no-ops.
- **R2-a** -> D-27 decline by non-recipient reuses `not-recipient`; D-28 `not-sender` for withdraw; D-29 `previously-declined`; D-30 one shared `not-pending`.
- **R2-b** -> D-31: `request-not-found` for decline and withdraw.

- **Send breaking a rule with an id already used** -> D-32: business rules first; `request-id-taken` only when the rules allow the send.
