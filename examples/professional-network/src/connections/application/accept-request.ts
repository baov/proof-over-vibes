import { newConnection } from "../domain/connection.js";
import { accept } from "../domain/connection-request.js";
import type { AcceptRejection as RequestRejection, ConnectionRequest, RequestId } from "../domain/connection-request.js";
import type { MemberId } from "../domain/member-id.js";
import { rejected } from "../domain/result.js";
import type { Result } from "../domain/result.js";
import { blankIdRejection } from "./blank-ids.js";
import type { RequestStore } from "./ports.js";

export type AcceptRejection = RequestRejection | "request-not-found" | "blank-member-id";

export async function acceptRequest(
  deps: { store: RequestStore },
  id: RequestId,
  actingMember: MemberId,
): Promise<Result<ConnectionRequest, AcceptRejection>> {
  const blank = blankIdRejection(actingMember);
  if (blank) return blank;
  const request = await deps.store.findRequest(id);
  if (!request) return rejected("request-not-found");
  const result = accept(request, actingMember);
  if (result.ok) {
    await deps.store.saveAccepted(result.value, newConnection(request.sender, request.recipient));
  }
  return result;
}
