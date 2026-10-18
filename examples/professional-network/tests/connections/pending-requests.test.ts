import { describe, expect, it } from "vitest";
import { alice, bob, carol, dave, erin, freshConnections, sendOrFail } from "./support.js";

describe("requests pending for a recipient", () => {
  it("lists only the requests addressed to the member, oldest first", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);
    await sendOrFail(connections, carol, bob);
    await sendOrFail(connections, dave, erin);
    await sendOrFail(connections, bob, dave);

    const pending = await connections.listPendingRequests(bob);

    expect(pending).toEqual([
      { id: "req-1", sender: alice, recipient: bob, state: "pending" },
      { id: "req-2", sender: carol, recipient: bob, state: "pending" },
    ]);
  });

  it("is an empty list for a member with no request", async () => {
    const connections = freshConnections();

    expect(await connections.listPendingRequests(bob)).toEqual([]);
  });

  it("does not show a request to its sender", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);

    expect(await connections.listPendingRequests(alice)).toEqual([]);
  });
});
