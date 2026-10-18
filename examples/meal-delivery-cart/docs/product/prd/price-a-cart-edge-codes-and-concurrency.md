# PRD: price a cart, edge cases on codes and simultaneous use

Status: ready. Q4 answered and read by the human; none delegated. C2 to C6 restate R3 and R5, not a new bet. Follows `price-a-cart.md` and settles the two reserved items "blank or empty identifiers and codes" and "two operations on the same cart at the same moment" (D-30 style reservation, PRD section 6). Current promotion matching: exact text, case-sensitive, no trimming; the rules may have no promotion (D-34); an unknown code gives the reason UNKNOWN_CODE and no discount (D-33).

## 1. Problem

- Facts to confirm: a code that is empty or only blank is, today, either matched as ordinary text (so it gives UNKNOWN_CODE) or accepted as a promotion code in the rules; nobody decided which one the business wants. The code was not read for this PRD.
- A customer who clears the code field should not be told that a code failed.
- Several callers may price the same cart at the same moment (for example two screens, or a retry). Nothing states what the business expects.

## 2. Goal and success

A blank code never produces a surprising price or message. Whatever the number of simultaneous pricings, each gets the answer it would get alone. Success: O1 holds under repeated and parallel calls.

## 3. Users and use

Same caller as `price-a-cart.md`; the code arrives as text from a customer, possibly empty.

## 4. Scope

In: the promotion code supplied with a cart; a blank promotion code in the rules; simultaneous pricing.
Out: amounts (see `price-a-cart-edge-amounts.md`); a catalogue, sessions, editing a cart.

## 5. Requirements

Definition: a text is *empty* when it has no characters and *blank* when it is empty or has only whitespace.

Independent of the open questions:
- C1. A non-blank code keeps its present meaning: exact text, case-sensitive, no trimming (D-34); a code with a leading or trailing space is a different, unknown code.
- C2. Pricing a cart does not change the cart or the rules (R5), so one pricing can never alter the result of another.
- C3. Any number of pricings of the same cart and rules at the same moment each return the same breakdown, identical to the breakdown the same pricing gives alone (R3), whatever the order or timing.
- C4. A pricing never waits for, or fails because of, another pricing of the same cart.
- C5. A result always matches one whole cart as it was handed in: never a mix of two versions of a cart.
- C6. No result depends on a hidden counter, clock, or earlier call (R3).

Blank codes (Q4):
- C7. A blank or empty code supplied with a cart means no code: no discount, no reason, pricing succeeds as without a code (R11).
- C8. A blank or empty promotion code in the rules is refused when the rules are built; no cart is priced with them.
- C9. The currency is not affected: it is a typed currency, not text, so C8 concerns the promotion code only. No other blank identifier is known to the feature or the decisions.

## 6. Risks and open questions left open

Technical, named not answered, for the architect and orchestrator: how whitespace is defined (which characters); that the cart and rules are immutable from outside; how C3 to C5 are checked by tests (repeated and parallel calls); thread-safety of anything shared. The business asks only that C2 to C6 be true, not how.

If a later feature lets a caller edit a cart while it is priced, C5 would need to be read again with that feature.

## 7. Open questions

None remaining. Q4 (C7 to C9) was answered and read by the human.
