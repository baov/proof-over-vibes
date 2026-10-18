import { getPairState } from "./application/pair-state.js";
import { listPendingRequests } from "./application/pending-requests.js";
import { acceptRequest } from "./application/accept-request.js";
import type { AcceptRejection } from "./application/accept-request.js";
import { eraseMember } from "./application/erase-member.js";
import { declineRequest } from "./application/decline-request.js";
import type { DeclineRejection } from "./application/decline-request.js";
import { withdrawRequest } from "./application/withdraw-request.js";
import type { WithdrawRejection } from "./application/withdraw-request.js";
import { sendRequest } from "./application/send-request.js";
import type { SendRejection } from "./application/send-request.js";
import type { IdGenerator } from "./application/ports.js";
import type { ConnectionRequest, RequestId } from "./domain/connection-request.js";
import type { MemberId } from "./domain/member-id.js";
import type { PairState } from "./domain/pair-state.js";
import type { Result } from "./domain/result.js";
import { InMemoryStore } from "./infrastructure/in-memory-store.js";

export { memberId } from "./domain/member-id.js";
export type { MemberId } from "./domain/member-id.js";
export type { ConnectionRequest, RequestId } from "./domain/connection-request.js";
export type { PairState } from "./domain/pair-state.js";
export type { SendRejection, AcceptRejection, DeclineRejection, WithdrawRejection };
export type { IdGenerator } from "./application/ports.js";

export interface Connections {
  sendRequest(sender: MemberId, recipient: MemberId): Promise<Result<ConnectionRequest, SendRejection>>;
  acceptRequest(id: RequestId, actingMember: MemberId): Promise<Result<ConnectionRequest, AcceptRejection>>;
  declineRequest(id: RequestId, actingMember: MemberId): Promise<Result<ConnectionRequest, DeclineRejection>>;
  withdrawRequest(id: RequestId, actingMember: MemberId): Promise<Result<ConnectionRequest, WithdrawRejection>>;
  eraseMember(member: MemberId): Promise<{ ok: true }>;
  getPairState(a: MemberId, b: MemberId): Promise<PairState>;
  listPendingRequests(recipient: MemberId): Promise<readonly ConnectionRequest[]>;
}

export function createConnections(options: { ids: IdGenerator }): Connections {
  const deps = { store: new InMemoryStore(), ids: options.ids };
  return {
    sendRequest: (sender, recipient) => sendRequest(deps, sender, recipient),
    acceptRequest: (id, actingMember) => acceptRequest(deps, id, actingMember),
    declineRequest: (id, actingMember) => declineRequest(deps, id, actingMember),
    withdrawRequest: (id, actingMember) => withdrawRequest(deps, id, actingMember),
    eraseMember: (member) => eraseMember(deps, member),
    getPairState: (a, b) => getPairState(deps, a, b),
    listPendingRequests: (recipient) => listPendingRequests(deps, recipient),
  };
}
