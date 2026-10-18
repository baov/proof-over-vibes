import { describe, expect, it } from "vitest";
import { alice, bob, carol, dave, freshConnections, sendOrFail, stateOf, pendingOf } from "./support.js";

const none = { connected: false, requestState: "none" };

describe("erase a member", () => {
  it("leaves no request, connection or list entry that involves the erased member", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);
    await sendOrFail(connections, carol, alice);
    const connected = await sendOrFail(connections, alice, dave);
    await connections.acceptRequest(connected, dave);
    const elsewhere = await sendOrFail(connections, bob, carol);
    await connections.acceptRequest(elsewhere, carol);

    const result = await connections.eraseMember(alice);

    expect(result).toEqual({ ok: true });
    expect(await stateOf(connections, alice, bob)).toEqual(none);
    expect(await stateOf(connections, alice, carol)).toEqual(none);
    expect(await stateOf(connections, alice, dave)).toEqual(none);
    expect(await pendingOf(connections, bob)).toEqual([]);
    expect(await pendingOf(connections, alice)).toEqual([]);
    expect(await stateOf(connections, bob, carol)).toEqual({ connected: true, requestState: "accepted" });
  });

  it("lifts the decline block when either member of the declined pair is erased", async () => {
    const connections = freshConnections();
    const first = await sendOrFail(connections, alice, bob);
    await connections.declineRequest(first, bob);
    await connections.eraseMember(alice);
    expect(await stateOf(connections, alice, bob)).toEqual(none);
    expect((await connections.sendRequest(alice, bob)).ok).toBe(true);

    const second = await sendOrFail(connections, carol, dave);
    await connections.declineRequest(second, dave);
    await connections.eraseMember(dave);
    expect(await stateOf(connections, carol, dave)).toEqual(none);
    expect((await connections.sendRequest(carol, dave)).ok).toBe(true);
  });

  it("keeps the decline block when a third member is erased", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.declineRequest(id, bob);

    await connections.eraseMember(carol);

    expect(await connections.sendRequest(alice, bob)).toEqual({ ok: false, reason: "previously-declined" });
  });

  it("ends the connection of an erased member, and the other member can send a request again", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.acceptRequest(id, bob);

    await connections.eraseMember(alice);

    expect(await stateOf(connections, bob, alice)).toEqual(none);
    expect((await connections.sendRequest(bob, alice)).ok).toBe(true);
  });

  it("succeeds when the member is erased twice, or was never known, and changes nothing", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);

    expect(await connections.eraseMember(carol)).toEqual({ ok: true });
    expect(await connections.eraseMember(alice)).toEqual({ ok: true });
    expect(await connections.eraseMember(alice)).toEqual({ ok: true });

    expect(await pendingOf(connections, bob)).toEqual([]);
    expect(await stateOf(connections, alice, bob)).toEqual(none);
  });
});
