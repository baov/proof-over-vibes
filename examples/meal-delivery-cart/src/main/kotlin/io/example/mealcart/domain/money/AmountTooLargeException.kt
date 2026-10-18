package io.example.mealcart.domain.money

/**
 * An amount, or the result of an operation on amounts, is beyond what [Money] can hold (a signed 64-bit count of minor units).
 * An [ArithmeticException], so a caller that already catches that one still catches this one; never an [IllegalArgumentException],
 * which stays the refusal of invalid input. The message is for a human and is not a contract.
 */
class AmountTooLargeException(message: String) : ArithmeticException(message)
