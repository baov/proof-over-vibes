import type { MemberId } from "../domain/member-id.js";
import { blankIdRejection } from "./blank-ids.js";
import type { RequestStore } from "./ports.js";

export type EraseResult = { ok: true } | { ok: false; reason: "blank-member-id" };

/** Nothing about the member remains. It always succeeds, also for a member the module never saw (D-26). */
export async function eraseMember(deps: { store: RequestStore }, member: MemberId): Promise<EraseResult> {
  const blank = blankIdRejection(member);
  if (blank) return blank;
  await deps.store.eraseMember(member);
  return { ok: true };
}
