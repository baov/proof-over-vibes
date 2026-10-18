# Roadmap: meal-delivery cart

Status: validated by the human. Horizons, not dates. Each epic serves a vision outcome (O1 total equals order total, O2 breakdown opened, O3 abandonment after fees).

## Now: walking skeleton (committed, detailed in the backlog)

- Cart basics, serves O1.
- Fees and total, one fee line, live total, serves O1 and O3.
- Promotions, one type with visible effect, serves O2 and O3.
- Order handoff, total equals displayed total, serves O1.
- Money rules configuration, serves all (no market built in).
- Outcome measurement, serves O1 to O3.

Assumption to re-check: one fee line and one promotion type are enough to tell whether visible fees change ordering (unknown 1 in `research.md`).

## Next: intended, shaped but open

- Full fee lines (service, small order), tax, tip: serves O1, O3.
- Promotion variants: serves O2, O3.
- Price transparency: line explanations, before/after a promotion: serves O2.

Assumption: customers read the breakdown (O2 shows it); promotions do change fees (weak source, unknown 3).

## Later: direction, no commitment

- Subscriptions that waive fees.
- Multi-restaurant carts.

Assumption: the fee-transparent customer cart finds its users before these widen scope.
