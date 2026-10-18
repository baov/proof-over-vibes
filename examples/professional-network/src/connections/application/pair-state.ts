import type { MemberId } from "../domain/member-id.js";
import { accepted } from "../domain/result.js";
import type { Result } from "../domain/result.js";
import { pairState } from "../domain/pair-state.js";
import type { PairState } from "../domain/pair-state.js";
import { blankIdRejection } from "./blank-ids.js";
import type { RequestStore } from "./ports.js";

export async function getPairState(
  deps: { store: RequestStore },
  a: MemberId,
  b: MemberId,
): Promise<Result<PairState, "blank-member-id">> {
  const blank = blankIdRejection(a, b);
  if (blank) return blank;
  const between = await deps.store.requestsBetween(a, b);
  const connection = await deps.store.findConnection(a, b);
  return accepted(pairState(between, connection));
}
