import type { Connection } from "../domain/connection.js";
import type { ConnectionRequest, RequestId } from "../domain/connection-request.js";
import type { MemberId } from "../domain/member-id.js";
import type { RequestStore } from "../application/ports.js";

export class InMemoryStore implements RequestStore {
  /** Insertion order is the creation order. */
  private readonly requests: ConnectionRequest[] = [];
  private readonly connections = new Map<string, Connection>();

  async addRequest(request: ConnectionRequest): Promise<"added" | "id-taken"> {
    if (this.requests.some((r) => r.id === request.id)) return "id-taken";
    this.requests.push(request);
    return "added";
  }

  async replaceRequest(request: ConnectionRequest): Promise<void> {
    const index = this.requests.findIndex((r) => r.id === request.id);
    if (index !== -1) this.requests[index] = request;
  }

  async saveAccepted(request: ConnectionRequest, connection: Connection): Promise<void> {
    await this.replaceRequest(request);
    this.connections.set(pairKey(...connection.members), connection);
  }

  async findConnection(a: MemberId, b: MemberId): Promise<Connection | undefined> {
    return this.connections.get(pairKey(a, b));
  }

  async findRequest(id: RequestId): Promise<ConnectionRequest | undefined> {
    return this.requests.find((r) => r.id === id);
  }

  async requestsBetween(a: MemberId, b: MemberId): Promise<readonly ConnectionRequest[]> {
    return this.requests.filter(
      (r) => (r.sender === a && r.recipient === b) || (r.sender === b && r.recipient === a),
    );
  }

  async eraseMember(member: MemberId): Promise<void> {
    keepOnly(this.requests, (r) => r.sender !== member && r.recipient !== member);
    for (const [key, connection] of this.connections) {
      if (connection.members.includes(member)) this.connections.delete(key);
    }
  }

  async pendingFor(recipient: MemberId): Promise<readonly ConnectionRequest[]> {
    return this.requests.filter((r) => r.recipient === recipient && r.state === "pending");
  }
}

function pairKey(a: MemberId, b: MemberId): string {
  return [a, b].sort().join(":");
}

function keepOnly<T>(items: T[], keep: (item: T) => boolean): void {
  const kept = items.filter(keep);
  items.splice(0, items.length, ...kept);
}
