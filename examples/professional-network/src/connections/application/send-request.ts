import { newRequest } from "../domain/connection-request.js";
import type { ConnectionRequest } from "../domain/connection-request.js";
import type { MemberId } from "../domain/member-id.js";
import { accepted, rejected } from "../domain/result.js";
import type { Result } from "../domain/result.js";
import { decideSend } from "../domain/send-rules.js";
import type { SendRejection as RuleRejection } from "../domain/send-rules.js";
import { blankIdRejection } from "./blank-ids.js";
import type { IdGenerator, RequestStore } from "./ports.js";

export type SendRejection = RuleRejection | "request-id-taken" | "blank-member-id";

export async function sendRequest(
  deps: { store: RequestStore; ids: IdGenerator },
  sender: MemberId,
  recipient: MemberId,
): Promise<Result<ConnectionRequest, SendRejection>> {
  const blank = blankIdRejection(sender, recipient);
  if (blank) return blank;
  const between = await deps.store.requestsBetween(sender, recipient);
  const connection = await deps.store.findConnection(sender, recipient);
  const reason = decideSend({ sender, recipient, between, connection });
  if (reason) return rejected(reason);
  const request = newRequest(deps.ids.next(), sender, recipient);
  const stored = await deps.store.addRequest(request);
  return stored === "added" ? accepted(request) : rejected("request-id-taken");
}
