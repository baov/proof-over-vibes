package io.example.medical;

import io.example.medical.adapters.InMemoryBookingStore;
import io.example.medical.application.BookSlot;
import io.example.medical.domain.Booking;
import io.example.medical.domain.BookingOutcome;
import io.example.medical.domain.PatientId;
import io.example.medical.domain.PractitionerId;
import io.example.medical.domain.RefusalReason;
import io.example.medical.domain.Slot;
import io.example.medical.domain.SlotId;
import io.example.medical.domain.TimeRange;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.HashSet;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Function;
import java.util.function.Supplier;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Simultaneous bookings: when requests arrive at the same moment, each conflict has one winner and every other
 * request is refused with the reason it would get had it come right after. Who wins is not decided (D-35), so no
 * test names the winner: it is the request whose outcome is {@code Booked}. Every race goes through {@link Race},
 * which forms the dangerous interleaving without any timed wait.
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
    private static final PatientId C = new PatientId("patient-c");
    private static final PatientId D = new PatientId("patient-d");
    private static final PatientId E = new PatientId("patient-e");
    private static final SlotId S3 = new SlotId("slot-3");

    @Test
    void oneOfTwoSimultaneousBookingsOfASlotWinsAndTheOtherSeesTaken() {
        InMemoryBookingStore store = new InMemoryBookingStore(List.of(slot(S, DOCTOR, 60, 120)));
        Race race = new Race(store);
        BookSlot book = new BookSlot(race.store(), CLOCK);

        List<BookingOutcome> outcomes = race.run(List.of(() -> book.book(A, S), () -> book.book(B, S)));

        PatientId[] patients = {A, B};
        int winner = winnerOf(outcomes);
        int loser = 1 - winner;
        assertEquals(new BookingOutcome.Booked(new Booking(patients[winner], S)), outcomes.get(winner));
        assertEquals(new BookingOutcome.Refused(RefusalReason.TAKEN), outcomes.get(loser), "outcomes: " + outcomes);
        assertEquals(Optional.of(new Booking(patients[winner], S)), store.activeBookingOf(S));
        assertEquals(List.of(), store.slotsHeldBy(patients[loser]));
    }

    @Test
    void oneOfTwoSimultaneousOverlappingBookingsOfAPatientWinsAndTheOtherSeesOverlapping() {
        InMemoryBookingStore store = new InMemoryBookingStore(
                List.of(slot(S, DOCTOR, 60, 120), slot(S2, OTHER_DOCTOR, 90, 150)));
        Race race = new Race(store);
        BookSlot book = new BookSlot(race.store(), CLOCK);

        List<BookingOutcome> outcomes = race.run(List.of(() -> book.book(A, S), () -> book.book(A, S2)));

        SlotId[] slots = {S, S2};
        int winner = winnerOf(outcomes);
        int loser = 1 - winner;
        assertEquals(new BookingOutcome.Booked(new Booking(A, slots[winner])), outcomes.get(winner));
        assertEquals(new BookingOutcome.Refused(RefusalReason.OVERLAPPING), outcomes.get(loser),
                "outcomes: " + outcomes);
        assertEquals(List.of(store.findSlot(slots[winner]).orElseThrow()), store.slotsHeldBy(A));
        assertEquals(Optional.empty(), store.activeBookingOf(slots[loser]));
    }

    @Test
    void aPatientBookingTheSameSlotTwiceAtOnceSeesTakenForTheOther() {
        InMemoryBookingStore store = new InMemoryBookingStore(List.of(slot(S, DOCTOR, 60, 120)));
        Race race = new Race(store);
        BookSlot book = new BookSlot(race.store(), CLOCK);

        List<BookingOutcome> outcomes = race.run(List.of(() -> book.book(A, S), () -> book.book(A, S)));

        int winner = winnerOf(outcomes);
        assertEquals(new BookingOutcome.Booked(new Booking(A, S)), outcomes.get(winner));
        assertEquals(new BookingOutcome.Refused(RefusalReason.TAKEN), outcomes.get(1 - winner),
                "outcomes: " + outcomes);
        assertEquals(Optional.of(new Booking(A, S)), store.activeBookingOf(S));
        assertEquals(List.of(store.findSlot(S).orElseThrow()), store.slotsHeldBy(A));
    }

    @Test
    void manySimultaneousBookingsLeaveOneWinnerAndTheRestRefusedForTheSameReason() {
        InMemoryBookingStore store = new InMemoryBookingStore(List.of(slot(S, DOCTOR, 60, 120),
                slot(S2, DOCTOR, 200, 260), slot(S3, OTHER_DOCTOR, 70, 130), slot(new SlotId("slot-4"), DOCTOR, 80, 140)));
        Race race = new Race(store);
        BookSlot book = new BookSlot(race.store(), CLOCK);

        List<BookingOutcome> fivePatients = race.run(List.of(() -> book.book(A, S2), () -> book.book(B, S2),
                () -> book.book(C, S2), () -> book.book(D, S2), () -> book.book(E, S2)));

        winnerOf(fivePatients);
        assertEquals(4, count(fivePatients, new BookingOutcome.Refused(RefusalReason.TAKEN)),
                "outcomes: " + fivePatients);
        assertEquals(1, bookingsOnSlots(store, S2));

        Race overlapping = new Race(store);
        BookSlot bookOverlapping = new BookSlot(overlapping.store(), CLOCK);
        SlotId s4 = new SlotId("slot-4");
        List<BookingOutcome> threeSlots = overlapping.run(List.of(() -> bookOverlapping.book(A, S),
                () -> bookOverlapping.book(A, S3), () -> bookOverlapping.book(A, s4)));

        winnerOf(threeSlots);
        assertEquals(2, count(threeSlots, new BookingOutcome.Refused(RefusalReason.OVERLAPPING)),
                "outcomes: " + threeSlots);
        assertEquals(1, bookingsOnSlots(store, S, S3, s4));
    }

    private static long count(List<BookingOutcome> outcomes, BookingOutcome wanted) {
        return outcomes.stream().filter(wanted::equals).count();
    }

    private static long bookingsOnSlots(InMemoryBookingStore store, SlotId... slots) {
        return Arrays.stream(slots).filter(slot -> store.activeBookingOf(slot).isPresent()).count();
    }

    private record Request(PatientId patient, SlotId slot) {
    }

    /** What a run leaves behind: the outcome of each request, in request order, and every booking in the store. */
    private record Result(List<BookingOutcome> outcomes, Set<Booking> bookings) {
    }

    @Test
    void aSimultaneousOutcomeIsOneThatSomeOrderOneAfterTheOtherWouldGive() {
        Slot s = slot(S, DOCTOR, 60, 120);
        Slot s2 = slot(S2, OTHER_DOCTOR, 90, 150);
        Slot chain3 = slot(S3, DOCTOR, 130, 190);
        Slot held = slot(new SlotId("slot-x"), OTHER_DOCTOR, 30, 90);

        // (a) A wants both overlapping slots while B wants the second.
        assertSomeOrderExplainsTheRace(List.of(s, s2), List.of(),
                List.of(new Request(A, S), new Request(A, S2), new Request(B, S2)));
        // (b) A chain: the first and the third do not overlap, so both may be booked.
        assertSomeOrderExplainsTheRace(List.of(s, s2, chain3), List.of(),
                List.of(new Request(A, S), new Request(A, S2), new Request(A, S3)));
        // (c) C already holds a slot that overlaps S; C and B race for S.
        List<BookingOutcome> contested = assertSomeOrderExplainsTheRace(List.of(s, held),
                List.of(new Booking(C, held.id())), List.of(new Request(B, S), new Request(C, S)));
        assertEquals(new BookingOutcome.Booked(new Booking(B, S)), contested.get(0));
    }

    /** Runs the requests at the same moment and checks that one order, one after the other, gives the same result. */
    private static List<BookingOutcome> assertSomeOrderExplainsTheRace(List<Slot> slots, List<Booking> alreadyBooked,
                                                                     List<Request> requests) {
        InMemoryBookingStore store = new InMemoryBookingStore(slots);
        alreadyBooked.forEach(store::save);
        Race race = new Race(store);
        BookSlot book = new BookSlot(race.store(), CLOCK);
        List<Supplier<BookingOutcome>> attempts = requests.stream()
                .<Supplier<BookingOutcome>>map(request -> () -> book.book(request.patient(), request.slot()))
                .toList();

        List<BookingOutcome> outcomes = race.run(attempts);

        Result concurrent = new Result(outcomes, bookingsIn(store, slots));
        Set<Result> possible = new HashSet<>();
        permutations(requests.size(), new ArrayList<>(), possible, order -> {
            InMemoryBookingStore fresh = new InMemoryBookingStore(slots);
            alreadyBooked.forEach(fresh::save);
            BookSlot sequential = new BookSlot(fresh, CLOCK);
            BookingOutcome[] vector = new BookingOutcome[requests.size()];
            for (int index : order) {
                vector[index] = sequential.book(requests.get(index).patient(), requests.get(index).slot());
            }
            return new Result(List.of(vector), bookingsIn(fresh, slots));
        });
        assertTrue(possible.contains(concurrent),
                "no order one after the other gives " + concurrent + "; possible: " + possible);
        return outcomes;
    }

    private static Set<Booking> bookingsIn(InMemoryBookingStore store, List<Slot> slots) {
        Set<Booking> bookings = new HashSet<>();
        slots.forEach(slot -> store.activeBookingOf(slot.id()).ifPresent(bookings::add));
        return bookings;
    }

    /** Every order of the requests 0..size-1, each replayed through {@code replay}; results collected in {@code into}. */
    private static void permutations(int size, List<Integer> order, Set<Result> into,
                                     Function<List<Integer>, Result> replay) {
        if (order.size() == size) {
            into.add(replay.apply(order));
            return;
        }
        for (int next = 0; next < size; next++) {
            if (!order.contains(next)) {
                List<Integer> longer = new ArrayList<>(order);
                longer.add(next);
                permutations(size, longer, into, replay);
            }
        }
    }

    @Test
    void aLoserJudgedAfterTheSlotHasStartedSeesPastNotTakenOrOverlapping() {
        for (boolean onePatient : new boolean[] {false, true}) {
            InMemoryBookingStore store = new InMemoryBookingStore(
                    List.of(slot(S, DOCTOR, 60, 120), slot(S2, OTHER_DOCTOR, 90, 150)));
            // The clock moves past the start of both slots the moment the winner is saved, inside the atomic unit.
            AtomicReference<Instant> now = new AtomicReference<>(NOW);
            Clock movable = new Clock() {
                @Override
                public ZoneId getZone() {
                    return ZoneOffset.UTC;
                }

                @Override
                public Clock withZone(ZoneId zone) {
                    return this;
                }

                @Override
                public Instant instant() {
                    return now.get();
                }
            };
            Race race = new Race(store, () -> now.set(NOW.plus(Duration.ofMinutes(100))));
            BookSlot book = new BookSlot(race.store(), movable);

            List<BookingOutcome> outcomes = onePatient
                    ? race.run(List.of(() -> book.book(A, S), () -> book.book(A, S2)))
                    : race.run(List.of(() -> book.book(A, S), () -> book.book(B, S)));

            int winner = winnerOf(outcomes);
            assertEquals(new BookingOutcome.Refused(RefusalReason.PAST), outcomes.get(1 - winner),
                    (onePatient ? "one patient, two overlapping slots: " : "two patients, one slot: ") + outcomes);
        }
    }

    @Test
    void simultaneousBookingsOfAnUnknownSlotAreAllRefusedAsUnknown() {
        InMemoryBookingStore store = new InMemoryBookingStore(List.of(slot(S, DOCTOR, 60, 120)));
        Race race = new Race(store);
        BookSlot book = new BookSlot(race.store(), CLOCK);
        SlotId unknown = new SlotId("slot-unknown");

        List<BookingOutcome> outcomes = race.run(List.of(
                () -> book.book(A, unknown), () -> book.book(B, unknown), () -> book.book(C, S)));

        BookingOutcome unknownSlot = new BookingOutcome.Refused(RefusalReason.UNKNOWN_SLOT);
        assertEquals(List.of(unknownSlot, unknownSlot, new BookingOutcome.Booked(new Booking(C, S))), outcomes);
        assertEquals(Optional.empty(), store.activeBookingOf(unknown));
        assertEquals(List.of(), store.slotsHeldBy(A));
        assertEquals(List.of(), store.slotsHeldBy(B));
    }

    @Test
    void aMissingIdentifierIsReportedAsMissingWhileSomeoneElseBooksTheSlot() {
        InMemoryBookingStore store = new InMemoryBookingStore(List.of(slot(S, DOCTOR, 60, 120)));
        Race race = new Race(store);
        BookSlot book = new BookSlot(race.store(), CLOCK);
        BookingOutcome missing = new BookingOutcome.Refused(RefusalReason.MISSING_IDENTIFIER);

        List<BookingOutcome> outcomes = race.run(List.of(() -> book.book(A, S),
                () -> book.book(new PatientId("  "), S), () -> book.book(B, null)));

        assertEquals(List.of(new BookingOutcome.Booked(new Booking(A, S)), missing, missing), outcomes);
        assertEquals(Optional.of(new Booking(A, S)), store.activeBookingOf(S));

        InMemoryBookingStore other = new InMemoryBookingStore(List.of(slot(S, DOCTOR, 60, 120)));
        Race twoBlank = new Race(other);
        BookSlot bookOther = new BookSlot(twoBlank.store(), CLOCK);

        List<BookingOutcome> blanks = twoBlank.run(List.of(
                () -> bookOther.book(new PatientId(""), S), () -> bookOther.book(null, S)));

        assertEquals(List.of(missing, missing), blanks);
        assertEquals(Optional.empty(), other.activeBookingOf(S));
    }

    @Test
    void aRefusedSimultaneousBookingLeavesNothingBehind() {
        // One slot, two patients: the winner's booking is intact, the loser can book elsewhere or ask again.
        InMemoryBookingStore store = new InMemoryBookingStore(
                List.of(slot(S, DOCTOR, 60, 120), slot(S2, OTHER_DOCTOR, 200, 260)));
        Race race = new Race(store);
        BookSlot book = new BookSlot(race.store(), CLOCK);
        PatientId[] patients = {A, B};

        List<BookingOutcome> outcomes = race.run(List.of(() -> book.book(A, S), () -> book.book(B, S)));

        int winner = winnerOf(outcomes);
        PatientId loser = patients[1 - winner];
        assertEquals(Optional.of(((BookingOutcome.Booked) outcomes.get(winner)).booking()), store.activeBookingOf(S));
        assertEquals(new BookingOutcome.Refused(RefusalReason.TAKEN), book.book(loser, S));
        assertEquals(Optional.of(new Booking(patients[winner], S)), store.activeBookingOf(S));
        assertEquals(new BookingOutcome.Booked(new Booking(loser, S2)), book.book(loser, S2));

        // One patient, two overlapping slots: the slot of the refused request is still free for someone else.
        InMemoryBookingStore overlapping = new InMemoryBookingStore(
                List.of(slot(S, DOCTOR, 60, 120), slot(S2, OTHER_DOCTOR, 90, 150)));
        Race second = new Race(overlapping);
        BookSlot bookOverlapping = new BookSlot(second.store(), CLOCK);
        SlotId[] slots = {S, S2};

        List<BookingOutcome> both = second.run(List.of(
                () -> bookOverlapping.book(A, S), () -> bookOverlapping.book(A, S2)));

        SlotId free = slots[1 - winnerOf(both)];
        assertEquals(Optional.empty(), overlapping.activeBookingOf(free));
        assertEquals(new BookingOutcome.Booked(new Booking(B, free)), bookOverlapping.book(B, free));
    }

    private static Slot slot(SlotId id, PractitionerId practitioner, int startMinutes, int endMinutes) {
        return new Slot(id, practitioner, new TimeRange(
                NOW.plus(Duration.ofMinutes(startMinutes)), NOW.plus(Duration.ofMinutes(endMinutes))));
    }

    /** The index of the one request that booked; fails when nobody or several did. */
    private static int winnerOf(List<BookingOutcome> outcomes) {
        List<Integer> booked = new ArrayList<>();
        for (int i = 0; i < outcomes.size(); i++) {
            if (outcomes.get(i) instanceof BookingOutcome.Booked) {
                booked.add(i);
            }
        }
        assertEquals(1, booked.size(), "exactly one request must book; outcomes: " + outcomes);
        return booked.get(0);
    }
}
