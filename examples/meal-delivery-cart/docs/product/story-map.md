# Story map: meal-delivery cart

Status: validated by the human. No existing product: no `done` item.

| Step | Epic | Candidate features (unordered) |
|---|---|---|
| 1. Choose dishes | Cart basics | Add a dish; change quantity; remove a dish; see the food subtotal |
| 2. Apply a promotion | Promotions | Enter a code; see the discount and what it changes; remove a code; refusal reason when a code does not apply |
| 3. See the fees | Fees and total | Delivery fee; other fee lines (service, small order); tax; tip; total updated live |
| 4. Understand the price | Price transparency | Line-by-line breakdown; why each line is there; before/after a promotion |
| 5. Order | Order handoff | Confirm the cart; the confirmed total equals the displayed total |
| Cross-cutting | Money rules configuration | Fee, tax, tip, currency and promotion rules as parameters, no market built in |

## Slices

1. **Walking skeleton (Now).** Add, change, remove dishes; subtotal; one fee line; one promotion type with its visible effect; live total; order handoff; money rules as parameters.
2. **Next.** Full fee lines (service, small order), tax, tip, promotion variants, breakdown explanations.
3. **Later.** Subscriptions, multi-restaurant carts (not on the backbone yet).
