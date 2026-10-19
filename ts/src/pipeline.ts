// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
// Commercial licenses for use outside the AGPL: see COMMERCIAL.md
// Composition: Lagged feeds a procedure the recent past of some inputs; mirrors pipeline.py.
import type { Json } from "./canonical.js";
import { InputContract, type StatInput, validateInput } from "./contracts.js";
import { fromIdentity, identity, type Identity, type Output, type Procedure, register, requireState, type State } from "./procedure.js";
import type { SplitMix64 } from "./rng.js";
import { BaseProcedure, type Config, invalid, obj } from "./procedures/util.js";

/** The name of an input's value `lag` steps ago, as Lagged passes it on. */
export function lagName(source: string, lag: number): string {
  return `${source}_lag${lag}`;
}

type LaggedState = { n: number; past: { [source: string]: number[] }; inner: State };

const plainObject = (v: unknown): v is Record<string, Json> => v !== null && typeof v === "object" && !Array.isArray(v);

/** Run `inner` with the recent past of some inputs as extra inputs (source_lag1, ..., source_lagk); see pipeline.py. */
export class Lagged extends BaseProcedure {
  readonly name = "lagged";
  readonly version = "1";
  override readonly randomized: boolean;
  readonly lags: Record<string, number>;
  private readonly generated: string[];
  private readonly contracts: Record<string, InputContract>;

  constructor(readonly inner: Procedure, lags: Record<string, number>) {
    super();
    if (!plainObject(lags) || !Object.keys(lags).length) invalid("lags must map at least one input name to a number of lags");
    for (const [source, k] of Object.entries(lags)) {
      if (!source) invalid("lag sources must be non-empty strings");
      if (!(typeof k === "number" && Number.isInteger(k) && k >= 1)) invalid(`the number of lags of '${source}' must be a positive int`);
    }
    if (!inner.jointInputs) invalid("the inner procedure must take all its inputs in every step");
    this.lags = Object.fromEntries(Object.keys(lags).sort().map((s) => [s, lags[s]]));
    const contracts = inner.inputs();
    this.generated = Object.entries(this.lags).flatMap(([s, k]) => Array.from({ length: k }, (_, j) => lagName(s, j + 1)));
    const missing = this.generated.filter((n) => !(n in contracts));
    if (missing.length) invalid(`${inner.name} does not take the lagged inputs [${missing.map((n) => `'${n}'`).join(", ")}]`);
    const clash = Object.keys(this.lags).filter((s) => this.generated.includes(s));
    if (clash.length) invalid(`a source is named like a lag: [${clash.map((n) => `'${n}'`).join(", ")}]`);
    this.contracts = Object.fromEntries(Object.entries(contracts).filter(([n]) => !this.generated.includes(n)));
    for (const s of Object.keys(this.lags)) {
      if (!(s in this.contracts)) this.contracts[s] = new InputContract(s);
      else if (this.contracts[s].shape.length !== 0) invalid(`source '${s}' must be a scalar input`);
    }
    this.randomized = inner.randomized;
  }

  static fromConfig(c: Config): Lagged {
    const inner = fromIdentity(obj(c, "inner") as unknown as Identity);
    return new Lagged(inner, obj(c, "lags") as Record<string, number>);
  }

  config(): Config {
    return { inner: identity(this.inner) as unknown as Json, lags: { ...this.lags } };
  }

  inputs(): Record<string, InputContract> {
    return { ...this.contracts };
  }

  initialState(): LaggedState {
    return { n: 0, past: Object.fromEntries(Object.keys(this.lags).map((s) => [s, []])), inner: this.inner.initialState() };
  }

  step(state: State, x: StatInput, rng: SplitMix64 | null = null): [State, Output] {
    const s = state as LaggedState;
    const ready = Object.entries(this.lags).every(([src, k]) => s.past[src].length === k);
    let inner = s.inner;
    let out: Output | null = null;
    if (ready) {
      const innerContracts = this.inner.inputs();
      const x2: StatInput = {};
      for (const n of Object.keys(innerContracts)) if (!this.generated.includes(n)) x2[n] = x[n];
      for (const [src, k] of Object.entries(this.lags)) for (let j = 0; j < k; j++) x2[lagName(src, j + 1)] = s.past[src][j];
      validateInput(innerContracts, this.inner.jointInputs, x2);
      [inner, out] = this.inner.step(s.inner, x2, rng);
    }
    const past = Object.fromEntries(Object.entries(this.lags).map(([src, k]) => [src, [x[src] as number, ...s.past[src]].slice(0, k)]));
    return [{ n: s.n + 1, past, inner }, { ready, inner: out }];
  }

  override isTerminal(state: State): boolean {
    return this.inner.isTerminal((state as LaggedState).inner);
  }

  decodeState(data: Json): LaggedState {
    requireState(plainObject(data) && Object.keys(data).sort().join("\u0000") === ["inner", "n", "past"].join("\u0000"), "a lagged state");
    const d = data as Record<string, Json>;
    const n = d.n, past = d.past;
    requireState(typeof n === "number" && Number.isInteger(n) && n >= 0, "the step count");
    const sources = Object.keys(this.lags);
    requireState(plainObject(past) && Object.keys(past).length === sources.length && sources.every((s) => s in past), "one past per source");
    const out: { [source: string]: number[] } = {};
    for (const [s, k] of Object.entries(this.lags)) {
      const p = (past as Record<string, Json>)[s];
      requireState(Array.isArray(p) && p.length === Math.min(n as number, k) && p.every((v) => typeof v === "number" && Number.isFinite(v)),
        `the past of '${s}'`);
      out[s] = [...(p as number[])];
    }
    return { n: n as number, past: out, inner: this.inner.decodeState(d.inner) };
  }
}

register("lagged", "1", (c) => Lagged.fromConfig(c));
