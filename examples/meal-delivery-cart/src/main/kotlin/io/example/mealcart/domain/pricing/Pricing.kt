package io.example.mealcart.domain.pricing

import io.example.mealcart.domain.cart.Cart
import io.example.mealcart.domain.money.Money
import io.example.mealcart.domain.result.Price
import io.example.mealcart.domain.result.PromotionNotApplied
import io.example.mealcart.domain.rules.PricingRules

fun price(cart: Cart, rules: PricingRules, code: String? = null): Price {
    require(cart.lines.all { it.unitPrice.currency == rules.currency }) {
        "A line is not in the currency of the rules, ${rules.currency}"
    }
    val zero = Money.zero(rules.currency)
    val subtotal = cart.lines.fold(zero) { sum, line -> sum + line.unitPrice * line.quantity }
    val promotion = rules.promotion
    val notApplied = when {
        code == null -> null
        promotion == null || code != promotion.code -> PromotionNotApplied.UNKNOWN_CODE
        subtotal < promotion.minimumSubtotal -> PromotionNotApplied.SUBTOTAL_BELOW_MINIMUM
        else -> null
    }
    val discount = if (code != null && promotion != null && notApplied == null) subtotal * promotion.rate else zero
    val feeLine = if (cart.lines.isEmpty()) null else rules.deliveryFee
    return Price(subtotal, discount, feeLine, total = subtotal - discount + (feeLine ?: zero), promotionNotApplied = notApplied)
}
