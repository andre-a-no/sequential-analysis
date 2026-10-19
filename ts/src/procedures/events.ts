// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
// Commercial licenses for use outside the AGPL: see COMMERCIAL.md
// Streams of events: self-exciting arrivals (Hawkes) and the market's reaction to events; mirrors procedures/events.py.
import type { Json } from "../canonical.js";
import { InputContract, type StatInput } from "../contracts.js";
import { ContractViolation } from "../errors.js";
import { neumaierAdd, requireFinite } from "../numerics.js";
import { decodeFields, type Output, register, requireState, type State } from "../procedure.js";
import type { SplitMix64 } from "../rng.js";
import { checkMatrix } from "./forecast.js";
import { BaseProcedure, type Config, int, invalid, num, optNum, str } from "./util.js";

// ------------------------------------------------------------------------------------------ Hawkes

type HawkesState = { n: number; last: number; excess: number; log_likelihood: number; comp: number };

/** Exact filter of an exponential-kernel Hawkes process; see events.py. */
export class HawkesProcess extends BaseProcedure {
  readonly name = "hawkes_process";
  readonly version = "1";

  constructor(
    readonly baseline: number, readonly excitation: number, readonly decay: number, readonly start = 0.0,
    readonly window: number | null = null, readonly input = "t",
  ) {
    super();
    for (const [name, v] of [["baseline", baseline], ["decay", decay]] as [string, number][])
      if (!(0.0 < v && v < Infinity)) invalid(`${name} must be positive and finite`);
    if (!(0.0 <= excitation && excitation < decay)) invalid("excitation must lie in [0, decay): a branching ratio below 1");
    if (!Number.isFinite(start)) invalid("start must be finite");
    if (window !== null && !(0.0 < window && window < Infinity)) invalid("window must be positive and finite, or None");
  }

  static fromConfig(c: Config): HawkesProcess {
    return new HawkesProcess(num(c, "baseline"), num(c, "excitation"), num(c, "decay"), num(c, "start"), optNum(c, "window"), str(c, "input"));
  }

  get branching(): number {
    return this.excitation / this.decay;
  }

  config(): Config {
    return { baseline: this.baseline, excitation: this.excitation, decay: this.decay, start: this.start, window: this.window, input: this.input };
  }

  inputs(): Record<string, InputContract> {
    return { [this.input]: new InputContract(this.input) };
  }

  initialState(): HawkesState {
    return { n: 0, last: this.start, excess: 0.0, log_likelihood: 0.0, comp: 0.0 };
  }

  /** The intensity at time t >= the last event, if no event came in between. */
  intensityAt(state: State, t: number): number {
    const s = state as HawkesState;
    if (t < s.last) invalid("t is before the last event");
    return this.baseline + s.excess * Math.exp(-this.decay * (t - s.last));
  }

  /** Expected events in the next `window` time units from current intensity, cascades included. */
  expectedEvents(intensity: number, window: number): number {
    const rate = this.decay - this.excitation;
    const mean = this.baseline * this.decay / rate;
    return mean * window + (intensity - mean) * -Math.expm1(-rate * window) / rate;
  }

  step(state: State, x: StatInput, _rng: SplitMix64 | null = null): [State, Output] {
    const s = state as HawkesState;
    const t = x[this.input] as number;
    if (t < s.last) throw new ContractViolation(`input '${this.input}': event time ${t} is before the previous one (${s.last})`);
    const gap = t - s.last;
    const decay = Math.exp(-this.decay * gap);
    const before = s.excess * decay;
    const compensator = this.baseline * gap + s.excess * -Math.expm1(-this.decay * gap) / this.decay;
    const intensityBefore = this.baseline + before;
    const score = Math.log(intensityBefore) - compensator;
    const [logLik, comp] = neumaierAdd(s.log_likelihood, s.comp, score);
    const excess = requireFinite(before + this.excitation, "intensity");
    const next: HawkesState = { n: s.n + 1, last: t, excess, log_likelihood: logLik, comp };
    const intensity = this.baseline + excess;
    const expected = this.window === null ? null : this.expectedEvents(intensity, this.window);
    return [next, {
      n: next.n, intensity, intensity_before: intensityBefore, compensator, log_score: score, log_likelihood: logLik, expected,
    }];
  }

  decodeState(data: Json): HawkesState {
    const s = decodeFields({ n: "count", last: "number", excess: "number", log_likelihood: "number", comp: "number" }, data) as HawkesState;
    requireState(s.excess >= 0 && s.last >= this.start, "the excess intensity and the last time");
    requireState(s.n > 0 || (s.excess === 0 && s.last === this.start), "an excess without events");
    return s;
  }
}

register("hawkes_process", "1", (c) => HawkesProcess.fromConfig(c));

// -------------------------------------------------------------------------------------- event study

type EventStudyState = { n: number; active: number[][]; events: number; skipped: number; mean: number[]; m2: number[] };

const OVERLAPS = ["skip", "allow"];

