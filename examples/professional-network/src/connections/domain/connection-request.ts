import type { MemberId } from "./member-id.js";
import { accepted, rejected } from "./result.js";
import type { Result } from "./result.js";

export type RequestId = string;

export type RequestState = "pending" | "accepted" | "declined" | "withdrawn";

export interface ConnectionRequest {
  readonly id: RequestId;
  readonly sender: MemberId;
  readonly recipient: MemberId;
  readonly state: RequestState;
}

export function newRequest(id: RequestId, sender: MemberId, recipient: MemberId): ConnectionRequest {
  return { id, sender, recipient, state: "pending" };
}

export type AcceptRejection = "not-recipient" | "not-pending";
export type DeclineRejection = "not-recipient" | "not-pending";
export type WithdrawRejection = "not-sender" | "not-pending";

/** Who may act is checked before the state (D-13); only a pending request changes state. */
function change<R extends string>(
  request: ConnectionRequest,
  mayAct: boolean,
  notAllowed: R,
  state: RequestState,
): Result<ConnectionRequest, R | "not-pending"> {
  if (!mayAct) return rejected(notAllowed);
  if (request.state !== "pending") return rejected("not-pending");
  return accepted({ ...request, state });
}

/** The recipient accepts a pending request. */
export function accept(
  request: ConnectionRequest,
  actingMember: MemberId,
): Result<ConnectionRequest, AcceptRejection> {
  return change(request, actingMember === request.recipient, "not-recipient", "accepted");
}

/** The recipient declines a pending request. */
export function decline(
  request: ConnectionRequest,
  actingMember: MemberId,
): Result<ConnectionRequest, DeclineRejection> {
  return change(request, actingMember === request.recipient, "not-recipient", "declined");
}

/** The sender withdraws a pending request. The recipient may not. */
export function withdraw(
  request: ConnectionRequest,
  actingMember: MemberId,
): Result<ConnectionRequest, WithdrawRejection> {
  return change(request, actingMember === request.sender, "not-sender", "withdrawn");
}
