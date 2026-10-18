# Roadmap

Horizons, not dates. Each epic serves an outcome of `vision.md`. Validated by the human.

## Now (committed; features in the backlog)

- **E1 Browse free slots**: a patient sees a practitioner's free slots. Serves: easy booking.
- **E2 Book a slot**: a patient books one; never double-booked. Serves: no double-booking, easy booking.
- **E3 Cancel a booking**: a patient cancels; the slot is bookable again. Serves: slot reuse.
- **E4 Practitioner availability**: a practitioner defines when they are free. Serves: slots exist at all.

Assumption: one practitioner is enough to prove the three verbs; availability can be preloaded first (skeleton), then made practitioner-managed.

## Next (intended, shaped but open)

- **E5 Data protection**: collect the minimum, keep health-related booking data protected. Serves: anti-goal "collecting more than needed". Assumption: GDPR applies (EU), still *unverified* from primary texts.
- **E6 Reminders**: patients are reminded before a visit. Serves: fewer lost slots. Assumption: forgetting drives no-shows (sourced in `research.md`, setting-specific).

## Later (direction, no commitment)

- **E7 Rescheduling**: move a booking in one step. Assumption: cancel then book is acceptable until then.

Out of scope: pricing (learning example), video, messaging, marketplace reach (anti-goal: feature creep).
