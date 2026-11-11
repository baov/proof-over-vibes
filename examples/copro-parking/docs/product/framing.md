# Framing: parking rental in a co-ownership

Source: `brief.md` ("Renting parking spaces within a co-ownership."). Status: answered; the defaults below were recommendations.

## Ambiguities

- **Who rents out**: an owner lending their own space, the co-ownership (syndic) renting common spaces, or both.
- **Who rents**: other residents only, outside visitors, or both.
- **"Renting"**: long-term lease (monthly), short-term (day/hour), or both.
- **"Within a co-ownership"**: one building, or a platform serving many.

## Assumptions

- Spaces are individually numbered and owned by lots (*inferred*).
- A co-ownership exists as a legal frame, hence a French-law notion (*inferred*: France).
- Rent is paid by the renter (*inferred*).

## Contradictions

None.

## Missing information

Delivery stage, actors and their rights, money rules, legal frame, booking rules (conflicts, calendar), notification channels. Technical unknowns (storage, auth): for `architect`.

## Questions (ranked)

1. **Delivery stage** — decision: size of the scope. Risk: a product-grade scope for a proof of concept. Default: proof of concept.
2. **Who rents and who owns** — decision: actors and permissions. Risk: wrong core model. Default: owners offer spaces, residents rent them, a manager arbitrates.
3. **Money rules** — decision: is payment, pricing and rent calculation in scope. Risk: scope explosion. Default: the product records a price and the amount due; no payment processing.
4. **Jurisdiction** — decision: which rules (lease duration, owner consent, taxes) apply. Risk: rules built for the wrong country. Default: France, and no legal rule encoded in the first increment.

## Answers (human)

1. Stage: **C**, a product for many co-ownerships.
2. Actors: **A**, owners offer their spaces, residents rent them, a manager arbitrates.
3. Money: **A**, record price and amount due only, no payment processing.
4. Jurisdiction: **B**, France, lease and consent rules encoded from the start (the rules themselves: *unverified*, to source).

## Decisions after the market watch (human)

- Positioning: resident-to-resident rental under a manager's control.
- French rules: the human will provide the list before E5 starts; none invented, E5 outside the first PRD.
- Order: core cycle, then legal rules, then multi-tenancy.
- First PRD: F1.2 Register lots and spaces.
