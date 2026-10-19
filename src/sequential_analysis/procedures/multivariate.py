# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""Several series at once: vector autoregression, lead-lag correlations, regression on drifting coefficients.

VectorAutoRegressive forecasts d series jointly from the last p values of
all of them,

    y_t = c + A_1 y_{t-1} + ... + A_p y_{t-p} + e_t,   e_t ~ N(0, Sigma),

so that one series' past can move another's forecast.  With fixed
coefficients and Sigma (from `fit_var`) the forecasts are Gaussian.
Learnt online, the coefficients and Sigma have the conjugate
normal-inverse-Wishart posterior with exponential forgetting lambda: the
data's information decays by lambda per step, the ridge prior on the
coefficients does not.  With x_t = (1, y_{t-1}, ..., y_{t-p}),
M = lambda X'X + ridge I, nu the discounted number of observations and S
the discounted scatter of the one-step errors, the next value has the
multivariate Student t predictive with nu' = lambda nu - d + 1 degrees of
freedom and scale matrix (1 + x' M^-1 x) lambda S / nu' -- exact under the
model.  The recursion is

    nu <- lambda nu + 1,   S <- lambda S + e e' / (1 + x' M^-1 x),

the multivariate form of AutoRegressive's (with d = 1 the two are the same
model).  Forecasts h > 1 steps ahead iterate the point forecast and add
the variance the errors propagate, Psi_i Sigma Psi_i', to the one-step
variance: a plug-in approximation, as in AutoRegressive.

CrossCorrelation tracks the correlation of a_t with b_{t-l} for every lag
l from -L to L, with exponential forgetting: a positive lag with a large
correlation says that b leads a by l steps.  It describes; it does not
test.  Test a lead with an AnytimeLinearModel of a on its own lags and the
lags of b, under Lagged (an anytime-valid Granger test), and with many
pairs and lags control the false discoveries with OnlineFDR.

DynamicRegression regresses y on regressors with coefficients that drift
as a random walk -- the hedge ratio of a pair of assets, a time-varying
beta.  It is the dynamic linear model with discount factor delta and an
unknown observation variance learnt alongside (West and Harrison 1997,
sections 4.5 and 6.3): the coefficients' covariance is inflated by 1/delta
before each observation, and the one-step forecast of y is Student t.  The
state holds the precision (the inverse covariance), updated as
delta P + f f', a sum of positive semi-definite terms: the covariance
form loses tiny variances to cancellation when a regressor is huge.  Its
standardized forecast error z is the spread signal of pairs trading.

Cost per step (PERFORMANCE.md): VectorAutoRegressive is O(k^3 + k^2 d) for
k = 1 + d p coefficients per series; CrossCorrelation O(L);
DynamicRegression O(k^3) in its k coefficients.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import NormalDist

from .. import linalg as la
from ..contracts import InputContract
from ..core import Procedure, decode_fields, require_state
from ..distributions import t_isf_log
from ..numerics import neumaier_add, require_finite
from .forecast import (
    _accumulate,
    _backward,
    _check_coverage,
    _check_horizon,
    _check_learning,
    _cholesky_floor,
    _forward,
    _quad,
    log_density,
)

_LOG_PI = math.log(math.pi)


def _names(names: Sequence[str], what: str) -> tuple[str, ...]:
    out = tuple(names)
    if not out or not all(isinstance(n, str) and n for n in out) or len(set(out)) != len(out):
        raise ValueError(f"{what} must be distinct non-empty strings")
    return out


def _strict_cholesky(a) -> la.Matrix | None:
    try:
        return la.cholesky(a)
    except ValueError:
        return None


