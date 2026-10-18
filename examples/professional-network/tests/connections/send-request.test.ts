import { describe, expect, it } from "vitest";
import { alice, bob, carol, connectionsWithIds, dave, freshConnections, sendOrFail } from "./support.js";

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
    expect(await connections.listPendingRequests(alice)).toEqual([]);
  });

  it("rejects a second request to the same member while one is pending", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);

    const result = await connections.sendRequest(alice, bob);

    expect(result).toEqual({ ok: false, reason: "duplicate-pending" });
    expect(await connections.listPendingRequests(bob)).toHaveLength(1);
  });

  it("rejects a request to a member who has a pending request to the sender, without accepting it", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);

    const result = await connections.sendRequest(bob, alice);

    expect(result).toEqual({ ok: false, reason: "reverse-pending" });
    expect(await connections.listPendingRequests(bob)).toEqual([
      { id: "req-1", sender: alice, recipient: bob, state: "pending" },
    ]);
    expect(await connections.listPendingRequests(alice)).toEqual([]);
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
    expect(await connections.listPendingRequests(bob)).toEqual([]);
    expect(await connections.listPendingRequests(alice)).toEqual([]);
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
    expect(await connections.getPairState(alice, bob)).toEqual({ connected: false, requestState: "pending" });
    expect(await connections.listPendingRequests(bob)).toEqual([
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
      expect(await connections.listPendingRequests(bob)).toHaveLength(1);
      await connections.withdrawRequest(id, alice);
    }

    expect(new Set(ids).size).toBe(3);
    expect(await connections.listPendingRequests(bob)).toEqual([]);
  });

  it("rejects a new request from the member whose request was declined, and stores nothing", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.declineRequest(id, bob);

    const result = await connections.sendRequest(alice, bob);

    expect(result).toEqual({ ok: false, reason: "previously-declined" });
    expect(await connections.getPairState(alice, bob)).toEqual({ connected: false, requestState: "declined" });
    expect(await connections.listPendingRequests(bob)).toEqual([]);
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
    expect(await connections.listPendingRequests(bob)).toEqual([
      { id: "req-1", sender: alice, recipient: bob, state: "pending" },
    ]);
    expect(await connections.getPairState(carol, bob)).toEqual({ connected: false, requestState: "none" });
  });

  it("reports a broken business rule before an id that is already used", async () => {
    const connections = connectionsWithIds("req-1", "req-1");
    await sendOrFail(connections, alice, bob);

    expect(await connections.sendRequest(alice, bob)).toEqual({ ok: false, reason: "duplicate-pending" });
  });
});
