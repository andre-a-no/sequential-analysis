// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
// Commercial licenses for use outside the AGPL: see COMMERCIAL.md
// Volatility: the GARCH(1,1) / GJR-GARCH(1,1) filter; mirrors procedures/volatility.py.
import type { Json } from "../canonical.js";
import { InputContract, type StatInput } from "../contracts.js";
import { neumaierAdd, requireFinite } from "../numerics.js";
import { decodeFields, type Output, register, requireState, type State } from "../procedure.js";
import type { SplitMix64 } from "../rng.js";
import { lgamma, tIsfLog } from "./distributions.js";
import { checkCoverage, checkHorizon } from "./forecast.js";
import { normalInvCdf } from "./group_sequential.js";
import { BaseProcedure, type Config, int, invalid, num, optNum, str } from "./util.js";

const LOG_2PI = Math.log(2.0 * Math.PI);

/** Log density of a residual with the given variance: normal (df null) or unit-variance Student t. */
export function garchLogDensity(error: number, variance: number, df: number | null): number {
  if (df === null) return -0.5 * (LOG_2PI + Math.log(variance) + error * error / variance);
  return (lgamma(0.5 * (df + 1.0)) - lgamma(0.5 * df) - 0.5 * Math.log(Math.PI * (df - 2.0))
    - 0.5 * Math.log(variance) - 0.5 * (df + 1.0) * Math.log1p(error * error / (variance * (df - 2.0))));
}

type GARCHState = { n: number; variance: number; log_likelihood: number; comp: number };

/** GARCH(1,1) or GJR-GARCH(1,1) filter with fixed parameters; see volatility.py. */
export class GARCH extends BaseProcedure {
  readonly name = "garch";
  readonly version = "1";
  readonly persistence: number;
  readonly initialVariance: number;
  private readonly q: number;

  constructor(
    readonly omega: number, readonly alpha: number, readonly beta: number, readonly gamma = 0.0, readonly mean = 0.0,
    readonly distribution = "normal", readonly df: number | null = null, initialVariance: number | null = null,
    readonly horizon = 1, readonly coverage = 0.9, readonly input = "r",
  ) {
    super();
    if (!Number.isFinite(omega) || !Number.isFinite(mean)) invalid("omega and mean must be finite");
    if (!(omega > 0.0)) invalid("omega must be positive");
    if (!(alpha >= 0.0 && beta >= 0.0 && alpha + gamma >= 0.0 && Number.isFinite(alpha + beta + gamma)))
      invalid("need alpha >= 0, beta >= 0 and alpha + gamma >= 0");
    if (distribution !== "normal" && distribution !== "t") invalid("distribution must be one of ('normal', 't')");
    if (distribution === "t") {
      if (df === null || !(2.0 < df && df < Infinity)) invalid("a Student t distribution needs df > 2");
    } else if (df !== null) invalid("df is for the Student t distribution");
    this.persistence = alpha + beta + 0.5 * gamma;
    if (initialVariance === null) {
      if (!(this.persistence < 1.0)) invalid("without an initial_variance the persistence alpha + beta + gamma / 2 must be below 1");
      this.initialVariance = omega / (1.0 - this.persistence);
    } else {
      if (!(0.0 < initialVariance && initialVariance < Infinity)) invalid("initial_variance must be positive and finite");
      this.initialVariance = initialVariance;
    }
    checkHorizon(horizon);
    checkCoverage(coverage);
    const tail = 0.5 * (1.0 - coverage);
    this.q = df === null ? -normalInvCdf(tail) : tIsfLog(Math.log(tail), df) * Math.sqrt((df - 2.0) / df);
  }

  static fromConfig(c: Config): GARCH {
    return new GARCH(num(c, "omega"), num(c, "alpha"), num(c, "beta"), num(c, "gamma"), num(c, "mean"), str(c, "distribution"),
      optNum(c, "df"), num(c, "initial_variance"), int(c, "horizon"), num(c, "coverage"), str(c, "input"));
  }

  config(): Config {
    return {
      omega: this.omega, alpha: this.alpha, beta: this.beta, gamma: this.gamma, mean: this.mean, distribution: this.distribution,
      df: this.df, initial_variance: this.initialVariance, horizon: this.horizon, coverage: this.coverage, input: this.input,
    };
  }

  inputs(): Record<string, InputContract> {
    return { [this.input]: new InputContract(this.input) };
  }

  initialState(): GARCHState {
    return { n: 0, variance: this.initialVariance, log_likelihood: 0.0, comp: 0.0 };
  }

  nextVariance(variance: number, error: number): number {
    let v = this.omega + this.alpha * error * error + this.beta * variance;
    if (error < 0.0) v += this.gamma * error * error;
    return requireFinite(v, "conditional variance");
  }

  forecast(variance: number): number[] {
    const out = [variance];
    for (let h = 1; h < this.horizon; h++) out.push(this.omega + this.persistence * out[out.length - 1]);
    return out;
  }

  step(state: State, x: StatInput, _rng: SplitMix64 | null = null): [State, Output] {
    const s = state as GARCHState;
    const r = x[this.input] as number;
    const error = r - this.mean;
    const sigma = Math.sqrt(s.variance);
    const score = garchLogDensity(error, s.variance, this.df);
    const [logLik, comp] = neumaierAdd(s.log_likelihood, s.comp, score);
    const variance = this.nextVariance(s.variance, error);
    const next: GARCHState = { n: s.n + 1, variance, log_likelihood: logLik, comp };
    const ahead = this.forecast(variance);
    const sds = ahead.map((v) => Math.sqrt(v));
    const cumulative: number[] = [];
    let total = 0.0;
    for (const v of ahead) {
      total += v;
      cumulative.push(Math.sqrt(total));
    }
    return [next, {
      n: next.n, sigma, z: error / sigma, log_score: score, log_likelihood: logLik, forecast_sd: sds, cumulative_sd: cumulative,
      lower: sds.map((sd) => this.mean - this.q * sd), upper: sds.map((sd) => this.mean + this.q * sd),
    }];
  }

  decodeState(data: Json): GARCHState {
    const s = decodeFields({ n: "count", variance: "number", log_likelihood: "number", comp: "number" }, data) as GARCHState;
    requireState(s.variance > 0.0, "the variance must be positive");
    return s;
  }
}

register("garch", "1", (c) => GARCH.fromConfig(c));
