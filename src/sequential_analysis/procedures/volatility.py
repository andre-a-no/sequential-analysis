# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""Volatility: the GARCH(1,1) filter, with an optional leverage term (GJR).

Returns r_t = mu + e_t with e_t = sigma_t z_t, the z_t independent with
mean 0 and variance 1 (normal, or Student t scaled to unit variance), and

    sigma^2_t = omega + alpha e^2_{t-1} + gamma e^2_{t-1} 1{e_{t-1} < 0} + beta sigma^2_{t-1}

(Bollerslev 1986; gamma > 0 is the leverage effect of Glosten, Jagannathan
and Runkle 1993: falls raise volatility more than rises).  Given the
parameters the filter is exact: sigma^2_t is known before r_t arrives, so
each step gives the one-step predictive density, the standardized residual
z_t (independent, unit variance under the model) and the forecast of the
next variances.  With persistence p = alpha + beta + gamma / 2 below 1,

    E[sigma^2_{t+h}] = v + p^(h-1) (sigma^2_{t+1} - v),   v = omega / (1 - p),

and the variance of the sum of the next h returns is the sum of these, as
the returns are uncorrelated.  The intervals for h > 1 use the predictive
law's shape with that variance: an approximation, as the h-step law is a
scale mixture.  Fit the parameters on a history with `fit_garch`, which
matches the arch package.

Cost per step (PERFORMANCE.md): constant, 6 microseconds with a 10-step forecast.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

from ..contracts import InputContract
from ..core import Procedure, decode_fields, require_state
from ..distributions import t_isf_log
from ..numerics import neumaier_add, require_finite
from .forecast import _check_coverage, _check_horizon

DISTRIBUTIONS = ("normal", "t")
_LOG_2PI = math.log(2.0 * math.pi)


def garch_log_density(error: float, variance: float, df: float | None) -> float:
    """Log density of a residual with the given variance: normal (df None) or unit-variance Student t."""
    if df is None:
        return -0.5 * (_LOG_2PI + math.log(variance) + error * error / variance)
    return (math.lgamma(0.5 * (df + 1.0)) - math.lgamma(0.5 * df) - 0.5 * math.log(math.pi * (df - 2.0))
            - 0.5 * math.log(variance) - 0.5 * (df + 1.0) * math.log1p(error * error / (variance * (df - 2.0))))


@dataclass(frozen=True)
class GARCHState:
    n: int
    variance: float  # sigma^2 of the next return
    log_likelihood: float = 0.0
    comp: float = 0.0


@dataclass(frozen=True)
class GARCHOutput:
    n: int
    sigma: float  # the conditional standard deviation this return was drawn with
    z: float  # standardized residual (r - mu) / sigma
    log_score: float
    log_likelihood: float
    forecast_sd: tuple[float, ...]  # conditional standard deviations of the next 1..horizon returns
    cumulative_sd: tuple[float, ...]  # standard deviation of the sum of the next 1..h returns
    lower: tuple[float, ...]  # central `coverage` interval of each of the next returns
    upper: tuple[float, ...]


class GARCH(Procedure):
    """GARCH(1,1) or GJR-GARCH(1,1) filter with fixed parameters; see the module docstring.

    `distribution` "normal" or "t" (with `df` > 2).  `initial_variance`
    is sigma^2 of the first return; None takes the unconditional variance,
    which needs persistence below 1.
    """

    name = "garch"
    version = "1"
    guarantee = "model"

    def __init__(self, omega: float, alpha: float, beta: float, *, gamma: float = 0.0, mean: float = 0.0,
                 distribution: str = "normal", df: float | None = None, initial_variance: float | None = None,
                 horizon: int = 1, coverage: float = 0.9, input: str = "r"):
        for name, v in (("omega", omega), ("mean", mean)):
            if not math.isfinite(v):
                raise ValueError(f"{name} must be finite")
        if not omega > 0.0:
            raise ValueError("omega must be positive")
        if not (alpha >= 0.0 and beta >= 0.0 and alpha + gamma >= 0.0 and math.isfinite(alpha + beta + gamma)):
            raise ValueError("need alpha >= 0, beta >= 0 and alpha + gamma >= 0")
        if distribution not in DISTRIBUTIONS:
            raise ValueError(f"distribution must be one of {DISTRIBUTIONS}")
        if distribution == "t":
            if df is None or not 2.0 < df < math.inf:
                raise ValueError("a Student t distribution needs df > 2")
        elif df is not None:
            raise ValueError("df is for the Student t distribution")
        self.omega, self.alpha, self.beta, self.gamma = float(omega), float(alpha), float(beta), float(gamma)
        self.mean, self.distribution = float(mean), distribution
        self.df = None if df is None else float(df)
        self.persistence = self.alpha + self.beta + 0.5 * self.gamma
        if initial_variance is None:
            if not self.persistence < 1.0:
                raise ValueError("without an initial_variance the persistence alpha + beta + gamma / 2 must be below 1")
            self.initial_variance = self.omega / (1.0 - self.persistence)
        else:
            if not 0.0 < initial_variance < math.inf:
                raise ValueError("initial_variance must be positive and finite")
            self.initial_variance = float(initial_variance)
        self.horizon, self.coverage, self.input = _check_horizon(horizon), _check_coverage(coverage), input
        tail = 0.5 * (1.0 - self.coverage)
        if self.df is None:
            self._q = -NormalDist().inv_cdf(tail)
        else:  # the t quantile, scaled to unit variance
            self._q = t_isf_log(math.log(tail), self.df) * math.sqrt((self.df - 2.0) / self.df)

    def config(self) -> dict:
        return {"omega": self.omega, "alpha": self.alpha, "beta": self.beta, "gamma": self.gamma, "mean": self.mean,
                "distribution": self.distribution, "df": self.df, "initial_variance": self.initial_variance,
                "horizon": self.horizon, "coverage": self.coverage, "input": self.input}

    def inputs(self):
        return {self.input: InputContract(self.input)}

    def initial_state(self) -> GARCHState:
        return GARCHState(0, self.initial_variance)

    def next_variance(self, variance: float, error: float) -> float:
        v = self.omega + self.alpha * error * error + self.beta * variance
        if error < 0.0:
            v += self.gamma * error * error
        return require_finite(v, "conditional variance")

    def forecast(self, variance: float) -> list[float]:
        """Expected conditional variances of the next 1..horizon returns, from sigma^2 of the next one."""
        out = [variance]
        for _ in range(1, self.horizon):
            out.append(self.omega + self.persistence * out[-1])
        return out

    def step(self, state: GARCHState, x, rng=None):
        r = float(x[self.input])
        error = r - self.mean
        sigma = math.sqrt(state.variance)
        score = garch_log_density(error, state.variance, self.df)
        log_lik, comp = neumaier_add(state.log_likelihood, state.comp, score)
        variance = self.next_variance(state.variance, error)
        new = GARCHState(state.n + 1, variance, log_lik, comp)
        ahead = self.forecast(variance)
        sds = tuple(math.sqrt(v) for v in ahead)
        cumulative, total = [], 0.0
        for v in ahead:
            total += v
            cumulative.append(math.sqrt(total))
        lower = tuple(self.mean - self._q * s for s in sds)
        upper = tuple(self.mean + self._q * s for s in sds)
        return new, GARCHOutput(new.n, sigma, error / sigma, score, log_lik, sds, tuple(cumulative), lower, upper)

    def decode_state(self, data) -> GARCHState:
        state = decode_fields(GARCHState, data)
        require_state(state.variance > 0.0, "the variance must be positive")
        return state
