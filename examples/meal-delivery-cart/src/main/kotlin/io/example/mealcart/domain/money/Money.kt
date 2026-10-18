package io.example.mealcart.domain.money

import java.math.BigInteger
import java.util.Currency

/** An amount in the smallest unit of its currency. Arithmetic is exact: it refuses mixed currencies, and a result beyond the range of a Long is refused with [AmountTooLargeException]. */
data class Money(val minorUnits: Long, val currency: Currency) {

    operator fun plus(other: Money): Money {
        requireSameCurrency(other)
        return Money(exactly("$this + $other") { Math.addExact(minorUnits, other.minorUnits) }, currency)
    }

    operator fun minus(other: Money): Money {
        requireSameCurrency(other)
        return Money(exactly("$this - $other") { Math.subtractExact(minorUnits, other.minorUnits) }, currency)
    }

    operator fun times(quantity: Int): Money =
        Money(exactly("$this x $quantity") { Math.multiplyExact(minorUnits, quantity.toLong()) }, currency)

    operator fun compareTo(other: Money): Int {
        requireSameCurrency(other)
        return minorUnits.compareTo(other.minorUnits)
    }

    /**
     * The share of this amount the rate takes, rounded once, half up, to the smallest unit.
     * Both the amount and the numerator of the rate must be zero or more: the rounding is defined for them only.
     * The product is computed wide, so it is exact at any scale; the result must fit, or [AmountTooLargeException].
     */
    operator fun times(rate: Percentage): Money {
        require(minorUnits >= 0) { "A negative amount has no share: $minorUnits" }
        require(rate.numerator >= 0) { "A negative rate has no share: ${rate.numerator}" }
        val product = BigInteger.valueOf(minorUnits) * BigInteger.valueOf(rate.numerator)
        val (quotient, remainder) = product.divideAndRemainder(BigInteger.valueOf(rate.denominator))
        val roundedUp = if (remainder * TWO >= BigInteger.valueOf(rate.denominator)) quotient + BigInteger.ONE else quotient
        return Money(exactly("$this x $rate") { roundedUp.longValueExact() }, currency)
    }

    private inline fun exactly(operation: String, compute: () -> Long): Long =
        try {
            compute()
        } catch (overflow: ArithmeticException) {
            throw AmountTooLargeException("The result of $operation is beyond the range of an amount")
        }

    private fun requireSameCurrency(other: Money) =
        require(currency == other.currency) { "Amounts in different currencies: $currency and ${other.currency}" }

    companion object {
        private val TWO = BigInteger.valueOf(2)

        fun zero(currency: Currency) = Money(0, currency)
    }
}
