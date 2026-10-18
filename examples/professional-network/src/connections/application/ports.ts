import type { Connection } from "../domain/connection.js";
import type { ConnectionRequest, RequestId } from "../domain/connection-request.js";
import type { MemberId } from "../domain/member-id.js";

/** Produces the id of a new request. Kept out of the domain so tests can make it predictable. */
export interface IdGenerator {
  next(): RequestId;
}

export interface RequestStore {
  /** Stores a new request. An id already in use is refused and nothing is stored (D-25). */
  addRequest(request: ConnectionRequest): Promise<"added" | "id-taken">;
  /** Replaces the stored request with the same id, keeping its place in the order. */
  replaceRequest(request: ConnectionRequest): Promise<void>;
  findRequest(id: RequestId): Promise<ConnectionRequest | undefined>;
  /** Every request exchanged between the two members, in either direction, oldest first. */
  requestsBetween(a: MemberId, b: MemberId): Promise<readonly ConnectionRequest[]>;
  /** Stores the accepted request and the connection it creates together, so a store can make it one atomic write. */
  saveAccepted(request: ConnectionRequest, connection: Connection): Promise<void>;
  findConnection(a: MemberId, b: MemberId): Promise<Connection | undefined>;
  /** Hard-deletes every request and every connection that involves the member (D-14, D-26). */
  eraseMember(member: MemberId): Promise<void>;
  /** The pending requests addressed to the member, oldest first. */
  pendingFor(recipient: MemberId): Promise<readonly ConnectionRequest[]>;
}
