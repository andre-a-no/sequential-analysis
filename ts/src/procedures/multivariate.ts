// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
// Commercial licenses for use outside the AGPL: see COMMERCIAL.md
// Several series at once: vector autoregression, lead-lag correlations, regression on drifting coefficients;
// mirrors procedures/multivariate.py.
import type { Json } from "../canonical.js";
import { InputContract, type StatInput } from "../contracts.js";
import * as la from "../linalg.js";
import { neumaierAdd, requireFinite } from "../numerics.js";
import { decodeFields, type Output, register, requireState, type State } from "../procedure.js";
import type { SplitMix64 } from "../rng.js";
import { lgamma, tIsfLog } from "./distributions.js";
import {
  accumulate, backward, checkCoverage, checkHorizon, checkLearning, checkMatrix, choleskyFloor, forward, logDensity, quad, strs,
} from "./forecast.js";
import { normalInvCdf } from "./group_sequential.js";
import { BaseProcedure, bool, type Config, int, invalid, num, pyMax, pyMin, str } from "./util.js";

const LOG_PI = Math.log(Math.PI);

function names(values: string[], what: string): string[] {
  const out = [...values];
  if (!out.length || !out.every((n) => typeof n === "string" && n.length > 0) || new Set(out).size !== out.length)
    invalid(`${what} must be distinct non-empty strings`);
  return out;
}

function strictCholesky(a: la.Matrix): la.Matrix | null {
  try {
    return la.cholesky(a);
  } catch (error) {
    if (error instanceof RangeError) return null;
    throw error;
  }
}

/** Log density at `error` from the location of a normal (df null) or Student t law with scale L L'. */
export function multivariateTLogDensity(error: number[], low: la.Matrix, df: number | null): number {
  const d = error.length;
  const z = forward(low, error);
  let q = 0.0;
  let logDet = 0.0;
  for (let i = 0; i < d; i++) {
    q += z[i] * z[i];
    logDet += Math.log(low[i][i]);
  }
  if (df === null) return -0.5 * d * Math.log(2.0 * Math.PI) - logDet - 0.5 * q;
  return (lgamma(0.5 * (df + d)) - lgamma(0.5 * df) - 0.5 * d * (Math.log(df) + LOG_PI) - logDet
    - 0.5 * (df + d) * Math.log1p(q / df));
}

const zeros = (rows: number, cols: number): number[][] => Array.from({ length: rows }, () => Array.from({ length: cols }, () => 0.0));

// ------------------------------------------------------------------------------------------ VAR

type VARState = {
  n: number; lags: number[][]; information: number[][]; moment: number[][]; dof: number; scatter: number[][];
  log_likelihood: number; comp: number;
};

/** (means, standard deviations, degrees of freedom or null) for 1..horizon steps. */
export type VARForecast = [number[][], number[][], number | null];

/** VAR(p) forecasts of several series, with fixed coefficients or learnt online; see multivariate.py. */
export class VectorAutoRegressive extends BaseProcedure {
  readonly name = "vector_autoregressive";
  readonly version = "1";
  readonly series: string[];
  readonly d: number;
  readonly k: number;
  readonly coefficients: la.Matrix[] | null;
  readonly intercept: la.Vector | null;
  readonly covariance: la.Matrix | null;
  readonly horizon: number;
  readonly coverage: number;

  constructor(
    series: string[], readonly order: number, options: {
      coefficients?: number[][][] | null; intercept?: number[] | null; covariance?: number[][] | null; forgetting?: number;
      ridge?: number; horizon?: number; coverage?: number;
    } = {},
  ) {
    super();
    const { coefficients = null, intercept = null, covariance = null, forgetting = 1.0, ridge = 1e-6, horizon = 1, coverage = 0.9 } = options;
    this.series = names(series, "series");
    const d = (this.d = this.series.length);
    if (!(Number.isInteger(order) && order >= 1)) invalid("order must be a positive int");
    this.k = 1 + d * order;
    if (coefficients !== null) {
      if (intercept === null || covariance === null) invalid("fixed coefficients need an intercept and a covariance");
      if (forgetting !== 1.0 || ridge !== 1e-6) invalid("forgetting and ridge are for learnt coefficients");
      if (coefficients.length !== order) invalid("need one coefficient matrix per lag");
      this.coefficients = coefficients.map((a) => la.matrix(a, d, d, "coefficients"));
      this.intercept = la.vector(intercept, d, "intercept");
      const cov = la.matrix(covariance, d, d, "covariance");
      if (!la.isSymmetric(cov) || strictCholesky(cov) === null) invalid("the covariance must be symmetric positive definite");
      this.covariance = cov;
    } else {
      if (intercept !== null || covariance !== null) invalid("intercept and covariance come with fixed coefficients");
      checkLearning(forgetting, ridge);
      this.coefficients = this.intercept = this.covariance = null;
    }
    this.forgetting = forgetting;
    this.ridge = ridge;
    this.horizon = checkHorizon(horizon);
    this.coverage = checkCoverage(coverage);
  }

