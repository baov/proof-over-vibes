import { createConnections, memberId } from "../../src/connections/index.js";
import type { Connections, ConnectionRequest, IdGenerator, MemberId, PairState } from "../../src/connections/index.js";

export const alice = memberId("alice");
export const bob = memberId("bob");
export const carol = memberId("carol");
export const dave = memberId("dave");
export const erin = memberId("erin");

/** Ids req-1, req-2, ... so that a test can predict them. */
function sequentialIds(): IdGenerator {
  let last = 0;
  return { next: () => `req-${++last}` };
}

/** A fresh module on an in-memory store, with deterministic request ids. */
export function freshConnections(): Connections {
  return createConnections({ ids: sequentialIds() });
}

/** Sends a request that must be accepted by the rules, and returns its id. */
export async function sendOrFail(
  module: Connections,
  sender: MemberId,
  recipient: MemberId,
): Promise<string> {
  const result = await module.sendRequest(sender, recipient);
  if (!result.ok) throw new Error(`setup failed: ${result.reason}`);
  return result.value.id;
}

/** A fresh module whose id generator hands out the given ids in order, repeating the last one. */
export function connectionsWithIds(...ids: string[]): Connections {
  let index = 0;
  return createConnections({ ids: { next: () => ids[Math.min(index++, ids.length - 1)] as string } });
}

/** The state of a pair, which must be answered (not rejected). */
export async function stateOf(module: Connections, a: MemberId, b: MemberId): Promise<PairState> {
  const result = await module.getPairState(a, b);
  if (!result.ok) throw new Error(`state query rejected: ${result.reason}`);
  return result.value;
}

/** The pending requests of a member, which must be answered (not rejected). */
export async function pendingOf(module: Connections, member: MemberId): Promise<readonly ConnectionRequest[]> {
  const result = await module.listPendingRequests(member);
  if (!result.ok) throw new Error(`pending list rejected: ${result.reason}`);
  return result.value;
}
