# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""Streams of events: self-exciting arrivals and the market's reaction to events.

HawkesProcess is the exact filter of a Hawkes process with exponential
kernel, the standard model of arrivals that come in bursts (news that
breeds news, trades that breed trades):

    lambda(t) = mu + sum over events t_i < t of alpha exp(-beta (t - t_i)),

baseline mu, each event raising the intensity by alpha, the excess decaying
at rate beta; n = alpha / beta is the branching ratio, the expected number
of events each event triggers (n < 1 for a stationary process).  The
excess decays geometrically between events, so the intensity, the
log-likelihood

    sum_i log lambda(t_i-) - integral of lambda from start to the last event,

and the compensator of each gap, the integral of lambda over it, are
updated exactly in constant time per event (Ozaki 1979).  Under the model
the compensators are independent standard exponentials (time rescaling,
Brown et al. 2002): a monitor of them -- a QuantileEDetector, say --
detects when the process stops behaving as fitted.  The expected number
of events in the next `window` time units, with all the cascades they
trigger, is exact: the mean intensity relaxes to mu / (1 - n) at rate
beta - alpha.  Fit the parameters on a history with `fit_hawkes`.

EventStudy measures how a series moves after events: for each event, the
cumulative sum of the next `horizon` values of r (abnormal returns: the
return minus what the market explains, e.g. the error of a
DynamicRegression on the market) at 1..horizon steps, averaged over
events with an asymptotic confidence sequence for each horizon (as in
AsymptoticConfidenceSequence, at level alpha / horizon each, so that all
horizons hold together).  It assumes the events' reactions are
independent with a common mean: with `overlap="skip"` (the default) an
event inside the window of the previous one is skipped and counted, so
that no two windows share a value; with "allow" they may, and the
intervals are then too narrow when reactions overlap.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from ..contracts import InputContract
from ..core import Procedure, decode_fields, require_state
from ..errors import ContractViolation
from ..numerics import neumaier_add, require_finite

# ------------------------------------------------------------------------------------------ Hawkes


@dataclass(frozen=True)
class HawkesState:
    n: int
    last: float  # time of the last event (start before the first)
    excess: float  # lambda - mu just after the last event
    log_likelihood: float = 0.0
    comp: float = 0.0


@dataclass(frozen=True)
class HawkesOutput:
    n: int
    intensity: float  # just after this event
    intensity_before: float  # just before it: the rate at which it came
    compensator: float  # integral of the intensity over the gap before it; Exp(1) under the model
    log_score: float  # log lambda(t-) - compensator: this event's term of the log-likelihood
    log_likelihood: float
    expected: float | None  # expected events in the next `window` time units (None without a window)


class HawkesProcess(Procedure):
    """Exact filter of an exponential-kernel Hawkes process; see the module docstring.

    Each step is one event, its time under `input`; times must not
    decrease.  `start` is when observation began (the log-likelihood
    counts the quiet time before the first event).
    """

    name = "hawkes_process"
    version = "1"
    guarantee = "model"

    def __init__(self, baseline: float, excitation: float, decay: float, *, start: float = 0.0,
                 window: float | None = None, input: str = "t"):
        for name, v in (("baseline", baseline), ("decay", decay)):
            if not 0.0 < v < math.inf:
                raise ValueError(f"{name} must be positive and finite")
        if not 0.0 <= excitation < decay:
            raise ValueError("excitation must lie in [0, decay): a branching ratio below 1")
        if not math.isfinite(start):
            raise ValueError("start must be finite")
        if window is not None and not 0.0 < window < math.inf:
            raise ValueError("window must be positive and finite, or None")
        self.baseline, self.excitation, self.decay = float(baseline), float(excitation), float(decay)
        self.start, self.window, self.input = float(start), None if window is None else float(window), input

    @property
    def branching(self) -> float:
        return self.excitation / self.decay

    def config(self) -> dict:
        return {"baseline": self.baseline, "excitation": self.excitation, "decay": self.decay,
                "start": self.start, "window": self.window, "input": self.input}

    def inputs(self):
        return {self.input: InputContract(self.input)}

    def initial_state(self) -> HawkesState:
        return HawkesState(0, self.start, 0.0)

    def intensity_at(self, state: HawkesState, t: float) -> float:
        """The intensity at time t >= the last event, if no event came in between."""
        if t < state.last:
            raise ValueError("t is before the last event")
        return self.baseline + state.excess * math.exp(-self.decay * (t - state.last))

    def expected_events(self, intensity: float, window: float) -> float:
        """Expected events in the next `window` time units from current intensity, cascades included."""
        rate = self.decay - self.excitation
        mean = self.baseline * self.decay / rate
        return mean * window + (intensity - mean) * -math.expm1(-rate * window) / rate

    def step(self, state: HawkesState, x, rng=None):
        t = x[self.input]
        if t < state.last:
            raise ContractViolation(f"input {self.input!r}: event time {t} is before the previous one ({state.last})")
        gap = t - state.last
        decay = math.exp(-self.decay * gap)
        before = state.excess * decay
        compensator = self.baseline * gap + state.excess * -math.expm1(-self.decay * gap) / self.decay
        intensity_before = self.baseline + before
        score = math.log(intensity_before) - compensator
        log_lik, comp = neumaier_add(state.log_likelihood, state.comp, score)
        excess = require_finite(before + self.excitation, "intensity")
        new = HawkesState(state.n + 1, float(t), excess, log_lik, comp)
        intensity = self.baseline + excess
        expected = None if self.window is None else self.expected_events(intensity, self.window)
        return new, HawkesOutput(new.n, intensity, intensity_before, compensator, score, log_lik, expected)

    def decode_state(self, data) -> HawkesState:
        state = decode_fields(HawkesState, data)
        require_state(state.excess >= 0 and state.last >= self.start, "the excess intensity and the last time")
        require_state(state.n > 0 or (state.excess == 0 and state.last == self.start), "an excess without events")
        return state


