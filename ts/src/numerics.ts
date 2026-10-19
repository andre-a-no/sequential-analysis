// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
// Commercial licenses for use outside the AGPL: see COMMERCIAL.md
import { NumericalError } from "./errors.js";

/** One step of Neumaier summation; the represented value is total + comp. */
export function neumaierAdd(total: number, comp: number, x: number): [number, number] {
  const t = total + x;
  if (Math.abs(total) >= Math.abs(x)) comp += total - t + x;
  else comp += x - t + total;
  return [t, comp];
}

export function requireFinite(value: number, what: string): number {
  if (!Number.isFinite(value)) throw new NumericalError(`${what} is not finite: ${value}`);
  return value;
}

/** log(sum exp(v)) with the largest term factored out and a left-to-right sum. */
export function logSumExp(values: number[]): number {
  if (values.length === 0) return -Infinity;
  const m = Math.max(...values);
  if (!Number.isFinite(m)) return m;
  let total = 0;
  for (const v of values) total += Math.exp(v - m);
  return m + Math.log(total);
}

/** 2 ** x from +, *, / only, as Python's portable_exp2: identical in every IEEE 754 implementation. */
export function portableExp2(x: number): number {
  if (!Number.isFinite(x)) throw new Error("portableExp2 needs a finite argument");
  if (x < -1100.0) return 0.0;
  if (x > 1024.0) throw new RangeError("2**x overflows");
  let n = Math.floor(x);
  const y = (x - n) * 0.6931471805599453;
  let r = 1.0;
  for (let k = 20; k > 0; k--) r = 1.0 + (y * r) / k;
  while (n < 0) { r *= 0.5; n += 1; }
  while (n > 0) { r *= 2.0; n -= 1; }
  return r;
}
