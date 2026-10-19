// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
// Commercial licenses for use outside the AGPL: see COMMERCIAL.md
// Data topology: how observations become statistical inputs (SPEC.md, "Topologies").
import type { Json } from "./canonical.js";
import type { StatInput } from "./contracts.js";
import { ContractViolation, OrderingError } from "./errors.js";
import { complete, type Observation } from "./observation.js";
import { portableExp2 } from "./numerics.js";

/** Stands for an input a transformation could not map; the run reports and skips it. */
export class InvalidInput {
  constructor(readonly violation: ContractViolation) {}
}

export interface Topology {
  spec(): Json;
  push(obs: Observation): (StatInput | InvalidInput)[];
  state(): Json;
  restore(state: Json): void;
}

export class Independent implements Topology {
  spec(): Json {
    return { type: "independent" };
  }
  push(obs: Observation): StatInput[] {
    return [{ [obs.input]: obs.value }];
  }
  state(): Json {
    return null;
  }
  restore(): void {}
}

abstract class Buffered {
  readonly inputs: string[];
  constructor(inputs: string[]) {
    if (inputs.length < 2 || new Set(inputs).size !== inputs.length) throw new Error("need at least two distinct logical inputs");
    this.inputs = [...inputs];
  }
  protected check(obs: Observation): void {
    if (!this.inputs.includes(obs.input)) throw new ContractViolation(`observation for input '${obs.input}' is not part of this topology`);
  }
}

/** Pair the i-th observation of every input. */
export class PositionalPair extends Buffered implements Topology {
  private queues: Record<string, Json[]> = {};
  constructor(inputs: string[]) {
    super(inputs);
    for (const n of this.inputs) this.queues[n] = [];
  }
  spec(): Json {
    return { type: "positional_pair", inputs: this.inputs };
  }
  push(obs: Observation): StatInput[] {
    this.check(obs);
    this.queues[obs.input].push(obs.value);
    const out: StatInput[] = [];
    while (this.inputs.every((n) => this.queues[n].length)) {
      const x: StatInput = {};
      for (const n of this.inputs) x[n] = this.queues[n].shift()!;
      out.push(x);
    }
    return out;
  }
  state(): Json {
    return Object.fromEntries(this.inputs.map((n) => [n, [...this.queues[n]]]));
  }
  restore(state: Json): void {
    const s = state as Record<string, Json[]>;
    this.queues = Object.fromEntries(this.inputs.map((n) => {
      if (!Array.isArray(s[n])) throw new Error(`no queue for input '${n}'`);
      return [n, [...s[n]]];
    }));
  }
}

/** Join observations that carry the same key; emits in completion order. */
export class KeyJoin extends Buffered implements Topology {
  private partial = new Map<string | number, Record<string, Json>>();
  spec(): Json {
    return { type: "key_join", inputs: this.inputs };
  }
  push(obs: Observation): StatInput[] {
    this.check(obs);
    const key = complete(obs).key;
    if (typeof key !== "string" && typeof key !== "number")
      throw new ContractViolation(`key join needs a str or int key on every observation, got ${JSON.stringify(key)}`);
    let row = this.partial.get(key);
    if (!row) this.partial.set(key, (row = {}));
    if (obs.input in row) throw new OrderingError(`key ${JSON.stringify(key)}: input '${obs.input}' was observed twice`);
    row[obs.input] = obs.value;
    if (Object.keys(row).length < this.inputs.length) return [];
    this.partial.delete(key);
    return [Object.fromEntries(this.inputs.map((n) => [n, row![n]]))];
  }
  state(): Json {
    return [...this.partial].map(([k, row]) => [k, { ...row }]);
  }
  restore(state: Json): void {
    this.partial = new Map((state as [string | number, Record<string, Json>][]).map(([k, row]) => [k, { ...row }]));
  }
}

