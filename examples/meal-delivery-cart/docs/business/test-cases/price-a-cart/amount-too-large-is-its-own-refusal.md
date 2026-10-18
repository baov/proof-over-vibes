---
feature: price-a-cart
type: functional
priority: high
source: PRD A3, D-38
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::amount too large is its own refusal, apart from invalid input
status: covered
---

# Amount too large is its own refusal, apart from invalid input

- Given: a cart beyond the money range, a line of quantity zero and a rate out of range
- When: each is priced or built
- Then: the first gives amount too large (an arithmetic error, not invalid input); the others still give invalid input and never amount too large
