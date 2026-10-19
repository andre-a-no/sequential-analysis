# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""Data topology: how logical inputs are related before inference.

A topology operator turns delivered observations into statistical inputs.
Operators may hold state (observations waiting for a partner); that state
is part of the run checkpoint, because it has been consumed from the
sources but has not yet reached the procedure.

Confluence
----------
An operator is *confluent* if its output sequence depends only on the
per-input order of observations, not on how the inputs interleave.
PositionalPair and TimeAlign are confluent.  Independent, KeyJoin and
AsOfJoin are not: their output follows arrival (or completion) order, so
the ordering policy is part of the experiment and is recorded in
provenance.
"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .core import Observation
from .errors import ContractViolation, OrderingError
from .numerics import portable_exp2
from .transforms import Difference, identity_of


class Topology(ABC):
    confluent: bool = False

    @abstractmethod
    def spec(self) -> dict:
        """JSON description, recorded in provenance and checked on restore."""

    @abstractmethod
    def push(self, obs: Observation) -> list[dict]:
        """Accept one delivered observation; return zero or more statistical inputs."""

    def state(self) -> Any:
        return None

    def restore(self, state: Any) -> None:
        return None

    def map(self, fn: Callable[[dict], dict | None], name: str | None = None) -> Topology:
        """Apply a stateless transformation to every emitted input.

        `fn` should be a `Transform`, whose name, version and configuration
        are recorded; a plain function needs a `name`, and only that is.
        """
        return Mapped(self, fn, name)


class Independent(Topology):
    """Unpaired samples: every observation is a statistical input of its own."""

    def spec(self) -> dict:
        return {"type": "independent"}

    def push(self, obs: Observation) -> list[dict]:
        return [{obs.input: obs.value}]


class _Buffered(Topology):
    def __init__(self, inputs: Sequence[str]):
        if len(inputs) < 2 or len(set(inputs)) != len(inputs):
            raise ValueError("need at least two distinct logical inputs")
        self.inputs = tuple(inputs)

    def _check(self, obs: Observation) -> None:
        if obs.input not in self.inputs:
            raise ContractViolation(f"observation for input {obs.input!r} is not part of this topology")


class PositionalPair(_Buffered):
    """Pair the i-th observation of every input: (A_1, B_1), (A_2, B_2), ..."""

    confluent = True

    def __init__(self, inputs: Sequence[str]):
        super().__init__(inputs)
        self._queues: dict[str, deque] = {n: deque() for n in self.inputs}

    def spec(self) -> dict:
        return {"type": "positional_pair", "inputs": list(self.inputs)}

    def push(self, obs: Observation) -> list[dict]:
        self._check(obs)
        self._queues[obs.input].append(obs.value)
        out = []
        while all(self._queues.values()):
            out.append({n: q.popleft() for n, q in self._queues.items()})
        return out

    def state(self) -> Any:
        return {n: list(q) for n, q in self._queues.items()}

    def restore(self, state: Any) -> None:
        self._queues = {n: deque(state[n]) for n in self.inputs}


class KeyJoin(_Buffered):
    """Join observations that carry the same key.  Emits in completion order."""

    def __init__(self, inputs: Sequence[str]):
        super().__init__(inputs)
        self._partial: dict[Any, dict[str, Any]] = {}

    def spec(self) -> dict:
        return {"type": "key_join", "inputs": list(self.inputs)}

    def push(self, obs: Observation) -> list[dict]:
        self._check(obs)
        if type(obs.key) not in (str, int):
            raise ContractViolation(
                f"key join needs a str or int key on every observation, got {type(obs.key).__name__} {obs.key!r}; "
                f"keys are stored in checkpoints as JSON, so build a composite key as a string in the adapter, "
                f"e.g. f\"{{subject}}/{{visit}}\""
            )
        row = self._partial.setdefault(obs.key, {})
        if obs.input in row:
            raise OrderingError(f"key {obs.key!r}: input {obs.input!r} was observed twice")
        row[obs.input] = obs.value
        if len(row) < len(self.inputs):
            return []
        del self._partial[obs.key]
        return [{n: row[n] for n in self.inputs}]

    def state(self) -> Any:
        return [[k, dict(row)] for k, row in self._partial.items()]

    def restore(self, state: Any) -> None:
        self._partial = {k: dict(row) for k, row in state}


