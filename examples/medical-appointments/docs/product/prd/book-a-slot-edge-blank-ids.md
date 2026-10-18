# PRD: book a slot, edge case: empty, blank or absent identifiers

Edge case of `book-a-slot.md` (open point "empty or blank patient or slot identifiers", decision D-22). Status: ready.

## 1. Problem

A booking request can arrive with a patient identifier or a slot identifier that is absent, empty or only blank. Today the behavior is unspecified (D-22). The case asks plainly: what must the service answer, and must it ever create a booking?

## 2. Goal and success

No booking is ever created for a patient or slot that cannot be identified, and the caller learns that this is the reason. Measure: every such request is refused and changes nothing.

## 3. Users and use

A patient (through whatever calls the service) submits a booking request whose patient identifier or slot identifier is missing. The request is refused and nothing changes.

## 4. Scope

**In.** Absent, empty or blank patient identifier; absent, empty or blank slot identifier; where this check sits in the refusal order (D-21); whether it needs its own reason (D-26).

**Out.** Identifiers that are well-formed but unknown (already UNKNOWN_SLOT); surrounding whitespace inside an otherwise non-blank identifier; identifier format or length; patient accounts and authentication; how a caller is shown the refusal.

## 5. Requirements

1. A patient identifier that is absent, empty or blank is refused; no booking is created.
2. A slot identifier that is absent, empty or blank is refused; no booking is created.
3. "Blank" means an identifier with no character other than Unicode white space (spaces, tabs, line breaks and the other characters the Unicode standard classes as white space). An identifier with any other character is not blank, whatever surrounds it.
4. These refusals have one new reason, the same for the patient and the slot identifier, distinct from UNKNOWN_SLOT, PAST, TAKEN and OVERLAPPING. Its public name is left to the plan.
5. The check comes first: a request with a missing identifier is refused for that reason whatever the other rules would say. The order becomes: missing identifier, unknown slot, past, taken, overlap.
6. If both identifiers are missing, one refusal is reported.
7. The refusal changes nothing, as for every other refusal (req. 12 of `book-a-slot.md`).

## 6. Risks and open questions

Decisions:
- "Blank" = empty or white space only (Q1), **delegated** (recommendation of the Product Manager, relayed by the orchestrator, nobody read it; cheap to reverse).
- One new common reason (Q2), **human**.
- Check first in the order (Q3), **delegated**.

Technical unknown, for the architect: how an absent value reaches the service (not decided here).
