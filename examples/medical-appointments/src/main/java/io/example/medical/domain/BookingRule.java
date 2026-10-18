package io.example.medical.domain;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

/** The only place where booking refusals are decided and ordered (D-21). */
public final class BookingRule {

    public BookingOutcome decide(PatientId patient, Optional<Slot> slot, Instant now, Optional<Booking> activeBookingOnSlot,
                                  List<Slot> slotsHeldByPatient) {
        if (slot.isEmpty()) {
            return new BookingOutcome.Refused(RefusalReason.UNKNOWN_SLOT);
        }
        if (slot.get().range().start().isBefore(now)) {
            return new BookingOutcome.Refused(RefusalReason.PAST);
        }
        if (activeBookingOnSlot.isPresent()) {
            return new BookingOutcome.Refused(RefusalReason.TAKEN);
        }
        if (slotsHeldByPatient.stream().anyMatch(held -> held.range().overlaps(slot.get().range()))) {
            return new BookingOutcome.Refused(RefusalReason.OVERLAPPING);
        }
        return new BookingOutcome.Booked(new Booking(patient, slot.get().id()));
    }
}