class TimeAlign(_Buffered):
    """Align two time-ordered inputs within a tolerance.

    The heads of the two queues are paired when their event times differ by
    at most `tolerance`; otherwise the earlier head has no partner and is
    discarded.  Discarded observations change the observation history, so
    they are counted and the count is checkpointed.
    """

    confluent = True

    def __init__(self, inputs: Sequence[str], tolerance: float):
        super().__init__(inputs)
        if len(self.inputs) != 2:
            raise ValueError("time alignment is defined for exactly two inputs")
        if type(tolerance) not in (int, float) or not (0 <= tolerance < math.inf):
            raise ValueError(f"tolerance must be a finite non-negative number, got {tolerance!r}")
        self.tolerance = float(tolerance)
        self.unmatched = 0
        self._queues: dict[str, deque] = {n: deque() for n in self.inputs}
        self._last: dict[str, float | None] = {n: None for n in self.inputs}

    def spec(self) -> dict:
        return {"type": "time_align", "inputs": list(self.inputs), "tolerance": self.tolerance}

    def push(self, obs: Observation) -> list[dict]:
        self._check(obs)
        if obs.time is None:
            raise ContractViolation("time alignment needs an event time on every observation")
        last = self._last[obs.input]
        if last is not None and obs.time < last:
            raise OrderingError(f"input {obs.input!r}: event time went backwards ({obs.time} < {last})")
        self._last[obs.input] = obs.time
        self._queues[obs.input].append((obs.time, obs.value))
        a, b = self.inputs
        qa, qb = self._queues[a], self._queues[b]
        out = []
        while qa and qb:
            (ta, va), (tb, vb) = qa[0], qb[0]
            if abs(ta - tb) <= self.tolerance:
                qa.popleft()
                qb.popleft()
                out.append({a: va, b: vb})
            elif ta < tb:
                qa.popleft()
                self.unmatched += 1
            else:
                qb.popleft()
                self.unmatched += 1
        return out

    def state(self) -> Any:
        return {
            "queues": {n: [list(item) for item in q] for n, q in self._queues.items()},
            "last": dict(self._last),
            "unmatched": self.unmatched,
        }

    def restore(self, state: Any) -> None:
        self._queues = {n: deque(tuple(item) for item in state["queues"][n]) for n in self.inputs}
        self._last = {n: state["last"][n] for n in self.inputs}
        self.unmatched = int(state["unmatched"])


