/** A rejection is a returned value with a reason, never an exception. */
export type Result<T, R extends string> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly reason: R };

export const accepted = <T>(value: T): { readonly ok: true; readonly value: T } => ({
  ok: true,
  value,
});

export const rejected = <R extends string>(reason: R): { readonly ok: false; readonly reason: R } => ({
  ok: false,
  reason,
});