def multivariate_t_log_density(error: Sequence[float], low: la.Matrix, df: float | None) -> float:
    """Log density at `error` from the location of a normal (df None) or Student t law with scale L L'."""
    d = len(error)
    z = _forward(low, error)
    q = 0.0
    log_det = 0.0
    for i in range(d):
        q += z[i] * z[i]
        log_det += math.log(low[i][i])
    if df is None:
        return -0.5 * d * math.log(2.0 * math.pi) - log_det - 0.5 * q
    return (math.lgamma(0.5 * (df + d)) - math.lgamma(0.5 * df) - 0.5 * d * (math.log(df) + _LOG_PI) - log_det
            - 0.5 * (df + d) * math.log1p(q / df))


# ------------------------------------------------------------------------------------------ VAR


@dataclass(frozen=True)
class VectorAutoRegressiveState:
    n: int
    lags: tuple[tuple[float, ...], ...]  # the most recent vectors, newest first (fewer than p at the start)
    information: tuple[tuple[float, ...], ...]  # k x k, sum of lambda^(n-t) x_t x_t'; () with fixed coefficients
    moment: tuple[tuple[float, ...], ...]  # k x d, sum of lambda^(n-t) x_t y_t'
    dof: float  # nu, the discounted number of one-step errors
    scatter: tuple[tuple[float, ...], ...]  # d x d, S
    log_likelihood: float = 0.0
    comp: float = 0.0


@dataclass(frozen=True)
class VectorAutoRegressiveOutput:
    n: int
    forecast: tuple[tuple[float, ...], ...] | None  # for 1..horizon steps ahead, one value per series
    scale: tuple[tuple[float, ...], ...] | None  # the forecasts' standard deviations (scales for Student t)
    lower: tuple[tuple[float, ...], ...] | None  # central `coverage` interval of each series, step by step
    upper: tuple[tuple[float, ...], ...] | None
    error: tuple[float, ...] | None  # this observation minus its one-step forecast
    log_score: float | None  # log predictive density of this observation
    log_likelihood: float  # sum of the log scores


