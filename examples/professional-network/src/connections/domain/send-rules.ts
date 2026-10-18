import type { Connection } from "./connection.js";
import type { ConnectionRequest } from "./connection-request.js";
import type { MemberId } from "./member-id.js";
export type SendRejection = "self-request" | "already-connected" | "duplicate-pending" | "reverse-pending" | "previously-declined";

/** What a guard looks at: the two members and the requests already exchanged between them. */
interface SendCase {
  readonly sender: MemberId;
  readonly recipient: MemberId;
  readonly between: readonly ConnectionRequest[];
  readonly connection: Connection | undefined;
}

type Guard = (c: SendCase) => SendRejection | undefined;

const selfRequest: Guard = (c) => (c.sender === c.recipient ? "self-request" : undefined);

const alreadyConnected: Guard = (c) => (c.connection ? "already-connected" : undefined);

const pendingFrom = (c: SendCase, from: MemberId): boolean =>
  c.between.some((r) => r.state === "pending" && r.sender === from);

const duplicatePending: Guard = (c) => (pendingFrom(c, c.sender) ? "duplicate-pending" : undefined);

const reversePending: Guard = (c) => (pendingFrom(c, c.recipient) ? "reverse-pending" : undefined);

/** A decline blocks the same sender from asking the same recipient again, with no expiry (D-7, D-14). */
const previouslyDeclined: Guard = (c) =>
  c.between.some((r) => r.state === "declined" && r.sender === c.sender) ? "previously-declined" : undefined;

const GUARDS: readonly Guard[] = [selfRequest, alreadyConnected, duplicatePending, reversePending, previouslyDeclined];

/** The reason a member may not send a request to another, or nothing if they may. Each rule is one named guard. */
export function decideSend(c: SendCase): SendRejection | undefined {
  for (const guard of GUARDS) {
    const reason = guard(c);
    if (reason) return reason;
  }
  return undefined;
}
