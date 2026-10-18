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

    operator fun compareTo(other: Money): Int {
        requireSameCurrency(other)
        return minorUnits.compareTo(other.minorUnits)
    }

    /** The share of this amount the rate takes, rounded once, half up, to the smallest unit. */
    operator fun times(rate: Percentage): Money =
        Money(divideHalfUp(Math.multiplyExact(minorUnits, rate.numerator), rate.denominator), currency)

    private fun divideHalfUp(dividend: Long, divisor: Long): Long {
        val quotient = dividend / divisor
        val remainder = dividend % divisor
        return if (2 * remainder >= divisor) quotient + 1 else quotient
    }

    private fun requireSameCurrency(other: Money) =
        require(currency == other.currency) { "Amounts in different currencies: $currency and ${other.currency}" }

    companion object {
        fun zero(currency: Currency) = Money(0, currency)
    }
}