class VectorAutoRegressive(Procedure):
    """VAR(p) forecasts of several series, with fixed coefficients or learnt online; see the module docstring.

    `series` names the inputs, one number each per step.  For fixed
    training give `coefficients` -- p matrices, `coefficients[j][i][k]` the
    effect of series k at lag j + 1 on series i -- with `intercept` and the
    noise `covariance`.  Leave them out to learn them, with `forgetting`
    and `ridge` as in AutoRegressive.
    """

    name = "vector_autoregressive"
    version = "1"
    guarantee = "model"

    def __init__(self, series: Sequence[str], order: int, *,
                 coefficients: Sequence[Sequence[Sequence[float]]] | None = None,
                 intercept: Sequence[float] | None = None, covariance: Sequence[Sequence[float]] | None = None,
                 forgetting: float = 1.0, ridge: float = 1e-6, horizon: int = 1, coverage: float = 0.9):
        self.series = _names(series, "series")
        d = self.d = len(self.series)
        if type(order) is not int or order < 1:
            raise ValueError("order must be a positive int")
        self.order = order
        self.k = 1 + d * order
        if coefficients is not None:
            if intercept is None or covariance is None:
                raise ValueError("fixed coefficients need an intercept and a covariance")
            if forgetting != 1.0 or ridge != 1e-6:
                raise ValueError("forgetting and ridge are for learnt coefficients")
            if len(coefficients) != order:
                raise ValueError("need one coefficient matrix per lag")
            self.coefficients: tuple[la.Matrix, ...] | None = tuple(
                la.matrix(a, d, d, "coefficients") for a in coefficients)
            self.intercept: la.Vector | None = la.vector(intercept, d, "intercept")
            cov = la.matrix(covariance, d, d, "covariance")
            if not la.is_symmetric(cov) or _strict_cholesky(cov) is None:
                raise ValueError("the covariance must be symmetric positive definite")
            self.covariance: la.Matrix | None = cov
        else:
            if intercept is not None or covariance is not None:
                raise ValueError("intercept and covariance come with fixed coefficients")
            _check_learning(forgetting, ridge)
            self.coefficients = self.intercept = self.covariance = None
        self.forgetting, self.ridge = float(forgetting), float(ridge)
        self.horizon, self.coverage = _check_horizon(horizon), _check_coverage(coverage)

    def config(self) -> dict:
        out: dict = {"series": list(self.series), "order": self.order, "coefficients": None, "intercept": None,
                     "covariance": None}
        if self.coefficients is not None and self.intercept is not None and self.covariance is not None:
            out["coefficients"] = [[list(r) for r in a] for a in self.coefficients]
            out["intercept"] = list(self.intercept)
            out["covariance"] = [list(r) for r in self.covariance]
        return {**out,
                "forgetting": self.forgetting, "ridge": self.ridge, "horizon": self.horizon,
                "coverage": self.coverage}

    def inputs(self):
        return {s: InputContract(s) for s in self.series}

    def initial_state(self) -> VectorAutoRegressiveState:
        d, k = self.d, self.k
        if self.coefficients is not None:
            return VectorAutoRegressiveState(0, (), (), (), 0.0, ())
        return VectorAutoRegressiveState(0, (), tuple((0.0,) * k for _ in range(k)),
                                         tuple((0.0,) * d for _ in range(k)), 0.0,
                                         tuple((0.0,) * d for _ in range(d)))

    def _design(self, lags) -> list[float]:
        u = [1.0]
        for v in lags:
            u.extend(v)
        return u

    def _theta(self, state: VectorAutoRegressiveState):
        """(k x d coefficient matrix by rows of the design, Cholesky factor of M or None)."""
        if self.coefficients is not None:
            assert self.intercept is not None
            theta = [list(self.intercept)]
            for a in self.coefficients:
                for k in range(self.d):
                    theta.append([a[i][k] for i in range(self.d)])
            return theta, None
        lam = self.forgetting
        precision = [[lam * state.information[i][j] + (self.ridge if i == j else 0.0) for j in range(self.k)]
                     for i in range(self.k)]
        low = _cholesky_floor(precision)
        columns = [_backward(low, _forward(low, [lam * state.moment[r][i] for r in range(self.k)]))
                   for i in range(self.d)]
        return [[columns[i][r] for i in range(self.d)] for r in range(self.k)], low

    def _point(self, theta, u: Sequence[float]) -> list[float]:
        out = []
        for i in range(self.d):
            total = 0.0
            for r in range(self.k):
                total += theta[r][i] * u[r]
            out.append(total)
        return out

    def _noise(self, state: VectorAutoRegressiveState):
        """(scale matrix Sigma, degrees of freedom or None), or None while it is not yet defined."""
        if self.covariance is not None:
            return self.covariance, None
        lam = self.forgetting
        df = lam * state.dof - self.d + 1.0
        if not df > 0.0:
            return None
        sigma = tuple(tuple(lam * state.scatter[i][j] / df for j in range(self.d)) for i in range(self.d))
        if _strict_cholesky(sigma) is None:
            return None
        return sigma, df

    def step(self, state: VectorAutoRegressiveState, x, rng=None):
        y = tuple(float(x[s]) for s in self.series)
        lags = ((y, *state.lags))[: self.order]
        log_lik, comp = state.log_likelihood, state.comp
        if len(state.lags) < self.order:
            new = VectorAutoRegressiveState(state.n + 1, lags, state.information, state.moment, state.dof,
                                            state.scatter, log_lik, comp)
            return new, self._output(new, None, None)
        u = self._design(state.lags)
        theta, low = self._theta(state)
        error = tuple(a - b for a, b in zip(y, self._point(theta, u)))
        s = 1.0 if low is None else 1.0 + _quad(low, u)
        noise = self._noise(state)
        score = None
        if noise is not None:
            sigma, df = noise
            factor = _strict_cholesky(la.scale(sigma, s))
            if factor is not None:
                score = multivariate_t_log_density(error, factor, df)
                log_lik, comp = neumaier_add(log_lik, comp, score)
        if self.coefficients is not None:
            new = VectorAutoRegressiveState(state.n + 1, lags, (), (), 0.0, (), log_lik, comp)
            return new, self._output(new, error, score)
        lam = self.forgetting
        information = _accumulate(state.information, (0.0,) * self.k, u, 0.0, lam)[0]
        moment = tuple(tuple(require_finite(lam * state.moment[r][i] + u[r] * y[i], "moment")
                             for i in range(self.d)) for r in range(self.k))
        scatter = tuple(tuple(require_finite(lam * state.scatter[i][j] + error[i] * error[j] / s, "scatter")
                              for j in range(self.d)) for i in range(self.d))
        new = VectorAutoRegressiveState(state.n + 1, lags, information, moment, lam * state.dof + 1.0, scatter,
                                        log_lik, comp)
        return new, self._output(new, error, score)

    def _quantile(self, df: float | None) -> float:
        tail = 0.5 * (1.0 - self.coverage)
        return -NormalDist().inv_cdf(tail) if df is None else t_isf_log(math.log(tail), df)

    def _output(self, state: VectorAutoRegressiveState, error, score) -> VectorAutoRegressiveOutput:
        forecast = self.forecast(state)
        if forecast is None:
            return VectorAutoRegressiveOutput(state.n, None, None, None, None, error, score, state.log_likelihood)
        mean, scale, df = forecast
        q = self._quantile(df)
        lower = tuple(tuple(m - q * v for m, v in zip(ms, ss)) for ms, ss in zip(mean, scale))
        upper = tuple(tuple(m + q * v for m, v in zip(ms, ss)) for ms, ss in zip(mean, scale))
        return VectorAutoRegressiveOutput(state.n, mean, scale, lower, upper, error, score, state.log_likelihood)

    def forecast(self, state: VectorAutoRegressiveState):
        """(means, standard deviations, degrees of freedom or None) for 1..horizon steps, or None."""
        if len(state.lags) < self.order:
            return None
        noise = self._noise(state)
        if noise is None:
            return None
        sigma, df = noise
        theta, low = self._theta(state)
        d, p = self.d, self.order
        extra = 0.0 if low is None else _quad(low, self._design(state.lags))
        # A_j[i][k] from theta, for the error propagation Psi_h = sum_j A_j Psi_{h-j}
        a = [tuple(tuple(theta[1 + j * d + k][i] for k in range(d)) for i in range(d)) for j in range(p)]
        psi = [la.identity(d)]
        history = list(state.lags)
        total = la.scale(sigma, extra)
        means, scales = [], []
        for h in range(1, self.horizon + 1):
            value = tuple(self._point(theta, self._design(history)))
            means.append(value)
            history = [value, *history[:-1]]
            total = la.add(total, la.quadratic(psi[h - 1], sigma))
            scales.append(tuple(math.sqrt(total[i][i]) for i in range(d)))
            nxt = tuple((0.0,) * d for _ in range(d))
            for j in range(1, min(h, p) + 1):
                nxt = la.add(nxt, la.matmul(a[j - 1], psi[h - j]))
            psi.append(nxt)
        return tuple(means), tuple(scales), df

    def parameters(self, state: VectorAutoRegressiveState) -> dict:
        """The intercept, the coefficient matrices and the noise scale matrix the next forecast uses."""
        if self.coefficients is not None:
            return {"intercept": list(self.intercept or ()), "coefficients": [[list(r) for r in a]
                                                                             for a in self.coefficients],
                    "covariance": [list(r) for r in self.covariance or ()]}
        if len(state.lags) < self.order:
            return {"intercept": None, "coefficients": None, "covariance": None}
        theta, _ = self._theta(state)
        d = self.d
        noise = self._noise(state)
        return {"intercept": list(theta[0]),
                "coefficients": [[[theta[1 + j * d + k][i] for k in range(d)] for i in range(d)]
                                 for j in range(self.order)],
                "covariance": None if noise is None else [list(r) for r in noise[0]]}

    def decode_state(self, data) -> VectorAutoRegressiveState:
        state = decode_fields(VectorAutoRegressiveState, data)
        require_state(len(state.lags) == min(state.n, self.order) and all(len(v) == self.d for v in state.lags),
                      "one lag vector per observation, up to the order")
        if self.coefficients is not None:
            require_state(state.information == state.moment == state.scatter == () and state.dof == 0,
                          "learnt statistics with fixed coefficients")
        else:
            k, d = self.k, self.d
            require_state(len(state.information) == k and all(len(r) == k for r in state.information)
                          and len(state.moment) == k and all(len(r) == d for r in state.moment)
                          and len(state.scatter) == d and all(len(r) == d for r in state.scatter),
                          "statistics' sizes")
            require_state(la.is_symmetric(state.information) and la.is_symmetric(state.scatter)
                          and all(state.information[i][i] >= 0 for i in range(k))
                          and all(state.scatter[i][i] >= 0 for i in range(d)) and state.dof >= 0,
                          "statistics must be symmetric with non-negative diagonals")
        return state

    def encode_output(self, output: VectorAutoRegressiveOutput):
        def rows(v):
            return None if v is None else [list(r) for r in v]
        return {"n": output.n, "forecast": rows(output.forecast), "scale": rows(output.scale),
                "lower": rows(output.lower), "upper": rows(output.upper),
                "error": None if output.error is None else list(output.error), "log_score": output.log_score,
                "log_likelihood": output.log_likelihood}


