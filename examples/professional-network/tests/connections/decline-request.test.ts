import { describe, expect, it } from "vitest";
import { alice, bob, carol, freshConnections, sendOrFail, stateOf, pendingOf } from "./support.js";

const notConnected = (requestState: string) => ({ connected: false, requestState });

describe("decline a connection request", () => {
  it("the recipient declines a pending request: not connected, state declined, no longer pending", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await sendOrFail(connections, carol, bob);

    const result = await connections.declineRequest(id, bob);

    expect(result).toEqual({
      ok: true,
      value: { id, sender: alice, recipient: bob, state: "declined" },
    });
    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("declined"));
    expect(await stateOf(connections, bob, alice)).toEqual(notConnected("declined"));
    expect(await pendingOf(connections, bob)).toEqual([
      { id: "req-2", sender: carol, recipient: bob, state: "pending" },
    ]);
  });

  it("rejects a member who is not the recipient, the sender included, and the request stays pending", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);

    expect(await connections.declineRequest(id, carol)).toEqual({ ok: false, reason: "not-recipient" });
    expect(await connections.declineRequest(id, alice)).toEqual({ ok: false, reason: "not-recipient" });

    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("pending"));
    expect(await pendingOf(connections, bob)).toHaveLength(1);
  });

  it("rejects declining a request that is not found, whoever asks", async () => {
    const connections = freshConnections();

    expect(await connections.declineRequest("req-404", bob)).toEqual({ ok: false, reason: "request-not-found" });
    expect(await connections.declineRequest("req-404", carol)).toEqual({ ok: false, reason: "request-not-found" });
  });

  it("rejects declining a request that is no longer pending, and the state is unchanged", async () => {
    const connections = freshConnections();
    const accepted = await sendOrFail(connections, alice, bob);
    await connections.acceptRequest(accepted, bob);
    const declined = await sendOrFail(connections, carol, bob);
    await connections.declineRequest(declined, bob);
    const withdrawn = await sendOrFail(connections, carol, alice);
    await connections.withdrawRequest(withdrawn, carol);

    expect(await connections.declineRequest(accepted, bob)).toEqual({ ok: false, reason: "not-pending" });
    expect(await connections.declineRequest(declined, bob)).toEqual({ ok: false, reason: "not-pending" });
    expect(await connections.declineRequest(withdrawn, alice)).toEqual({ ok: false, reason: "not-pending" });

    expect(await stateOf(connections, alice, bob)).toEqual({ connected: true, requestState: "accepted" });
    expect(await stateOf(connections, carol, bob)).toEqual(notConnected("declined"));
    expect(await stateOf(connections, carol, alice)).toEqual(notConnected("withdrawn"));
  });

  it("tells a member who is not the recipient so, even if the request is no longer pending", async () => {
    const connections = freshConnections();
    const accepted = await sendOrFail(connections, alice, bob);
    await connections.acceptRequest(accepted, bob);
    const declined = await sendOrFail(connections, carol, bob);
    await connections.declineRequest(declined, bob);
    const withdrawn = await sendOrFail(connections, carol, alice);
    await connections.withdrawRequest(withdrawn, carol);

    expect(await connections.declineRequest(accepted, carol)).toEqual({ ok: false, reason: "not-recipient" });
    expect(await connections.declineRequest(declined, alice)).toEqual({ ok: false, reason: "not-recipient" });
    expect(await connections.declineRequest(withdrawn, bob)).toEqual({ ok: false, reason: "not-recipient" });
  });
});
