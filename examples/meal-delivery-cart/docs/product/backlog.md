# Backlog: meal-delivery cart

Status: validated by the human. Order = priority. No stories, no acceptance criteria: they come in a PRD when the human picks an item. Status of all items: *idea*, except items 4 to 7 (*picked*, as one feature "price a cart").

Method: MoSCoW for the skeleton (Now); value against effort within Next (coarse judgment, no data, to be revised). Reasoning is given per line.

## Now: walking skeleton (MoSCoW)

| # | Epic / feature | Value | MoSCoW |
|---|---|---|---|
| 1 | Cart basics / add a dish | Without it there is no cart | Must |
| 2 | Cart basics / change quantity and remove a dish | A cart that cannot be corrected is unusable | Must |
| 3 | Cart basics / food subtotal | Base of every other line | Must |
| 4 | Money rules configuration / fee, promotion and currency rules as parameters | Vision stance: no market built in | Must | *(picked: feature "price a cart", `prd/price-a-cart.md`)*
| 5 | Fees and total / one fee line shown, labelled | The core promise, minimal form (O1, O3) | Must | *(picked: feature "price a cart", `prd/price-a-cart.md`)*
| 6 | Fees and total / live total | The customer sees the cost as the cart changes (O1) | Must | *(picked: feature "price a cart", `prd/price-a-cart.md`)*
| 7 | Promotions / apply one promotion type and see its effect | Second half of the promise (O2, O3) | Must | *(picked: feature "price a cart", `prd/price-a-cart.md`)*
| 8 | Order handoff / confirm cart, confirmed total equals displayed total | Anti-goal and O1 | Must |
| 9 | Promotions / remove a code; reason when a code does not apply | Avoids a dead end; skeleton works without it | Should |
| 10 | Outcome measurement / track O1 to O3 | Vision outcomes need data; a skeleton can ship before it | Should |

Won't (skeleton): tax, tip, extra fee lines, promotion variants, explanations (all in Next).

## Next: value against effort (judgment, unverified)

| # | Epic / feature | Value | Effort | Reasoning |
|---|---|---|---|---|
| 11 | Price transparency / line-by-line explanations | High | Medium | The positioning itself (O2) |
| 12 | Fees and total / service and small-order fee lines | High | Medium | Completes the fee picture (O1, O3) |
| 13 | Price transparency / before and after a promotion | High | Low | Cheap once 7 exists (O2) |
| 14 | Promotions / variants | Medium | Medium | Widens coverage; depends on 7 |
| 15 | Fees and total / tax | Medium | High | Rules differ by place, so parameters get heavy |
| 16 | Fees and total / tip | Low | Low | Common but not core to the promise |

## Later

| # | Epic / feature | Note |
|---|---|---|
| 17 | Subscriptions that waive fees | Direction only |
| 18 | Multi-restaurant carts | Direction only |
