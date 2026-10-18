import type { MemberId } from "../domain/member-id.js";
import { pairState } from "../domain/pair-state.js";
import type { PairState } from "../domain/pair-state.js";
import type { RequestStore } from "./ports.js";

export async function getPairState(
  deps: { store: RequestStore },
  a: MemberId,
  b: MemberId,
): Promise<PairState> {
  const between = await deps.store.requestsBetween(a, b);
  const connection = await deps.store.findConnection(a, b);
  return pairState(between, connection);
}
