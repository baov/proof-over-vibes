import type { Connection } from "./connection.js";
import type { ConnectionRequest, RequestState } from "./connection-request.js";

export interface PairState {
  readonly connected: boolean;
  /** "none" is a state of its own: a query always answers (D-11). */
  readonly requestState: RequestState | "none";
}

/** The state of a pair, from the requests between the two members and their connection if any. */
export function pairState(
  between: readonly ConnectionRequest[],
  connection: Connection | undefined,
): PairState {
  // The pending request if there is one, otherwise the most recent (D-12). A pending request is always
  // the latest of its pair, since a pending one blocks any newer request (R9, R10): one rule covers both.
  const request = between.at(-1);
  return { connected: connection !== undefined, requestState: request ? request.state : "none" };
}
