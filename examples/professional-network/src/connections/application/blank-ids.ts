import { isBlankMemberId } from "../domain/member-id.js";
import type { MemberId } from "../domain/member-id.js";
import { rejected } from "../domain/result.js";

/** The rejection to return first when any of the given member ids is blank. */
export function blankIdRejection(...ids: MemberId[]): { ok: false; reason: "blank-member-id" } | undefined {
  return ids.some(isBlankMemberId) ? rejected("blank-member-id") : undefined;
}
