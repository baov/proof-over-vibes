package io.example.mealcart.domain.rules

import io.example.mealcart.domain.money.Money
import java.util.Currency

/** The money rules, all given by the caller: nothing is built in. The fee must be in the currency of the rules. */
data class PricingRules(val currency: Currency, val deliveryFee: Money) {
    init {
        require(deliveryFee.currency == currency) {
            "The delivery fee is in ${deliveryFee.currency}, the rules are in $currency"
        }
    }
}
