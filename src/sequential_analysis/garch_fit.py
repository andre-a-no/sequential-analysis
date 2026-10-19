# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""Fitting GARCH(1,1) and GJR-GARCH(1,1) to a history of returns (see procedures.volatility).

`fit_garch` maximizes the Gaussian or Student t likelihood as the arch
package does: residuals r_t - mu, the recursion started from the backcast
v0 = sum_i w_i e_i^2 over the first min(75, n) residuals with weights
proportional to 0.94^i, so that sigma^2_1 = omega + (alpha + gamma / 2 + beta) v0.
As in arch, v0 is computed once, from the residuals around the sample
mean (or 0 with `zero_mean`), and held fixed while mu varies.
The parameters are found by Nelder-Mead over mu, log omega, the
persistence p = alpha + beta + gamma / 2 in (0, 1) (logit) and its split
between the terms (softmax), and log(df - 2) for Student t, from the best
of a small grid.  The fitted GARCH procedure starts from that sigma^2_1, so
a run over the history reproduces the fitted likelihood and continues
live from `state`.
"""
from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from .forecasting import _logit, _sigmoid, _values, nelder_mead
from .procedures.volatility import DISTRIBUTIONS, GARCH, garch_log_density


@dataclass(frozen=True)
class GARCHFit:
    model: GARCH  # the fitted filter, from the first return of the history
    state: Any  # its state after the history
    log_likelihood: float
    aic: float
    parameters: dict  # mean, omega, alpha, beta, gamma, df, persistence, unconditional_variance
    backcast: float
    evaluations: int


def backcast(residuals: Sequence[float]) -> float:
    """arch's starting value: an exponentially weighted mean of the first min(75, n) squared residuals."""
    tau = min(75, len(residuals))
    weights = [0.94 ** i for i in range(tau)]
    total = 0.0
    for w in weights:
        total += w
    value = 0.0
    for w, e in zip(weights, residuals):
        value += w / total * e * e
    return value


def garch_log_likelihood(returns: Sequence[float], mean: float, omega: float, alpha: float, beta: float,
                         gamma: float = 0.0, df: float | None = None, v0: float | None = None) -> float:
    """The log-likelihood arch maximizes: Gaussian (df None) or unit-variance Student t, from the backcast v0.

    v0 defaults to the backcast of the residuals around the sample mean, as arch computes it.
    """
    residuals = [r - mean for r in returns]
    if v0 is None:
        centre = 0.0
        for r in returns:
            centre += r
        v0 = backcast([r - centre / len(returns) for r in returns])
    variance = omega + (alpha + 0.5 * gamma + beta) * v0
    total = 0.0
    for e in residuals:
        total += garch_log_density(e, variance, df)
        variance = omega + alpha * e * e + beta * variance + (gamma * e * e if e < 0.0 else 0.0)
    return total


def fit_garch(inputs: Iterable[Any], *, distribution: str = "normal", asymmetric: bool = False,
              zero_mean: bool = False, input: str = "r", horizon: int = 1, coverage: float = 0.9,
              max_evaluations: int = 4000) -> GARCHFit:
    """Maximum-likelihood GARCH(1,1), or GJR-GARCH(1,1) with `asymmetric`; see the module docstring."""
    if distribution not in DISTRIBUTIONS:
        raise ValueError(f"distribution must be one of {DISTRIBUTIONS}")
    returns = _values(list(inputs), input)
    n = len(returns)
    if n < 20:
        raise ValueError("need at least 20 returns")
    student = distribution == "t"
    centre = 0.0
    if not zero_mean:
        for r in returns:
            centre += r
        centre /= n
    var = 0.0
    for r in returns:
        var += (r - centre) * (r - centre)
    var /= n
    if not var > 0.0:
        raise ValueError("the returns are constant")
    terms = 3 if asymmetric else 2
    v0 = backcast([r - centre for r in returns])

    def unpack(u: Sequence[float]):
        k = 0
        mu = 0.0
        if not zero_mean:
            mu, k = u[0] * math.sqrt(var) + centre, 1
        omega = math.exp(u[k]) * var
        p = _sigmoid(u[k + 1])
        logits = [0.0, *u[k + 2:k + 1 + terms]]
        m = max(logits)
        shares = [math.exp(v - m) for v in logits]
        s = sum(shares)
        shares = [v / s for v in shares]
        alpha, beta = p * shares[0], p * shares[-1]
        gamma = 2.0 * p * shares[1] if asymmetric else 0.0
        df = 2.0 + math.exp(u[k + 1 + terms]) if student else None
        return mu, omega, alpha, beta, gamma, df

    def objective(u: Sequence[float]) -> float:
        if not all(abs(v) < 40.0 for v in u):
            return math.inf
        mu, omega, alpha, beta, gamma, df = unpack(u)
        try:
            value = -garch_log_likelihood(returns, mu, omega, alpha, beta, gamma, df, v0)
        except (ValueError, OverflowError, ZeroDivisionError):
            return math.inf
        return value if math.isfinite(value) else math.inf

    starts: list[tuple[float, int, list[float]]] = []
    for p in (0.9, 0.97, 0.995):
        for a in (0.05, 0.12):
            for g in ((0.0, 0.1) if asymmetric else (None,)):
                for nu in ((5.0, 10.0) if student else (None,)):
                    alpha, gamma = a, (g or 0.0)
                    beta = p - alpha - 0.5 * gamma
                    if beta <= 0.0:
                        continue
                    u = [] if zero_mean else [0.0]
                    u += [math.log(1.0 - p), _logit(p)]
                    u += [math.log(0.5 * gamma / alpha) if asymmetric and gamma > 0 else -3.0] if asymmetric else []
                    u += [math.log(beta / alpha)]
                    if nu is not None:
                        u.append(math.log(nu - 2.0))
                    starts.append((objective(u), len(starts), u))
    starts.sort()
    evaluations = len(starts)
    best_u, best = starts[0][2], starts[0][0]
    for _, _, start in starts[:4]:
        x, value, used = nelder_mead(objective, start, max_evaluations=max_evaluations)
        x, value, more = nelder_mead(objective, x, step=0.1, max_evaluations=max_evaluations)
        evaluations += used + more
        if value < best:
            best_u, best = x, value
    mu, omega, alpha, beta, gamma, df = unpack(best_u)
    model = GARCH(omega, alpha, beta, gamma=gamma, mean=mu, distribution=distribution, df=df,
                  initial_variance=omega + (alpha + 0.5 * gamma + beta) * v0, horizon=horizon, coverage=coverage,
                  input=input)
    state = model.initial_state()
    for r in returns:
        state, _ = model.step(state, {input: r})
    persistence = alpha + beta + 0.5 * gamma
    parameters = {"mean": mu, "omega": omega, "alpha": alpha, "beta": beta, "gamma": gamma, "df": df,
                  "persistence": persistence,
                  "unconditional_variance": omega / (1.0 - persistence) if persistence < 1.0 else None}
    k = (0 if zero_mean else 1) + 1 + terms + (1 if student else 0)
    return GARCHFit(model, state, -best, 2.0 * k + 2.0 * best, parameters, v0, evaluations)
