package io.example.medical.domain;

import java.util.Optional;

/** The only place where booking refusals are decided and ordered (D-21). */
public final class BookingRule {

    public BookingOutcome decide(PatientId patient, Slot slot, Optional<Booking> activeBookingOnSlot) {
        if (activeBookingOnSlot.isPresent()) {
            return new BookingOutcome.Refused(RefusalReason.TAKEN);
        }
        return new BookingOutcome.Booked(new Booking(patient, slot.id()));
    }
}
