import { describe, expect, it } from "vitest";
import { alice, bob, carol, connectionsWithIds, dave, freshConnections, sendOrFail, stateOf, pendingOf } from "./support.js";

describe("send a connection request", () => {
  it("a member sends a request to another member and it is pending", async () => {
    const connections = freshConnections();

    const result = await connections.sendRequest(alice, bob);

    expect(result).toEqual({
      ok: true,
      value: { id: "req-1", sender: alice, recipient: bob, state: "pending" },
    });
  });

  it("rejects a request a member sends to themselves, and stores nothing", async () => {
    const connections = freshConnections();

    const result = await connections.sendRequest(alice, alice);

    expect(result).toEqual({ ok: false, reason: "self-request" });
    expect(await pendingOf(connections, alice)).toEqual([]);
  });

  it("rejects a second request to the same member while one is pending", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);

    const result = await connections.sendRequest(alice, bob);

    expect(result).toEqual({ ok: false, reason: "duplicate-pending" });
    expect(await pendingOf(connections, bob)).toHaveLength(1);
  });

  it("rejects a request to a member who has a pending request to the sender, without accepting it", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);

    const result = await connections.sendRequest(bob, alice);

    expect(result).toEqual({ ok: false, reason: "reverse-pending" });
    expect(await pendingOf(connections, bob)).toEqual([
      { id: "req-1", sender: alice, recipient: bob, state: "pending" },
    ]);
    expect(await pendingOf(connections, alice)).toEqual([]);
  });

  it("still allows a request to another member while one is pending", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);

    const result = await connections.sendRequest(alice, carol);

    expect(result.ok).toBe(true);
  });

  it("rejects a request between two connected members, whichever of them sends it", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.acceptRequest(id, bob);

    expect(await connections.sendRequest(alice, bob)).toEqual({ ok: false, reason: "already-connected" });
    expect(await connections.sendRequest(bob, alice)).toEqual({ ok: false, reason: "already-connected" });
    expect(await pendingOf(connections, bob)).toEqual([]);
    expect(await pendingOf(connections, alice)).toEqual([]);
  });

  it("lets the sender send again after withdrawing: a new pending request, the old one not listed", async () => {
    const connections = freshConnections();
    const first = await sendOrFail(connections, alice, bob);
    await connections.withdrawRequest(first, alice);

    const result = await connections.sendRequest(alice, bob);

    expect(result).toEqual({
      ok: true,
      value: { id: "req-2", sender: alice, recipient: bob, state: "pending" },
    });
    expect(await stateOf(connections, alice, bob)).toEqual({ connected: false, requestState: "pending" });
    expect(await pendingOf(connections, bob)).toEqual([
      { id: "req-2", sender: alice, recipient: bob, state: "pending" },
    ]);
  });

  it("does not let a withdrawn request block the other member from sending", async () => {
    const connections = freshConnections();
    const first = await sendOrFail(connections, alice, bob);
    await connections.withdrawRequest(first, alice);

    const result = await connections.sendRequest(bob, alice);

    expect(result.ok).toBe(true);
  });

  it("accepts a new request each time after a withdrawal, however many times", async () => {
    const connections = freshConnections();
    const ids: string[] = [];
    for (let round = 0; round < 3; round++) {
      const id = await sendOrFail(connections, alice, bob);
      ids.push(id);
      expect(await pendingOf(connections, bob)).toHaveLength(1);
      await connections.withdrawRequest(id, alice);
    }

    expect(new Set(ids).size).toBe(3);
    expect(await pendingOf(connections, bob)).toEqual([]);
  });

  it("rejects a new request from the member whose request was declined, and stores nothing", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.declineRequest(id, bob);

    const result = await connections.sendRequest(alice, bob);

    expect(result).toEqual({ ok: false, reason: "previously-declined" });
    expect(await stateOf(connections, alice, bob)).toEqual({ connected: false, requestState: "declined" });
    expect(await pendingOf(connections, bob)).toEqual([]);
  });

  it("limits the decline block to that pair: the sender may ask others, others may ask the decliner", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.declineRequest(id, bob);

    expect((await connections.sendRequest(alice, carol)).ok).toBe(true);
    expect((await connections.sendRequest(carol, bob)).ok).toBe(true);
  });

  it("keeps the decline block whatever else happens between other members", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.declineRequest(id, bob);
    const other = await sendOrFail(connections, carol, dave);
    await connections.acceptRequest(other, dave);
    await sendOrFail(connections, alice, carol);

    expect(await connections.sendRequest(alice, bob)).toEqual({ ok: false, reason: "previously-declined" });
  });

  it("rejects a request whose generated id is already used, and leaves the existing request unchanged", async () => {
    const connections = connectionsWithIds("req-1", "req-1");
    await sendOrFail(connections, alice, bob);

    const result = await connections.sendRequest(carol, bob);

    expect(result).toEqual({ ok: false, reason: "request-id-taken" });
    expect(await pendingOf(connections, bob)).toEqual([
      { id: "req-1", sender: alice, recipient: bob, state: "pending" },
    ]);
    expect(await stateOf(connections, carol, bob)).toEqual({ connected: false, requestState: "none" });
  });

  it("reports a broken business rule before an id that is already used", async () => {
    const connections = connectionsWithIds("req-1", "req-1");
    await sendOrFail(connections, alice, bob);

    expect(await connections.sendRequest(alice, bob)).toEqual({ ok: false, reason: "duplicate-pending" });
  });

  describe("the decliner writes back", () => {
    async function declinedByBob() {
      const connections = freshConnections();
      const first = await sendOrFail(connections, alice, bob);
      await connections.declineRequest(first, bob);
      return { connections, first };
    }

    it("lets the decliner send a request back, pending, and keeps the declined request as it was", async () => {
      const { connections, first } = await declinedByBob();

      const result = await connections.sendRequest(bob, alice);

      expect(result).toEqual({ ok: true, value: { id: "req-2", sender: bob, recipient: alice, state: "pending" } });
      expect(await pendingOf(connections, alice)).toEqual([
        { id: "req-2", sender: bob, recipient: alice, state: "pending" },
      ]);
      expect(await connections.acceptRequest(first, bob)).toEqual({ ok: false, reason: "not-pending" });
    });

    it("still rejects the original sender while the decliner's request is pending", async () => {
      const { connections } = await declinedByBob();
      await sendOrFail(connections, bob, alice);

      expect(await connections.sendRequest(alice, bob)).toEqual({ ok: false, reason: "reverse-pending" });
      expect(await connections.sendRequest(alice, bob)).toEqual({ ok: false, reason: "reverse-pending" });
      expect(await pendingOf(connections, bob)).toEqual([]);
      expect(await stateOf(connections, alice, bob)).toEqual({ connected: false, requestState: "pending" });
    });

    it("rejects a second request of the decliner while the first is pending", async () => {
      const { connections } = await declinedByBob();
      await sendOrFail(connections, bob, alice);

      expect(await connections.sendRequest(bob, alice)).toEqual({ ok: false, reason: "duplicate-pending" });
      expect(await pendingOf(connections, alice)).toHaveLength(1);
    });

    it("blocks both members once the original sender declines the decliner's request", async () => {
      const { connections } = await declinedByBob();
      const second = await sendOrFail(connections, bob, alice);
      await connections.declineRequest(second, alice);

      expect(await connections.sendRequest(bob, alice)).toEqual({ ok: false, reason: "previously-declined" });
      expect(await connections.sendRequest(alice, bob)).toEqual({ ok: false, reason: "previously-declined" });
      expect(await stateOf(connections, alice, bob)).toEqual({ connected: false, requestState: "declined" });
      expect(await stateOf(connections, bob, alice)).toEqual({ connected: false, requestState: "declined" });
      expect(await pendingOf(connections, alice)).toEqual([]);
      expect(await pendingOf(connections, bob)).toEqual([]);
    });

    it("rejects a send between members connected through the decliner's request as already-connected", async () => {
      const { connections } = await declinedByBob();
      const second = await sendOrFail(connections, bob, alice);
      await connections.acceptRequest(second, alice);

      expect(await connections.sendRequest(alice, bob)).toEqual({ ok: false, reason: "already-connected" });
      expect(await connections.sendRequest(bob, alice)).toEqual({ ok: false, reason: "already-connected" });
      expect(await pendingOf(connections, alice)).toEqual([]);
      expect(await pendingOf(connections, bob)).toEqual([]);
    });
  });
});
