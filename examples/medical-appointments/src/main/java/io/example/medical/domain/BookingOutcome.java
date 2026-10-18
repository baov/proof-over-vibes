package io.example.medical.domain;

/** Result of a booking attempt (D-25): booked with the booking, or refused with one reason. */
public sealed interface BookingOutcome {

    record Booked(Booking booking) implements BookingOutcome {
    }

    record Refused(RefusalReason reason) implements BookingOutcome {
    }
}