/** Average cumulative reaction of r over the `horizon` steps after an event; see events.py. */
export class EventStudy extends BaseProcedure {
  readonly name = "event_study";
  readonly version = "1";
  private readonly level: number;
  private readonly rho2: number;

  constructor(
    readonly horizon = 5, readonly alpha = 0.05, readonly start = 30, readonly tunedFor = 100.0, readonly overlap = "skip",
    readonly returns = "r", readonly event = "event",
  ) {
    super();
    if (!(Number.isInteger(horizon) && horizon >= 1)) invalid("horizon must be a positive int");
    if (!(0.0 < alpha && alpha < 1.0)) invalid("alpha must lie in (0, 1)");
    if (!(Number.isInteger(start) && start >= 2)) invalid("start must be an int, at least 2");
    if (!(Number.isFinite(tunedFor) && tunedFor >= 1)) invalid("tuned_for must be a number of events, at least 1");
    if (!OVERLAPS.includes(overlap)) invalid('overlap must be "skip" or "allow"');
    if (!(returns && event) || returns === event) invalid("returns and event must be two distinct input names");
    this.level = alpha / horizon;
    const c = -2.0 * Math.log(this.level);
    this.rho2 = (c + Math.log1p(c)) / tunedFor;
  }

  static fromConfig(c: Config): EventStudy {
    return new EventStudy(int(c, "horizon"), num(c, "alpha"), int(c, "start"), num(c, "tuned_for"), str(c, "overlap"), str(c, "returns"),
      str(c, "event"));
  }

  config(): Config {
    return {
      horizon: this.horizon, alpha: this.alpha, start: this.start, tuned_for: this.tunedFor, overlap: this.overlap, returns: this.returns,
      event: this.event,
    };
  }

  inputs(): Record<string, InputContract> {
    return { [this.returns]: new InputContract(this.returns), [this.event]: new InputContract(this.event, "binary") };
  }

  initialState(): EventStudyState {
    const zeros = Array.from({ length: this.horizon }, () => 0.0);
    return { n: 0, active: [], events: 0, skipped: 0, mean: [...zeros], m2: [...zeros] };
  }

  halfWidth(n: number, sd: number): number {
    const v = n * this.rho2 + 1.0;
    return sd * Math.sqrt(2.0 * v / (n * n * this.rho2) * (0.5 * Math.log(v) - Math.log(this.level)));
  }

  step(state: State, x: StatInput, _rng: SplitMix64 | null = null): [State, Output] {
    const s = state as EventStudyState;
    const r = x[this.returns] as number, happened = x[this.event] === 1;
    let events = s.events;
    const mean = [...s.mean], m2 = [...s.m2];
    const active: number[][] = [];
    for (const window of s.active) {
      const cum = [...window, requireFinite((window.length ? window[window.length - 1] : 0.0) + r, "cumulative return")];
      if (cum.length < this.horizon) {
        active.push(cum);
        continue;
      }
      events += 1;
      const frac = (events - 1) / events;
      cum.forEach((v, h) => {
        const delta = v - mean[h];
        mean[h] += delta / events;
        m2[h] += frac * delta * delta; // Welford's delta (v - new mean), never negative
      });
    }
    let skipped = s.skipped;
    if (happened) {
      if (this.overlap === "skip" && active.length) skipped += 1;
      else active.push([]);
    }
    const next: EventStudyState = { n: s.n + 1, active, events, skipped, mean, m2 };
    return [next, this.output(next)];
  }

  private output(s: EventStudyState): Output {
    if (s.events === 0) return { n: s.n, events: 0, skipped: s.skipped, open: s.active.length, mean: null, lower: null, upper: null };
    let lower: number[] | null = null, upper: number[] | null = null;
    if (s.events >= this.start && s.m2.every((v) => v > 0.0)) {
      const hs = s.m2.map((v) => this.halfWidth(s.events, Math.sqrt(v / (s.events - 1))));
      lower = s.mean.map((m, i) => m - hs[i]);
      upper = s.mean.map((m, i) => m + hs[i]);
    }
    return { n: s.n, events: s.events, skipped: s.skipped, open: s.active.length, mean: [...s.mean], lower, upper };
  }

  decodeState(data: Json): EventStudyState {
    const s = decodeFields({ n: "count", active: "json", events: "count", skipped: "count", mean: "numbers", m2: "numbers" }, data) as EventStudyState;
    checkMatrix("active", s.active);
    const h = this.horizon;
    requireState(s.mean.length === h && s.m2.length === h && s.m2.every((v) => v >= 0), "one mean and sum of squares per horizon");
    requireState(s.active.every((w) => w.length < h) && s.active.length <= h, "open windows shorter than the horizon");
    requireState(this.overlap === "allow" || s.active.length <= 1, "overlapping windows");
    requireState(s.events >= 0 && s.skipped >= 0, "event counts");
    return s;
  }
}

register("event_study", "1", (c) => EventStudy.fromConfig(c));
