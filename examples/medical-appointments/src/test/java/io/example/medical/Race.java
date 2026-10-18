package io.example.medical;

import io.example.medical.application.BookingStore;
import io.example.medical.domain.Booking;
import io.example.medical.domain.BookingOutcome;
import io.example.medical.domain.PatientId;
import io.example.medical.domain.Slot;
import io.example.medical.domain.SlotId;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;

/**
 * Test support: runs several booking attempts at the same moment and forms the dangerous interleaving on purpose,
 * with no timed wait. Each attempt runs on its own thread. After an attempt has read everything its decision needs,
 * it waits at a gate until every other attempt has entered the store and is either at the gate too, waiting on the
 * lock of the atomic unit or finished. With an atomic unit, the first attempt holds the gate
 * while the others are parked on the lock; without one, all of them reach the gate having read the same state and
 * then all decide: a double booking is certain, not likely.
 */
final class Race {

    /** Only a guard: a race that does not form fails with a message instead of hanging the build. */
    private static final long GUARD_NANOS = 10_000_000_000L;

    private final BookingStore inner;
    private final Runnable afterSave;
    private final Set<Thread> entered = ConcurrentHashMap.newKeySet();
    private final Set<Thread> arrived = ConcurrentHashMap.newKeySet();
    private volatile List<Thread> racers = List.of();

    Race(BookingStore inner) {
        this(inner, () -> { });
    }

    /** {@code afterSave} runs inside the unit, right after any booking is saved. */
    Race(BookingStore inner, Runnable afterSave) {
        this.inner = inner;
        this.afterSave = afterSave;
    }

    /** The store the use case under test must be built on. */
    BookingStore store() {
        return new GatedStore();
    }

    /** Runs every attempt at the same moment and returns the outcomes in the order of the attempts. */
    List<BookingOutcome> run(List<Supplier<BookingOutcome>> attempts) {
        CountDownLatch go = new CountDownLatch(1);
        AtomicReference<Throwable> failure = new AtomicReference<>();
        BookingOutcome[] outcomes = new BookingOutcome[attempts.size()];
        List<Thread> threads = new ArrayList<>();
        for (int i = 0; i < attempts.size(); i++) {
            int index = i;
            threads.add(new Thread(() -> {
                try {
                    go.await();
                    outcomes[index] = attempts.get(index).get();
                } catch (Throwable t) {
                    failure.compareAndSet(null, t);
                }
            }, "racer-" + i));
        }
        racers = List.copyOf(threads);
        threads.forEach(Thread::start);
        go.countDown();
        try {
            for (Thread thread : threads) {
                thread.join(2 * GUARD_NANOS / 1_000_000);
                if (thread.isAlive()) {
                    throw new AssertionError("the race did not finish: " + thread.getName());
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new AssertionError("interrupted while waiting for the race", e);
        } finally {
            threads.forEach(Thread::interrupt);
        }
        if (failure.get() != null) {
            throw new AssertionError("an attempt failed: " + failure.get(), failure.get());
        }
        return List.of(outcomes);
    }

    private void waitAtTheGate() {
        Thread me = Thread.currentThread();
        if (!racers.contains(me)) {
            return;
        }
        arrived.add(me);
        long deadline = System.nanoTime() + GUARD_NANOS;
        while (!othersAreHeldBack(me)) {
            if (System.nanoTime() - deadline > 0) {
                throw new IllegalStateException("the race never formed: entered=" + entered.size()
                        + ", arrived=" + arrived.size() + " of " + racers.size());
            }
            Thread.yield();
        }
    }

    private boolean othersAreHeldBack(Thread me) {
        for (Thread other : racers) {
            if (other == me) {
                continue;
            }
            // Before it has entered the store, a thread may look parked (it waits for the start): not held back.
            if (!entered.contains(other)) {
                return false;
            }
            if (!(arrived.contains(other) || isFinished(other) || isWaitingAtTheDoor(other))) {
                return false;
            }
        }
        return true;
    }

    private static boolean isFinished(Thread thread) {
        return thread.getState() == Thread.State.TERMINATED;
    }

    /**
     * True when the thread is parked or blocked inside the store's {@code atomically}, i.e. on the lock of the unit.
     * A thread that is only blocked for another reason (class loading, say) does not count: judged by the first frame
     * that is not part of the JDK.
     */
    private static boolean isWaitingAtTheDoor(Thread thread) {
        Thread.State state = thread.getState();
        if (state != Thread.State.WAITING && state != Thread.State.TIMED_WAITING && state != Thread.State.BLOCKED) {
            return false;
        }
        for (StackTraceElement frame : thread.getStackTrace()) {
            String owner = frame.getClassName();
            if (!(owner.startsWith("java.") || owner.startsWith("jdk.") || owner.startsWith("sun."))) {
                return frame.getMethodName().equals("atomically");
            }
        }
        return false;
    }

    private final class GatedStore implements BookingStore {

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
            waitAtTheGate();
            return held;
        }

        @Override
        public void save(Booking booking) {
            inner.save(booking);
            afterSave.run();
        }

        @Override
        public <T> T atomically(Supplier<T> unit) {
            entered.add(Thread.currentThread());
            return inner.atomically(unit);
        }
    }
}
