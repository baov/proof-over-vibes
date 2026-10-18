import type { MemberId } from "../domain/member-id.js";
import type { RequestStore } from "./ports.js";

/** Nothing about the member remains. It always succeeds, also for a member the module never saw (D-26). */
export async function eraseMember(deps: { store: RequestStore }, member: MemberId): Promise<{ ok: true }> {
  await deps.store.eraseMember(member);
  return { ok: true };
}
