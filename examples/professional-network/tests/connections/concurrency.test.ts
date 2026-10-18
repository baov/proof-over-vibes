import { describe, expect, it } from "vitest";
import { createConnections, memberId } from "../../src/connections/index.js";
import type { Connections } from "../../src/connections/index.js";
import {
  alice,
  bob,
  bothOrders,
  carol,
  dave,
  freshConnections,
  pendingOf,
  sendOrFail,
  simultaneously,
  stateOf,
} from "./support.js";
import type { Scenario } from "./support.js";

const notPending = { ok: false, reason: "not-pending" };
const none = { connected: false, requestState: "none" };

/** Pair state and pending lists of alice and bob: what a caller can see of their pair. */
async function pairView(module: Connections) {
  return {
    state: await stateOf(module, alice, bob),
    pendingForAlice: await pendingOf(module, alice),
    pendingForBob: await pendingOf(module, bob),
  };
}

type View = Awaited<ReturnType<typeof pairView>>;
type Op = (module: Connections) => Promise<unknown>;

/** The request alice sent to bob, then the scenario's operations on it. */
function onPendingRequest<A, B>(
  a: (module: Connections, id: string) => Promise<A>,
  b: (module: Connections, id: string) => Promise<B>,
): Scenario<string, A, B, View> {
  return {
    setup: (module) => sendOrFail(module, alice, bob),
    a,
    b,
    observe: (module) => pairView(module),
  };
}

/** Starts the call only after the given number of microtask turns, so that it lands inside an operation in flight. */
async function afterTurns<T>(turns: number, call: () => Promise<T>): Promise<T> {
  for (let turn = 0; turn < turns; turn++) await Promise.resolve();
  return call();
}

/** The simultaneous run must be the exact result of one of the two sequential orders (R1). */
async function expectOneOfTheOrders<C, A, B, O>(scenario: Scenario<C, A, B, O>) {
  const outcome = await simultaneously(scenario);
  expect(await bothOrders(scenario)).toContainEqual(outcome);
  return outcome;
}

