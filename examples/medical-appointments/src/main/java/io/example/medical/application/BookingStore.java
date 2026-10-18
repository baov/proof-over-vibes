package io.example.medical.application;

import io.example.medical.domain.Booking;
import io.example.medical.domain.PatientId;
import io.example.medical.domain.Slot;
import io.example.medical.domain.SlotId;

import java.util.List;
import java.util.Optional;
import java.util.function.Supplier;

/** Port: slots and their bookings. Check and save of a booking happen in one atomic unit. */
public interface BookingStore {

    Optional<Slot> findSlot(SlotId slot);

    Optional<Booking> activeBookingOf(SlotId slot);

    /** The slots a patient holds through an active booking. */
    List<Slot> slotsHeldBy(PatientId patient);

    void save(Booking booking);

    <T> T atomically(Supplier<T> unit);
}
