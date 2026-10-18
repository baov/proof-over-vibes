package io.example.mealcart.domain.rules

import io.example.mealcart.domain.money.Money
import java.util.Currency

/** The money rules, all given by the caller: nothing is built in. The fee and the promotion minimum must be in the currency of the rules, and the promotion rate within 0 to 100 percent. */
data class PricingRules(val currency: Currency, val deliveryFee: Money, val promotion: Promotion? = null) {
    init {
        require(deliveryFee.currency == currency) {
            "The delivery fee is in ${deliveryFee.currency}, the rules are in $currency"
        }
        if (promotion != null) {
            val rate = promotion.rate
            require(rate.numerator in 0..rate.denominator) {
                "The promotion rate ${rate.numerator}/10^${rate.scale} is outside 0 to 100 percent"
            }
            require(promotion.minimumSubtotal.currency == currency) {
                "The promotion minimum is in ${promotion.minimumSubtotal.currency}, the rules are in $currency"
            }
        }
    }
}
