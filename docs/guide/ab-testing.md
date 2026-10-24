---
description: How to stop an A/B test early without inflating false positives, in Python. Anytime-valid tests for conversion and bounded revenue, a sample ratio mismatch check and false discovery rate control over many metrics, with sequential-analysis.
---

# How do I stop an A/B test early without inflating false positives?

**Short answer.** Use a test that is anytime-valid: its p-value and
confidence interval stay valid however often you look, so you may stop
as soon as the result is clear. In sequential-analysis:

| Metric | Procedure | Guarantee |
|---|---|---|
| conversion rate (0/1) | `TwoProportionTest` | exact |
| any bounded metric (capped revenue, share) | `BoundedABTest` | exact |
| events per unit of exposure | `RateRatioTest` | exact for Poisson counts |
| ratio metric (revenue per session) | `RatioABTest` | asymptotic |
| mean with a pre-experiment covariate (CUPED) | `ABTest` | asymptotic |
| is the traffic split as intended? | `SampleRatioMismatch` | exact |
| several metrics or arms together | `MultipleTests` (e-BH) | false discovery rate, exact |

Feed each procedure one user at a time: `state, out = test.step(state, {...})`.
Act on `out.decision` whenever you like.

## Conversion: stop when the data are conclusive

Control converts 10% of users, treatment 12%. The test is looked at
after every user and stops at its first decision:

```python
import random

from sequential_analysis.procedures import TwoProportionTest

def users(n, rates=(0.10, 0.12), seed=1):
    """(arm, converted) per user; arm 1 is the treatment."""
    rnd = random.Random(seed)
    for _ in range(n):
        arm = int(rnd.random() < 0.5)
        yield arm, int(rnd.random() < rates[arm])

test = TwoProportionTest(alpha=0.05)
state = test.initial_state()
for arm, converted in users(60_000):
    state, out = test.step(state, {"arm": arm, "y": converted})
    if out.decision is not None:
        break
print(f"stopped after {out.n} users: conversion {out.rates[0]:.4f} (treatment) vs {out.rates[1]:.4f}, "
      f"anytime-valid p = {out.p_value:.4f}, decision: {out.decision}")
```

```text
stopped after 16469 users: conversion 0.1259 (treatment) vs 0.1068, anytime-valid p = 0.0496, decision: reject_h0
```

For comparison, a fixed-sample test with 80% power for this lift needs
about 3,850 users per arm, 7,700 in total, and may be read only once,
at the end. The anytime-valid test pays for its freedom: to reach the
same power it needs 1.3–1.6 times the users of a single analysis, and
this run took more than that. In exchange there is no sample size to
fix in advance, and you may look at the result daily and stop as soon
as it is clear. When the effect is larger than planned, that happens
much earlier.

## Revenue: an exact interval for a bounded metric

`BoundedABTest` needs only bounds on the metric. Cap revenue at a value
you choose before the test (here 30), and the confidence sequence for
the difference in means is exact for any distribution:

```python
from sequential_analysis.procedures import BoundedABTest

rnd = random.Random(2)
revenue = BoundedABTest(lower=0.0, upper=30.0, allocation=0.5, input="revenue", grid=300)
state = revenue.initial_state()
for _ in range(20_000):
    arm = int(rnd.random() < 0.5)
    spend = min(rnd.expovariate(1 / (5.0 if arm == 0 else 5.6)), 30.0)   # capped at 30
    state, out = revenue.step(state, {"arm": arm, "revenue": spend})
print(f"after {out.n} users: mean revenue {out.means[0]:.2f} (treatment) vs {out.means[1]:.2f}, "
      f"95% confidence sequence for the difference [{out.lower:.2f}, {out.upper:.2f}]")
```

```text
after 20000 users: mean revenue 5.47 (treatment) vs 4.99, 95% confidence sequence for the difference [-0.30, 1.30]
```

The interval holds at every one of the 20,000 looks at once, not only
at the last. Here it still contains 0: 20,000 users are not enough to
establish a lift of about 0.5 on a metric this noisy, so the experiment
continues.

## Check the traffic split first

A sample ratio mismatch means the split differs from what was
configured, for example because of a bug in assignment or in logging.
Effect estimates from such an experiment are not trustworthy. A
mismatch from 50/50 to 52/48 is caught while the experiment runs:

```python
from sequential_analysis.procedures import SampleRatioMismatch

srm = SampleRatioMismatch(weights=(0.5, 0.5), alpha=0.001)
state = srm.initial_state()
rnd = random.Random(3)
for _ in range(50_000):
    state, out = srm.step(state, {"arm": int(rnd.random() < 0.52)})
    if out.decision is not None:
        break
print(f"mismatch detected after {out.n} users: split {out.proportions[0]:.3f} / {out.proportions[1]:.3f}")
```

```text
mismatch detected after 4927 users: split 0.470 / 0.530
```

## Many metrics at once

Testing ten independent metrics at 5% each gives about a 40% chance of at least one
false discovery. `MultipleTests` combines the e-values of all the tests
with the e-BH procedure, so the false discovery rate stays at `alpha` at
any stopping time:

```python
from sequential_analysis.procedures import MultipleTests

metrics = MultipleTests({
    "conversion": TwoProportionTest(input="converted"),
    "revenue": BoundedABTest(lower=0.0, upper=30.0, input="revenue", grid=100),
    "traffic split": SampleRatioMismatch((0.5, 0.5)),
}, alpha=0.05)
state = metrics.initial_state()
rnd = random.Random(4)
for _ in range(15_000):
    arm = int(rnd.random() < 0.5)
    converted = int(rnd.random() < (0.10, 0.13)[arm])
    spend = min(rnd.expovariate(1 / 5.0), 30.0)                          # no effect on revenue
    state, out = metrics.step(state, {"arm": arm, "converted": converted, "revenue": spend})
print("discoveries:", out.rejected)
```

```text
discoveries: ('conversion',)
```

## Pitfalls

* **Randomise the unit you analyse.** If users are randomised, feed one
  record per user, not per page view. For per-session metrics use
  `RatioABTest`, which works on user totals.
* **Fix the cap of a bounded metric before the test.** Choosing it after
  seeing the data voids the guarantee.
* **Asymptotic procedures need large samples.** For `ABTest` and
  `RatioABTest` the interval is only approximately valid in long runs.
  Prefer the exact procedures when they fit.
* **Adaptive traffic allocation** (bandits) needs a test that stays valid
  when the split depends on the outcomes:
  `TwoProportionTest(method="universal")` or
  `BoundedABTest(propensity_input=...)`. See
  [tutorial §10](../tutorials/ab-test.md).

More: the [A/B test tutorial](../tutorials/ab-test.md) (CUPED, ratio
metrics, rates, planning the duration) and
[a programme of experiments](../tutorials/experiment-programme.md)
(false discovery rate over many experiments).