  readonly forgetting: number;
  readonly ridge: number;

  static fromConfig(c: Config): VectorAutoRegressive {
    const matrices = (key: string): Json => (key in c ? c[key] : invalid(`config is missing '${key}'`));
    return new VectorAutoRegressive(strs(c, "series"), int(c, "order"), {
      coefficients: matrices("coefficients") as number[][][] | null, intercept: matrices("intercept") as number[] | null,
      covariance: matrices("covariance") as number[][] | null, forgetting: num(c, "forgetting"), ridge: num(c, "ridge"),
      horizon: int(c, "horizon"), coverage: num(c, "coverage"),
    });
  }

  config(): Config {
    const fixed = this.coefficients !== null && this.intercept !== null && this.covariance !== null;
    return {
      series: [...this.series], order: this.order,
      coefficients: fixed ? (this.coefficients as la.Matrix[]).map((a) => a.map((r) => [...r])) : null,
      intercept: fixed ? [...(this.intercept as la.Vector)] : null,
      covariance: fixed ? (this.covariance as la.Matrix).map((r) => [...r]) : null,
      forgetting: this.forgetting, ridge: this.ridge, horizon: this.horizon, coverage: this.coverage,
    };
  }

  inputs(): Record<string, InputContract> {
    return Object.fromEntries(this.series.map((s) => [s, new InputContract(s)]));
  }

  initialState(): VARState {
    const { d, k } = this;
    if (this.coefficients !== null)
      return { n: 0, lags: [], information: [], moment: [], dof: 0.0, scatter: [], log_likelihood: 0.0, comp: 0.0 };
    return { n: 0, lags: [], information: zeros(k, k), moment: zeros(k, d), dof: 0.0, scatter: zeros(d, d), log_likelihood: 0.0, comp: 0.0 };
  }

  private design(lags: number[][]): number[] {
    const u = [1.0];
    for (const v of lags) u.push(...v);
    return u;
  }

  /** (k x d coefficient matrix by rows of the design, Cholesky factor of M or null). */
  private theta(s: VARState): [number[][], number[][] | null] {
    if (this.coefficients !== null) {
      const theta = [[...(this.intercept as la.Vector)]];
      for (const a of this.coefficients)
        for (let k = 0; k < this.d; k++) theta.push(Array.from({ length: this.d }, (_, i) => a[i][k]));
      return [theta, null];
    }
    const lam = this.forgetting;
    const precision = Array.from({ length: this.k }, (_, i) =>
      Array.from({ length: this.k }, (_, j) => lam * s.information[i][j] + (i === j ? this.ridge : 0.0)));
    const low = choleskyFloor(precision);
    const columns = Array.from({ length: this.d }, (_, i) =>
      backward(low, forward(low, Array.from({ length: this.k }, (_, r) => lam * s.moment[r][i]))));
    return [Array.from({ length: this.k }, (_, r) => Array.from({ length: this.d }, (_, i) => columns[i][r])), low];
  }

  private point(theta: number[][], u: number[]): number[] {
    const out: number[] = [];
    for (let i = 0; i < this.d; i++) {
      let total = 0.0;
      for (let r = 0; r < this.k; r++) total += theta[r][i] * u[r];
      out.push(total);
    }
    return out;
  }

  /** (scale matrix Sigma, degrees of freedom or null), or null while it is not yet defined. */
  private noise(s: VARState): [la.Matrix, number | null] | null {
    if (this.covariance !== null) return [this.covariance, null];
    const lam = this.forgetting;
    const df = lam * s.dof - this.d + 1.0;
    if (!(df > 0.0)) return null;
    const sigma = Array.from({ length: this.d }, (_, i) => Array.from({ length: this.d }, (_, j) => lam * s.scatter[i][j] / df));
    if (strictCholesky(sigma) === null) return null;
    return [sigma, df];
  }

