# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""Composition.  A chain of procedures is itself a procedure; nothing inherits from "Pipeline".

Chain feeds the outputs of one procedure into another.  Lagged feeds a
procedure the recent past of some inputs: with lags {"x": 2} it receives,
besides its own inputs, x_lag1 = the value of x one step ago and x_lag2 =
two steps ago.  The past is part of the state, so it is checkpointed and
restored with everything else.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from .contracts import InputContract, validate_input
from .core import Procedure, StatInput, require_state
from .errors import ContractViolation
from .transforms import identity_of


@dataclass(frozen=True)
class ChainOutput:
    first: Any
    second: Any


class Chain(Procedure):
    """Feed the outputs of `first` into `second`.

    `link` maps an output of `first` to a statistical input of `second`, or
    returns None when there is nothing to pass on for this step.  The chain
    is terminal as soon as either stage is.

    If `link` fails, or produces an input that violates the contract of
    `second`, the step raises ContractViolation and neither stage advances:
    the run handles the whole input X_t by its `on_invalid` policy.
    """

    def __init__(
        self,
        first: Procedure,
        second: Procedure,
        link: Callable[[Any], StatInput | None],
        link_name: str | None = None,
    ):
        self.first, self.second, self.link = first, second, link
        self.link_identity = identity_of(link, link_name)
        self.link_name = link_name or self.link_identity["name"]
        self.name = f"chain({first.name},{second.name})"
        self.version = f"{first.version}+{second.version}"
        self.randomized = first.randomized or second.randomized
        self.joint_inputs = first.joint_inputs

    def config(self) -> dict:
        return {"first": self.first.identity(), "second": self.second.identity(), "link": self.link_identity}

    def inputs(self) -> Mapping[str, InputContract]:
        return self.first.inputs()

    def initial_state(self):
        return (self.first.initial_state(), self.second.initial_state())

    def step(self, state, x, rng):
        s1, s2 = state
        s1, o1 = self.first.step(s1, x, rng)
        o2 = None
        try:
            x2 = self.link(o1)
        except Exception as error:  # as a failing transform in a topology: this input is invalid
            raise ContractViolation(
                f"link {self.link_name!r} failed on the output of {self.first.name}: {type(error).__name__}: {error}"
            ) from error
        if x2 is not None and not self.second.is_terminal(s2):
            try:
                validate_input(self.second, x2)
            except ContractViolation as violation:
                raise ContractViolation(
                    f"{self.second.name} (second stage, via {self.link_name!r}): {violation}"
                ) from violation
            s2, o2 = self.second.step(s2, x2, rng)
        return (s1, s2), ChainOutput(o1, o2)

    def is_terminal(self, state) -> bool:
        return self.first.is_terminal(state[0]) or self.second.is_terminal(state[1])

    def encode_state(self, state):
        return {"first": self.first.encode_state(state[0]), "second": self.second.encode_state(state[1])}

    def decode_state(self, data):
        return (self.first.decode_state(data["first"]), self.second.decode_state(data["second"]))

    def encode_output(self, output):
        return {
            "first": self.first.encode_output(output.first),
            "second": None if output.second is None else self.second.encode_output(output.second),
        }


@dataclass(frozen=True)
class LaggedState:
    n: int
    past: tuple[tuple[float, ...], ...]  # per source, in the order of `lags`: the latest values, newest first
    inner: Any


@dataclass(frozen=True)
class LaggedOutput:
    ready: bool  # False while some source has fewer past values than its lags; the inner procedure waits
    inner: Any


def lag_name(source: str, lag: int) -> str:
    """The name of an input's value `lag` steps ago, as Lagged passes it on."""
    return f"{source}_lag{lag}"