class AsOfJoin(Topology):
    """Attach to every bar what a stream of events said up to the bar's time.

    `bars` is a regular stream (prices, returns); `events` an irregular one
    (news items scored by sentiment, trades, alerts), each event a number.
    Every bar is emitted at once, with its value -- a number under the
    name `bars`, or a mapping of named numbers -- and, for the events that
    arrived since the previous bar and whose time is not after the bar's:

        <prefix>_count   how many there were
        <prefix>_sum     the sum of their values

    and with a `half_life`, the influence of all events so far, each
    decaying by half every half_life units of time:

        <prefix>_decayed        sum of value * 2^-(bar time - event time) / half_life
        <prefix>_decayed_count  the same with every value 1

    An event whose time is after the bar waits for a later bar.  An event
    that arrives after a bar later than its own time goes to the next bar
    and is counted as late: the bar could not have known it.  So a bar
    never sees an event that had not arrived when it did, and to rule out
    look-ahead in a replay the event's time must be when it became
    available (received, parsed and scored), not when it was published.
    Times must not decrease within either input.  The decay is computed
    with `portable_exp2`, so that the join's output, which enters the
    recorded history, is the same in every executor.

    Not confluent: what a bar sees depends on which events arrived before
    it, so a replay must deliver both inputs in their original order.
    """

    def __init__(self, bars: str, events: str, *, half_life: float | None = None, prefix: str | None = None):
        if not (isinstance(bars, str) and bars and isinstance(events, str) and events) or bars == events:
            raise ValueError("bars and events must be two distinct non-empty input names")
        if half_life is not None and (type(half_life) not in (int, float) or not 0 < half_life < math.inf):
            raise ValueError("half_life must be a positive finite number or None")
        if prefix is not None and not (isinstance(prefix, str) and prefix):
            raise ValueError("prefix must be a non-empty string or None")
        self.bars, self.events = bars, events
        self.half_life = None if half_life is None else float(half_life)
        self.prefix = prefix if prefix is not None else events
        self.inputs = (bars, events)
        self.fields = tuple(f"{self.prefix}_{f}" for f in
                            (("count", "sum") + (("decayed", "decayed_count") if half_life is not None else ())))
        self._pending: deque = deque()  # (time, value) of events not yet given to a bar, oldest first
        self._last_bar: float | None = None
        self._last_event: float | None = None
        self._decayed = self._decayed_count = 0.0
        self.late = 0

    def spec(self) -> dict:
        return {"type": "as_of_join", "bars": self.bars, "events": self.events, "half_life": self.half_life,
                "prefix": self.prefix}

    @staticmethod
    def _number(v: Any) -> bool:
        return type(v) in (int, float) and math.isfinite(v)

    def push(self, obs: Observation) -> list[dict]:
        if obs.input not in self.inputs:
            raise ContractViolation(f"observation for input {obs.input!r} is not part of this topology")
        if obs.time is None:
            raise ContractViolation("an as-of join needs an event time on every observation")
        if obs.input == self.events:
            if not self._number(obs.value):
                raise ContractViolation(f"input {self.events!r}: an event's value must be a finite number")
            if self._last_event is not None and obs.time < self._last_event:
                raise OrderingError(f"input {self.events!r}: event time went backwards "
                                    f"({obs.time} < {self._last_event})")
            self._last_event = obs.time
            self._pending.append((obs.time, obs.value))
            return []
        if self._last_bar is not None and obs.time < self._last_bar:
            raise OrderingError(f"input {self.bars!r}: event time went backwards ({obs.time} < {self._last_bar})")
        if isinstance(obs.value, Mapping):
            row = dict(obs.value)
            clash = sorted(set(row) & set(self.fields))
            if clash:
                raise ContractViolation(f"input {self.bars!r}: fields {clash} are the join's own")
        else:
            row = {self.bars: obs.value}
        now = obs.time
        count, total, decayed, decayed_count = 0, 0.0, self._decayed, self._decayed_count
        if self.half_life is not None and self._last_bar is not None:
            f = portable_exp2(-(now - self._last_bar) / self.half_life)
            decayed, decayed_count = decayed * f, decayed_count * f
        while self._pending and self._pending[0][0] <= now:
            t, v = self._pending.popleft()
            if self._last_bar is not None and t <= self._last_bar:
                self.late += 1
            count += 1
            total += v
            if self.half_life is not None:
                w = portable_exp2(-(now - t) / self.half_life)
                decayed += v * w
                decayed_count += w
        self._last_bar, self._decayed, self._decayed_count = now, decayed, decayed_count
        row[self.fields[0]], row[self.fields[1]] = count, total
        if self.half_life is not None:
            row[self.fields[2]], row[self.fields[3]] = decayed, decayed_count
        return [row]

    def state(self) -> Any:
        return {"pending": [[t, v] for t, v in self._pending], "last_bar": self._last_bar,
                "last_event": self._last_event, "decayed": self._decayed, "decayed_count": self._decayed_count,
                "late": self.late}

    def restore(self, state: Any) -> None:
        self._pending = deque((t, v) for t, v in state["pending"])
        self._last_bar, self._last_event = state["last_bar"], state["last_event"]
        self._decayed, self._decayed_count = float(state["decayed"]), float(state["decayed_count"])
        self.late = int(state["late"])


@dataclass(frozen=True)
class InvalidInput:
    """Stands, in a topology's output, for an input a transformation could not map.

    It keeps its place among the inputs, so that the run applies the
    inputs before it, reports it as invalid input and then goes on.
    """

    violation: ContractViolation


class Mapped(Topology):
    """A topology followed by a stateless map or filter (return None to drop)."""

    def __init__(self, inner: Topology, fn: Callable[[dict], dict | None], name: str | None = None):
        self.inner, self.fn, self.name = inner, fn, name
        self.map_identity = identity_of(fn, name)
        self.confluent = inner.confluent

    def spec(self) -> dict:
        return {"type": "mapped", "map": self.map_identity, "inner": self.inner.spec()}

    def push(self, obs: Observation) -> list:
        """Map every input the inner topology emits.

        A transformation that fails on an input (a value of the wrong type
        that reached it before any contract could see it, a missing field)
        makes that input invalid, not the run: an InvalidInput takes its
        place in the output, and the run reports and skips it in order.
        """
        out: list = []
        for x in self.inner.push(obs):
            if isinstance(x, InvalidInput):
                out.append(x)
                continue
            try:
                y = self.fn(x)
            except Exception as error:
                message = f"{self.map_identity['name']} failed on {x!r}: {type(error).__name__}: {error}"
                out.append(InvalidInput(ContractViolation(message)))
                continue
            if y is not None:
                out.append(y)
        return out

    def state(self) -> Any:
        return self.inner.state()

    def restore(self, state: Any) -> None:
        self.inner.restore(state)


def difference(a: str, b: str, out: str = "x") -> Difference:
    """Map a paired input {a, b} to the single input {out: a - b}."""
    return Difference(a, b, out)