  step(state: State, x: StatInput, _rng: SplitMix64 | null = null): [State, Output] {
    const s = state as VARState;
    const y = this.series.map((name) => x[name] as number);
    const lags = [y, ...s.lags].slice(0, this.order);
    let logLik = s.log_likelihood, comp = s.comp;
    if (s.lags.length < this.order) {
      const next: VARState = { ...s, n: s.n + 1, lags };
      return [next, this.output(next, null, null)];
    }
    const u = this.design(s.lags);
    const [theta, low] = this.theta(s);
    const point = this.point(theta, u);
    const error = y.map((a, i) => a - point[i]);
    const sv = low === null ? 1.0 : 1.0 + quad(low, u);
    const noise = this.noise(s);
    let score: number | null = null;
    if (noise !== null) {
      const [sigma, df] = noise;
      const factor = strictCholesky(la.scale(sigma, sv));
      if (factor !== null) {
        score = multivariateTLogDensity(error, factor, df);
        [logLik, comp] = neumaierAdd(logLik, comp, score);
      }
    }
    if (this.coefficients !== null) {
      const next: VARState = { n: s.n + 1, lags, information: [], moment: [], dof: 0.0, scatter: [], log_likelihood: logLik, comp };
      return [next, this.output(next, error, score)];
    }
    const lam = this.forgetting;
    const information = accumulate(s.information, Array.from({ length: this.k }, () => 0.0), u, 0.0, lam)[0];
    const moment = Array.from({ length: this.k }, (_, r) =>
      Array.from({ length: this.d }, (_, i) => requireFinite(lam * s.moment[r][i] + u[r] * y[i], "moment")));
    const scatter = Array.from({ length: this.d }, (_, i) =>
      Array.from({ length: this.d }, (_, j) => requireFinite(lam * s.scatter[i][j] + error[i] * error[j] / sv, "scatter")));
    const next: VARState = { n: s.n + 1, lags, information, moment, dof: lam * s.dof + 1.0, scatter, log_likelihood: logLik, comp };
    return [next, this.output(next, error, score)];
  }

  private quantile(df: number | null): number {
    const tail = 0.5 * (1.0 - this.coverage);
    return df === null ? -normalInvCdf(tail) : tIsfLog(Math.log(tail), df);
  }

  private output(s: VARState, error: number[] | null, score: number | null): Output {
    const f = this.forecast(s);
    const n = s.n, logLik = s.log_likelihood;
    if (f === null) return { n, forecast: null, scale: null, lower: null, upper: null, error, log_score: score, log_likelihood: logLik };
    const [mean, scale, df] = f;
    const q = this.quantile(df);
    const lower = mean.map((ms, h) => ms.map((m, i) => m - q * scale[h][i]));
    const upper = mean.map((ms, h) => ms.map((m, i) => m + q * scale[h][i]));
    return { n, forecast: mean, scale, lower, upper, error, log_score: score, log_likelihood: logLik };
  }

  /** (means, standard deviations, degrees of freedom or null) for 1..horizon steps, or null. */
  forecast(state: State): VARForecast | null {
    const s = state as VARState;
    if (s.lags.length < this.order) return null;
    const noise = this.noise(s);
    if (noise === null) return null;
    const [sigma, df] = noise;
    const [theta, low] = this.theta(s);
    const d = this.d, p = this.order;
    const extra = low === null ? 0.0 : quad(low, this.design(s.lags));
    // A_j[i][k] from theta, for the error propagation Psi_h = sum_j A_j Psi_{h-j}
    const a = Array.from({ length: p }, (_, j) =>
      Array.from({ length: d }, (_, i) => Array.from({ length: d }, (_, k) => theta[1 + j * d + k][i])));
    const psi = [la.identity(d)];
    let history = [...s.lags];
    let total = la.scale(sigma, extra);
    const means: number[][] = [], scales: number[][] = [];
    for (let h = 1; h <= this.horizon; h++) {
      const value = this.point(theta, this.design(history));
      means.push(value);
      history = [value, ...history.slice(0, -1)];
      total = la.add(total, la.quadratic(psi[h - 1], sigma));
      scales.push(Array.from({ length: d }, (_, i) => Math.sqrt(total[i][i])));
      let nxt = zeros(d, d);
      for (let j = 1; j <= Math.min(h, p); j++) nxt = la.add(nxt, la.matmul(a[j - 1], psi[h - j]));
      psi.push(nxt);
    }
    return [means, scales, df];
  }