class Lagged(Procedure):
    """Run `inner` with the recent past of some inputs as extra inputs.

    `lags` maps each source input to a number of lags k: the inner
    procedure gets source_lag1, ..., source_lagk, the source's values one
    to k steps ago (`lag_name`), and must declare them as inputs.  Its
    other inputs pass through unchanged; a source need not be one of them.
    The first steps, before every source has k past values, only fill the
    past: the inner procedure does not step and the output is not ready.

    A typical use is a test of whether one series leads another: an
    AnytimeLinearModel of y on its own lags (nuisance) and the lags of x
    (tested) is an anytime-valid Granger test.  The guarantee is the inner
    procedure's.
    """

    name = "lagged"
    version = "1"

    def __init__(self, inner: Procedure, lags: Mapping[str, int]):
        if not isinstance(lags, Mapping) or not lags:
            raise ValueError("lags must map at least one input name to a number of lags")
        for source, k in lags.items():
            if not (isinstance(source, str) and source):
                raise ValueError("lag sources must be non-empty strings")
            if type(k) is not int or k < 1:
                raise ValueError(f"the number of lags of {source!r} must be a positive int")
        if not inner.joint_inputs:
            raise ValueError("the inner procedure must take all its inputs in every step")
        self.inner, self.lags = inner, {s: lags[s] for s in sorted(lags)}
        contracts = inner.inputs()
        self._generated = [lag_name(s, j) for s, k in self.lags.items() for j in range(1, k + 1)]
        missing = [n for n in self._generated if n not in contracts]
        if missing:
            raise ValueError(f"{inner.name} does not take the lagged inputs {missing}")
        clash = [s for s in self.lags if s in self._generated]
        if clash:
            raise ValueError(f"a source is named like a lag: {clash}")
        self._contracts = {n: c for n, c in contracts.items() if n not in self._generated}
        for s in self.lags:
            if s not in self._contracts:
                self._contracts[s] = InputContract(s)
            elif self._contracts[s].shape != ():
                raise ValueError(f"source {s!r} must be a scalar input")
        self.randomized = inner.randomized
        self.guarantee = inner.guarantee

    def config(self) -> dict:
        return {"inner": self.inner.identity(), "lags": dict(self.lags)}

    def inputs(self) -> Mapping[str, InputContract]:
        return self._contracts

    def initial_state(self) -> LaggedState:
        return LaggedState(0, tuple(() for _ in self.lags), self.inner.initial_state())

    def step(self, state: LaggedState, x, rng=None):
        ready = all(len(p) == k for p, k in zip(state.past, self.lags.values()))
        inner, out = state.inner, None
        if ready:
            x2 = {n: x[n] for n in self.inner.inputs() if n not in self._generated}
            for p, (s, k) in zip(state.past, self.lags.items()):
                for j in range(k):
                    x2[lag_name(s, j + 1)] = p[j]
            validate_input(self.inner, x2)
            inner, out = self.inner.step(state.inner, x2, rng)
        past = tuple((float(x[s]), *p)[:k] for p, (s, k) in zip(state.past, self.lags.items()))
        return LaggedState(state.n + 1, past, inner), LaggedOutput(ready, out)

    def is_terminal(self, state: LaggedState) -> bool:
        return self.inner.is_terminal(state.inner)

    def encode_state(self, state: LaggedState):
        return {"n": state.n, "past": {s: list(p) for s, p in zip(self.lags, state.past)},
                "inner": self.inner.encode_state(state.inner)}

    def decode_state(self, data) -> LaggedState:
        require_state(isinstance(data, Mapping) and set(data) == {"n", "past", "inner"}, "a lagged state")
        n, past = data["n"], data["past"]
        require_state(type(n) is int and n >= 0, "the step count")
        require_state(isinstance(past, Mapping) and set(past) == set(self.lags), "one past per source")
        out = []
        for s, k in self.lags.items():
            p = past[s]
            require_state(isinstance(p, list) and len(p) == min(n, k)
                          and all(type(v) in (int, float) and math.isfinite(v) for v in p), f"the past of {s!r}")
            out.append(tuple(float(v) for v in p))
        return LaggedState(n, tuple(out), self.inner.decode_state(data["inner"]))

    def encode_output(self, output: LaggedOutput):
        return {"ready": output.ready,
                "inner": None if output.inner is None else self.inner.encode_output(output.inner)}
