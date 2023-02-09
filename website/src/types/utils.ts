/* eslint-disable @typescript-eslint/no-explicit-any */
// https://github.com/ts-essentials/ts-essentials/blob/25cae45c162f8784e3cdae8f43783d0c66370a57/lib/types.ts#L437
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type ElementOf<T extends readonly any[]> = T extends readonly (infer ET)[] ? ET : never;
type AnyRecord<T = any> = Record<KeyofBase, T>;
type KeyofBase = keyof any;

export type AnyArray<T = any> = Array<T> | ReadonlyArray<T>;

export type StrictOmit<T extends AnyRecord, K extends keyof T> = T extends AnyArray ? never : Omit<T, K>;
