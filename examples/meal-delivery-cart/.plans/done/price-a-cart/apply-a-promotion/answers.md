---
role: product-owner
status: done
reasons: []
---

# Answers to the Planner (story 2)

1. Q1, reasons: (a) closed set UNKNOWN_CODE and SUBTOTAL_BELOW_MINIMUM in one field; empty when applied or no code supplied; a valid code whose discount rounds to zero is applied. `answered` (human). D-33.
2. Q2, promotion in the rules: (a) optional; one promotion = one code, one rate, one minimum; exact-text code match. `answered` (human). D-34.
3. Q3, Percentage: (a) numerator over 10^scale, scale 0..18; negative numerator built, refused by the rules. `answered-by-delegate`. D-35.
4. Conflict architect note vs D-28: follow D-28; Percentage validates only its scale, the rules reject any rate outside 0..100 percent. `answered-by-delegate`. D-36.
