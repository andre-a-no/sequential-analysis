---
description: Why checking a p-value every day inflates false positives in A/B tests and trials (the peeking problem), and the three families of sequential methods that fix it, in Python with sequential-analysis.
---

# Why can't I look at a p-value every day?

**Short answer.** A fixed-sample test promises a 5% false-positive rate
only if you look at the result once, at the planned sample size. If you
look repeatedly and stop the first time p < 0.05, you get many chances
to be fooled. With 20 looks the false-positive rate rises to about 25%.
Sequential methods are built to be looked at repeatedly. With them the
rate stays at or below 5% however often you look and whenever you stop.

## The peeking problem, measured

Two arms with the same 10% conversion rate (an A/A test), 2,000 users,
200 repetitions. "Peeking" runs the usual two-proportion z-test after
every 100 users and stops at the first p < 0.05. The sequential
`TwoProportionTest` is checked after every single user:

```python
import math
import random

from sequential_analysis.procedures import TwoProportionTest

def a_a_test(seed, users=2000):
    """Alternating arms, both converting 10% of the time: any 'effect' is a false positive."""
    rnd = random.Random(seed)
    return [(user % 2, int(rnd.random() < 0.10)) for user in range(users)]

def peeking(data, looks):
    """The z-test for two proportions after every len(data) / looks users; True if it ever rejects."""
    successes, trials, every = [0, 0], [0, 0], len(data) // looks
    for i, (arm, y) in enumerate(data, start=1):
        successes[arm] += y
        trials[arm] += 1
        if i % every == 0:
            pooled = sum(successes) / sum(trials)
            se = math.sqrt(pooled * (1 - pooled) * (1 / trials[0] + 1 / trials[1]))
            if se > 0 and abs(successes[1] / trials[1] - successes[0] / trials[0]) / se > 1.96:
                return True
    return False

def sequential(data):
    """The anytime-valid test, looked at after every user; True if it ever rejects."""
    test = TwoProportionTest(alpha=0.05)
    state = test.initial_state()
    for arm, y in data:
        state, out = test.step(state, {"arm": arm, "y": y})
        if out.decision is not None:
            return True
    return False

runs = [a_a_test(seed) for seed in range(200)]
print(f"z-test, one look at the end:   {sum(peeking(r, 1) for r in runs) / len(runs):.1%} false positives")
print(f"z-test, 20 looks:              {sum(peeking(r, 20) for r in runs) / len(runs):.1%}")
print(f"TwoProportionTest, 2000 looks: {sum(sequential(r) for r in runs) / len(runs):.1%}")
```

```text
z-test, one look at the end:   4.5% false positives
z-test, 20 looks:              28.0%
TwoProportionTest, 2000 looks: 5.0%
```

The single look keeps its promise. Twenty looks multiply the error rate
about six times. The sequential test, looked at after every one of the
2,000 users, keeps it at 5%. That is the promise: its guarantee is
**exact** (`TwoProportionTest.guarantee == "exact"`), a false-positive
rate of at most 5% at every sample size, however often you look. With
200 repetitions, 10 false positives are what an exact 5% gives.

## The three families of sequential methods

| Family | You may look | Typical use | In sequential-analysis |
|---|---|---|---|
| **Sequential probability ratio tests** (Wald 1945) | after every observation | one simple hypothesis against another, fewest observations on average: quality control, simulation, psychophysics | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Group sequential designs** (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | at a few planned interim analyses | clinical trials with a data monitoring committee | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Anytime-valid inference**: e-values, confidence sequences, mixture SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | after every observation, stopping for any reason | online A/B tests, monitoring dashboards | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**What it costs.** Looking more often needs more data at the effect you
planned for:

* a group sequential design with four analyses needs 1–20% more
  patients than a single analysis;
* an anytime-valid test of two proportions needs 1.3–1.6 times the users
  of a single analysis.

In exchange, a large effect stops the experiment early, and nobody has
to fix the sample size in advance.

## When this is not the problem

Peeking only inflates errors when what you do depends on what you saw.
If you look at the dashboard but always run the experiment to its
planned size and test once, the fixed-sample test is valid. It is also
the most efficient choice in that case.

Next: [stop an A/B test early](ab-testing.md),
[confidence sequences](confidence-sequences.md),
[the glossary](glossary.md).