# -------------------------------------------------------------------------------- lead and lag


@dataclass(frozen=True)
class CrossCorrelationState:
    n: int
    past_a: tuple[float, ...]  # newest first, up to max_lag values
    past_b: tuple[float, ...]
    stats: tuple[tuple[float, ...], ...]  # per lag -L..L: (w, w2, mean_a, mean_b, caa, cbb, cab)


@dataclass(frozen=True)
class CrossCorrelationOutput:
    n: int
    lags: tuple[int, ...]  # -L..L
    correlations: tuple[float | None, ...]  # corr(a_t, b_{t-lag}); None until defined
    pairs: tuple[float, ...]  # effective number of pairs behind each, (sum w)^2 / sum w^2
    lead: int | None  # the lag with the largest |correlation|; positive: b leads a
    correlation: float | None  # its correlation


class CrossCorrelation(Procedure):
    """Correlations of a_t with b_{t-lag} for lags -max_lag..max_lag, with optional forgetting.

    `forgetting` lambda in (0, 1] weights a pair lag steps old by lambda^age
    (1: plain correlations).  Descriptive only: see the module docstring
    for how to test a lead.
    """

    name = "cross_correlation"
    version = "1"
    guarantee = "none"

    def __init__(self, a: str = "a", b: str = "b", *, max_lag: int = 5, forgetting: float = 1.0):
        if not (isinstance(a, str) and a and isinstance(b, str) and b) or a == b:
            raise ValueError("a and b must be two distinct non-empty input names")
        if type(max_lag) is not int or max_lag < 0:
            raise ValueError("max_lag must be a non-negative int")
        if not 0.0 < forgetting <= 1.0:
            raise ValueError("forgetting must lie in (0, 1]")
        self.a, self.b, self.max_lag, self.forgetting = a, b, max_lag, float(forgetting)

    def config(self) -> dict:
        return {"a": self.a, "b": self.b, "max_lag": self.max_lag, "forgetting": self.forgetting}

    def inputs(self):
        return {self.a: InputContract(self.a), self.b: InputContract(self.b)}

    def initial_state(self) -> CrossCorrelationState:
        return CrossCorrelationState(0, (), (), tuple((0.0,) * 7 for _ in range(2 * self.max_lag + 1)))

    def _update(self, s: tuple[float, ...], a: float, b: float) -> tuple[float, ...]:
        lam = self.forgetting
        w, w2, ma, mb, caa, cbb, cab = s
        w = lam * w + 1.0
        w2 = lam * lam * w2 + 1.0
        da, db = a - ma, b - mb
        ma += da / w
        mb += db / w
        frac = (w - 1.0) / w  # the old weight's share: lambda w_old / w
        caa = lam * caa + frac * da * da
        cbb = lam * cbb + frac * db * db
        cab = lam * cab + frac * da * db
        return tuple(require_finite(v, "cross moments") for v in (w, w2, ma, mb, caa, cbb, cab))

    def step(self, state: CrossCorrelationState, x, rng=None):
        a, b = float(x[self.a]), float(x[self.b])
        big = self.max_lag
        stats = list(state.stats)
        for idx in range(2 * big + 1):
            lag = idx - big
            if lag >= 0 and len(state.past_b) >= lag:
                stats[idx] = self._update(stats[idx], a, b if lag == 0 else state.past_b[lag - 1])
            elif lag < 0 and len(state.past_a) >= -lag:
                stats[idx] = self._update(stats[idx], state.past_a[-lag - 1], b)
        new = CrossCorrelationState(state.n + 1, ((a, *state.past_a))[:big], ((b, *state.past_b))[:big],
                                    tuple(stats))
        return new, self.summary(new)

    def summary(self, state: CrossCorrelationState) -> CrossCorrelationOutput:
        lags = tuple(range(-self.max_lag, self.max_lag + 1))
        corrs: list[float | None] = []
        pairs = []
        lead = best = None
        for lag, (w, w2, _ma, _mb, caa, cbb, cab) in zip(lags, state.stats):
            pairs.append(w * w / w2 if w2 > 0 else 0.0)
            r = None
            if caa > 0.0 and cbb > 0.0:
                r = max(-1.0, min(1.0, cab / math.sqrt(caa * cbb)))
                if best is None or abs(r) > abs(best):
                    lead, best = lag, r
            corrs.append(r)
        return CrossCorrelationOutput(state.n, lags, tuple(corrs), tuple(pairs), lead, best)

    def decode_state(self, data) -> CrossCorrelationState:
        state = decode_fields(CrossCorrelationState, data)
        m = min(state.n, self.max_lag)
        require_state(len(state.past_a) == m and len(state.past_b) == m, "the past, up to max_lag values")
        require_state(len(state.stats) == 2 * self.max_lag + 1 and all(len(s) == 7 for s in state.stats),
                      "one set of moments per lag")
        require_state(all(s[0] >= 0 and s[1] >= 0 and s[4] >= 0 and s[5] >= 0 for s in state.stats),
                      "weights and sums of squares must be non-negative")
        return state


