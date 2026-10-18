# ADR-0002: Operations of a module are serialized in the process

Status: accepted (answered by delegate; no escalation needed: no dependency, no change of the store port)

## Context

The `connections` use cases read, decide, then write, with awaits in between. Two simultaneous operations on the same pair of members can both read the old state and both write (two pending requests for one pair, a connection for a withdrawn request). The PRD `connection-requests-edge-concurrency.md` requires the result of any two simultaneous operations to equal one of the two sequential orders.

## Decision

- Every operation of the public entry point of `connections` (the five writes and the two reads) runs through one first-in-first-out queue owned by the module: one operation at a time, whole use case as the unit (the rule check and the write are never split). The queue is plain TypeScript with no dependency, in `infrastructure`, wired in `src/connections/index.ts`. A failed operation does not block the next one.
- The module runs as **one process instance**. The queue protects one process only.
- The store port is unchanged. Its existing promise stays binding: `saveAccepted` writes the request and the connection as one atomic write.
- Moving to several instances, or to a store shared with another process, requires a new ADR first. At that point the store port must gain conditional writes (a pending request unique per pair, a replace conditioned on the expected state) and the queue is no longer the guarantee.

Considered and rejected: a lock per pair (an operation by request id learns its pair only after a read, and erasure touches every pair; the gain is speed, which is out of scope); conditional writes in the store port now (a contract a real database would have to honor, with no deployment that needs it); an external lock service (a dependency with no need).

Associated executable invariants: INV-011 (docs/technical/invariants.md).

## Consequences

- An erase running at the same moment as another operation is one more serialized operation: the outcome is that of erase first or erase last, with no third state.
- Which of two simultaneous operations wins is the order of arrival; no priority exists.
- Throughput of the module is that of a single writer. Revisit with the first real load figure or the first multi-instance plan.
- The executable invariant (harness engineer): every method of `Connections` built in `createConnections` goes through the queue.
