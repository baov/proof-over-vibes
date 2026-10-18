/** A member, known to this module by its id alone. No validity rule on purpose (D-15). */
export type MemberId = string & { readonly __brand: "MemberId" };

export function memberId(value: string): MemberId {
  return value as MemberId;
}
