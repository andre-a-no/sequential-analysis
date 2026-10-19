# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""Streams of events: Hawkes processes and event studies.

* HawkesProcess: its log-likelihood is the direct O(n^2) formula; under
  the true parameters its compensators are standard exponentials; the
  expected number of events in a window matches simulation.
* fit_hawkes recovers the parameters of a simulated process and attains
  at least the likelihood of the true ones.
* EventStudy: the average cumulative reactions are those computed by
  hand, overlapping events are skipped or kept, and with no reaction the
  confidence sequences miss 0 rarely.
"""
import math
import random
import unittest

from sequential_analysis.errors import ContractViolation
from sequential_analysis.events import fit_hawkes, hawkes_log_likelihood, simulate_hawkes
from sequential_analysis.procedures import EventStudy, HawkesProcess


def direct_log_likelihood(ts, mu, alpha, beta, start, end):
    total = 0.0
    for i, t in enumerate(ts):
        total += math.log(mu + sum(alpha * math.exp(-beta * (t - s)) for s in ts[:i]))
    return total - mu * (end - start) - sum(alpha / beta * -math.expm1(-beta * (end - s)) for s in ts)


class Hawkes(unittest.TestCase):
    times = simulate_hawkes(0.5, 0.8, 1.2, 3000.0, seed=3)

    def test_log_likelihood_is_the_direct_formula(self):
        ts = self.times[:150]
        ref = direct_log_likelihood(ts, 0.5, 0.8, 1.2, 0.0, ts[-1])
        self.assertAlmostEqual(hawkes_log_likelihood(ts, 0.5, 0.8, 1.2, 0.0, ts[-1]), ref, delta=1e-9)
        model = HawkesProcess(0.5, 0.8, 1.2)
        state = model.initial_state()
        for t in ts:
            state, out = model.step(state, {"t": t})
        self.assertAlmostEqual(out.log_likelihood, ref, delta=1e-9)
        self.assertAlmostEqual(model.intensity_at(state, ts[-1]), out.intensity, delta=1e-12)

    def test_compensators_are_standard_exponential(self):
        model = HawkesProcess(0.5, 0.8, 1.2)
        state, comps = model.initial_state(), []
        for t in self.times:
            state, out = model.step(state, {"t": t})
            comps.append(out.compensator)
        n = len(comps)
        self.assertAlmostEqual(sum(comps) / n, 1.0, delta=4 / math.sqrt(n))
        above = sum(c > 1.0 for c in comps) / n
        self.assertAlmostEqual(above, math.exp(-1.0), delta=4 * math.sqrt(0.25 / n))

    def test_expected_events_match_simulation(self):
        model = HawkesProcess(0.5, 0.8, 1.2, window=4.0)
        expected = model.expected_events(0.5, 4.0)  # from the baseline, nothing excited yet
        counts = [len(simulate_hawkes(0.5, 0.8, 1.2, 4.0, seed=s)) for s in range(3000)]
        mean = sum(counts) / len(counts)
        sd = math.sqrt(sum((c - mean) ** 2 for c in counts) / (len(counts) - 1))
        self.assertAlmostEqual(mean, expected, delta=4 * sd / math.sqrt(len(counts)))
        # in the long run, the stationary rate mu / (1 - n)
        self.assertAlmostEqual(model.expected_events(1.5, 1e6) / 1e6, 0.5 / (1 - 0.8 / 1.2), delta=1e-6)

    def test_fit_recovers_parameters(self):
        fit = fit_hawkes(self.times, start=0.0, end=3000.0)
        p = fit.parameters
        self.assertAlmostEqual(p["baseline"], 0.5, delta=0.1)
        self.assertAlmostEqual(p["branching"], 0.8 / 1.2, delta=0.06)
        self.assertAlmostEqual(p["decay"], 1.2, delta=0.3)
        self.assertGreaterEqual(fit.log_likelihood,
                                hawkes_log_likelihood(self.times, 0.5, 0.8, 1.2, 0.0, 3000.0) - 1e-9)
        self.assertEqual(fit.state.n, len(self.times))

    def test_refusals(self):
        for make in (lambda: HawkesProcess(0.0, 0.1, 1.0), lambda: HawkesProcess(1.0, 1.0, 1.0),
                     lambda: HawkesProcess(1.0, 0.1, 1.0, window=0.0)):
            with self.assertRaises(ValueError):
                make()
        model = HawkesProcess(1.0, 0.5, 1.0)
        state, _ = model.step(model.initial_state(), {"t": 2.0})
        with self.assertRaises(ContractViolation):
            model.step(state, {"t": 1.0})
        with self.assertRaises(ValueError):
            fit_hawkes([1.0, 0.5, 2.0])


class Study(unittest.TestCase):
    def run_study(self, model, rows):
        state, out = model.initial_state(), None
        for r, e in rows:
            state, out = model.step(state, {"r": r, "event": e})
        return state, out

    def test_cumulative_reactions_by_hand(self):
        rows = [(0.0, 1), (1.0, 0), (2.0, 0), (-1.0, 1), (0.5, 0), (0.5, 0), (3.0, 0)]
        _, out = self.run_study(EventStudy(2, start=2), rows)
        # windows: event 0 sees 1, 2 -> (1, 3); event 3 sees 0.5, 0.5 -> (0.5, 1)
        self.assertEqual(out.events, 2)
        self.assertEqual(out.mean, (0.75, 2.0))
        self.assertIsNotNone(out.lower)

    def test_overlap(self):
        rows = [(1.0, 1), (1.0, 1), (1.0, 0), (1.0, 0)]
        state, out = self.run_study(EventStudy(2), rows)
        self.assertEqual((out.events, out.skipped), (1, 1))
        state, out = self.run_study(EventStudy(2, overlap="allow"), rows)
        self.assertEqual((out.events, out.skipped), (2, 0))

    def test_rarely_misses_zero_without_reaction(self):
        misses, runs = 0, 60
        for seed in range(runs):
            rnd = random.Random(seed)
            model = EventStudy(3, alpha=0.1)
            state = model.initial_state()
            missed = False
            for _ in range(3000):
                state, out = model.step(state, {"r": rnd.gauss(0.0, 1.0), "event": int(rnd.random() < 0.05)})
                if out.lower is not None and any(lo > 0 or hi < 0 for lo, hi in zip(out.lower, out.upper)):
                    missed = True
            misses += missed
        self.assertLessEqual(misses / runs, 0.1)

    def test_refusals(self):
        for make in (lambda: EventStudy(0), lambda: EventStudy(overlap="maybe"), lambda: EventStudy(start=1),
                     lambda: EventStudy(returns="x", event="x")):
            with self.assertRaises(ValueError):
                make()


if __name__ == "__main__":
    unittest.main()
