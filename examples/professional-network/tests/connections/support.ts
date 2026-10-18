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

/** Two operations on the same fresh module, plus what is observed once both have answered. */
export interface Scenario<Context, A, B, Observed> {
  /** Builds the starting state; its result is handed to both operations and to `observe`. */
  setup: (module: Connections) => Promise<Context>;
  a: (module: Connections, context: Context) => Promise<A>;
  b: (module: Connections, context: Context) => Promise<B>;
  /** The final state worth comparing (pair state, pending lists, next id...). */
  observe: (module: Connections, context: Context) => Promise<Observed>;
}

export interface Outcome<A, B, Observed> {
  a: A;
  b: B;
  final: Observed;
}

/** Runs the two operations one after the other on a fresh module, in the given order. */
async function runSequentially<Context, A, B, Observed>(
  scenario: Scenario<Context, A, B, Observed>,
  first: "a" | "b",
): Promise<Outcome<A, B, Observed>> {
  const module = freshConnections();
  const context = await scenario.setup(module);
  let a: A;
  let b: B;
  if (first === "a") {
    a = await scenario.a(module, context);
    b = await scenario.b(module, context);
  } else {
    b = await scenario.b(module, context);
    a = await scenario.a(module, context);
  }
  return { a, b, final: await scenario.observe(module, context) };
}

/** The oracle: the two outcomes of running the operations sequentially, a then b and b then a. */
export async function bothOrders<Context, A, B, Observed>(
  scenario: Scenario<Context, A, B, Observed>,
): Promise<[Outcome<A, B, Observed>, Outcome<A, B, Observed>]> {
  return [await runSequentially(scenario, "a"), await runSequentially(scenario, "b")];
}

/** Starts both operations in the same tick, before either has answered, on a fresh module. */
export async function simultaneously<Context, A, B, Observed>(
  scenario: Scenario<Context, A, B, Observed>,
): Promise<Outcome<A, B, Observed>> {
  const module = freshConnections();
  const context = await scenario.setup(module);
  const [a, b] = await Promise.all([scenario.a(module, context), scenario.b(module, context)]);
  return { a, b, final: await scenario.observe(module, context) };
}
