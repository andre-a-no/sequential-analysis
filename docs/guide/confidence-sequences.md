---
description: Confidence sequences are confidence intervals that stay valid at every sample size at once, so they can be monitored continuously. How to compute them in Python for a bounded mean, a median or quantile, and a mean with heavy tails, with sequential-analysis.
---

# How do I get a confidence interval that stays valid when I keep looking?

**Short answer.** Use a **confidence sequence**. It is a sequence of
intervals, one after each observation, that contains the true value at
all sample sizes simultaneously with probability at least 95%. You may
watch it, stop when it is narrow enough or excludes zero, and report the
interval you stopped at. A usual 95% confidence interval promises 95%
only at one sample size fixed in advance.

| What you estimate | Assumption | Procedure | Guarantee |
|---|---|---|---|
| mean of bounded data (rates, scores, capped revenue) | values in `[lower, upper]` | `BettingConfidenceSequence` | exact |
| median, 90th percentile, any quantile | none | `QuantileConfidenceSequence` | exact |
| mean with heavy tails or outliers | a bound on the standard deviation | `CatoniConfidenceSequence` | exact |
| mean of normal data, variance unknown | normality | `TMixtureSPRT` (`lower`, `upper`) | exact under normality |
| mean of anything, long runs | finite variance | `AsymptoticConfidenceSequence` | asymptotic |
| difference between two arms | see [A/B tests](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## The usual interval fails when watched

Draw 500 observations of a 0/1 variable with mean 0.3, and from the
30th on compute the textbook 95% interval after each one: the mean ±
1.96 standard errors. In how many of 100 runs does the interval miss
the true mean at some point?

```python
import math
import random

def stream(seed, n=500, p=0.3):
    rnd = random.Random(seed)
    return [float(rnd.random() < p) for _ in range(n)]

def textbook_ever_misses(xs, truth=0.3):
    total = total2 = 0.0
    for n, x in enumerate(xs, start=1):
        total, total2 = total + x, total2 + x * x
        if n >= 30:
            mean = total / n
            se = math.sqrt(max(total2 / n - mean * mean, 1e-12) / n)
            if abs(mean - truth) > 1.96 * se:
                return True
    return False

runs = [stream(seed) for seed in range(100)]
print(f"textbook interval misses the truth at some n in {sum(map(textbook_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
textbook interval misses the truth at some n in 28% of runs
```

Its "95%" holds only at a sample size fixed in advance. The confidence
sequence for the same data, by betting (Waudby-Smith and Ramdas 2024),
misses at some n in at most 5% of runs by construction:

```python
from sequential_analysis.procedures import BettingConfidenceSequence

def sequence_ever_misses(xs, truth=0.3):
    cs = BettingConfidenceSequence(lower=0.0, upper=1.0, alpha=0.05, grid=100)
    state = cs.initial_state()
    for x in xs:
        state, out = cs.step(state, {"x": x})
        if not out.lower <= truth <= out.upper:
            return True
    return False

print(f"confidence sequence misses the truth at some n in {sum(map(sequence_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
confidence sequence misses the truth at some n in 1% of runs
```

## A median latency, with no assumption at all

Latencies are skewed and heavy-tailed, so a mean ± standard error
interval is not trustworthy for them. `QuantileConfidenceSequence`
covers any quantile of any distribution, ties included:

```python
from sequential_analysis.procedures import QuantileConfidenceSequence

rnd = random.Random(7)
median = QuantileConfidenceSequence(p=0.5, alpha=0.05)
p90 = QuantileConfidenceSequence(p=0.9, alpha=0.05)
m_state, q_state = median.initial_state(), p90.initial_state()
for _ in range(2000):
    latency = rnd.lognormvariate(math.log(120.0), 0.6)   # milliseconds; true median 120
    m_state, m = median.step(m_state, {"x": latency})
    q_state, q = p90.step(q_state, {"x": latency})
print(f"median: {m.estimate:.1f} ms, 95% confidence sequence [{m.lower:.1f}, {m.upper:.1f}]")
print(f"90th percentile: {q.estimate:.1f} ms, [{q.lower:.1f}, {q.upper:.1f}]")
```

```text
median: 117.3 ms, 95% confidence sequence [111.3, 122.6]
90th percentile: 252.7 ms, [237.9, 272.5]
```

The true values are 120 ms and 258.8 ms. Both intervals hold at all
2,000 sample sizes at once.

## Pitfalls

* **Bounds and caps are part of the assumption.** Choose `lower` and
  `upper` before seeing data. A value outside them is refused.
* **No method gives exact coverage for the mean of arbitrary unbounded
  data.** For such data use a quantile, cap the values, assume a bound
  on the standard deviation (Catoni), or accept an asymptotic sequence.
* **Confidence sequences are wider than a single interval** at the same
  sample size. The width is the price of being valid at every sample
  size at once.

More: [Which method?](../choosing.md),
[reference: anytime-valid and nonparametric](../reference/anytime.md).