# ------------------------------------------------------------------- regression, drifting coefficients


@dataclass(frozen=True)
class DynamicRegressionState:
    n: int
    mean: tuple[float, ...]  # posterior mean of the coefficients (intercept first)
    precision: tuple[tuple[float, ...], ...]  # inverse of their covariance, in units of the observation variance
    dof: float  # discounted number of observations behind the variance estimate
    sum_squares: float  # discounted sum of standardized squared errors
    log_likelihood: float = 0.0
    comp: float = 0.0


@dataclass(frozen=True)
class DynamicRegressionOutput:
    n: int
    coefficients: tuple[float, ...]  # after this observation (intercept first)
    sd: tuple[float, ...] | None  # their posterior standard deviations, once the variance is estimated
    error: float  # y minus its one-step forecast from the coefficients before this observation
    scale: float | None  # that forecast's scale (Student t)
    z: float | None  # error / scale: the standardized spread
    log_score: float | None
    log_likelihood: float


class DynamicRegression(Procedure):
    """Regression of y on `regressors` with coefficients that drift; see the module docstring.

    `discount` delta in (0, 1]: the coefficients' covariance grows by 1/delta
    per step (1: fixed coefficients, recursive least squares; 0.99 lets them
    move by about a tenth of their uncertainty per step).
    `variance_discount` does the same for the noise variance.  The prior is
    centred at 0 with covariance `prior_scale` times the noise variance.
    """

    name = "dynamic_regression"
    version = "1"
    guarantee = "model"

    def __init__(self, regressors: Sequence[str] = ("x",), *, discount: float = 0.99, variance_discount: float = 1.0,
                 intercept: bool = True, prior_scale: float = 1e4, input: str = "y"):
        self.regressors = _names(regressors, "regressors")
        if input in self.regressors or not (isinstance(input, str) and input):
            raise ValueError("input must be a non-empty name, not one of the regressors")
        if not 0.0 < discount <= 1.0 or not 0.0 < variance_discount <= 1.0:
            raise ValueError("discounts must lie in (0, 1]")
        if not 0.0 < prior_scale < math.inf:
            raise ValueError("prior_scale must be positive and finite")
        if type(intercept) is not bool:
            raise ValueError("intercept must be True or False")
        self.discount, self.variance_discount = float(discount), float(variance_discount)
        self.intercept, self.prior_scale, self.input = intercept, float(prior_scale), input
        self.k = len(self.regressors) + (1 if intercept else 0)

    def config(self) -> dict:
        return {"regressors": list(self.regressors), "discount": self.discount,
                "variance_discount": self.variance_discount, "intercept": self.intercept,
                "prior_scale": self.prior_scale, "input": self.input}

    def inputs(self):
        names = (self.input, *self.regressors)
        return {n: InputContract(n) for n in names}

    def initial_state(self) -> DynamicRegressionState:
        k = self.k
        prec = tuple(tuple(1.0 / self.prior_scale if i == j else 0.0 for j in range(k)) for i in range(k))
        return DynamicRegressionState(0, (0.0,) * k, prec, 0.0, 0.0)

    def step(self, state: DynamicRegressionState, x, rng=None):
        k = self.k
        f = ([1.0] if self.intercept else []) + [float(x[r]) for r in self.regressors]
        y = float(x[self.input])
        # the prior precision delta P, the inverse of R = C / delta; Rf and q = f'Rf + 1 from its Cholesky factor
        low = _cholesky_floor([[self.discount * state.precision[i][j] for j in range(k)] for i in range(k)])
        q = 1.0 + _quad(low, f)
        rf = _backward(low, _forward(low, f))
        error = y - la.dot(f, state.mean)
        lam = self.variance_discount
        scale = z = score = None
        log_lik, comp = state.log_likelihood, state.comp
        if state.dof > 0.0 and state.sum_squares > 0.0:
            df = lam * state.dof
            scale = math.sqrt(state.sum_squares / state.dof * q)
            z = error / scale
            score = log_density(error, scale, df)
            log_lik, comp = neumaier_add(log_lik, comp, score)
        mean = tuple(require_finite(m + g / q * error, "coefficients") for m, g in zip(state.mean, rf))
        # information form: delta P + f f' is a sum of positive semi-definite matrices, so no cancellation
        prec = tuple(tuple(require_finite(self.discount * state.precision[i][j] + f[i] * f[j], "precision")
                           for j in range(k)) for i in range(k))
        dof = lam * state.dof + 1.0
        ss = require_finite(lam * state.sum_squares + error * error / q, "sum of squares")
        new = DynamicRegressionState(state.n + 1, mean, prec, dof, ss, log_lik, comp)
        sd = None
        if ss > 0.0:
            v = ss / dof
            low = _cholesky_floor(prec)
            sd = tuple(math.sqrt(_quad(low, [1.0 if j == i else 0.0 for j in range(k)]) * v) for i in range(k))
        return new, DynamicRegressionOutput(new.n, mean, sd, error, scale, z, score, log_lik)

    def decode_state(self, data) -> DynamicRegressionState:
        state = decode_fields(DynamicRegressionState, data)
        k = self.k
        require_state(len(state.mean) == k and len(state.precision) == k
                      and all(len(r) == k for r in state.precision), "one coefficient per regressor")
        require_state(la.is_symmetric(state.precision) and all(state.precision[i][i] > 0 for i in range(k)),
                      "the precision must be symmetric with a positive diagonal")
        require_state(state.dof >= 0 and state.sum_squares >= 0, "variance statistics")
        return state
