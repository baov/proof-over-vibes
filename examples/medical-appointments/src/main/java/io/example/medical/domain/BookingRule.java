package io.example.medical.domain;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.regex.Pattern;

/** The only place where booking refusals are decided and ordered (D-21). */
public final class BookingRule {

    /** Empty, or only Unicode White_Space: String.isBlank would miss non-breaking spaces (D-33, D-37). */
    private static final Pattern ONLY_WHITE_SPACE = Pattern.compile("\\p{IsWhite_Space}*");

    /** True when an identifier is absent, empty or blank: the booking cannot even be looked at. */
    public static boolean isMissing(PatientId patient, SlotId slot) {
        return isMissing(patient == null ? null : patient.value()) || isMissing(slot == null ? null : slot.value());
    }

    private static boolean isMissing(String value) {
        return value == null || ONLY_WHITE_SPACE.matcher(value).matches();
    }

    public BookingOutcome decide(PatientId patient, SlotId slotId, Optional<Slot> slot, Instant now,
                                  Optional<Booking> activeBookingOnSlot, List<Slot> slotsHeldByPatient) {
        if (isMissing(patient, slotId)) {
            return new BookingOutcome.Refused(RefusalReason.MISSING_IDENTIFIER);
        }
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
