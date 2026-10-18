import { describe, expect, it } from "vitest";
import { memberId } from "../../src/connections/index.js";
import { freshConnections, sendOrFail, stateOf } from "./support.js";

// Member ids are free strings (D-15): these two pairs are made of the same characters
// once joined with ":", yet they share no member.
const annBo = memberId("ann:bo");
const cy = memberId("cy");
const ann = memberId("ann");
const boCy = memberId("bo:cy");

const none = { connected: false, requestState: "none" };
const connected = { connected: true, requestState: "accepted" };

describe("members whose ids look alike once joined", () => {
  it("does not show two unrelated members as connected, and lets one send to the other", async () => {
    const connections = freshConnections();
    const id = await sendOrFail(connections, annBo, cy);
    await connections.acceptRequest(id, cy);

    expect(await stateOf(connections, ann, boCy)).toEqual(none);
    expect(await stateOf(connections, boCy, ann)).toEqual(none);
    const result = await connections.sendRequest(ann, boCy);

    expect(result.ok).toBe(true);
    expect(await stateOf(connections, ann, boCy)).toEqual({ connected: false, requestState: "pending" });
    expect(await stateOf(connections, annBo, cy)).toEqual(connected);
  });

  it("keeps two connections apart, so erasing a member ends only the connection that member is in", async () => {
    const connections = freshConnections();
    const first = await sendOrFail(connections, annBo, cy);
    const second = await sendOrFail(connections, ann, boCy);
    await connections.acceptRequest(first, cy);
    await connections.acceptRequest(second, boCy);

    expect(await stateOf(connections, annBo, cy)).toEqual(connected);
    expect(await stateOf(connections, ann, boCy)).toEqual(connected);

    await connections.eraseMember(annBo);

    expect(await stateOf(connections, annBo, cy)).toEqual(none);
    expect(await stateOf(connections, ann, boCy)).toEqual(connected);
  });
});
