import type { ConnectionRequest } from "../domain/connection-request.js";
import type { MemberId } from "../domain/member-id.js";
import { accepted } from "../domain/result.js";
import type { Result } from "../domain/result.js";
import { blankIdRejection } from "./blank-ids.js";
import type { RequestStore } from "./ports.js";

export async function listPendingRequests(
  deps: { store: RequestStore },
  recipient: MemberId,
): Promise<Result<readonly ConnectionRequest[], "blank-member-id">> {
  const blank = blankIdRejection(recipient);
  if (blank) return blank;
  return accepted(await deps.store.pendingFor(recipient));
}
