import { decline } from "../domain/connection-request.js";
import type { DeclineRejection as RequestRejection, ConnectionRequest, RequestId } from "../domain/connection-request.js";
import type { MemberId } from "../domain/member-id.js";
import { rejected } from "../domain/result.js";
import type { Result } from "../domain/result.js";
import type { RequestStore } from "./ports.js";

export type DeclineRejection = RequestRejection | "request-not-found";

export async function declineRequest(
  deps: { store: RequestStore },
  id: RequestId,
  actingMember: MemberId,
): Promise<Result<ConnectionRequest, DeclineRejection>> {
  const request = await deps.store.findRequest(id);
  if (!request) return rejected("request-not-found");
  const result = decline(request, actingMember);
  if (result.ok) await deps.store.replaceRequest(result.value);
  return result;
}
