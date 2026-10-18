import { describe, expect, it } from "vitest";
import { alice, bob, carol, freshConnections, sendOrFail } from "./support.js";

const notConnected = (requestState: string) => ({ connected: false, requestState });

describe("withdraw a connection request", () => {
  it("the sender withdraws a pending request: not connected, state withdrawn, no longer pending", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);

    const result = await connections.withdrawRequest(id, alice);

    expect(result).toEqual({
      ok: true,
      value: { id, sender: alice, recipient: bob, state: "withdrawn" },
    });
    expect(await connections.getPairState(alice, bob)).toEqual(notConnected("withdrawn"));
    expect(await connections.getPairState(bob, alice)).toEqual(notConnected("withdrawn"));
    expect(await connections.listPendingRequests(bob)).toEqual([]);
  });

  it("rejects a member who is not the sender, the recipient included, and the request stays pending", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);

    expect(await connections.withdrawRequest(id, carol)).toEqual({ ok: false, reason: "not-sender" });
    expect(await connections.withdrawRequest(id, bob)).toEqual({ ok: false, reason: "not-sender" });

    expect(await connections.getPairState(alice, bob)).toEqual(notConnected("pending"));
    expect(await connections.listPendingRequests(bob)).toHaveLength(1);
  });

  it("rejects withdrawing a request that is not found, whoever asks", async () => {
    const connections = freshConnections();

    expect(await connections.withdrawRequest("req-404", alice)).toEqual({ ok: false, reason: "request-not-found" });
    expect(await connections.withdrawRequest("req-404", carol)).toEqual({ ok: false, reason: "request-not-found" });
  });

  it("rejects withdrawing a request that is no longer pending, and the state is unchanged", async () => {
    const connections = freshConnections();
    const accepted = await sendOrFail(connections, alice, bob);
    await connections.acceptRequest(accepted, bob);
    const declined = await sendOrFail(connections, carol, bob);
    await connections.declineRequest(declined, bob);
    const withdrawn = await sendOrFail(connections, carol, alice);
    await connections.withdrawRequest(withdrawn, carol);

    expect(await connections.withdrawRequest(accepted, alice)).toEqual({ ok: false, reason: "not-pending" });
    expect(await connections.withdrawRequest(declined, carol)).toEqual({ ok: false, reason: "not-pending" });
    expect(await connections.withdrawRequest(withdrawn, carol)).toEqual({ ok: false, reason: "not-pending" });

    expect(await connections.getPairState(alice, bob)).toEqual({ connected: true, requestState: "accepted" });
    expect(await connections.getPairState(carol, bob)).toEqual(notConnected("declined"));
    expect(await connections.getPairState(carol, alice)).toEqual(notConnected("withdrawn"));
  });

  it("tells a member who is not the sender so, even if the request is no longer pending", async () => {
    const connections = freshConnections();
    const accepted = await sendOrFail(connections, alice, bob);
    await connections.acceptRequest(accepted, bob);
    const declined = await sendOrFail(connections, carol, bob);
    await connections.declineRequest(declined, bob);
    const withdrawn = await sendOrFail(connections, carol, alice);
    await connections.withdrawRequest(withdrawn, carol);

    expect(await connections.withdrawRequest(accepted, bob)).toEqual({ ok: false, reason: "not-sender" });
    expect(await connections.withdrawRequest(declined, bob)).toEqual({ ok: false, reason: "not-sender" });
    expect(await connections.withdrawRequest(withdrawn, alice)).toEqual({ ok: false, reason: "not-sender" });
  });
});
