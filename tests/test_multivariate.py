# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""Several series: vector autoregression, lead-lag correlations, regression on drifting coefficients.

* VectorAutoRegressive with one series is AutoRegressive, forgetting
  included; learnt with several, its coefficients are the ridge regression
  and its scatter the batch residual scatter Y'Y - B'MB (the conjugate
  identity), and its one-step density is the multivariate t (scipy).
* fit_var reproduces statsmodels' VAR: coefficients, the ML covariance,
  the log-likelihood, the order chosen by AIC, the forecasts and their
  variances (up to statsmodels' degrees-of-freedom correction).
* CrossCorrelation equals the batch (weighted) correlation at every lag
  and finds the lag by which one series leads the other.
* DynamicRegression with discount 1 is the batch Bayesian regression; with
  a discount it equals an information-form implementation of the West and
  Harrison recursions, and it tracks a drifting coefficient.
"""
import math
import random
import unittest

from sequential_analysis.forecasting import fit_var
from sequential_analysis.procedures import (
    AutoRegressive,
    CrossCorrelation,
    DynamicRegression,
    VectorAutoRegressive,
)
from sequential_analysis.procedures.multivariate import multivariate_t_log_density

try:
    import numpy as np
    from statsmodels.tsa.api import VAR
except ImportError:  # optional reference
    VAR = None

try:
    from scipy.stats import multivariate_t
except ImportError:  # optional reference
    multivariate_t = None


def solve(a, b):
    """Gaussian elimination with partial pivoting."""
    n = len(a)
    m = [list(row) for row in a]
    for row, v in zip(m, b):
        row.append(v)
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(m[r][i]))
        m[i], m[p] = m[p], m[i]
        for r in range(i + 1, n):
            f = m[r][i] / m[i][i]
            for c in range(i, n + 1):
                m[r][c] -= f * m[i][c]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (m[i][n] - sum(m[i][c] * x[c] for c in range(i + 1, n))) / m[i][i]
    return x


def var_rows(n, seed, d=2):
    rnd = random.Random(seed)
    rows = [[0.0] * d, [0.0] * d]
    for _ in range(n - 2):
        a, b = rows[-1], rows[-2]
        new = [0.2 + 0.5 * a[0] + 0.3 * a[1 % d] - 0.2 * b[d - 1] + rnd.gauss(0.0, 1.0)]
        for i in range(1, d):
            new.append(-0.1 + 0.1 * a[0] + 0.4 * a[i] + 0.2 * b[0] + rnd.gauss(0.0, 1.0))
        rows.append(new)
    return rows


class VectorAutoRegression(unittest.TestCase):
    def test_one_series_is_autoregressive(self):
        rnd = random.Random(3)
        ys = [0.0]
        for _ in range(300):
            ys.append(0.5 + 0.6 * ys[-1] + rnd.gauss(0.0, 1.0))
        for forgetting in (1.0, 0.97):
            v = VectorAutoRegressive(("y",), 2, forgetting=forgetting, horizon=3)
            a = AutoRegressive(2, forgetting=forgetting, horizon=3)
            sv, sa = v.initial_state(), a.initial_state()
            for y in ys:
                sv, ov = v.step(sv, {"y": y})
                sa, oa = a.step(sa, {"y": y})
                self.assertEqual(ov.forecast is None, oa.mean == ())
                if ov.forecast is not None:
                    for h in range(3):
                        self.assertAlmostEqual(ov.forecast[h][0], oa.mean[h], delta=1e-12)
                        self.assertAlmostEqual(ov.scale[h][0], oa.scale[h], delta=1e-12)
                        self.assertAlmostEqual(ov.lower[h][0], oa.lower[h], delta=1e-10)
                self.assertAlmostEqual(ov.log_likelihood, oa.log_likelihood, delta=1e-9)

    def test_learnt_statistics_are_the_batch_posterior(self):
        rows = var_rows(120, 4)
        ridge = 0.5
        model = VectorAutoRegressive(("a", "b"), 2, ridge=ridge)
        state = model.initial_state()
        for r in rows:
            state, _ = model.step(state, {"a": r[0], "b": r[1]})
        xs = [[1.0, *rows[t - 1], *rows[t - 2]] for t in range(2, len(rows))]  # novermin (not PEP 798)
        ys = rows[2:]
        k = 5
        m = [[sum(x[i] * x[j] for x in xs) + (ridge if i == j else 0.0) for j in range(k)] for i in range(k)]
        theta = [solve(m, [sum(x[i] * y[c] for x, y in zip(xs, ys)) for i in range(k)]) for c in range(2)]
        p = model.parameters(state)
        self.assertAlmostEqual(p["intercept"][1], theta[1][0], delta=1e-10)
        for j in range(2):
            for i in range(2):
                for c in range(2):
                    self.assertAlmostEqual(p["coefficients"][j][i][c], theta[i][1 + 2 * j + c], delta=1e-10)
        # S = Y'Y - B' M B with B the posterior mean: the conjugate identity behind the recursion
        for i in range(2):
            for j in range(2):
                yy = sum(y[i] * y[j] for y in ys)
                bmb = sum(theta[i][r] * m[r][s] * theta[j][s] for r in range(k) for s in range(k))
                self.assertAlmostEqual(state.scatter[i][j], yy - bmb, delta=1e-8 * abs(yy))
        self.assertEqual(state.dof, len(ys))

    @unittest.skipIf(multivariate_t is None, "scipy is not installed")
    def test_multivariate_t_density(self):
        from sequential_analysis import linalg as la
        scale = ((2.0, 0.3, 0.1), (0.3, 1.0, -0.2), (0.1, -0.2, 0.5))
        low = la.cholesky(scale)
        for df, e in ((3.0, (0.5, -1.0, 0.2)), (40.5, (2.0, 0.0, -1.0))):
            ref = multivariate_t(loc=[0, 0, 0], shape=scale, df=df).logpdf(e)
            self.assertAlmostEqual(multivariate_t_log_density(e, low, df), ref, delta=1e-12)

    def test_cross_effects_move_forecasts(self):
        # b leads a: the learnt VAR forecasts a from b's past better than an AR on a alone
        rnd = random.Random(8)
        b = [rnd.gauss(0.0, 1.0) for _ in range(800)]
        a = [0.0] + [0.8 * b[t - 1] + rnd.gauss(0.0, 0.5) for t in range(1, 800)]
        v, ar = VectorAutoRegressive(("a", "b"), 1), AutoRegressive(1)
        sv, sa = v.initial_state(), ar.initial_state()
        joint = alone = 0.0
        for t, (x, y) in enumerate(zip(a, b)):
            sv, ov = v.step(sv, {"a": x, "b": y})
            sa, oa = ar.step(sa, {"y": x})
            if t >= 50:
                joint += ov.error[0] ** 2
                alone += oa.error ** 2
        self.assertLess(joint, 0.4 * alone)  # one-step errors of a: 0.5^2 against 0.8^2 + 0.5^2
        self.assertAlmostEqual(v.parameters(sv)["coefficients"][0][0][1], 0.8, delta=0.05)

    def test_refusals(self):
        for make in (lambda: VectorAutoRegressive((), 1), lambda: VectorAutoRegressive(("a", "a"), 1),
                     lambda: VectorAutoRegressive(("a",), 0),
                     lambda: VectorAutoRegressive(("a",), 1, coefficients=[[[0.5]]]),
                     lambda: VectorAutoRegressive(("a",), 1, coefficients=[[[0.5]]], intercept=[0.0],
                                                  covariance=[[-1.0]]),
                     lambda: VectorAutoRegressive(("a",), 1, forgetting=0.0)):
            with self.assertRaises(ValueError):
                make()


@unittest.skipIf(VAR is None, "statsmodels is not installed")
class FitVAR(unittest.TestCase):
    def test_matches_statsmodels(self):
        rows = var_rows(300, 7, d=3)
        records = [{"a": r[0], "b": r[1], "c": r[2]} for r in rows]
        y = np.array(rows)
        fit = fit_var(records, ("a", "b", "c"), max_order=6)
        order = fit.parameters["order"]
        self.assertEqual(order, VAR(y).select_order(6).selected_orders["aic"])
        res = VAR(y).fit(order, trend="c")
        self.assertLess(np.max(np.abs(np.array(fit.parameters["coefficients"]) - res.coefs)), 1e-10)
        self.assertLess(np.max(np.abs(np.array(fit.parameters["intercept"]) - res.intercept)), 1e-10)
        self.assertLess(np.max(np.abs(np.array(fit.parameters["covariance"]) - res.sigma_u_mle)), 1e-10)
        self.assertAlmostEqual(fit.log_likelihood, res.llf, delta=1e-8)
        model = VectorAutoRegressive(("a", "b", "c"), order, coefficients=fit.parameters["coefficients"],
                                     intercept=fit.parameters["intercept"],
                                     covariance=fit.parameters["covariance"], horizon=4)
        mean, scale, df = model.forecast(fit.state)
        self.assertIsNone(df)
        self.assertLess(np.max(np.abs(np.array(mean) - res.forecast(y[-order:], 4))), 1e-10)
        # statsmodels' forecast variances use sigma_u = SSR / (T - k); ours the ML SSR / T
        correction = (res.nobs - res.df_model) / res.nobs
        ref = np.array([np.diag(c) for c in res.forecast_cov(4)]) * correction
        self.assertLess(np.max(np.abs(np.array(scale) ** 2 - ref)), 1e-10)

    def test_too_short(self):
        with self.assertRaises(ValueError):
            fit_var([{"a": 1.0, "b": 2.0}] * 3, ("a", "b"), 2)


def weighted_correlation(pairs, lam):
    n = len(pairs)
    w = [lam ** (n - 1 - i) for i in range(n)]
    sw = sum(w)
    ma = sum(wi * a for wi, (a, _) in zip(w, pairs)) / sw
    mb = sum(wi * b for wi, (_, b) in zip(w, pairs)) / sw
    caa = sum(wi * (a - ma) ** 2 for wi, (a, _) in zip(w, pairs))
    cbb = sum(wi * (b - mb) ** 2 for wi, (_, b) in zip(w, pairs))
    cab = sum(wi * (a - ma) * (b - mb) for wi, (a, b) in zip(w, pairs))
    return cab / math.sqrt(caa * cbb), sw * sw / sum(wi * wi for wi in w)


class LeadLag(unittest.TestCase):
    def test_equals_batch_correlations(self):
        rnd = random.Random(5)
        b = [rnd.gauss(0.0, 1.0) for _ in range(300)]
        a = [0.0, 0.0] + [0.7 * b[t - 2] + rnd.gauss(0.0, 0.7) for t in range(2, 300)]
        for lam in (1.0, 0.98):
            model = CrossCorrelation(max_lag=3, forgetting=lam)
            state = model.initial_state()
            for x, y in zip(a, b):
                state, out = model.step(state, {"a": x, "b": y})
            for lag, r, pairs in zip(out.lags, out.correlations, out.pairs):
                if lag >= 0:
                    data = [(a[t], b[t - lag]) for t in range(lag, len(a))]
                else:
                    data = [(a[t + lag], b[t]) for t in range(-lag, len(a))]
                ref, n_eff = weighted_correlation(data, lam)
                self.assertAlmostEqual(r, ref, delta=1e-12)
                self.assertAlmostEqual(pairs, n_eff, delta=1e-9 * n_eff)
            self.assertEqual(out.lead, 2)

    def test_undefined_until_variance(self):
        model = CrossCorrelation(max_lag=1)
        _, out = model.step(model.initial_state(), {"a": 1.0, "b": 2.0})
        self.assertEqual(out.correlations, (None, None, None))
        self.assertIsNone(out.lead)

    def test_refusals(self):
        for make in (lambda: CrossCorrelation("a", "a"), lambda: CrossCorrelation(max_lag=-1),
                     lambda: CrossCorrelation(forgetting=1.5)):
            with self.assertRaises(ValueError):
                make()


def west_harrison(rows, discount, prior_scale, lam):
    """The same model in information form, written independently: C^-1 = R^-1 + f f'."""
    k = len(rows[0][0])
    m = [0.0] * k
    c = [[prior_scale if i == j else 0.0 for j in range(k)] for i in range(k)]
    dof = ss = 0.0
    out = []
    for f, y in rows:
        r = [[v / discount for v in row] for row in c]
        e = y - sum(fi * mi for fi, mi in zip(f, m))
        q = 1.0 + sum(f[i] * r[i][j] * f[j] for i in range(k) for j in range(k))
        z = e / math.sqrt(ss / dof * q) if dof > 0 else None
        r_inv = [solve(r, [1.0 if i == j else 0.0 for i in range(k)]) for j in range(k)]
        info = [[r_inv[i][j] + f[i] * f[j] for j in range(k)] for i in range(k)]
        c = [solve(info, [1.0 if i == j else 0.0 for i in range(k)]) for j in range(k)]
        rhs = [sum(r_inv[i][j] * m[j] for j in range(k)) + f[i] * y for i in range(k)]
        m = solve(info, rhs)
        dof, ss = lam * dof + 1.0, lam * ss + e * e / q
        out.append((tuple(m), z))
    return out


class DriftingRegression(unittest.TestCase):
    def rows(self, n, seed):
        rnd = random.Random(seed)
        beta, out = 1.0, []
        for _ in range(n):
            beta += rnd.gauss(0.0, 0.02)
            x = rnd.gauss(0.0, 1.0)
            out.append((x, 0.5 + beta * x + rnd.gauss(0.0, 0.3), beta))
        return out

    def test_matches_information_form(self):
        data = self.rows(150, 2)
        for discount, lam in ((1.0, 1.0), (0.97, 0.99)):
            model = DynamicRegression(discount=discount, variance_discount=lam, prior_scale=100.0)
            ref = west_harrison([((1.0, x), y) for x, y, _ in data], discount, 100.0, lam)
            state = model.initial_state()
            for (x, y, _), (m, z) in zip(data, ref):
                state, out = model.step(state, {"x": x, "y": y})
                for a, b in zip(out.coefficients, m):
                    self.assertAlmostEqual(a, b, delta=1e-9)
                if z is None:
                    self.assertIsNone(out.z)
                else:
                    self.assertAlmostEqual(out.z, z, delta=1e-9)

    def test_discount_one_is_batch_regression(self):
        data = self.rows(80, 3)
        model = DynamicRegression(discount=1.0, prior_scale=50.0)
        state = model.initial_state()
        for x, y, _ in data:
            state, out = model.step(state, {"x": x, "y": y})
        gram = [[sum(1.0 for _ in data) + 1 / 50.0, sum(x for x, _, _ in data)],
                [sum(x for x, _, _ in data), sum(x * x for x, _, _ in data) + 1 / 50.0]]
        theta = solve(gram, [sum(y for _, y, _ in data), sum(x * y for x, y, _ in data)])
        for a, b in zip(out.coefficients, theta):
            self.assertAlmostEqual(a, b, delta=1e-10)

    def test_tracks_a_drifting_coefficient(self):
        data = self.rows(2000, 4)
        model = DynamicRegression(discount=0.98)
        state = model.initial_state()
        errors, zs = [], []
        for x, y, beta in data:
            state, out = model.step(state, {"x": x, "y": y})
            errors.append(abs(out.coefficients[1] - beta))
            if out.z is not None:
                zs.append(out.z)
        self.assertLess(sum(errors[500:]) / len(errors[500:]), 0.12)
        late = zs[200:]
        self.assertAlmostEqual(sum(z * z for z in late) / len(late), 1.0, delta=0.25)  # a roughly calibrated spread

    def test_refusals(self):
        for make in (lambda: DynamicRegression(()), lambda: DynamicRegression(("y",)),
                     lambda: DynamicRegression(discount=0.0), lambda: DynamicRegression(prior_scale=0.0)):
            with self.assertRaises(ValueError):
                make()


if __name__ == "__main__":
    unittest.main()