  /** The intercept, the coefficient matrices and the noise scale matrix the next forecast uses. */
  parameters(state: State): { [key: string]: Json } {
    const s = state as VARState;
    if (this.coefficients !== null) {
      return {
        intercept: [...(this.intercept as la.Vector)], coefficients: this.coefficients.map((a) => a.map((r) => [...r])),
        covariance: (this.covariance as la.Matrix).map((r) => [...r]),
      };
    }
    if (s.lags.length < this.order) return { intercept: null, coefficients: null, covariance: null };
    const [theta] = this.theta(s);
    const d = this.d;
    const noise = this.noise(s);
    return {
      intercept: [...theta[0]],
      coefficients: Array.from({ length: this.order }, (_, j) =>
        Array.from({ length: d }, (_, i) => Array.from({ length: d }, (_, k) => theta[1 + j * d + k][i]))),
      covariance: noise === null ? null : noise[0].map((r) => [...r]),
    };
  }

  decodeState(data: Json): VARState {
    const s = decodeFields({
      n: "count", lags: "json", information: "json", moment: "json", dof: "number", scatter: "json", log_likelihood: "number",
      comp: "number",
    }, data) as VARState;
    for (const key of ["lags", "information", "moment", "scatter"] as const) checkMatrix(key, s[key]);
    requireState(s.lags.length === Math.min(s.n, this.order) && s.lags.every((v) => v.length === this.d),
      "one lag vector per observation, up to the order");
    if (this.coefficients !== null) {
      requireState(s.information.length === 0 && s.moment.length === 0 && s.scatter.length === 0 && s.dof === 0,
        "learnt statistics with fixed coefficients");
    } else {
      const { k, d } = this;
      requireState(s.information.length === k && s.information.every((r) => r.length === k)
        && s.moment.length === k && s.moment.every((r) => r.length === d)
        && s.scatter.length === d && s.scatter.every((r) => r.length === d), "statistics' sizes");
      let diagonals = s.dof >= 0;
      for (let i = 0; i < k; i++) diagonals = diagonals && s.information[i][i] >= 0;
      for (let i = 0; i < d; i++) diagonals = diagonals && s.scatter[i][i] >= 0;
      requireState(la.isSymmetric(s.information) && la.isSymmetric(s.scatter) && diagonals,
        "statistics must be symmetric with non-negative diagonals");
    }
    return s;
  }
}

register("vector_autoregressive", "1", (c) => VectorAutoRegressive.fromConfig(c));

// -------------------------------------------------------------------------------- lead and lag

type CrossCorrelationState = { n: number; past_a: number[]; past_b: number[]; stats: number[][] };

/** Correlations of a_t with b_{t-lag} for lags -max_lag..max_lag, with optional forgetting; see multivariate.py. */
export class CrossCorrelation extends BaseProcedure {
  readonly name = "cross_correlation";
  readonly version = "1";

  constructor(readonly a = "a", readonly b = "b", readonly maxLag = 5, readonly forgetting = 1.0) {
    super();
    if (!(typeof a === "string" && a && typeof b === "string" && b) || a === b)
      invalid("a and b must be two distinct non-empty input names");
    if (!(Number.isInteger(maxLag) && maxLag >= 0)) invalid("max_lag must be a non-negative int");
    if (!(0.0 < forgetting && forgetting <= 1.0)) invalid("forgetting must lie in (0, 1]");
  }

  static fromConfig(c: Config): CrossCorrelation {
    return new CrossCorrelation(str(c, "a"), str(c, "b"), int(c, "max_lag"), num(c, "forgetting"));
  }

  config(): Config {
    return { a: this.a, b: this.b, max_lag: this.maxLag, forgetting: this.forgetting };
  }

  inputs(): Record<string, InputContract> {
    return { [this.a]: new InputContract(this.a), [this.b]: new InputContract(this.b) };
  }

  initialState(): CrossCorrelationState {
    return { n: 0, past_a: [], past_b: [], stats: zeros(2 * this.maxLag + 1, 7) };
  }

