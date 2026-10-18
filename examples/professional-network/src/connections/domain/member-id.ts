/** A member, known to this module by its id alone. No validity rule on purpose (D-15). */
export type MemberId = string & { readonly __brand: "MemberId" };

export function memberId(value: string): MemberId {
  return value as MemberId;
}

/** Standard Unicode whitespace only: zero-width and invisible characters are not whitespace (D-33). */
const ONLY_WHITESPACE = /^\p{White_Space}*$/u;

/** A member id is blank when it is empty or made only of whitespace. */
export function isBlankMemberId(id: MemberId): boolean {
  return ONLY_WHITESPACE.test(id);
}
