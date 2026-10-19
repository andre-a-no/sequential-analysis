# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""GARCH(1,1) and GJR-GARCH(1,1).

* fit_garch reaches the arch package's maximum likelihood (normal and
  Student t, with and without leverage, constant or zero mean), and its
  filter reproduces arch's conditional volatility and variance forecasts.
* The filter's log-likelihood over the history is the fitted one; its
  densities are the normal and the unit-variance t (scipy).
* The intervals cover: under the model, about `coverage` of returns fall
  inside the one-step interval; the standardized residuals have variance 1.
"""
import math
import random
import unittest

from sequential_analysis.garch_fit import backcast, fit_garch, garch_log_likelihood
from sequential_analysis.procedures import GARCH
from sequential_analysis.procedures.volatility import garch_log_density

try:
    import numpy as np
    from arch import arch_model
except ImportError:  # optional reference
    arch_model = None

try:
    from scipy import stats
except ImportError:  # optional reference
    stats = None


def simulate(n, seed, omega=0.05, alpha=0.08, beta=0.9, gamma=0.0, df=None, mean=0.03):
    rnd = random.Random(seed)
    v = omega / (1.0 - alpha - beta - 0.5 * gamma)
    out = []
    for _ in range(n):
        z = rnd.gauss(0.0, 1.0)
        if df is not None:
            z = z / math.sqrt(rnd.gammavariate(df / 2.0, 2.0 / df)) * math.sqrt((df - 2.0) / df)
        e = math.sqrt(v) * z
        out.append(mean + e)
        v = omega + alpha * e * e + beta * v + (gamma * e * e if e < 0.0 else 0.0)
    return out


CASES = [
    ("normal", False, False, {}),
    ("t", False, False, {"df": 6.0}),
    ("normal", True, False, {"gamma": 0.1, "alpha": 0.03}),
    ("t", True, False, {"gamma": 0.1, "alpha": 0.03, "df": 7.0}),
    ("normal", False, True, {"mean": 0.0}),
]


@unittest.skipIf(arch_model is None, "arch is not installed")
class AgainstArch(unittest.TestCase):
    def test_fits_and_filters_like_arch(self):
        for distribution, asymmetric, zero_mean, kw in CASES:
            with self.subTest(distribution=distribution, asymmetric=asymmetric, zero_mean=zero_mean):
                ys = simulate(1500, 3, **kw)
                fit = fit_garch(ys, distribution=distribution, asymmetric=asymmetric, zero_mean=zero_mean,
                                horizon=5)
                ref = arch_model(np.array(ys), mean="Zero" if zero_mean else "Constant", vol="GARCH", p=1,
                                 o=1 if asymmetric else 0, q=1, dist="t" if distribution == "t" else "normal",
                                 rescale=False).fit(disp="off")
                self.assertGreaterEqual(fit.log_likelihood, ref.loglikelihood - 1e-6)
                # our filter at arch's parameters gives arch's volatility and forecasts
                p = ref.params
                v0 = backcast(ys if zero_mean else [y - sum(ys) / len(ys) for y in ys])
                gamma = p.get("gamma[1]", 0.0)
                model = GARCH(p["omega"], p["alpha[1]"], p["beta[1]"], gamma=gamma, mean=p.get("mu", 0.0),
                              distribution=distribution, df=p.get("nu"),
                              initial_variance=p["omega"] + (p["alpha[1]"] + 0.5 * gamma + p["beta[1]"]) * v0,
                              horizon=5)
                state, sigmas = model.initial_state(), []
                for y in ys:
                    state, out = model.step(state, {"r": y})
                    sigmas.append(out.sigma)
                self.assertLess(max(abs(a - b) for a, b in zip(sigmas, ref.conditional_volatility)), 1e-10)
                self.assertAlmostEqual(out.log_likelihood, ref.loglikelihood, delta=1e-7)
                forecast = ref.forecast(horizon=5, reindex=False).variance.values[-1]
                for ours, theirs in zip(out.forecast_sd, forecast):
                    self.assertAlmostEqual(ours * ours, theirs, delta=1e-10 * theirs)


class Filter(unittest.TestCase):
    def test_history_reproduces_the_fitted_likelihood(self):
        ys = simulate(800, 4, df=8.0)
        fit = fit_garch(ys, distribution="t")
        model = fit.model
        state = model.initial_state()
        for y in ys:
            state, out = model.step(state, {"r": y})
        self.assertAlmostEqual(out.log_likelihood, fit.log_likelihood, delta=1e-8)
        self.assertEqual(state, fit.state)
        p = fit.parameters
        self.assertAlmostEqual(fit.log_likelihood, garch_log_likelihood(ys, p["mean"], p["omega"], p["alpha"],
                                                                        p["beta"], p["gamma"], p["df"]), delta=1e-8)

    @unittest.skipIf(stats is None, "scipy is not installed")
    def test_densities(self):
        for e, v in ((0.3, 2.0), (-4.0, 0.5)):
            self.assertAlmostEqual(garch_log_density(e, v, None), stats.norm.logpdf(e, scale=math.sqrt(v)),
                                   delta=1e-12)
            for df in (3.5, 12.0):
                scale = math.sqrt(v * (df - 2.0) / df)
                self.assertAlmostEqual(garch_log_density(e, v, df), stats.t.logpdf(e, df, scale=scale), delta=1e-12)

    def test_forecasts_relax_to_the_unconditional_variance(self):
        model = GARCH(0.05, 0.08, 0.9, gamma=0.02, horizon=400)
        _, out = model.step(model.initial_state(), {"r": 3.0})
        v = 0.05 / (1.0 - 0.99)
        self.assertGreater(out.forecast_sd[0] ** 2, v)
        self.assertAlmostEqual(out.forecast_sd[-1] ** 2, v, delta=0.02 * v)
        self.assertAlmostEqual(out.cumulative_sd[2] ** 2, sum(s * s for s in out.forecast_sd[:3]), delta=1e-12)

    def test_intervals_cover_and_residuals_are_standard(self):
        for df in (None, 5.0):
            ys = simulate(20000, 5, df=df)
            model = GARCH(0.05, 0.08, 0.9, mean=0.03, distribution="t" if df else "normal", df=df, coverage=0.9)
            state, inside, zs = model.initial_state(), 0, []
            previous = None
            for y in ys:
                state, out = model.step(state, {"r": y})
                zs.append(out.z)
                if previous is not None:
                    inside += previous[0] <= y <= previous[1]
                previous = (out.lower[0], out.upper[0])
            self.assertAlmostEqual(inside / (len(ys) - 1), 0.9, delta=0.01)
            self.assertAlmostEqual(sum(z * z for z in zs) / len(zs), 1.0, delta=0.05)

    def test_refusals(self):
        for make in (lambda: GARCH(0.0, 0.1, 0.8), lambda: GARCH(0.1, -0.1, 0.8), lambda: GARCH(0.1, 0.3, 0.8),
                     lambda: GARCH(0.1, 0.1, 0.8, distribution="t"), lambda: GARCH(0.1, 0.1, 0.8, df=5.0),
                     lambda: GARCH(0.1, 0.1, 0.8, distribution="laplace")):
            with self.assertRaises(ValueError):
                make()
        self.assertEqual(GARCH(0.1, 0.3, 0.8, initial_variance=1.0).initial_state().variance, 1.0)
        with self.assertRaises(ValueError):
            fit_garch([0.0] * 30)


if __name__ == "__main__":
    unittest.main()