/** Align two time-ordered inputs within a tolerance. */
export class TimeAlign extends Buffered implements Topology {
  unmatched = 0;
  private queues: Record<string, [number, Json][]> = {};
  private last: Record<string, number | null> = {};
  constructor(inputs: string[], readonly tolerance: number) {
    super(inputs);
    if (this.inputs.length !== 2) throw new Error("time alignment is defined for exactly two inputs");
    if (!(Number.isFinite(tolerance) && tolerance >= 0)) throw new Error("tolerance must be a finite non-negative number");
    for (const n of this.inputs) {
      this.queues[n] = [];
      this.last[n] = null;
    }
  }
  spec(): Json {
    return { type: "time_align", inputs: this.inputs, tolerance: this.tolerance };
  }
  push(obs: Observation): StatInput[] {
    this.check(obs);
    const time = complete(obs).time;
    if (time === null) throw new ContractViolation("time alignment needs an event time on every observation");
    const last = this.last[obs.input];
    if (last !== null && time < last) throw new OrderingError(`input '${obs.input}': event time went backwards (${time} < ${last})`);
    this.last[obs.input] = time;
    this.queues[obs.input].push([time, obs.value]);
    const [a, b] = this.inputs;
    const qa = this.queues[a], qb = this.queues[b];
    const out: StatInput[] = [];
    while (qa.length && qb.length) {
      const [ta, va] = qa[0], [tb, vb] = qb[0];
      if (Math.abs(ta - tb) <= this.tolerance) {
        qa.shift();
        qb.shift();
        out.push({ [a]: va, [b]: vb });
      } else if (ta < tb) {
        qa.shift();
        this.unmatched += 1;
      } else {
        qb.shift();
        this.unmatched += 1;
      }
    }
    return out;
  }
  state(): Json {
    return {
      queues: Object.fromEntries(this.inputs.map((n) => [n, this.queues[n].map(([t, v]) => [t, v])])),
      last: { ...this.last },
      unmatched: this.unmatched,
    };
  }
  restore(state: Json): void {
    const s = state as { queues: Record<string, [number, Json][]>; last: Record<string, number | null>; unmatched: number };
    this.queues = Object.fromEntries(this.inputs.map((n) => [n, s.queues[n].map(([t, v]) => [t, v] as [number, Json])]));
    this.last = Object.fromEntries(this.inputs.map((n) => [n, s.last[n]]));
    this.unmatched = s.unmatched;
  }
}

const finiteNumber = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const pyList = (names: string[]): string => `[${names.map((n) => `'${n}'`).join(", ")}]`;

/**
 * Attach to every bar what a stream of events said up to the bar's time: <prefix>_count and <prefix>_sum of the
 * events since the previous bar, and with a half-life <prefix>_decayed and <prefix>_decayed_count (see topology.py).
 * Not confluent: what a bar sees depends on which events arrived before it.
 */
export class AsOfJoin implements Topology {
  readonly halfLife: number | null;
  readonly prefix: string;
  readonly inputs: string[];
  readonly fields: string[];
  late = 0;
  private pending: [number, number][] = [];
  private lastBar: number | null = null;
  private lastEvent: number | null = null;
  private decayed = 0.0;
  private decayedCount = 0.0;

  constructor(readonly bars: string, readonly events: string, halfLife: number | null = null, prefix: string | null = null) {
    if (!(typeof bars === "string" && bars && typeof events === "string" && events) || bars === events)
      throw new Error("bars and events must be two distinct non-empty input names");
    if (halfLife !== null && !(typeof halfLife === "number" && 0 < halfLife && halfLife < Infinity))
      throw new Error("half_life must be a positive finite number or None");
    if (prefix !== null && !(typeof prefix === "string" && prefix)) throw new Error("prefix must be a non-empty string or None");
    this.halfLife = halfLife;
    this.prefix = prefix !== null ? prefix : events;
    this.inputs = [bars, events];
    this.fields = ["count", "sum", ...(halfLife !== null ? ["decayed", "decayed_count"] : [])].map((f) => `${this.prefix}_${f}`);
  }

  spec(): Json {
    return { type: "as_of_join", bars: this.bars, events: this.events, half_life: this.halfLife, prefix: this.prefix };
  }

