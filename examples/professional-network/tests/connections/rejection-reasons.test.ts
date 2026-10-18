import { describe, expect, it } from "vitest";
import { alice, bob, carol, connectionsWithIds, freshConnections, sendOrFail } from "./support.js";

async function rejection(result: Promise<{ ok: boolean; reason?: string }>): Promise<string> {
  const outcome = await result;
  if (outcome.ok || outcome.reason === undefined) throw new Error("expected a rejection");
  return outcome.reason;
}

describe("rejection reasons", () => {
  it("gives every rejected case its own reason", async () => {
    const connections = freshConnections();
    const selfRequest = await rejection(connections.sendRequest(alice, alice));

    const pendingId = await sendOrFail(connections, alice, bob);
    const duplicatePending = await rejection(connections.sendRequest(alice, bob));
    const reversePending = await rejection(connections.sendRequest(bob, alice));
    const notRecipient = await rejection(connections.acceptRequest(pendingId, carol));
    const requestNotFound = await rejection(connections.acceptRequest("req-404", bob));

    await connections.acceptRequest(pendingId, bob);
    const alreadyConnected = await rejection(connections.sendRequest(alice, bob));
    const notPending = await rejection(connections.acceptRequest(pendingId, bob));

    const reasons = [
      selfRequest,
      duplicatePending,
      reversePending,
      alreadyConnected,
      notRecipient,
      notPending,
      requestNotFound,
    ];
    expect(new Set(reasons).size).toBe(reasons.length);
    expect(reasons).toEqual([
      "self-request",
      "duplicate-pending",
      "reverse-pending",
      "already-connected",
      "not-recipient",
      "not-pending",
      "request-not-found",
    ]);
  });

  it("gives the rejections of declining and withdrawing their own reasons, distinct from the others", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);
    const notSender = await rejection(connections.withdrawRequest(id, bob));
    const notRecipient = await rejection(connections.declineRequest(id, alice));
    const requestNotFound = await rejection(connections.withdrawRequest("req-404", alice));
    await connections.declineRequest(id, bob);
    const notPending = await rejection(connections.withdrawRequest(id, alice));
    const previouslyDeclined = await rejection(connections.sendRequest(alice, bob));

    const taken = connectionsWithIds("req-1", "req-1");
    await sendOrFail(taken, alice, bob);
    const requestIdTaken = await rejection(taken.sendRequest(carol, bob));

    const reasons = [notSender, notRecipient, requestNotFound, notPending, previouslyDeclined, requestIdTaken];
    expect(new Set(reasons).size).toBe(reasons.length);
    expect(reasons).toEqual([
      "not-sender",
      "not-recipient",
      "request-not-found",
      "not-pending",
      "previously-declined",
      "request-id-taken",
    ]);
  });
});
