package io.example.mealcart.domain.money

import java.util.Currency
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import org.junit.jupiter.api.Test

class MoneyTest {

    private val eur: Currency = Currency.getInstance("EUR")
    private val jpy: Currency = Currency.getInstance("JPY")

    @Test
    fun `subtracting amounts in two currencies is refused`() {
        assertFailsWith<IllegalArgumentException> { Money(500, eur) - Money(200, jpy) }
    }

    @Test
    fun `subtracting gives the exact difference in the same currency`() {
        assertEquals(Money(300, eur), Money(500, eur) - Money(200, eur))
        assertEquals(Money(200, eur), Money(500, eur) - Money(300, eur))
    }

    @Test
    fun `amounts of the same currency compare by value, mixed currencies are refused`() {
        assertEquals(true, Money(999, eur) < Money(1000, eur))
        assertEquals(false, Money(1000, eur) < Money(1000, eur))
        assertEquals(true, Money(1001, eur) > Money(1000, eur))
        assertFailsWith<IllegalArgumentException> { Money(500, eur) < Money(200, jpy) }
    }

    private val max = Long.MAX_VALUE
    private val min = Long.MIN_VALUE

    private fun eur(minorUnits: Long) = Money(minorUnits, eur)

    @Test
    fun `adding stops exactly at the end of the range`() {
        assertEquals(eur(max), eur(max) + eur(0))
        assertEquals(eur(max), eur(max - 1) + eur(1))
        assertEquals(eur(min), eur(min) + eur(0))
        assertFailsWith<AmountTooLargeException> { eur(max) + eur(1) }
        assertFailsWith<AmountTooLargeException> { eur(max / 2 + 1) + eur(max / 2 + 1) }
        assertFailsWith<AmountTooLargeException> { eur(min) + eur(-1) }
        assertFailsWith<IllegalArgumentException> { eur(max) + Money(1, jpy) }
    }

    @Test
    fun `subtracting stops exactly at the end of the range`() {
        assertEquals(eur(min), eur(min) - eur(0))
        assertEquals(eur(min), eur(-1) - eur(max))
        assertEquals(eur(0), eur(max) - eur(max))
        assertFailsWith<AmountTooLargeException> { eur(-2) - eur(max) }
        assertFailsWith<AmountTooLargeException> { eur(0) - eur(min) }
        assertFailsWith<AmountTooLargeException> { eur(max) - eur(-1) }
    }

    @Test
    fun `multiplying by a quantity stops exactly at the end of the range`() {
        val twoToThe32 = 1L shl 32
        assertEquals(eur(max), eur(max) * 1)
        assertEquals(eur(min), eur(twoToThe32) * Int.MIN_VALUE)
        assertEquals(eur(0), eur(0) * Int.MAX_VALUE)
        assertFailsWith<AmountTooLargeException> { eur(max) * 2 }
        assertFailsWith<AmountTooLargeException> { eur(twoToThe32 + 1) * Int.MIN_VALUE }
        assertFailsWith<AmountTooLargeException> { eur(min) * -1 }
    }

    @Test
    fun `taking a rate stops exactly at the end of the range`() {
        assertEquals(eur(max), eur(max) * Percentage(1, 0))
        assertEquals(eur(max), eur(max) * Percentage(10L.pow(18), 18))
        assertEquals(eur(max - 1), eur(4611686018427387903) * Percentage(2, 0))
        assertEquals(eur(max), eur(1) * Percentage(max, 0))
        assertFailsWith<AmountTooLargeException> { eur(max) * Percentage(2, 0) }
        assertFailsWith<AmountTooLargeException> { eur(4611686018427387904) * Percentage(2, 0) }
        assertFailsWith<AmountTooLargeException> { eur(2) * Percentage(max, 0) }
        assertFailsWith<AmountTooLargeException> { eur(max) * Percentage(max, 18) }
    }

    @Test
    fun `a rate rounds half up before the result is checked against the range`() {
        // exact result max - 0.5 rounds up to max, which fits; exact result max + 0.5 rounds to max + 1, which does not
        assertEquals(eur(max), eur(252785) * Percentage(364870227143809, 1))
        assertFailsWith<AmountTooLargeException> { eur(33502085) * Percentage(2753074036095, 1) }
    }

    @Test
    fun `taking a rate of or from a negative amount is refused, zero is accepted`() {
        assertFailsWith<IllegalArgumentException> { eur(-1) * Percentage(10, 2) }
        assertFailsWith<IllegalArgumentException> { eur(min) * Percentage(10, 2) }
        assertFailsWith<IllegalArgumentException> { eur(100) * Percentage(-1, 2) }
        assertFailsWith<IllegalArgumentException> { eur(100) * Percentage(min, 2) }
        assertFailsWith<IllegalArgumentException> { eur(-1) * Percentage(0, 2) }
        assertFailsWith<IllegalArgumentException> { eur(0) * Percentage(-1, 2) }
        assertEquals(eur(0), eur(0) * Percentage(10, 2))
        assertEquals(eur(0), eur(100) * Percentage(0, 2))
        assertEquals(eur(0), eur(0) * Percentage(0, 18))
    }

    private fun Long.pow(exponent: Int) = (1..exponent).fold(1L) { power, _ -> power * this }
}
