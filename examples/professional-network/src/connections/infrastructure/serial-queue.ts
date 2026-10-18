/** Runs an operation once every operation queued before it has settled (ADR-0002). */
export type SerialQueue = <T>(operation: () => Promise<T>) => Promise<T>;

/**
 * A first-in-first-out queue: one operation at a time, in the order of the calls.
 * Each caller gets the outcome of its own operation, a rejection included; a rejection never blocks the next one.
 */
export function createSerialQueue(): SerialQueue {
  let tail: Promise<unknown> = Promise.resolve();
  return (operation) => {
    const outcome = tail.then(operation);
    tail = outcome.catch(() => undefined);
    return outcome;
  };
}