  private update(s: number[], a: number, b: number): number[] {
    const lam = this.forgetting;
    let [w, w2, ma, mb, caa, cbb, cab] = s;
    w = lam * w + 1.0;
    w2 = lam * lam * w2 + 1.0;
    const da = a - ma, db = b - mb;
    ma += da / w;
    mb += db / w;
    const frac = (w - 1.0) / w; // the old weight's share: lambda w_old / w
    caa = lam * caa + frac * da * da;
    cbb = lam * cbb + frac * db * db;
    cab = lam * cab + frac * da * db;
    return [w, w2, ma, mb, caa, cbb, cab].map((v) => requireFinite(v, "cross moments"));
  }

  step(state: State, x: StatInput, _rng: SplitMix64 | null = null): [State, Output] {
    const s = state as CrossCorrelationState;
    const a = x[this.a] as number, b = x[this.b] as number;
    const big = this.maxLag;
    const stats = [...s.stats];
    for (let idx = 0; idx < 2 * big + 1; idx++) {
      const lag = idx - big;
      if (lag >= 0 && s.past_b.length >= lag) stats[idx] = this.update(stats[idx], a, lag === 0 ? b : s.past_b[lag - 1]);
      else if (lag < 0 && s.past_a.length >= -lag) stats[idx] = this.update(stats[idx], s.past_a[-lag - 1], b);
    }
    const next: CrossCorrelationState = {
      n: s.n + 1, past_a: [a, ...s.past_a].slice(0, big), past_b: [b, ...s.past_b].slice(0, big), stats,
    };
    return [next, this.summary(next)];
  }

  summary(state: State): Output {
    const s = state as CrossCorrelationState;
    const lags = Array.from({ length: 2 * this.maxLag + 1 }, (_, i) => i - this.maxLag);
    const corrs: (number | null)[] = [], pairs: number[] = [];
    let lead: number | null = null, best: number | null = null;
    lags.forEach((lag, i) => {
      const [w, w2, , , caa, cbb, cab] = s.stats[i];
      pairs.push(w2 > 0 ? w * w / w2 : 0.0);
      let r: number | null = null;
      if (caa > 0.0 && cbb > 0.0) {
        r = pyMax(-1.0, pyMin(1.0, cab / Math.sqrt(caa * cbb)));
        if (best === null || Math.abs(r) > Math.abs(best)) [lead, best] = [lag, r];
      }
      corrs.push(r);
    });
    return { n: s.n, lags, correlations: corrs, pairs, lead, correlation: best };
  }

  decodeState(data: Json): CrossCorrelationState {
    const s = decodeFields({ n: "count", past_a: "numbers", past_b: "numbers", stats: "json" }, data) as CrossCorrelationState;
    checkMatrix("stats", s.stats);
    const m = Math.min(s.n, this.maxLag);
    requireState(s.past_a.length === m && s.past_b.length === m, "the past, up to max_lag values");
    requireState(s.stats.length === 2 * this.maxLag + 1 && s.stats.every((v) => v.length === 7), "one set of moments per lag");
    requireState(s.stats.every((v) => v[0] >= 0 && v[1] >= 0 && v[4] >= 0 && v[5] >= 0),
      "weights and sums of squares must be non-negative");
    return s;
  }
}

register("cross_correlation", "1", (c) => CrossCorrelation.fromConfig(c));

// ------------------------------------------------------------------- regression, drifting coefficients

type DynamicRegressionState = {
  n: number; mean: number[]; precision: number[][]; dof: number; sum_squares: number; log_likelihood: number; comp: number;
};

/** Regression of y on `regressors` with coefficients that drift (discounted dynamic linear model); see multivariate.py. */
export class DynamicRegression extends BaseProcedure {
  readonly name = "dynamic_regression";
  readonly version = "1";
  readonly regressors: string[];
  readonly k: number;

  constructor(
    regressors: string[] = ["x"], readonly discount = 0.99, readonly varianceDiscount = 1.0, readonly intercept = true,
    readonly priorScale = 1e4, readonly input = "y",
  ) {
    super();
    this.regressors = names(regressors, "regressors");
    if (this.regressors.includes(input) || !(typeof input === "string" && input))
      invalid("input must be a non-empty name, not one of the regressors");
    if (!(0.0 < discount && discount <= 1.0) || !(0.0 < varianceDiscount && varianceDiscount <= 1.0))
      invalid("discounts must lie in (0, 1]");
    if (!(0.0 < priorScale && priorScale < Infinity)) invalid("prior_scale must be positive and finite");
    if (typeof intercept !== "boolean") invalid("intercept must be True or False");
    this.k = this.regressors.length + (intercept ? 1 : 0);
  }

