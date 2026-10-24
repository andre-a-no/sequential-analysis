---
description: How to run Wald's sequential probability ratio test (SPRT) in Python with sequential-analysis. Error rates, average sample size against a fixed-sample test, and the truncated alternatives (2-SPRT, Kiefer–Weiss optimal plans).
---

# How do I run Wald's SPRT in Python?

**Short answer.** `SPRT(family, theta0, theta1, alpha, beta)` from
`sequential_analysis.procedures` implements Wald's sequential
probability ratio test. It decides between two simple hypotheses with
the fewest observations on average. Feed it one observation at a time
and stop at the first decision. In the example below it needs about
half the observations of a fixed-sample test with the same error rates:
65–76 items on average instead of 133. If you need a guaranteed maximum
sample size, use `TwoSPRT` or a plan from `kiefer_weiss_plan` instead.

## Example: is the defect rate 10% or 20%?

A batch is accepted if its defect rate is 10% and rejected if it is
20%, with both error rates 5%:

```python
import random

from sequential_analysis.procedures import SPRT, Bernoulli

test = SPRT(Bernoulli(), theta0=0.10, theta1=0.20, alpha=0.05, beta=0.05)

def inspect_items(rate, seed):
    """Inspect items until the test decides; returns (decision, items inspected)."""
    rnd = random.Random(seed)
    state = test.initial_state()
    while state.decision is None:
        state, out = test.step(state, {"x": int(rnd.random() < rate)})
    return state.decision, state.n

decision, n = inspect_items(0.10, seed=1)
print(f"a good batch: {decision} after {n} items")
```

```text
a good batch: accept_h0 after 108 items
```

How well does it do over many batches?

```python
for rate in (0.10, 0.20):
    results = [inspect_items(rate, seed) for seed in range(2000)]
    wrong = sum(d == ("reject_h0" if rate == 0.10 else "accept_h0") for d, _ in results) / len(results)
    average = sum(n for _, n in results) / len(results)
    longest = max(n for _, n in results)
    print(f"defect rate {rate:.0%}: wrong decision {wrong:.1%}, average {average:.0f} items, longest {longest}")
```

```text
defect rate 10%: wrong decision 3.5%, average 76 items, longest 370
defect rate 20%: wrong decision 4.3%, average 65 items, longest 315
```

A fixed-sample test with the same error rates inspects about 133 items
in every batch (normal approximation). The SPRT inspects 43–51% fewer
on average. Its sample size is random and has no upper limit, though,
and a few batches take much longer than the average.

The thresholds are Wald's: log((1 − β)/α) and log(β/(1 − α)). They
guarantee, for any sample size at stopping, that the actual error rates
α′ and β′ satisfy α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) and α′ + β′ ≤ α + β.
The likelihood ratio overshoots the thresholds when it stops, so in
practice the rates are below the nominal ones, as here. That is the
sense of `SPRT.guarantee == "exact"`. For error rates computed exactly
rather than bounded, use `operating_characteristic` on a plan (below).

## When you need a maximum sample size

* `TwoSPRT` (Lorden's 2-SPRT) stops by a fixed horizon and nearly
  minimises the worst-case expected sample size.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  in `sequential_analysis.design` computes the optimal plan with a
  maximum sample size by backward induction. `PlanTest` executes it,
  and `operating_characteristic` gives its exact error rates and
  expected sample size without simulation. See
  `examples/07_design_kiefer_weiss.py`.
* For a few planned looks instead of one per observation, use a
  [group sequential design](clinical-trials.md).

## When the SPRT is the wrong tool

* **The hypotheses are not simple.** "The rate is 10%" against "the
  rate is anything else" is a composite alternative. Use a mixture
  SPRT (`NormalMixtureSPRT`, `TMixtureSPRT`) or a test by betting
  (`BettingMeanTest`), which are anytime-valid against every
  alternative.
* **The true value lies between θ₀ and θ₁.** The SPRT is then slowest,
  and its expected sample size can exceed the fixed-sample size. The
  Kiefer–Weiss plan is built for exactly this case.

Families available for likelihood-ratio procedures: `Gaussian` (known
variance), `Bernoulli`, `Poisson`, `Exponential`.
