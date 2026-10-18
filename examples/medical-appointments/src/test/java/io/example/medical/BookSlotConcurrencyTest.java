package io.example.medical;

import io.example.medical.adapters.InMemoryBookingStore;
import io.example.medical.application.BookSlot;
import io.example.medical.application.BookingStore;
import io.example.medical.domain.Booking;
import io.example.medical.domain.BookingOutcome;
import io.example.medical.domain.PatientId;
import io.example.medical.domain.PractitionerId;
import io.example.medical.domain.Slot;
import io.example.medical.domain.SlotId;
import io.example.medical.domain.TimeRange;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Simultaneous bookings. These tests say nothing about what the person who loses is shown: that is an open
 * product question. They only require that the rules of a single booking hold under simultaneity.
 */
class BookSlotConcurrencyTest {

    private static final Instant NOW = Instant.parse("2030-01-01T09:00:00Z");
    private static final Clock CLOCK = Clock.fixed(NOW, ZoneOffset.UTC);
    private static final PractitionerId DOCTOR = new PractitionerId("dr-martin");
    private static final PractitionerId OTHER_DOCTOR = new PractitionerId("dr-durand");
    private static final SlotId S = new SlotId("slot-1");
    private static final SlotId S2 = new SlotId("slot-2");
    private static final PatientId A = new PatientId("patient-a");
    private static final PatientId B = new PatientId("patient-b");

    @Test
    void twoSimultaneousBookingsOfOneSlotNeverBothSucceed() throws Exception {
        BookingStore store = new MeetingStore(new InMemoryBookingStore(List.of(slot(S, DOCTOR, 60, 120))));
        BookSlot book = new BookSlot(store, CLOCK);

        List<BookingOutcome> outcomes = runTogether(() -> book.book(A, S), () -> book.book(B, S));

        List<Booking> booked = bookedIn(outcomes);
        assertTrue(booked.size() <= 1, "both bookings of the same slot succeeded: " + outcomes);
        assertEquals(booked.isEmpty() ? Optional.empty() : Optional.of(booked.get(0)), store.activeBookingOf(S));
    }

    @Test
    void twoSimultaneousOverlappingBookingsByOnePatientNeverBothSucceed() throws Exception {
        BookingStore store = new MeetingStore(new InMemoryBookingStore(
                List.of(slot(S, DOCTOR, 60, 120), slot(S2, OTHER_DOCTOR, 90, 150))));
        BookSlot book = new BookSlot(store, CLOCK);

        List<BookingOutcome> outcomes = runTogether(() -> book.book(A, S), () -> book.book(A, S2));

        assertTrue(bookedIn(outcomes).size() <= 1, "a patient booked two overlapping slots: " + outcomes);
        assertTrue(store.slotsHeldBy(A).size() <= 1, "the patient holds overlapping slots: " + store.slotsHeldBy(A));
    }

    private static Slot slot(SlotId id, PractitionerId practitioner, int startMinutes, int endMinutes) {
        return new Slot(id, practitioner, new TimeRange(
                NOW.plus(Duration.ofMinutes(startMinutes)), NOW.plus(Duration.ofMinutes(endMinutes))));
    }

    private static List<Booking> bookedIn(List<BookingOutcome> outcomes) {
        return outcomes.stream()
                .filter(BookingOutcome.Booked.class::isInstance)
                .map(outcome -> ((BookingOutcome.Booked) outcome).booking())
                .toList();
    }

    /** Starts both attempts at the same moment on two threads and returns their outcomes. */
    private static List<BookingOutcome> runTogether(Supplier<BookingOutcome> first, Supplier<BookingOutcome> second)
            throws Exception {
        ExecutorService threads = Executors.newFixedThreadPool(2);
        try {
            CountDownLatch go = new CountDownLatch(1);
            List<Future<BookingOutcome>> futures = new ArrayList<>();
            for (Supplier<BookingOutcome> attempt : List.of(first, second)) {
                futures.add(threads.submit(() -> {
                    go.await();
                    return attempt.get();
                }));
            }
            go.countDown();
            List<BookingOutcome> outcomes = new ArrayList<>();
            for (Future<BookingOutcome> future : futures) {
                outcomes.add(future.get(10, TimeUnit.SECONDS));
            }
            return outcomes;
        } finally {
            threads.shutdownNow();
        }
    }

    /**
     * Test-only decorator that makes the unprotected interleaving certain: a save waits, for a bounded time,
     * until two attempts have finished reading. Without an atomic unit both attempts pass their check before
     * either saves; with it, the second attempt cannot read until the first has saved, so the wait times out.
     */
    private static final class MeetingStore implements BookingStore {

        private static final long MAX_WAIT_MILLIS = 500;

        private final BookingStore inner;
        private final CountDownLatch bothHaveRead = new CountDownLatch(2);

        MeetingStore(BookingStore inner) {
            this.inner = inner;
        }

        @Override
        public Optional<Slot> findSlot(SlotId slot) {
            return inner.findSlot(slot);
        }

        @Override
        public Optional<Booking> activeBookingOf(SlotId slot) {
            return inner.activeBookingOf(slot);
        }

        @Override
        public List<Slot> slotsHeldBy(PatientId patient) {
            List<Slot> held = inner.slotsHeldBy(patient);
            bothHaveRead.countDown();
            return held;
        }

        @Override
        public void save(Booking booking) {
            try {
                bothHaveRead.await(MAX_WAIT_MILLIS, TimeUnit.MILLISECONDS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            inner.save(booking);
        }

        @Override
        public <T> T atomically(Supplier<T> unit) {
            return inner.atomically(unit);
        }
    }
}
