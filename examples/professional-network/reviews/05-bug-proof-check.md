---
role: reviewer
status: done
verdict: GO
reasons:
  - "reproduction replayed independently: fails on HEAD, passes with only in-memory-store.ts reverted to 347911f^"
  - "mechanism complete: pairKey joins ids with ':' (ambiguous, ids are free strings per D-15), so (ann:bo, cy) and (ann, bo:cy) share the key ann:bo:cy"
  - "no second cause found: all other pair lookups use exact equality; falsification probes behave as the cause predicts"
severity: major
open_majors:
  - "Same collision, other symptom: when two colliding pairs are both connected the later one overwrites the earlier one in the store, and erasing a member of the overwritten pair (ann:bo) leaves the connection (ann:bo, cy) reported as connected, contradicting D-26 (nothing about the member remains). The fix must cover it and the developer needs a test for it."
---

# Proof review: unrelated members shown as connected

Check of `.plans/in-progress/bug-unrelated-members-connected/diagnostician.md` and `repro/`. Skill applied: `premerge-review`, only the proof-check case (no diff, no gauntlet: nothing is to be merged yet).

## Verdict

GO. The Developer can start. One major finding (below) must be carried into the fix and its tests.

## What I checked

1. **Replay of the reproduction.** `repro/run.sh current` fails: send is `already-connected`, pair state is `{connected: true, requestState: "none"}`, exactly the report. `repro/run.sh before` (store as of `347911f^`, project untouched) passes. `git status` shows no modification of the project by the replay.
2. **Mechanism.** Read `in-memory-store.ts`: `saveAccepted` writes under `pairKey(...members)`, `findConnection` reads under `pairKey(a, b)`, `pairKey` is `[a, b].sort().join(":")`. Both pairs give `ann:bo:cy`. `sendRequest` and `getPairState` use `findConnection` alone for "connected", and `requestsBetween` uses exact equality, which explains `connected: true` with `requestState: "none"`. Chain: ambiguous join, key collision, foreign connection returned, `already-connected` and `connected: true`. Complete.
3. **Falsification, other symptoms predicted by the cause** (probe in the scratchpad, outside the project):
   - Other colliding shapes (`a` / `b:c:d` vs `a:b` / `c:d`, `a:b:c` / `d`), and the reversed argument order: all reported connected, as predicted.
   - Non-colliding id with `:` (`a:` / `b` vs `a` / `:b`): not connected, so the cause is the join collision and not "any `:`".
   - Unrelated simple ids: not connected.
   - Both colliding requests pending, then both accepted (accept does not consult `findConnection`): both accepted, the second connection overwrites the first. After `eraseMember("ann:bo")` the pair (`ann:bo`, `cy`) is still `connected: true` while (`ann`, `bo:cy`) is untouched. Predicted by the same cause; it is a second visible consequence.
4. **Second cause.** Searched `src` for other string compositions of a pair: `pairKey` is the only one. `requestsBetween`, `pendingFor`, `eraseMember`, `connects` compare ids exactly. None found.
5. **Hypotheses ruled out.** H1 (rules mix pairs): refuted, `requestState` is `none` and the rules read `connection` as given. H2 (wrong connection stored): the stored connection holds the right members (`newConnection(sender, recipient)`); the probe confirms the collision comes from the key. H4 (predates the index): refuted by the toggle I replayed. Sound.

## Findings

- **major** — The proof's "related risks" is imprecise on the collateral effect. It says one of two colliding connections "can be silently lost"; the observed effect is worse for D-26: after the overwrite, erasing a member of the overwritten connection leaves that connection visible (`connected: true`), because `eraseMember` tests `members.includes(member)` on the surviving object only. This is not a different root cause (same `pairKey`), so it does not stop the Developer, but the fix must be tested against it (two colliding connections, erase one member). Carried in `open_majors`.
- **minor** — The proof lists three fix approaches without picking one; acceptable, the human delegated the decision. Worth noting that approach (b) or an unambiguous key both close the finding above, whereas a mere separator change would not.
- **minor** — `repro/collision.repro.ts` reads the pair state before the send; the report has it after. Same result either way (verified), no action.

## Not checked

The carried-over open major (operation that never settles) is out of scope of this bug.
