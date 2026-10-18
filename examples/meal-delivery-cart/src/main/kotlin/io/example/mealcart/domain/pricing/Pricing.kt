package io.example.mealcart.domain.pricing

import io.example.mealcart.domain.cart.Cart
import io.example.mealcart.domain.money.Money
import io.example.mealcart.domain.result.Price
import io.example.mealcart.domain.rules.PricingRules

fun price(cart: Cart, rules: PricingRules): Price {
    val subtotal = cart.lines.fold(Money.zero(rules.currency)) { sum, line -> sum + line.unitPrice * line.quantity }
    val discount = Money.zero(rules.currency)
    val feeLine = if (cart.lines.isEmpty()) null else rules.deliveryFee
    return Price(subtotal, discount, feeLine, total = subtotal - discount + (feeLine ?: Money.zero(rules.currency)))
}
