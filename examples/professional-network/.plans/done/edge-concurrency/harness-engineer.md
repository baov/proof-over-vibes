---
role: harness-engineer
status: done
reasons: []
---

# Harness engineer: ADR-0002

- INV-011 added (warn): `tools/harness/check_serialized.mjs`, wired in `run_all.sh`, self-test added. Documented in `docs/technical/invariants.md`; ADR-0002 now lists it.
- Status is pending: while `src/connections/infrastructure/serial-queue.ts` is absent, the check prints a pending line and exits 0. Once the file exists it checks `src/connections/index.ts`: the queue is imported, `createConnections` creates it, and each returned method uses it. The Developer must import the queue from `./infrastructure/serial-queue` and call it inside each method (a local alias of the queue is accepted).
- Limit: structural only; the concurrency tests carry the behavior. No multiple-choice question; sensitive zones unchanged.
- `npm run harness`: exit 0 (INV-011 pending). `npm run harness:selftest`: 6/6 pass.
