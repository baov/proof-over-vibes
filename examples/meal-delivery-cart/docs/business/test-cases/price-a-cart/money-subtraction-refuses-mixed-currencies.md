---
feature: price-a-cart
type: functional
priority: medium
source: ADR-0002; Story 2 criterion 2 (derived)
automated_test: src/test/kotlin/io/example/mealcart/domain/money/MoneyTest.kt::subtracting amounts in two currencies is refused
status: covered
---

# Subtracting amounts in two currencies is refused

- Given: two amounts, one in euros and one in yen
- When: one is subtracted from the other
- Then: the subtraction is refused: amounts of different currencies are never mixed
