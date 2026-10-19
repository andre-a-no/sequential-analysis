# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""Fitting and simulating Hawkes processes (see procedures.events.HawkesProcess).

`fit_hawkes` finds the maximum-likelihood baseline, excitation and decay
of an exponential-kernel Hawkes process from the event times observed on
[start, end].  The log-likelihood is computed exactly in O(n) by the
recursion of the filter; it is maximized by Nelder-Mead over
(log mu, logit n, log beta), with the branching ratio n = alpha / beta kept
in (0, 1), started from the best of a small grid.

`simulate_hawkes` draws event times by Ogata's thinning, deterministically
from a seed: for examples and tests.
"""
from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .forecasting import _logit, _sigmoid, nelder_mead
from .procedures.events import HawkesProcess


@dataclass(frozen=True)
class HawkesFit:
    model: HawkesProcess  # the fitted filter
    state: Any  # its state after the last event
    log_likelihood: float  # of the events on [start, end]
    aic: float
    parameters: dict  # baseline, excitation, decay, branching
    evaluations: int


def hawkes_log_likelihood(times: Sequence[float], baseline: float, excitation: float, decay: float,
                          start: float, end: float) -> float:
    """Exact log-likelihood of event times on [start, end] under an exponential-kernel Hawkes process."""
    total, last, excess = 0.0, start, 0.0
    for t in times:
        gap = t - last
        before = excess * math.exp(-decay * gap)
        total += math.log(baseline + before) - baseline * gap - excess * -math.expm1(-decay * gap) / decay
        excess, last = before + excitation, t
    gap = end - last
    return total - baseline * gap - excess * -math.expm1(-decay * gap) / decay


def fit_hawkes(times: Sequence[float], *, start: float | None = None, end: float | None = None,
               window: float | None = None, input: str = "t", max_evaluations: int = 2000) -> HawkesFit:
    """Maximum-likelihood exponential-kernel Hawkes process; see the module docstring.

    `start` and `end` bound the observation period (default: the first and
    last event).  The result's model filters the events from `start` on;
    run it on to continue live.
    """
    ts = [float(t) for t in times]
    if len(ts) < 3:
        raise ValueError("need at least three events")
    if not all(math.isfinite(t) for t in ts) or any(b < a for a, b in zip(ts, ts[1:])):
        raise ValueError("event times must be finite and non-decreasing")
    t0 = ts[0] if start is None else float(start)
    t1 = ts[-1] if end is None else float(end)
    if ts[0] < t0 or ts[-1] > t1 or not t1 > t0:
        raise ValueError("the events must lie in [start, end], a non-empty period")
    rate = len(ts) / (t1 - t0)

    def unpack(u: Sequence[float]) -> tuple[float, float, float]:
        beta = math.exp(u[2])
        return math.exp(u[0]), beta * _sigmoid(u[1]), beta

    def objective(u: Sequence[float]) -> float:
        if not all(abs(v) < 50.0 for v in u):
            return math.inf
        mu, alpha, beta = unpack(u)
        value = -hawkes_log_likelihood(ts, mu, alpha, beta, t0, t1)
        return value if math.isfinite(value) else math.inf

    starts: list[tuple[float, int, list[float]]] = []
    for n in (0.2, 0.5, 0.8):
        for scale in (0.1, 1.0, 10.0):
            u = [math.log(rate * (1.0 - n)), _logit(n), math.log(scale * rate)]
            starts.append((objective(u), len(starts), u))
    starts.sort()
    evaluations = len(starts)
    best_u, best = starts[0][2], starts[0][0]
    for _, _, u in starts[:3]:
        x, value, used = nelder_mead(objective, u, max_evaluations=max_evaluations)
        x, value, more = nelder_mead(objective, x, step=0.1, max_evaluations=max_evaluations)
        evaluations += used + more
        if value < best:
            best_u, best = x, value
    mu, alpha, beta = unpack(best_u)
    model = HawkesProcess(mu, alpha, beta, start=t0, window=window, input=input)
    state = model.initial_state()
    for t in ts:
        state, _ = model.step(state, {input: t})
    log_lik = -best
    parameters = {"baseline": mu, "excitation": alpha, "decay": beta, "branching": alpha / beta}
    return HawkesFit(model, state, log_lik, 6.0 - 2.0 * log_lik, parameters, evaluations)


def simulate_hawkes(baseline: float, excitation: float, decay: float, end: float, *, start: float = 0.0,
                    seed: int = 0) -> list[float]:
    """Event times on [start, end] by Ogata's thinning (Python's random.Random(seed))."""
    if not (0.0 < baseline and 0.0 <= excitation < decay) or not end > start:
        raise ValueError("need baseline > 0, 0 <= excitation < decay and end > start")
    rnd = random.Random(seed)
    out: list[float] = []
    t, excess = start, 0.0  # excess intensity at time t
    while True:
        bound = baseline + excess  # the intensity only decreases until the next event
        gap = rnd.expovariate(bound)
        excess *= math.exp(-decay * gap)
        t += gap
        if t > end:
            return out
        if rnd.random() * bound <= baseline + excess:
            out.append(t)
            excess += excitation
