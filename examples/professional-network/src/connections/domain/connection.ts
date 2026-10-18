import type { MemberId } from "./member-id.js";

/** Two members connected to each other. The pair has no order: (A, B) is (B, A). */
export interface Connection {
  readonly members: readonly [MemberId, MemberId];
}

export function newConnection(a: MemberId, b: MemberId): Connection {
  return { members: [a, b] };
}

export function connects(connection: Connection, a: MemberId, b: MemberId): boolean {
  const [first, second] = connection.members;
  return (first === a && second === b) || (first === b && second === a);
}
