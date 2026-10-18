---
role: diagnostician
status: done
reasons: []
severity: major
---

# Diagnosis: unrelated members shown as connected

Skill applied: `systematic-debugging` (investigation kept in this file instead of `.debug/`, per the brief). The human delegated every decision.

## Framing

- Observed: after `ann:bo` and `cy` connect, `ann` sending to `bo:cy` is rejected `already-connected`, and the pair state of (`ann`, `bo:cy`) is `{connected: true, requestState: "none"}`.
- Expected: send succeeds (new pending request); pair state before the send is `{connected: false, requestState: "none"}`.
- Scope: deterministic, in-memory store, any pair of ids whose joined form collides. Timeline: the code was last changed by commit `347911f` ("index stored connections by pair in the in-memory store").

## Reproduction

`repro/run.sh current` (script `repro/collision.repro.ts`, vitest config `repro/vitest.config.ts`; outside `src/` and `tests/`). Deterministic. Output on HEAD:

```
send: {"ok":false,"reason":"already-connected"} state: {"ok":true,"value":{"connected":true,"requestState":"none"}}
× unrelated pair (ann, bo:cy) is not connected and the send succeeds
```

## Facts

- F1: `requestsBetween` filters on exact sender/recipient equality, so it cannot confuse the two pairs; the state `requestState: "none"` confirms it.
- F2: the only thing that says "connected" is `store.findConnection`, used by both `sendRequest` and `getPairState`.
- F3: since `347911f`, `InMemoryStore` keys connections with `pairKey(a, b) = [a, b].sort().join(":")` (`src/connections/infrastructure/in-memory-store.ts`).
- F4: member ids have no validity rule on purpose (D-15, `member-id.ts`), so ids may contain `:`.
- F5: before `347911f`, `findConnection` scanned the list with `connects()` (exact member equality).

## Hypotheses

| # | Statement | Falsifiable prediction | Cost | Status |
|---|-----------|------------------------|------|--------|
| H1 | The request/pair-state logic (`decideSend`, `pairState`) mixes up the two pairs | `requestsBetween(ann, bo:cy)` returns the `ann:bo`/`cy` request | fast | refuted: F1, state shows `requestState: "none"`; the rule functions only read `connection` as given |
| H2 | The accept step stores a wrong connection (wrong members) | the stored connection's members are not (`ann:bo`, `cy`) | fast | refuted by code reading: `saveAccepted` stores `connection.members` as given by `newConnection(request.sender, request.recipient)`; the store key is the only derived value |
| H3 | The store's pair key collides: `pairKey("ann:bo","cy")` equals `pairKey("ann","bo:cy")` | both give `"ann:bo:cy"`, so `findConnection(ann, bo:cy)` returns the other pair's connection | fast | confirmed |
| H4 | The bug predates the pair index (a `connects()` problem) | the same scenario fails on the store as of `347911f^` | fast | refuted: passes with the old store (see toggle) |

## Investigation log

- H3: `[ "ann:bo", "cy" ].sort().join(":")` is `"ann:bo:cy"`; `[ "ann", "bo:cy" ].sort().join(":")` is `"ann:bo:cy"`. Same key. `saveAccepted` writes under that key, `findConnection(ann, bo:cy)` reads it and returns a connection whose members are `ann:bo` and `cy`.
- H4 / toggle: `repro/run.sh before` runs the same scenario with only `in-memory-store.ts` replaced by its `347911f^` version (copy in a temp dir, project untouched) -> `Tests 1 passed`.
- No instrumentation was added; no project file was modified.

## Root cause

- Mechanism: the in-memory store indexes connections by `pairKey = sorted ids joined with ":"`. Member ids are arbitrary strings (D-15), so the join is ambiguous: distinct pairs (`ann:bo`, `cy`) and (`ann`, `bo:cy`) produce the same key `ann:bo:cy`. Accepting the first pair stores a connection under that key; a lookup for the unrelated second pair hits it. `sendRequest` then sees a connection and rejects `already-connected` (guard `alreadyConnected`), and `getPairState` reports `connected: true`.
- Demonstration: triggered at will by the colliding ids; disappears when only the store file is reverted to the list scan with exact equality (toggle above, not a fix proposal).
- Facts explained: F1 (`requestState: "none"` while `connected: true`, because only the connection lookup is wrong), F2, F3, F4, F5 (before the index: no bug), and the report's "ids can be any string".

## Handoff

- Fix approaches and trade-offs (none picked): (a) key with an unambiguous encoding (e.g. length-prefixed or JSON array of the sorted pair) -- keeps the O(1) lookup; (b) nested map keyed by member then member -- no string composition at all; (c) revert to the scan with `connects()` -- exact, but gives up the lookup speed the commit wanted. The `sort()` also deserves a check that ordering stays consistent for any string.
- Related risks: the same ambiguity must not exist elsewhere a pair is composed into a string (no other occurrence found in `src/connections`, only `pairKey`). `eraseMember` iterates stored connections and tests `members.includes(member)`, so erasing a member is exact; but erasing `ann:bo` also keeps/deletes entries by the colliding key: the colliding connection would also have overwritten another one with `set` (two real connections with colliding pairs overwrite each other, so one of them can be silently lost). Tests in `tests/connections` use simple ids, which is why none catch it.
