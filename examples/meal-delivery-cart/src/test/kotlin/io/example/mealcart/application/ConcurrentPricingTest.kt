package io.example.mealcart.application

import io.example.mealcart.domain.cart.Cart
import io.example.mealcart.domain.cart.CartLine
import io.example.mealcart.domain.money.Money
import io.example.mealcart.domain.money.Percentage
import io.example.mealcart.domain.rules.PricingRules
import io.example.mealcart.domain.rules.Promotion
import java.util.Currency
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test

/**
 * Simultaneous pricings of the same cart and rules each give the result they give alone.
 *
 * A green run shows that this run did not misbehave, not that no interleaving can: the guarantee for every
 * interleaving is structural (ADR-0004, INV-007, INV-004). These tests are a smoke check and a tripwire.
 */
class ConcurrentPricingTest {

    private val eur: Currency = Currency.getInstance("EUR")
    private val jpy: Currency = Currency.getInstance("JPY")
    private val code = "WELCOME10"
    private val threads = 16
    private val rounds = 20000
    private val timeoutSeconds = 30L

    private fun eur(minorUnits: Long) = Money(minorUnits, eur)

    private val rules = PricingRules(eur, eur(250), Promotion(code, Percentage(10, 2), eur(1000)))

    private val bigCart = Cart(listOf(CartLine(eur(800), 2), CartLine(eur(350), 1), CartLine(eur(125), 3)))
    private val smallCart = Cart(listOf(CartLine(eur(300), 2)))

    /** Starts [count] threads, releases them together, joins them within the timeout; returns what they threw. */
    private fun runTogether(count: Int, task: (Int) -> Unit): List<Throwable> {
        val thrown = ConcurrentLinkedQueue<Throwable>()
        val gate = CountDownLatch(1)
        val workers = (0 until count).map { index ->
            Thread {
                try {
                    gate.await()
                    task(index)
                } catch (t: Throwable) {
                    thrown.add(t)
                }
            }.apply { isDaemon = true }
        }
        workers.forEach { it.start() }
        gate.countDown()
        workers.forEach {
            it.join(TimeUnit.SECONDS.toMillis(timeoutSeconds))
            assertTrue(!it.isAlive, "a pricing did not finish within $timeoutSeconds seconds")
        }
        return thrown.toList()
    }

    @Test
    fun `simultaneous pricings of one cart give the result each gives alone`() {
        val calls = listOf(
            Triple(bigCart, code, "valid"),
            Triple(bigCart, "OTHER", "unknown"),
            Triple(smallCart, code, "below the minimum"),
            Triple(bigCart, " ", "blank"),
            Triple(bigCart, null, "no code"),
        )
        val solo = calls.map { (cart, supplied, _) -> PriceCart.price(cart, rules, supplied) }
        val linesBefore = bigCart.lines.toList()
        val rulesBefore = rules.copy()

        val thrown = runTogether(threads) {
            repeat(rounds) {
                calls.forEachIndexed { i, (cart, supplied, name) ->
                    assertEquals(solo[i], PriceCart.price(cart, rules, supplied), name)
                }
            }
        }

        assertEquals(emptyList(), thrown)
        assertEquals(linesBefore, bigCart.lines)
        assertEquals(rulesBefore, rules)
    }

    @Test
    fun `different carts priced at once never mix`() {
        val carts = (0 until threads).map { i ->
            Cart(listOf(CartLine(eur(100L + i * 7), i + 1), CartLine(eur(50), 1)))
        }
        val solo = carts.map { PriceCart.price(it, rules, code) }

        val thrown = runTogether(threads) { i ->
            repeat(rounds) {
                val result = PriceCart.price(carts[i], rules, code)
                assertEquals(solo[i], result, "cart $i")
                assertEquals(eur((100L + i * 7) * (i + 1) + 50), result.subtotal, "subtotal of cart $i")
            }
        }

        assertEquals(emptyList(), thrown)
        assertEquals(threads, solo.map { it.subtotal }.toSet().size)
    }

    @Test
    fun `repeated pricings give the same result in any order`() {
        val first = PriceCart.price(bigCart, rules, code)
        val second = PriceCart.price(smallCart, rules, code)

        repeat(1000) {
            assertEquals(first, PriceCart.price(bigCart, rules, code))
            assertEquals(second, PriceCart.price(smallCart, rules, code))
        }
        repeat(1000) {
            assertEquals(second, PriceCart.price(smallCart, rules, code))
            assertEquals(first, PriceCart.price(bigCart, rules, code))
        }
        repeat(1000) { PriceCart.price(smallCart, rules, code) }
        assertEquals(first, PriceCart.price(bigCart, rules, code))
    }

    @Test
    fun `a pricing never fails or waits because of another`() {
        val carts = (0 until threads).map { i -> Cart(listOf(CartLine(eur(100L + i), i + 1))) }

        val thrown = runTogether(threads * 2) { i ->
            repeat(rounds) {
                PriceCart.price(carts[i % threads], rules, if (i % 2 == 0) code else null)
                PriceCart.price(bigCart, rules, code)
            }
        }

        assertEquals(emptyList(), thrown)
    }

    @Test
    fun `a refusal in one thread does not disturb the other pricings`() {
        val foreign = Cart(listOf(CartLine(Money(500, jpy), 1)))
        val solo = PriceCart.price(bigCart, rules, code)
        val refusals = ConcurrentLinkedQueue<String>()

        val thrown = runTogether(threads) { i ->
            repeat(rounds) {
                if (i % 2 == 0) {
                    val refusal = assertFailsWith<IllegalArgumentException> { PriceCart.price(foreign, rules, code) }
                    refusals.add(refusal.javaClass.name)
                } else {
                    assertEquals(solo, PriceCart.price(bigCart, rules, code))
                }
            }
        }

        assertEquals(emptyList(), thrown)
        assertEquals(threads / 2 * rounds, refusals.size)
    }

    @Test
    fun `an empty cart priced at once with a blank code or no code gives the same result`() {
        val empty = Cart(emptyList())
        val solo = PriceCart.price(empty, rules)

        val thrown = runTogether(threads) { i ->
            repeat(rounds) {
                assertEquals(solo, PriceCart.price(empty, rules, if (i % 2 == 0) "" else null))
            }
        }

        assertEquals(emptyList(), thrown)
    }
}
