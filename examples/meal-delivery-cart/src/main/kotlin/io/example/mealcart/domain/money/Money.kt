package io.example.mealcart.domain.money

import java.util.Currency

/** An amount in the smallest unit of its currency. Arithmetic is exact and refuses mixed currencies. */
data class Money(val minorUnits: Long, val currency: Currency) {

    operator fun plus(other: Money): Money {
        requireSameCurrency(other)
        return Money(Math.addExact(minorUnits, other.minorUnits), currency)
    }

    operator fun minus(other: Money): Money {
        requireSameCurrency(other)
        return Money(Math.subtractExact(minorUnits, other.minorUnits), currency)
    }

    operator fun times(quantity: Int): Money = Money(Math.multiplyExact(minorUnits, quantity.toLong()), currency)

    private fun requireSameCurrency(other: Money) =
        require(currency == other.currency) { "Amounts in different currencies: $currency and ${other.currency}" }

    companion object {
        fun zero(currency: Currency) = Money(0, currency)
    }
}