# -------------------------------------------------------------------------------------- event study


@dataclass(frozen=True)
class EventStudyState:
    n: int  # steps seen
    active: tuple[tuple[float, ...], ...]  # open windows: cumulative sums so far, oldest window first
    events: int  # completed windows
    skipped: int  # events skipped because a window was open
    mean: tuple[float, ...]  # per horizon h = 1..H, over completed windows
    m2: tuple[float, ...]


@dataclass(frozen=True)
class EventStudyOutput:
    n: int
    events: int
    skipped: int
    open: int
    mean: tuple[float, ...] | None  # average cumulative reaction at 1..horizon steps; None before any event
    lower: tuple[float, ...] | None  # confidence sequence per horizon, None before `start` events
    upper: tuple[float, ...] | None


class EventStudy(Procedure):
    """Average cumulative reaction of r over the `horizon` steps after an event; see the module docstring.

    Inputs: `returns` (a real number, the abnormal return of the step) and
    `event` (1 if an event happened at this step).  A window opens at the
    event's step and collects r from the next step on.  The interval for
    horizon h holds, asymptotically and at all times together with the
    others, with probability 1 - alpha; there is none before `start` events
    (`tuned_for` as in AsymptoticConfidenceSequence).
    """

    name = "event_study"
    version = "1"
    guarantee = "asymptotic"

    def __init__(self, horizon: int = 5, *, alpha: float = 0.05, start: int = 30, tuned_for: float = 100.0,
                 overlap: str = "skip", returns: str = "r", event: str = "event"):
        if type(horizon) is not int or horizon < 1:
            raise ValueError("horizon must be a positive int")
        if not 0.0 < alpha < 1.0:
            raise ValueError("alpha must lie in (0, 1)")
        if type(start) is not int or start < 2:
            raise ValueError("start must be an int, at least 2")
        if not (math.isfinite(tuned_for) and tuned_for >= 1):
            raise ValueError("tuned_for must be a number of events, at least 1")
        if overlap not in ("skip", "allow"):
            raise ValueError('overlap must be "skip" or "allow"')
        if not (returns and event) or returns == event:
            raise ValueError("returns and event must be two distinct input names")
        self.horizon, self.alpha, self.start, self.tuned_for = horizon, float(alpha), start, float(tuned_for)
        self.overlap, self.returns, self.event = overlap, returns, event
        self._level = self.alpha / horizon
        c = -2.0 * math.log(self._level)
        self._rho2 = (c + math.log1p(c)) / self.tuned_for

    def config(self) -> dict:
        return {"horizon": self.horizon, "alpha": self.alpha, "start": self.start, "tuned_for": self.tuned_for,
                "overlap": self.overlap, "returns": self.returns, "event": self.event}

    def inputs(self):
        return {self.returns: InputContract(self.returns), self.event: InputContract(self.event, kind="binary")}

    def initial_state(self) -> EventStudyState:
        zeros = (0.0,) * self.horizon
        return EventStudyState(0, (), 0, 0, zeros, zeros)

    def half_width(self, n: int, sd: float) -> float:
        v = n * self._rho2 + 1.0
        return sd * math.sqrt(2.0 * v / (n * n * self._rho2) * (0.5 * math.log(v) - math.log(self._level)))

    def step(self, state: EventStudyState, x, rng=None):
        r, happened = float(x[self.returns]), x[self.event] == 1
        events, mean, m2 = state.events, list(state.mean), list(state.m2)
        active = []
        for window in state.active:
            cum = (*window, require_finite((window[-1] if window else 0.0) + r, "cumulative return"))
            if len(cum) < self.horizon:
                active.append(cum)
                continue
            events += 1
            frac = (events - 1) / events
            for h, v in enumerate(cum):
                delta = v - mean[h]
                mean[h] += delta / events
                m2[h] += frac * delta * delta  # Welford's delta (v - new mean), never negative
        skipped = state.skipped
        if happened:
            if self.overlap == "skip" and active:
                skipped += 1
            else:
                active.append(())
        new = EventStudyState(state.n + 1, tuple(active), events, skipped, tuple(mean), tuple(m2))
        return new, self._output(new)

    def _output(self, state: EventStudyState) -> EventStudyOutput:
        if state.events == 0:
            return EventStudyOutput(state.n, 0, state.skipped, len(state.active), None, None, None)
        lower = upper = None
        if state.events >= self.start and all(v > 0.0 for v in state.m2):
            hs = [self.half_width(state.events, math.sqrt(v / (state.events - 1))) for v in state.m2]
            lower = tuple(m - h for m, h in zip(state.mean, hs))
            upper = tuple(m + h for m, h in zip(state.mean, hs))
        return EventStudyOutput(state.n, state.events, state.skipped, len(state.active), state.mean, lower, upper)

    def decode_state(self, data) -> EventStudyState:
        state = decode_fields(EventStudyState, data)
        h = self.horizon
        require_state(len(state.mean) == h and len(state.m2) == h and all(v >= 0 for v in state.m2),
                      "one mean and sum of squares per horizon")
        require_state(all(len(w) < h for w in state.active) and len(state.active) <= h,
                      "open windows shorter than the horizon")
        require_state(self.overlap == "allow" or len(state.active) <= 1, "overlapping windows")
        require_state(state.events >= 0 and state.skipped >= 0, "event counts")
        return state
