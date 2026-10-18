package io.example.medical.adapters;

import io.example.medical.application.BookingStore;
import io.example.medical.domain.Booking;
import io.example.medical.domain.Slot;
import io.example.medical.domain.SlotId;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Supplier;

/** In-memory adapter: one lock makes check-and-save a single atomic unit. */
public final class InMemoryBookingStore implements BookingStore {

    private final Map<SlotId, Slot> slots = new HashMap<>();
    private final Map<SlotId, Booking> bookings = new HashMap<>();
    private final ReentrantLock lock = new ReentrantLock();

    public InMemoryBookingStore(List<Slot> slots) {
        slots.forEach(slot -> this.slots.put(slot.id(), slot));
    }

    @Override
    public Optional<Slot> findSlot(SlotId slot) {
        return Optional.ofNullable(slots.get(slot));
    }

    @Override
    public Optional<Booking> activeBookingOf(SlotId slot) {
        lock.lock();
        try {
            return Optional.ofNullable(bookings.get(slot));
        } finally {
            lock.unlock();
        }
    }

    @Override
    public void save(Booking booking) {
        lock.lock();
        try {
            bookings.put(booking.slot(), booking);
        } finally {
            lock.unlock();
        }
    }

    @Override
    public <T> T atomically(Supplier<T> unit) {
        lock.lock();
        try {
            return unit.get();
        } finally {
            lock.unlock();
        }
    }
}
