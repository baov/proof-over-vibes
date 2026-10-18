import { describe, expect, it } from "vitest";
import { alice, bob, carol, freshConnections, sendOrFail, stateOf, pendingOf } from "./support.js";

describe("accept a connection request", () => {
  it("the recipient accepts a pending request and it is no longer pending", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await sendOrFail(connections, carol, bob);

    const result = await connections.acceptRequest(id, bob);

    expect(result).toEqual({
      ok: true,
      value: { id, sender: alice, recipient: bob, state: "accepted" },
    });
    expect(await pendingOf(connections, bob)).toEqual([
      { id: "req-2", sender: carol, recipient: bob, state: "pending" },
    ]);
  });

  it("rejects a member who is not the recipient, and the request stays pending", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);

    const result = await connections.acceptRequest(id, carol);

    expect(result).toEqual({ ok: false, reason: "not-recipient" });
    expect(await pendingOf(connections, bob)).toHaveLength(1);
  });

  it("rejects the sender accepting their own request", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);

    const result = await connections.acceptRequest(id, alice);

    expect(result).toEqual({ ok: false, reason: "not-recipient" });
    expect(await pendingOf(connections, bob)).toHaveLength(1);
  });

  it("rejects a request that is not found, whoever asks", async () => {
    const connections = freshConnections();

    expect(await connections.acceptRequest("req-404", bob)).toEqual({
      ok: false,
      reason: "request-not-found",
    });
    expect(await connections.acceptRequest("req-404", carol)).toEqual({
      ok: false,
      reason: "request-not-found",
    });
  });

  it("rejects accepting a request that is already accepted, and nothing changes", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.acceptRequest(id, bob);

    const result = await connections.acceptRequest(id, bob);

    expect(result).toEqual({ ok: false, reason: "not-pending" });
  });

  it("tells a member who is not the recipient they are not the recipient, even if the request is not pending", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.acceptRequest(id, bob);

    const result = await connections.acceptRequest(id, carol);

    expect(result).toEqual({ ok: false, reason: "not-recipient" });
  });

  it("rejects accepting a request that was declined or withdrawn, and the state is unchanged", async () => {
    const connections = freshConnections();
    const declined = await sendOrFail(connections, alice, bob);
    await connections.declineRequest(declined, bob);
    const withdrawn = await sendOrFail(connections, carol, bob);
    await connections.withdrawRequest(withdrawn, carol);

    expect(await connections.acceptRequest(declined, bob)).toEqual({ ok: false, reason: "not-pending" });
    expect(await connections.acceptRequest(withdrawn, bob)).toEqual({ ok: false, reason: "not-pending" });

    expect(await stateOf(connections, alice, bob)).toEqual({ connected: false, requestState: "declined" });
    expect(await stateOf(connections, carol, bob)).toEqual({ connected: false, requestState: "withdrawn" });
  });

  it("connects the two when the original sender accepts the decliner's request", async () => {
    const connections = freshConnections();
    const first = await sendOrFail(connections, alice, bob);
    await connections.declineRequest(first, bob);
    const second = await sendOrFail(connections, bob, alice);

    const result = await connections.acceptRequest(second, alice);

    expect(result).toEqual({ ok: true, value: { id: second, sender: bob, recipient: alice, state: "accepted" } });
    expect(await stateOf(connections, alice, bob)).toEqual({ connected: true, requestState: "accepted" });
    expect(await stateOf(connections, bob, alice)).toEqual({ connected: true, requestState: "accepted" });
    expect(await connections.acceptRequest(first, bob)).toEqual({ ok: false, reason: "not-pending" });
  });
});