  push(obs: Observation): StatInput[] {
    if (!this.inputs.includes(obs.input)) throw new ContractViolation(`observation for input '${obs.input}' is not part of this topology`);
    const time = complete(obs).time;
    if (time === null) throw new ContractViolation("an as-of join needs an event time on every observation");
    if (obs.input === this.events) {
      if (!finiteNumber(obs.value)) throw new ContractViolation(`input '${this.events}': an event's value must be a finite number`);
      if (this.lastEvent !== null && time < this.lastEvent)
        throw new OrderingError(`input '${this.events}': event time went backwards (${time} < ${this.lastEvent})`);
      this.lastEvent = time;
      this.pending.push([time, obs.value]);
      return [];
    }
    if (this.lastBar !== null && time < this.lastBar)
      throw new OrderingError(`input '${this.bars}': event time went backwards (${time} < ${this.lastBar})`);
    let row: StatInput;
    const value = obs.value;
    if (value !== null && typeof value === "object" && !Array.isArray(value)) {
      row = { ...value };
      const clash = Object.keys(row).filter((k) => this.fields.includes(k)).sort();
      if (clash.length) throw new ContractViolation(`input '${this.bars}': fields ${pyList(clash)} are the join's own`);
    } else row = { [this.bars]: value };
    const now = time;
    let count = 0, total = 0.0, decayed = this.decayed, decayedCount = this.decayedCount;
    if (this.halfLife !== null && this.lastBar !== null) {
      const f = portableExp2(-(now - this.lastBar) / this.halfLife);
      decayed = decayed * f;
      decayedCount = decayedCount * f;
    }
    while (this.pending.length && this.pending[0][0] <= now) {
      const [t, v] = this.pending.shift()!;
      if (this.lastBar !== null && t <= this.lastBar) this.late += 1;
      count += 1;
      total += v;
      if (this.halfLife !== null) {
        const w = portableExp2(-(now - t) / this.halfLife);
        decayed += v * w;
        decayedCount += w;
      }
    }
    this.lastBar = now;
    this.decayed = decayed;
    this.decayedCount = decayedCount;
    row[this.fields[0]] = count;
    row[this.fields[1]] = total;
    if (this.halfLife !== null) {
      row[this.fields[2]] = decayed;
      row[this.fields[3]] = decayedCount;
    }
    return [row];
  }

  state(): Json {
    return {
      pending: this.pending.map(([t, v]) => [t, v]), last_bar: this.lastBar, last_event: this.lastEvent, decayed: this.decayed,
      decayed_count: this.decayedCount, late: this.late,
    };
  }

  restore(state: Json): void {
    const s = state as { pending: Json; last_bar: Json; last_event: Json; decayed: Json; decayed_count: Json; late: Json };
    if (!Array.isArray(s.pending) || !s.pending.every((item) => Array.isArray(item) && item.length === 2 && item.every(finiteNumber)))
      throw new Error("pending events must be [time, value] pairs");
    for (const k of ["last_bar", "last_event"] as const)
      if (s[k] !== null && !finiteNumber(s[k])) throw new Error(`${k} must be a number or null`);
    if (!finiteNumber(s.decayed) || !finiteNumber(s.decayed_count)) throw new Error("decayed sums must be numbers");
    if (!(finiteNumber(s.late) && Number.isInteger(s.late))) throw new Error("late must be an integer");
    this.pending = (s.pending as [number, number][]).map(([t, v]) => [t, v]);
    this.lastBar = s.last_bar as number | null;
    this.lastEvent = s.last_event as number | null;
    this.decayed = s.decayed;
    this.decayedCount = s.decayed_count;
    this.late = s.late;
  }
}

/** A topology followed by the difference transform {a, b} -> {out: a - b} (Python: topology.map(difference(a, b, out))). */
export class Difference implements Topology {
  constructor(readonly inner: Topology, readonly a: string, readonly b: string, readonly out = "x") {}
  spec(): Json {
    return { type: "mapped", map: { name: "difference", version: "1", config: { a: this.a, b: this.b, out: this.out } }, inner: this.inner.spec() };
  }
  push(obs: Observation): (StatInput | InvalidInput)[] {
    return this.inner.push(obs).map((x) => {
      if (x instanceof InvalidInput) return x;
      const u = x[this.a], v = x[this.b];
      if (typeof u !== "number" || typeof v !== "number")
        return new InvalidInput(new ContractViolation(`difference failed on ${JSON.stringify(x)}: not numbers`));
      return { [this.out]: u - v };
    });
  }
  state(): Json {
    return this.inner.state();
  }
  restore(state: Json): void {
    this.inner.restore(state);
  }
}

/** The topology a spec describes (the built-in ones; a mapped topology only with the difference transform). */
export function topologyFromSpec(spec: Json): Topology {
  const s = spec as Record<string, Json>;
  switch (s.type) {
    case "independent":
      return new Independent();
    case "positional_pair":
      return new PositionalPair(s.inputs as string[]);
    case "key_join":
      return new KeyJoin(s.inputs as string[]);
    case "time_align":
      return new TimeAlign(s.inputs as string[], s.tolerance as number);
    case "as_of_join":
      return new AsOfJoin(s.bars as string, s.events as string, s.half_life as number | null, s.prefix as string | null);
    case "mapped": {
      const map = s.map as { name: string; version: string; config: { a: string; b: string; out: string } };
      if (map.name !== "difference" || map.version !== "1") throw new Error(`transform ${map.name} has no TypeScript implementation`);
      return new Difference(topologyFromSpec(s.inner), map.config.a, map.config.b, map.config.out);
    }
    default:
      throw new Error(`unknown topology ${JSON.stringify(s.type)}`);
  }
}
