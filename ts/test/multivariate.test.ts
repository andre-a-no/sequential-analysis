// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
// Commercial licenses for use outside the AGPL: see COMMERCIAL.md
// Several series, streams of events and Lagged: the refusals the conformance vectors do not reach.
import assert from "node:assert/strict";
import { test } from "node:test";
import { ContractViolation } from "../src/errors.js";
import { fromIdentity, identity } from "../src/procedure.js";
import {
  AnytimeLinearModel, CrossCorrelation, DynamicRegression, EventStudy, HawkesProcess, Lagged, VectorAutoRegressive,
} from "../src/procedures/index.js";

test("hawkes_process refuses an event before the previous one, and inconsistent states", () => {
  const h = new HawkesProcess(0.5, 0.4, 1.0, 1.0);
  const [s] = h.step(h.initialState(), { t: 2.0 }, null);
  assert.throws(() => h.step(s, { t: 1.5 }, null), ContractViolation);
  assert.throws(() => h.decodeState({ ...s, last: 0.5 }), /inconsistent state/);
  assert.throws(() => h.decodeState({ n: 0, last: 1.0, excess: 0.4, log_likelihood: 0, comp: 0 }), /inconsistent state/);
  assert.throws(() => new HawkesProcess(0.5, 1.0, 1.0), RangeError); // branching ratio 1
  assert.throws(() => new HawkesProcess(0.5, 0.1, 1.0, 0.0, 0.0), RangeError);
});

test("event_study refuses overlapping windows with overlap skip, and bad arguments", () => {
  const e = new EventStudy(3, 0.05, 5);
  assert.throws(() => e.decodeState({ n: 2, active: [[], [0.1]], events: 0, skipped: 0, mean: [0, 0, 0], m2: [0, 0, 0] }), /overlapping/);
  assert.throws(() => e.decodeState({ n: 2, active: [[0.1, 0.2, 0.3]], events: 0, skipped: 0, mean: [0, 0, 0], m2: [0, 0, 0] }), /shorter/);
  assert.throws(() => new EventStudy(3, 0.05, 1), RangeError);
  assert.throws(() => new EventStudy(3, 0.05, 5, 100, "merge"), RangeError);
  assert.throws(() => new EventStudy(3, 0.05, 5, 100, "skip", "r", "r"), RangeError);
});

test("vector_autoregressive: fixed and learnt configurations, and their states", () => {
  assert.throws(() => new VectorAutoRegressive(["a", "a"], 1), RangeError);
  assert.throws(() => new VectorAutoRegressive(["a", "b"], 1, { coefficients: [[[0.1, 0], [0, 0.1]]] }), /intercept and a covariance/);
  assert.throws(() => new VectorAutoRegressive(["a"], 1, { coefficients: [[[0.5]]], intercept: [0], covariance: [[-1]] }), /positive definite/);
  const v = new VectorAutoRegressive(["a", "b"], 1, { forgetting: 0.9 });
  assert.equal(fromIdentity(identity(v)).name, "vector_autoregressive");
  const s = v.initialState();
  assert.throws(() => v.decodeState({ ...s, scatter: [[0, 1], [0, 0]] }), /symmetric/);
  assert.throws(() => v.decodeState({ ...s, lags: [[1, 2]] }), /lag vector/);
  const fixed = new VectorAutoRegressive(["a"], 1, { coefficients: [[[0.5]]], intercept: [0], covariance: [[1]] });
  assert.throws(() => fixed.decodeState({ ...fixed.initialState(), dof: 1 }), /learnt statistics/);
});

test("cross_correlation and dynamic_regression check their arguments and states", () => {
  assert.throws(() => new CrossCorrelation("a", "a"), RangeError);
  assert.throws(() => new CrossCorrelation("a", "b", 2, 0), RangeError);
  const c = new CrossCorrelation("a", "b", 1);
  assert.throws(() => c.decodeState({ ...c.initialState(), past_a: [1] }), /the past/);
  assert.throws(() => new DynamicRegression(["y"]), RangeError);
  assert.throws(() => new DynamicRegression(["x"], 1.5), RangeError);
  const d = new DynamicRegression(["x"]);
  assert.throws(() => d.decodeState({ ...d.initialState(), precision: [[1, 0.5], [0, 1]] }), /symmetric/);
});

test("lagged waits for the past, then steps the inner procedure; refuses inconsistent states", () => {
  const inner = new DynamicRegression(["b_lag1"], 0.99, 1.0, true, 1e4, "a");
  const l = new Lagged(inner, { b: 1 });
  assert.deepEqual(Object.keys(l.inputs()).sort(), ["a", "b"]);
  const [s1, o1] = l.step(l.initialState(), { a: 1, b: 2 }, null);
  assert.deepEqual(o1, { ready: false, inner: null });
  const [s2, o2] = l.step(s1, { a: 3, b: 4 }, null);
  assert.equal(o2.ready, true);
  assert.deepEqual(s2.past, { b: [4] });
  assert.equal(fromIdentity(identity(l)).name, "lagged");
  assert.throws(() => l.decodeState({ ...s2, past: { b: [] } }), /the past of 'b'/);
  assert.throws(() => l.decodeState({ ...s2, past: { c: [1] } }), /one past per source/);
  assert.throws(() => new Lagged(inner, { b: 2 }), /does not take the lagged inputs/);
  assert.throws(() => new Lagged(inner, { b: 0 }), RangeError);
  const alm = new AnytimeLinearModel([], ["x_lag1"]);
  assert.ok(new Lagged(alm, { x: 1 }).inputs().x);
});
