# Run notes

Written by the Orchestrator while the run happens. Honest log: what the roles did, what the human decided, and what the Orchestrator did itself.

## Delegation

Unlike the first example, the human chose the middle way here: the Orchestrator answers the cheap-to-reverse technical questions with the role's recommendation, and every bet of the Product Manager and every escalation of a role goes to the human. Entries in the decision log are `answered` (read by the human) or `answered-by-delegate` (Orchestrator's relay of a recommendation, nobody read it).

## Product phase

| Step | Role | Outcome |
|---|---|---|
| Idea (one sentence, written by the Orchestrator) | | "An online booking service for medical appointments where patients see a practitioner's free slots, book one, and cancel it." |
| Market watch | Product Manager | `research.md`; escalated 3 bets |
| Positioning, country, nature | human | narrow and simple; EU (GDPR); learning example (price model out of scope) |
| Vision | Product Manager | written; escalated success measures, first slice, horizons, prioritization |
| Success, first slice, horizons, prioritization | human | the three measures; see/book/cancel for one practitioner; Now = skeleton + practitioner availability (not the PM's recommendation); MoSCoW |
| Roadmap, story map, backlog | Product Manager | written, nothing picked |
| Backlog pick | human | F2.1 + F2.2, "book a slot" |
| PRD | Product Manager | escalated 3 rules |
| Rules | human | past slot refused; several bookings per patient but no overlap (not the PM's recommendation); re-booking an own slot refused |
| PRD | Product Manager | ready; two boundary conventions stated by the PM without source (back-to-back slots do not overlap, a slot starting exactly now can be booked), flagged, not asked: nobody read them |