  static fromConfig(c: Config): DynamicRegression {
    return new DynamicRegression(strs(c, "regressors"), num(c, "discount"), num(c, "variance_discount"), bool(c, "intercept"),
      num(c, "prior_scale"), str(c, "input"));
  }

  config(): Config {
    return {
      regressors: [...this.regressors], discount: this.discount, variance_discount: this.varianceDiscount, intercept: this.intercept,
      prior_scale: this.priorScale, input: this.input,
    };
  }

  inputs(): Record<string, InputContract> {
    return Object.fromEntries([this.input, ...this.regressors].map((n) => [n, new InputContract(n)]));
  }

  initialState(): DynamicRegressionState {
    const k = this.k;
    const prec = Array.from({ length: k }, (_, i) => Array.from({ length: k }, (_, j) => (i === j ? 1.0 / this.priorScale : 0.0)));
    return { n: 0, mean: Array.from({ length: k }, () => 0.0), precision: prec, dof: 0.0, sum_squares: 0.0, log_likelihood: 0.0, comp: 0.0 };
  }

  step(state: State, x: StatInput, _rng: SplitMix64 | null = null): [State, Output] {
    const s = state as DynamicRegressionState;
    const k = this.k;
    const f = [...(this.intercept ? [1.0] : []), ...this.regressors.map((r) => x[r] as number)];
    const y = x[this.input] as number;
    // the prior precision delta P, the inverse of R = C / delta; Rf and q = f'Rf + 1 from its Cholesky factor
    const low = choleskyFloor(Array.from({ length: k }, (_, i) => Array.from({ length: k }, (_, j) => this.discount * s.precision[i][j])));
    const q = 1.0 + quad(low, f);
    const rf = backward(low, forward(low, f));
    const error = y - la.dot(f, s.mean);
    const lam = this.varianceDiscount;
    let scale: number | null = null, z: number | null = null, score: number | null = null;
    let logLik = s.log_likelihood, comp = s.comp;
    if (s.dof > 0.0 && s.sum_squares > 0.0) {
      const df = lam * s.dof;
      scale = Math.sqrt(s.sum_squares / s.dof * q);
      z = error / scale;
      score = logDensity(error, scale, df);
      [logLik, comp] = neumaierAdd(logLik, comp, score);
    }
    const mean = s.mean.map((m, i) => requireFinite(m + rf[i] / q * error, "coefficients"));
    // information form: delta P + f f' is a sum of positive semi-definite matrices, so no cancellation
    const prec = Array.from({ length: k }, (_, i) =>
      Array.from({ length: k }, (_, j) => requireFinite(this.discount * s.precision[i][j] + f[i] * f[j], "precision")));
    const dof = lam * s.dof + 1.0;
    const ss = requireFinite(lam * s.sum_squares + error * error / q, "sum of squares");
    const next: DynamicRegressionState = { n: s.n + 1, mean, precision: prec, dof, sum_squares: ss, log_likelihood: logLik, comp };
    let sd: number[] | null = null;
    if (ss > 0.0) {
      const v = ss / dof;
      const low2 = choleskyFloor(prec);
      sd = Array.from({ length: k }, (_, i) => Math.sqrt(quad(low2, Array.from({ length: k }, (_, j) => (j === i ? 1.0 : 0.0))) * v));
    }
    return [next, { n: next.n, coefficients: mean, sd, error, scale, z, log_score: score, log_likelihood: logLik }];
  }

  decodeState(data: Json): DynamicRegressionState {
    const s = decodeFields({
      n: "count", mean: "numbers", precision: "json", dof: "number", sum_squares: "number", log_likelihood: "number", comp: "number",
    }, data) as DynamicRegressionState;
    checkMatrix("precision", s.precision);
    const k = this.k;
    requireState(s.mean.length === k && s.precision.length === k && s.precision.every((r) => r.length === k),
      "one coefficient per regressor");
    let diagonal = true;
    for (let i = 0; i < k; i++) diagonal = diagonal && s.precision[i][i] > 0;
    requireState(la.isSymmetric(s.precision) && diagonal, "the precision must be symmetric with a positive diagonal");
    requireState(s.dof >= 0 && s.sum_squares >= 0, "variance statistics");
    return s;
  }
}

register("dynamic_regression", "1", (c) => DynamicRegression.fromConfig(c));
