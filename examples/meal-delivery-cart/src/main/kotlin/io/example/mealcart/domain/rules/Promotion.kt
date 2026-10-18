package io.example.mealcart.domain.rules

import io.example.mealcart.domain.money.Money
import io.example.mealcart.domain.money.Percentage

/** One code, the rate it takes off the food subtotal, and the subtotal it needs to apply. */
data class Promotion(val code: String, val rate: Percentage, val minimumSubtotal: Money)
