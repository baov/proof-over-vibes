# ADR-0004: Offers: a separate store, an injected clock, the owner role with a declared name

Status: accepted

## TL;DR
Offers live in a third JSON file, apart from the register and the rules. "Today" comes from a `Clock` port. Offer use cases are the first to accept a role other than manager (the owner), identified only by a name the caller declares. This extends ADR-0003 and ADR-0002; it supersedes neither.

## Context
F2.1 (owner offers a space). There are no accounts (D-18); the offerer gives a name (D-46); a start date in the past is refused (D-47, D-53), so the domain needs to know today; offers must survive a restart and must not touch the register or rules files (PRD 13).

## Decision
- **Store**: one JSON file for the offers, `{"next_number": n, "offers": [{"number", "space", "start", "end"}]}`, dates in ISO `YYYY-MM-DD`. Same adapter pattern as ADR-0002 (whole file, shared atomic write, no constraint enforced by the store). A withdrawn offer is deleted; `next_number` is never reused. An unreadable file ends with `OffersUnreadable` (a `StoreUnreadable`) and is never overwritten. Overlap is not a load check: a stored file holding two offers of one space that share a day loads and both stay listed; overlap is checked only when adding an offer (D-63, D-64), because nothing can repair such a file before withdrawal exists (S3), so refusing to load it would lock the feature.
- **Clock**: a `Clock` port in `application` (`today() -> date`). The domain and the use cases never read the system date; the adapter returns the local date of the machine; tests inject a fixed one. No time of day, no time zone.
- **Role and identity**: offer and withdraw take the actor's role explicitly (ADR-0003) and accept `Role.OWNER` only; the offerer's name is compared with the current owner of the lot, ignoring case and surrounding spaces. The name proves nothing about who is typing: a stated limit, not a control.
- **Removal**: a new `OfferCheck` port (`has_open_offer(space_number)`) beside `RentalCheck`, which stays untouched ("no rental", PRD 14). `remove_space` takes both.

## Consequences
- The offers file format is a contract of the adapter only; changing it needs a migration.
- Public types (use case signatures, `OfferEntry`, `OfferRequest`, the new refusals) become a contract like ADR-0003's. The signature of `remove_space` gains the `offers` parameter: a breaking change for its callers, forced by D-51.
- Concurrency (decided by the human): single process, no lock, as ADR-0002. Several owners are now writers, so two simultaneous offers could both pass the overlap check; this limit is stated, not prevented. A lock becomes the concern of the adapter that introduces concurrency (a UI or a server).
- `change_space_number` also takes `OfferCheck` and refuses a space with an open offer as "space offered" (decided by the human); `withdraw_offer` takes the clock and refuses an offer that is no longer open as unknown.
