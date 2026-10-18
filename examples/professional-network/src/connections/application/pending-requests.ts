import type { ConnectionRequest } from "../domain/connection-request.js";
import type { MemberId } from "../domain/member-id.js";
import type { RequestStore } from "./ports.js";

export function listPendingRequests(
  deps: { store: RequestStore },
  recipient: MemberId,
): Promise<readonly ConnectionRequest[]> {
  return deps.store.pendingFor(recipient);
}
