---
role: developer
status: done
reasons:
  - "Story 1 implemented per plan; 22 tests, typecheck, harness (0 warnings), harness selftest all green. Mutation 98.9%, one survivor (see below). Two points for the reviewer: Vitest pinned to 4.x (toolchain), and no default id generator."
---

# Developer, iteration 1: connection requests, story 1 (ask-and-accept)

Announcement: I applied the implementation steps of `plan-driven-dev` and the `behavior-driven-testing` skill (tests through the public entry point, named after behaviors, exact reason and unchanged state asserted after each rejection).

## Commits (oldest first, all on the shared branch, nothing pushed)

1. `b3c0261` a member can send a connection request (skeleton folded in: no empty step-1 commit)
2. `7693cc0` a recipient lists their pending requests, oldest first
3. `b2cbd2e` reject a request a member sends to themselves
4. `deeb727` reject a duplicate or reverse pending request, keep other recipients allowed
5. `b23ba98` the recipient accepts a pending request
6. `ebf9d06` accept rejections, authorization before state, unknown request
7. `e3b9258` connected members, state of a pair, requests between connected members rejected
8. `55e62f0` every rejection has its own reason
9. `8a0ce23` pin Vitest to 4.x (see "Toolchain")
10. `d817179` a connection links only its two members; simplify pair and send decision

Each step went red (test run failing) then green. 22 test-case files under `docs/business/test-cases/connections/`, all `covered`, each with a `source`; no orphan test file.

## Commands run (final state)

- `npm test`: 5 files, 22 tests pass
- `npm run typecheck`: clean
- `npm run harness`: 0 layer violations, 0 shape violations, 22 test-cases / 22 covered_ok / 0 pending / 0 orphan; exit 0
- `npm run harness:selftest`: 5 pass, 0 fail
- `npm run mutation`: score 98.9% (88 killed / 89 generated), threshold none (not written, as instructed)

## Mutation: baseline to record (human decision)

Baseline: 98.9% on `src/connections/domain` + `application`, at `d817179` (rounded down: 98). One survivor:
- `domain/send-rules.ts:21`, `pendingFrom`: the check `r.state === "pending"` mutated to `true`. In story 1 it cannot be observed: the only non-pending request is an accepted one, and `already-connected` is decided before the pending guards. It starts to matter with declined and withdrawn requests (story 2), whose tests should kill it. Not excluded, not tested around.

Two equivalent mutants and one dead value were removed by simplifying the code rather than excluding (unordered pair no longer sorted; `decideSend` returns a reason or nothing). `stryker.config.mjs` untouched.

## Toolchain (for the reviewer and the human)

With Vitest 5.0.5 (the version `package.json` had) Stryker 10's Vitest runner never activates a mutant: every mutant "survived" with 0 tests run (10% score, only load-time mutants killed). Not a test problem; `vitest.related: false` and `coverageAnalysis: off` did not help. With Vitest 4.1.12 the same suite scores 91% on the first run. I pinned `vitest` to `^4.1.12` in `package.json` and `package-lock.json` (commit `8a0ce23`). Revert and re-pin if the human prefers another fix; INV-010 cannot work on Vitest 5 until the runner supports it.

## Behaviors added (not stated by the plan; none needs a decision, flagged for transparency)

- `createConnections` requires an `ids` option (an `IdGenerator`, `next(): string`); there is no default generator. Reason: a default would need `node:crypto` in infrastructure plus a choice of id format, which no document decides. A consumer wiring the module must supply ids (tests use `req-1`, `req-2`...). To decide before a real caller exists.
- Request ids are plain strings; `memberId(value)` is an unchecked constructor (D-15).
- Public shapes: a request is `{ id, sender, recipient, state }`, `state` being `"pending"` or `"accepted"`; the state query returns `{ connected, requestState }` with `requestState` in `"none" | "pending" | "accepted"`; all operations are asynchronous and return `{ ok: true, value }` or `{ ok: false, reason }` (the pending list and the state return values directly). Shapes follow the plan's "Public interface"; names are the Developer's.
- With one request per pair (all that story 1 allows), the state reported is the last request between the two; D-12 (pending if any, else most recent) is story 2 and not built.
- Accepting the same request twice, or a non-recipient accepting it, leaves the pair state unchanged (asserted).

## Open and untouched (as the brief says)

Member id validity (D-15), concurrency, a decliner sending back: nothing built, nothing tested. Store port `saveAccepted(request, connection)` writes both together so a real store can make it atomic. Sensitive zones touched, human review needed before merge: `src/connections/application/ports.ts`, `src/connections/infrastructure/in-memory-store.ts`, `src/connections/index.ts`.

## Not touched

`docs/product`, `docs/business/decisions.md` (it was already modified in the working tree before I started; I did not stage it), `tools/harness`, the plan, `stryker.config.mjs`.
