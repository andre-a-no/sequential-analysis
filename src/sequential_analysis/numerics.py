# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""Numerical building blocks and the numerical contract.

Long runs accumulate many small terms, so log-domain statistics are summed
with Neumaier's compensated scheme.  The running sum and its compensation
are both stored in the inferential state: the compensation is part of what
is needed to continue the run exactly.
"""
from __future__ import annotations

import math
from collections.abc import Iterable
from typing import Any

from ._compat import zip_strict
from .errors import NumericalError


def neumaier_add(total: float, comp: float, x: float) -> tuple[float, float]:
    """One step of Neumaier summation.  The represented value is total + comp."""
    t = total + x
    if abs(total) >= abs(x):
        comp += (total - t) + x
    else:
        comp += (x - t) + total
    return t, comp


def ordered_sum(values: Iterable[float]) -> float:
    """Plain left-to-right floating-point sum.

    The built-in `sum` adds floats with compensation since Python 3.12 and
    without it before, so its last bits depend on the Python version.  A
    procedure's trajectory must not, and every other language can repeat
    this loop exactly, so the inference path sums floats only with this
    function (or with the compensated `neumaier_add`, when the
    compensation is part of the state).
    """
    total = 0.0
    for v in values:
        total += v
    return total


def logsumexp(values: Iterable[float]) -> float:
    vals = list(values)
    if not vals:
        return -math.inf
    m = max(vals)
    if math.isinf(m):
        return m
    return m + math.log(ordered_sum(math.exp(v - m) for v in vals))


def portable_exp2(x: float) -> float:
    """2**x from additions, multiplications and divisions only, within a few units in the last place.

    IEEE 754 rounds these operations identically everywhere, unlike exp or
    pow, whose last bit differs between C libraries and JavaScript engines.
    So a value that enters the recorded history (a topology's output) is
    the same in every executor.  x = n + f with n an integer and f in
    [0, 1); 2^f = e^(f ln 2) by the Taylor series to 20 terms in Horner
    form, then exact halvings or doublings.
    """
    if not math.isfinite(x):
        raise ValueError("portable_exp2 needs a finite argument")
    if x < -1100.0:
        return 0.0
    if x > 1024.0:
        raise OverflowError("2**x overflows")
    n = math.floor(x)
    y = (x - n) * 0.6931471805599453
    r = 1.0
    for k in range(20, 0, -1):
        r = 1.0 + y * r / k
    while n < 0:
        r *= 0.5
        n += 1
    while n > 0:
        r *= 2.0
        n -= 1
    return r


def require_finite(value: float, what: str) -> float:
    if not math.isfinite(value):
        raise NumericalError(f"{what} is not finite: {value!r}")
    return value


def equivalent(a: Any, b: Any, abs_tol: float = 0.0, rel_tol: float = 0.0) -> bool:
    """Structural equivalence under a numerical contract.

    Numbers are compared within the given tolerances when either of them
    is a float; everything else (integer counts, decisions, labels,
    structure) must match exactly.  With both tolerances at zero, numbers
    must be equal as numbers -- as they are in canonical JSON, 0.0 equals
    -0.0 and 3 equals 3.0 -- except that NaN is considered equal to NaN.
    An infinity equals only itself, whatever the tolerances.
    """
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, float) or isinstance(b, float):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return False
        if math.isnan(a) or math.isnan(b):
            return math.isnan(a) and math.isnan(b)
        if a == b:
            return True
        if math.isinf(a) or math.isinf(b):
            return False
        return abs(a - b) <= max(abs_tol, rel_tol * max(abs(a), abs(b)))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(equivalent(a[k], b[k], abs_tol, rel_tol) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(equivalent(x, y, abs_tol, rel_tol) for x, y in zip_strict(a, b))
    return bool(a == b)