describe("simultaneous operations on the same pair", () => {
  it("creates one pending request and rejects the other as reverse-pending when two members send to each other at once, without connecting them", async () => {
    const outcome = await expectOneOfTheOrders<undefined, any, any, unknown>({
      setup: async () => undefined,
      a: (module) => module.sendRequest(alice, bob),
      b: (module) => module.sendRequest(bob, alice),
      observe: pairView,
    });

    const [first, second] = [outcome.a, outcome.b];
    expect([first.ok, second.ok].sort()).toEqual([false, true]);
    const winner = first.ok ? first : second;
    const loser = first.ok ? second : first;
    expect(winner.value).toMatchObject({ id: "req-1", state: "pending" });
    expect(loser).toEqual({ ok: false, reason: "reverse-pending" });
    expect(outcome.final).toMatchObject({ state: { connected: false, requestState: "pending" } });
    const view = outcome.final as View;
    const pendingLists = [view.pendingForAlice, view.pendingForBob];
    expect(pendingLists.map((list) => list.length).sort()).toEqual([0, 1]);
    const recipientList = winner.value.recipient === bob ? view.pendingForBob : view.pendingForAlice;
    expect(recipientList).toEqual([winner.value]);
  });

  it("draws a request id only for the send that wins a mutual send", async () => {
    await expectOneOfTheOrders({
      setup: async () => undefined,
      a: (module) => module.sendRequest(alice, bob),
      b: (module) => module.sendRequest(bob, alice),
      observe: (module) => sendOrFail(module, carol, dave),
    });

    const outcome = await simultaneously({
      setup: async () => undefined,
      a: (module) => module.sendRequest(alice, bob),
      b: (module) => module.sendRequest(bob, alice),
      observe: (module) => sendOrFail(module, carol, dave),
    });
    expect(outcome.final).toBe("req-2");
  });

  it("lets exactly one of accept and withdraw succeed on the same request, and the state matches the winner", async () => {
    const outcome = await expectOneOfTheOrders(
      onPendingRequest(
        (module, id) => module.acceptRequest(id, bob),
        (module, id) => module.withdrawRequest(id, alice),
      ),
    );

    if (outcome.a.ok) {
      expect(outcome.a.value).toEqual({ id: "req-1", sender: alice, recipient: bob, state: "accepted" });
      expect(outcome.b).toEqual(notPending);
      expect(outcome.final.state).toEqual({ connected: true, requestState: "accepted" });
    } else {
      expect(outcome.a).toEqual(notPending);
      expect(outcome.b.ok).toBe(true);
      expect(outcome.final.state).toEqual({ connected: false, requestState: "withdrawn" });
    }
    expect(outcome.final.pendingForBob).toEqual([]);
  });

  it("lets exactly one of accept and decline succeed on the same request, the other is not-pending", async () => {
    const outcome = await expectOneOfTheOrders(
      onPendingRequest(
        (module, id) => module.acceptRequest(id, bob),
        (module, id) => module.declineRequest(id, bob),
      ),
    );

    if (outcome.a.ok) {
      expect(outcome.b).toEqual(notPending);
      expect(outcome.final.state).toEqual({ connected: true, requestState: "accepted" });
    } else {
      expect(outcome.a).toEqual(notPending);
      expect(outcome.b.ok).toBe(true);
      expect(outcome.final.state).toEqual({ connected: false, requestState: "declined" });
    }
  });

  it("creates one request and rejects the others as duplicate-pending when the same send is made at once", async () => {
    const outcome = await expectOneOfTheOrders({
      setup: async () => undefined,
      a: (module) => module.sendRequest(alice, bob),
      b: (module) => module.sendRequest(alice, bob),
      observe: async (module) => ({ ...(await pairView(module)), nextId: await sendOrFail(module, alice, carol) }),
    });

    expect([outcome.a, outcome.b].filter((r) => r.ok)).toHaveLength(1);
    expect([outcome.a, outcome.b]).toContainEqual({ ok: false, reason: "duplicate-pending" });
    expect(outcome.final.pendingForBob).toHaveLength(1);
    expect(outcome.final.nextId).toBe("req-2");

    const module = freshConnections();
    const three = await Promise.all([
      module.sendRequest(alice, bob),
      module.sendRequest(alice, bob),
      module.sendRequest(alice, bob),
    ]);
    expect(three.filter((r) => r.ok)).toHaveLength(1);
    expect(three.filter((r) => !r.ok)).toEqual([
      { ok: false, reason: "duplicate-pending" },
      { ok: false, reason: "duplicate-pending" },
    ]);
    expect(await pendingOf(module, bob)).toHaveLength(1);
  });

  it("lets exactly one of withdraw and decline succeed on the same request", async () => {
    const outcome = await expectOneOfTheOrders(
      onPendingRequest(
        (module, id) => module.withdrawRequest(id, alice),
        (module, id) => module.declineRequest(id, bob),
      ),
    );

    if (outcome.a.ok) {
      expect(outcome.b).toEqual(notPending);
      expect(outcome.final.state).toEqual({ connected: false, requestState: "withdrawn" });
    } else {
      expect(outcome.a).toEqual(notPending);
      expect(outcome.b.ok).toBe(true);
      expect(outcome.final.state).toEqual({ connected: false, requestState: "declined" });
    }
  });

  it("connects the pair once when the recipient accepts twice at once", async () => {
    const outcome = await expectOneOfTheOrders({
      setup: (module: Connections) => sendOrFail(module, alice, bob),
      a: (module, id) => module.acceptRequest(id, bob),
      b: (module, id) => module.acceptRequest(id, bob),
      observe: async (module) => ({
        state: await stateOf(module, alice, bob),
        laterSend: await module.sendRequest(alice, bob),
      }),
    });

    expect([outcome.a, outcome.b].filter((r) => r.ok)).toHaveLength(1);
    expect([outcome.a, outcome.b]).toContainEqual(notPending);
    expect(outcome.final.state).toEqual({ connected: true, requestState: "accepted" });
    expect(outcome.final.laterSend).toEqual({ ok: false, reason: "already-connected" });
  });

  it("never shows a request accepted without its connection to a read made during the accept", async () => {
    const consistent = [
      { connected: false, requestState: "pending" },
      { connected: true, requestState: "accepted" },
    ];
    const consistentAfterWithdraw = [
      { connected: false, requestState: "pending" },
      { connected: false, requestState: "withdrawn" },
    ];
    for (let turns = 0; turns <= 12; turns++) {
      const accepting = freshConnections();
      const id = await sendOrFail(accepting, alice, bob);
      const [accept, fromAlice, fromBob, listed] = await Promise.all([
        accepting.acceptRequest(id, bob),
        afterTurns(turns, () => stateOf(accepting, alice, bob)),
        afterTurns(turns, () => stateOf(accepting, bob, alice)),
        afterTurns(turns, () => pendingOf(accepting, bob)),
      ]);
      expect(accept.ok).toBe(true);
      expect(consistent).toContainEqual(fromAlice);
      expect(consistent).toContainEqual(fromBob);
      expect([[], [{ id, sender: alice, recipient: bob, state: "pending" }]]).toContainEqual(listed);
      expect(await stateOf(accepting, alice, bob)).toEqual({ connected: true, requestState: "accepted" });

      const withdrawing = freshConnections();
      const withdrawnId = await sendOrFail(withdrawing, alice, bob);
      const [withdraw, seen, listedDuringWithdraw] = await Promise.all([
        withdrawing.withdrawRequest(withdrawnId, alice),
        afterTurns(turns, () => stateOf(withdrawing, alice, bob)),
        afterTurns(turns, () => pendingOf(withdrawing, bob)),
      ]);
      expect(withdraw.ok).toBe(true);
      expect(consistentAfterWithdraw).toContainEqual(seen);
      expect([[], [{ id: withdrawnId, sender: alice, recipient: bob, state: "pending" }]]).toContainEqual(
        listedDuringWithdraw,
      );
    }
  });

  it("gives the outcome of erase first or erase last when a member is erased during another operation", async () => {
    // Both listing orders: the operation started first must not decide the outcome.
    const accepts: Array<Scenario<string, unknown, unknown, View>> = [
      onPendingRequest(
        (module) => module.eraseMember(alice),
        (module, id) => module.acceptRequest(id, bob),
      ),
      onPendingRequest(
        (module, id) => module.acceptRequest(id, bob),
        (module) => module.eraseMember(alice),
      ),
    ];
    for (const scenario of accepts) {
      const outcome = await expectOneOfTheOrders(scenario);
      // The erase answers ok either way; the accept is ok (accept first) or request-not-found (erase first).
      const results = [outcome.a, outcome.b] as Array<{ ok: boolean; value?: unknown; reason?: string }>;
      expect(results).toContainEqual({ ok: true });
      const accept = results.find((r) => r.value !== undefined || r.reason !== undefined);
      expect(accept?.ok || accept?.reason === "request-not-found").toBe(true);
      expect(outcome.final).toEqual({ state: none, pendingForAlice: [], pendingForBob: [] });
    }

    // The erase also lands at every point inside an accept already in flight.
    for (let turns = 0; turns <= 8; turns++) {
      const outcome = await expectOneOfTheOrders(
        onPendingRequest(
          (module, id) => module.acceptRequest(id, bob),
          (module) => afterTurns(turns, () => module.eraseMember(alice)),
        ),
      );
      expect(outcome.final).toEqual({ state: none, pendingForAlice: [], pendingForBob: [] });
    }

    const sends: Array<{ a: Op; b: Op }> = [
      { a: (m: Connections) => m.eraseMember(alice), b: (m: Connections) => m.sendRequest(alice, bob) },
      { a: (m: Connections) => m.sendRequest(alice, bob), b: (m: Connections) => m.eraseMember(alice) },
    ];
    for (const { a, b } of sends) {
      const outcome = await expectOneOfTheOrders({ setup: async () => undefined, a, b, observe: pairView });
      expect([outcome.a, outcome.b]).toContainEqual({ ok: true });
      const view = outcome.final;
      // Send first then erased: nothing. Erase first then sent: a pending request with its owner.
      expect([none, { connected: false, requestState: "pending" }]).toContainEqual(view.state);
      expect(view.pendingForBob).toHaveLength(view.state.requestState === "pending" ? 1 : 0);
    }

    const twice = await expectOneOfTheOrders({
      setup: async () => undefined,
      a: (module) => module.eraseMember(alice),
      b: (module) => module.eraseMember(alice),
      observe: pairView,
    });
    expect([twice.a, twice.b]).toEqual([{ ok: true }, { ok: true }]);
  });

  it("lets simultaneous operations on different pairs all succeed", async () => {
    const outcome = await expectOneOfTheOrders({
      setup: async () => undefined,
      a: (module) => module.sendRequest(alice, bob),
      b: (module) => module.sendRequest(carol, dave),
      observe: async (module) => ({ forBob: await pendingOf(module, bob), forDave: await pendingOf(module, dave) }),
    });

    expect(outcome.a.ok && outcome.b.ok).toBe(true);
    expect(outcome.final.forBob).toHaveLength(1);
    expect(outcome.final.forDave).toHaveLength(1);
    const ids = [outcome.final.forBob[0]?.id, outcome.final.forDave[0]?.id].sort();
    expect(ids).toEqual(["req-1", "req-2"]);
  });

  it("gives a rejected operation its own reason and leaves the simultaneous valid one untouched", async () => {
    const outcome = await expectOneOfTheOrders({
      setup: async () => undefined,
      a: (module) => module.sendRequest(memberId(""), bob),
      b: (module) => module.sendRequest(alice, bob),
      observe: pairView,
    });
    expect(outcome.a).toEqual({ ok: false, reason: "blank-member-id" });
    expect(outcome.b).toMatchObject({ ok: true, value: { id: "req-1", sender: alice, recipient: bob } });

    const unknown = await expectOneOfTheOrders(
      onPendingRequest(
        (module) => module.acceptRequest("req-404", bob),
        (module, id) => module.acceptRequest(id, bob),
      ),
    );
    expect(unknown.a).toEqual({ ok: false, reason: "request-not-found" });
    expect(unknown.b.ok).toBe(true);
    expect(unknown.final.state).toEqual({ connected: true, requestState: "accepted" });
  });

  it("lets the operations behind a failing one run normally and gives its caller the original error", async () => {
    const failure = new Error("id generator is down");
    let calls = 0;
    const module = createConnections({
      ids: {
        next: () => {
          calls += 1;
          if (calls === 1) throw failure;
          return `req-${calls}`;
        },
      },
    });

    const [failing, other, read] = await Promise.allSettled([
      module.sendRequest(alice, bob),
      module.sendRequest(carol, dave),
      module.getPairState(alice, bob),
    ]);

    expect(failing).toEqual({ status: "rejected", reason: failure });
    expect(other).toMatchObject({ status: "fulfilled", value: { ok: true, value: { sender: carol, recipient: dave } } });
    expect(read).toEqual({ status: "fulfilled", value: { ok: true, value: none } });
    expect(await stateOf(module, alice, bob)).toEqual(none);
    expect(await pendingOf(module, bob)).toEqual([]);
    expect(await module.sendRequest(alice, bob)).toMatchObject({ ok: true, value: { sender: alice, recipient: bob } });
  });
});
