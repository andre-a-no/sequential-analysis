# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""Lagged inputs and the as-of join of events to bars.

* Lagged gives the inner procedure exactly the lags one would build by
  hand, waits until they exist, and survives a checkpoint mid-stream.
* AsOfJoin: the counts, sums and decayed sums are those recomputed from
  scratch for every bar; a bar never sees an event that arrived after it;
  late events go to the next bar and are counted; its state survives a
  checkpoint.
"""
import json
import math
import random
import unittest

from sequential_analysis import AsOfJoin, Lagged, Observation, Run, lag_name
from sequential_analysis.errors import ContractViolation, OrderingError
from sequential_analysis.procedures import AnytimeLinearModel, DynamicRegression


def granger(lags=2):
    names = [lag_name("y", j) for j in range(1, lags + 1)]
    tested = [lag_name("x", j) for j in range(1, lags + 1)]
    return Lagged(AnytimeLinearModel(covariates=tuple(names), tested=tuple(tested)), {"x": lags, "y": lags})


def leading(n, seed, effect=0.5):
    rnd = random.Random(seed)
    xs = [rnd.gauss(0.0, 1.0) for _ in range(n)]
    ys = [0.0] + [effect * xs[t - 1] + rnd.gauss(0.0, 1.0) for t in range(1, n)]
    return xs, ys


class LaggedInputs(unittest.TestCase):
    def test_same_as_lags_built_by_hand(self):
        xs, ys = leading(300, 1)
        model = granger()
        inner = AnytimeLinearModel(covariates=("y_lag1", "y_lag2"), tested=("x_lag1", "x_lag2"))
        state, ref = model.initial_state(), inner.initial_state()
        for t, (x, y) in enumerate(zip(xs, ys)):
            state, out = model.step(state, {"x": x, "y": y})
            self.assertEqual(out.ready, t >= 2)
            if t >= 2:
                ref, expected = inner.step(ref, {"y": y, "y_lag1": ys[t - 1], "y_lag2": ys[t - 2],
                                                 "x_lag1": xs[t - 1], "x_lag2": xs[t - 2]})
                self.assertEqual(out.inner, expected)
            else:
                self.assertIsNone(out.inner)
        self.assertEqual(out.inner.decision, "reject_h0")
        self.assertEqual(model.guarantee, inner.guarantee)

    def test_checkpoint_mid_stream(self):
        xs, ys = leading(120, 2)
        whole = Run(granger(), run_id="g", clock=lambda: 0.0)
        for x, y in zip(xs, ys):
            last = whole.step({"x": x, "y": y})
        first = Run(granger(), run_id="g", clock=lambda: 0.0)
        for x, y in zip(xs[:57], ys[:57]):
            first.step({"x": x, "y": y})
        cp = json.loads(json.dumps(first.checkpoint()))
        second = Run.restore(granger(), cp, clock=lambda: 0.0)
        second.start()
        for x, y in zip(xs[57:], ys[57:]):
            again = second.step({"x": x, "y": y})
        self.assertEqual(again.output, last.output)

    def test_refusals(self):
        inner = AnytimeLinearModel(covariates=(), tested=("x_lag1",))
        for make in (lambda: Lagged(inner, {}), lambda: Lagged(inner, {"x": 0}), lambda: Lagged(inner, {"x": 2}),
                     lambda: Lagged(inner, {"z": 1})):
            with self.assertRaises(ValueError):
                make()


def brute_force(observations, half_life):
    """For every bar, from scratch: the events that had arrived before it, by their times."""
    rows, arrived, given = [], [], set()
    last_bar = None
    for i, (name, value, t) in enumerate(observations):
        if name == "news":
            arrived.append((i, t, value))
            continue
        new = [(j, s, v) for j, s, v in arrived if s <= t and j not in given]
        given |= {j for j, _, _ in new}
        row = {"r": value, "news_count": len(new), "news_sum": sum(v for _, _, v in new)}
        seen = [(s, v) for j, s, v in arrived if j in given]
        row["news_decayed"] = sum(v * 2.0 ** (-(t - s) / half_life) for s, v in seen)
        row["news_decayed_count"] = sum(2.0 ** (-(t - s) / half_life) for s, _ in seen)
        row["late"] = sum(1 for _, s, _ in new if last_bar is not None and s <= last_bar)
        last_bar = t
        rows.append(row)
    return rows


def news_stream(n_bars, seed):
    """Bars every 1.0; news at random times, each arriving with a random delay (some after the next bar)."""
    rnd = random.Random(seed)
    news = []
    t = 0.0
    while t < n_bars:
        t += rnd.expovariate(0.7)
        news.append((t, round(rnd.uniform(-1.0, 1.0), 3)))
    events = [("r", round(rnd.gauss(0.0, 0.01), 5), float(b)) for b in range(1, n_bars + 1)]
    # an event's time is when it became available; it is delivered in that order, among the bars
    events += [("news", v, s) for s, v in news if s <= n_bars]
    events.sort(key=lambda e: (e[2], e[0] == "r"))
    return events


class AsOf(unittest.TestCase):
    def test_matches_brute_force(self):
        observations = news_stream(200, 3)
        join = AsOfJoin("r", "news", half_life=3.0)
        rows = []
        for i, (name, value, t) in enumerate(observations):
            rows += join.push(Observation(name, value, seq=i, time=t))
        ref = brute_force(observations, 3.0)
        self.assertEqual(len(rows), len(ref))
        for row, r in zip(rows, ref):
            self.assertEqual(row["news_count"], r["news_count"])
            for key in ("news_sum", "news_decayed", "news_decayed_count"):
                self.assertAlmostEqual(row[key], r[key], delta=1e-9)
        self.assertEqual(join.late, 0)

    def test_late_events_go_to_the_next_bar(self):
        join = AsOfJoin("r", "news")
        out = []
        for i, (name, value, t) in enumerate([("r", 0.1, 1.0), ("news", 0.5, 0.9), ("news", 0.2, 1.5),
                                              ("r", 0.2, 2.0), ("news", 0.7, 2.5), ("r", 0.3, 2.4)]):
            out += join.push(Observation(name, value, seq=i, time=t))
        self.assertEqual([r["news_count"] for r in out], [0, 2, 0])  # 2.5 is after the bar at 2.4
        self.assertEqual(join.late, 1)
        self.assertEqual(out[1]["news_sum"], 0.7)

    def test_bars_with_fields_and_refusals(self):
        join = AsOfJoin("bar", "news", prefix="n")
        self.assertEqual(join.push(Observation("bar", {"r": 1.0, "m": 0.5}, seq=0, time=1.0)),
                         [{"r": 1.0, "m": 0.5, "n_count": 0, "n_sum": 0.0}])
        with self.assertRaises(ContractViolation):
            join.push(Observation("bar", {"n_sum": 1.0}, seq=1, time=2.0))
        with self.assertRaises(ContractViolation):
            join.push(Observation("news", "good", seq=2, time=2.0))
        with self.assertRaises(ContractViolation):
            join.push(Observation("news", 1.0, seq=3))
        with self.assertRaises(OrderingError):
            join.push(Observation("bar", 1.0, seq=4, time=0.5))
        for make in (lambda: AsOfJoin("a", "a"), lambda: AsOfJoin("a", "b", half_life=0.0)):
            with self.assertRaises(ValueError):
                make()

    def test_in_a_run_with_checkpoint(self):
        observations = news_stream(60, 4)

        def fresh():
            return DynamicRegression(("news_count", "news_sum"), input="r")

        def obs(i, e):
            return Observation(e[0], e[1], seq=i, time=e[2])

        whole = Run(fresh(), topology=AsOfJoin("r", "news"), run_id="n", clock=lambda: 0.0)
        out = []
        for i, e in enumerate(observations):
            out += whole.offer(obs(i, e))
        cut = len(observations) // 2
        first = Run(fresh(), topology=AsOfJoin("r", "news"), run_id="n", clock=lambda: 0.0)
        for i, e in enumerate(observations[:cut]):
            first.offer(obs(i, e))
        cp = json.loads(json.dumps(first.checkpoint()))
        second = Run.restore(fresh(), cp, topology=AsOfJoin("r", "news"), clock=lambda: 0.0)
        second.start()
        rest = []
        for i, e in enumerate(observations[cut:], start=cut):
            rest += second.offer(obs(i, e))
        self.assertEqual([e.output for e in rest], [e.output for e in out[-len(rest):]])
        self.assertTrue(all(math.isfinite(e.output.error) for e in out))


if __name__ == "__main__":
    unittest.main()
