---
role: product-owner
status: done
reasons: []
---

# Answers to the Planner (story 2)

- **D-27 (answered, human):** a slot's time range is valid only if its end is strictly after its start. A zero-length, inverted or absent range is rejected at creation. This also settles the PRD's overlap formula versus its sentence for a zero-length slot.
- **D-28 (answered, human):** two overlapping slots of the same practitioner may be booked by two different patients. The overlap rule stays per patient (req 9); the practitioner's agenda consistency belongs to F4.1.
- **D-29 (answered-by-delegate):** an invalid time range is reported at slot creation by an exception (IllegalArgumentException), so every Slot is valid by construction. Source: D-27 and the Planner's recommendation.
