import { describe, expect, it } from "vitest";
import { alice, bob, carol, freshConnections, sendOrFail, stateOf } from "./support.js";

const notConnected = (requestState: string) => ({ connected: false, requestState });
const connected = (requestState: string) => ({ connected: true, requestState });

describe("state of a pair of members", () => {
  it("is not connected with request state none when the two never exchanged a request", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, carol);

    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("none"));
    expect(await stateOf(connections, bob, alice)).toEqual(notConnected("none"));
  });

  it("is not connected with request state none for a member and themselves", async () => {
    const connections = freshConnections();

    expect(await stateOf(connections, alice, alice)).toEqual(notConnected("none"));
  });

  it("is not connected with request state pending while a request is pending, seen from both members", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);

    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("pending"));
    expect(await stateOf(connections, bob, alice)).toEqual(notConnected("pending"));
  });

  it("is connected with request state accepted once the recipient accepts, seen from both members", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.acceptRequest(id, bob);

    expect(await stateOf(connections, alice, bob)).toEqual(connected("accepted"));
    expect(await stateOf(connections, bob, alice)).toEqual(connected("accepted"));
  });

  it("is left unchanged by rejected attempts to accept", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.acceptRequest(id, carol);
    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("pending"));

    await connections.acceptRequest(id, bob);
    await connections.acceptRequest(id, bob);
    await connections.acceptRequest(id, carol);
    expect(await stateOf(connections, alice, bob)).toEqual(connected("accepted"));
  });

  it("does not connect a member to anyone but the member they accepted", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.acceptRequest(id, bob);

    expect(await stateOf(connections, alice, carol)).toEqual(notConnected("none"));
    expect(await stateOf(connections, carol, alice)).toEqual(notConnected("none"));
    expect(await stateOf(connections, bob, carol)).toEqual(notConnected("none"));
    expect(await stateOf(connections, carol, bob)).toEqual(notConnected("none"));
    expect((await connections.sendRequest(carol, bob)).ok).toBe(true);
    expect((await connections.sendRequest(alice, carol)).ok).toBe(true);
  });

  it("is not connected with request state declined after a decline, seen from both members", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.declineRequest(id, bob);

    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("declined"));
    expect(await stateOf(connections, bob, alice)).toEqual(notConnected("declined"));
  });

  it("is not connected with request state withdrawn after a withdrawal, seen from both members", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    await connections.withdrawRequest(id, alice);

    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("withdrawn"));
    expect(await stateOf(connections, bob, alice)).toEqual(notConnected("withdrawn"));
  });

  it("reports the live request when the pair has several, otherwise the most recent", async () => {
    const connections = freshConnections();
    const first = await sendOrFail(connections, alice, bob);
    await connections.withdrawRequest(first, alice);
    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("withdrawn"));

    const second = await sendOrFail(connections, alice, bob);
    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("pending"));

    await connections.withdrawRequest(second, alice);
    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("withdrawn"));

    await sendOrFail(connections, alice, bob);
    await connections.acceptRequest("req-3", bob);
    expect(await stateOf(connections, alice, bob)).toEqual(connected("accepted"));
  });

  it("reports declined, the most recent, when a withdrawn request came before the declined one", async () => {
    const connections = freshConnections();
    const first = await sendOrFail(connections, alice, bob);
    await connections.withdrawRequest(first, alice);
    const second = await sendOrFail(connections, alice, bob);
    await connections.declineRequest(second, bob);

    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("declined"));
    expect(await stateOf(connections, bob, alice)).toEqual(notConnected("declined"));
  });

  it("reports the decliner's pending request over the earlier declined one, else the most recent", async () => {
    const connections = freshConnections();
    const first = await sendOrFail(connections, alice, bob);
    await connections.declineRequest(first, bob);
    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("declined"));
    expect(await stateOf(connections, bob, alice)).toEqual(notConnected("declined"));

    const second = await sendOrFail(connections, bob, alice);
    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("pending"));
    expect(await stateOf(connections, bob, alice)).toEqual(notConnected("pending"));

    await connections.declineRequest(second, alice);
    expect(await stateOf(connections, alice, bob)).toEqual(notConnected("declined"));
    expect(await stateOf(connections, bob, alice)).toEqual(notConnected("declined"));

    const other = freshConnections();
    const one = await sendOrFail(other, alice, bob);
    await other.declineRequest(one, bob);
    const two = await sendOrFail(other, bob, alice);
    await other.acceptRequest(two, alice);
    expect(await stateOf(other, alice, bob)).toEqual(connected("accepted"));
    expect(await stateOf(other, bob, alice)).toEqual(connected("accepted"));
  });
});
