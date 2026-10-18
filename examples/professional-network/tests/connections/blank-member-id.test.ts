import { describe, expect, it } from "vitest";
import { memberId } from "../../src/connections/index.js";
import { alice, bob, freshConnections, pendingOf, sendOrFail, stateOf } from "./support.js";

const blank = { ok: false, reason: "blank-member-id" };
const none = { connected: false, requestState: "none" };

const empty = memberId("");
const spaces = memberId("   ");
const tab = memberId("\t");
const lineBreak = memberId("\n");
const blankForms = [empty, spaces, tab, lineBreak, memberId(" \t\r\n ")];

describe("send with a blank member id", () => {
  it("rejects a send whose sender is blank, and stores nothing", async () => {
    for (const sender of [empty, spaces, tab, lineBreak]) {
      const connections = freshConnections();

      expect(await connections.sendRequest(sender, bob)).toEqual(blank);
      expect(await pendingOf(connections, bob)).toEqual([]);
      expect(await stateOf(connections, alice, bob)).toEqual(none);
    }
  });

  it("rejects a send whose recipient is blank, and stores nothing", async () => {
    for (const recipient of [empty, spaces, tab, lineBreak]) {
      const connections = freshConnections();

      expect(await connections.sendRequest(alice, recipient)).toEqual(blank);
      expect(await pendingOf(connections, alice)).toEqual([]);
      expect(await pendingOf(connections, bob)).toEqual([]);
    }
  });

  it("reports a send with both ids blank as blank-member-id, not as a request to oneself", async () => {
    const connections = freshConnections();

    expect(await connections.sendRequest(empty, empty)).toEqual(blank);
    expect(await connections.sendRequest(spaces, spaces)).toEqual(blank);
    expect(await connections.sendRequest(empty, spaces)).toEqual(blank);
  });

  it("does not draw a request id for a rejected blank send", async () => {
    const connections = freshConnections();
    await connections.sendRequest(empty, bob);
    await connections.sendRequest(alice, spaces);
    await connections.sendRequest(empty, empty);

    const result = await connections.sendRequest(alice, bob);

    expect(result.ok && result.value.id).toBe("req-1");
  });
});

describe("accept, decline and withdraw with a blank acting member", () => {
  const operations = [
    ["accept", (c: ReturnType<typeof freshConnections>, id: string, m: typeof empty) => c.acceptRequest(id, m)],
    ["decline", (c: ReturnType<typeof freshConnections>, id: string, m: typeof empty) => c.declineRequest(id, m)],
    ["withdraw", (c: ReturnType<typeof freshConnections>, id: string, m: typeof empty) => c.withdrawRequest(id, m)],
  ] as const;

  async function expectRejectedAndPending(operation: (typeof operations)[number]) {
    const connections = freshConnections();
    const id = await sendOrFail(connections, alice, bob);

    for (const member of blankForms) expect(await operation[1](connections, id, member)).toEqual(blank);

    expect(await stateOf(connections, alice, bob)).toEqual({ connected: false, requestState: "pending" });
    expect(await pendingOf(connections, bob)).toHaveLength(1);
  }

  it("rejects an accept by a blank member and leaves the request pending", () => expectRejectedAndPending(operations[0]));
  it("rejects a decline by a blank member and leaves the request pending", () => expectRejectedAndPending(operations[1]));
  it("rejects a withdrawal by a blank member and leaves the request pending", () => expectRejectedAndPending(operations[2]));

  it("reports a blank acting member before an unknown request id, on accept, decline and withdraw", async () => {
    const connections = freshConnections();

    for (const [, operation] of operations) expect(await operation(connections, "req-404", empty)).toEqual(blank);
  });

  it("reports a blank acting member before the not-recipient, not-sender and not-pending reasons", async () => {
    const connections = freshConnections();
    const pending = await sendOrFail(connections, alice, bob);
    for (const [, operation] of operations) expect(await operation(connections, pending, spaces)).toEqual(blank);

    const withdrawn = await sendOrFail(connections, alice, memberId("carol"));
    await connections.withdrawRequest(withdrawn, alice);
    const declined = await sendOrFail(connections, alice, memberId("dave"));
    await connections.declineRequest(declined, memberId("dave"));
    const accepted = await sendOrFail(connections, alice, memberId("erin"));
    await connections.acceptRequest(accepted, memberId("erin"));
    for (const id of [withdrawn, declined, accepted]) {
      for (const [, operation] of operations) expect(await operation(connections, id, tab)).toEqual(blank);
    }
  });
});

describe("reads and erase with a blank member id", () => {
  it("rejects a state query with a blank member on either side, also the same blank twice", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);

    expect(await connections.getPairState(empty, bob)).toEqual(blank);
    expect(await connections.getPairState(alice, spaces)).toEqual(blank);
    expect(await connections.getPairState(empty, spaces)).toEqual(blank);
    expect(await connections.getPairState(empty, empty)).toEqual(blank);
    expect(await connections.getPairState(alice, alice)).toEqual({ ok: true, value: none });
  });

  it("rejects a pending list for a blank member", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);

    for (const member of blankForms) expect(await connections.listPendingRequests(member)).toEqual(blank);
    expect(await pendingOf(connections, bob)).toHaveLength(1);
  });

  it("rejects the erasure of a blank member and erases nothing", async () => {
    const connections = freshConnections();
    await sendOrFail(connections, alice, bob);

    expect(await connections.eraseMember(empty)).toEqual(blank);
    expect(await connections.eraseMember(empty)).toEqual(blank);
    expect(await connections.eraseMember(tab)).toEqual(blank);

    expect(await stateOf(connections, alice, bob)).toEqual({ connected: false, requestState: "pending" });
    expect(await pendingOf(connections, bob)).toHaveLength(1);
    expect(await connections.eraseMember(memberId("carol"))).toEqual({ ok: true });
  });
});

describe("what counts as blank", () => {
  it("treats an empty id, spaces, tabs and line breaks as blank", async () => {
    const forms = ["", " ", "     ", "\t", "\n", "\r\n", " \t \n "];
    for (const form of forms) {
      const connections = freshConnections();

      expect(await connections.sendRequest(memberId(form), bob)).toEqual(blank);
      expect(await connections.getPairState(alice, memberId(form))).toEqual(blank);
    }
  });

  it("treats non-breaking and ideographic spaces as blank, and zero-width characters as not blank", async () => {
    for (const form of [" ", "　", " ", " ", "  　 "]) {
      expect(await freshConnections().sendRequest(memberId(form), bob)).toEqual(blank);
    }
    for (const form of ["​", "‍", "⁠", "﻿"]) {
      const connections = freshConnections();

      const result = await connections.sendRequest(memberId(form), bob);

      expect(result.ok && result.value.sender).toBe(form);
    }
  });

  it("keeps an id with blanks around or inside real characters as it is", async () => {
    const connections = freshConnections();
    const padded = memberId(" alice ");

    const spaced = await connections.sendRequest(memberId("a b"), bob);
    const result = await connections.sendRequest(padded, bob);

    expect(spaced.ok && spaced.value.sender).toBe("a b");
    expect(result.ok && result.value.sender).toBe(" alice ");
    expect(await stateOf(connections, padded, bob)).toEqual({ connected: false, requestState: "pending" });
    expect(await stateOf(connections, alice, bob)).toEqual(none);
  });
});
