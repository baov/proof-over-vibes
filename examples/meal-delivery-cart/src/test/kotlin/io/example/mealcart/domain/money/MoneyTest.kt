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
}
