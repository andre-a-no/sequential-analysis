---
description: How to plan and run interim analyses of a clinical trial in Python, with group sequential designs (O'Brien–Fleming, Pocock, Lan–DeMets alpha spending, futility bounds), sample sizes for means, proportions and survival, checked against rpact, with sequential-analysis.
---

# How do I plan interim analyses of a clinical trial?

**Short answer.** Use a group sequential design.
`group_sequential_design(alpha, fractions, spending=...)` from
`sequential_analysis.group_sequential` computes:

* the efficacy boundaries, with Lan–DeMets alpha spending (O'Brien–Fleming
  type, Pocock type and others);
* non-binding futility boundaries;
* power and expected sample size;
* the maximum sample size for means and proportions, or the number of
  events for survival.

The boundaries and sample sizes agree with the R package rpact. The test
procedures (`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) then run the
trial, patient by patient or event by event. They perform each interim
analysis when its information fraction is reached.

## Design: four analyses, O'Brien–Fleming spending

One-sided α = 0.025, analyses at 25%, 50%, 75% and 100% of the
patients, 90% power, with a futility boundary:

```python
from sequential_analysis.group_sequential import group_sequential_design

design = group_sequential_design(0.025, [0.25, 0.5, 0.75, 1.0], spending="obrien-fleming",
                                 futility="obrien-fleming", power=0.9)
for k, (t, b, f) in enumerate(zip(design.fractions, design.bounds, design.futility), start=1):
    print(f"analysis {k} at {t:.0%}: efficacy if Z >= {b:.3f}, futility if Z <= {f:.3f}")
print("patients for an effect of 0.3 standard deviations:", design.max_sample_size(effect=0.3, sigma=1.0))
print(f"expected share of the patients used: {design.expected_fraction(0.0):.2f} with no effect, "
      f"{design.expected_fraction(design.drift):.2f} with the planned effect")
```

```text
analysis 1 at 25%: efficacy if Z >= 4.333, futility if Z <= -1.403
analysis 2 at 50%: efficacy if Z >= 2.963, futility if Z <= 0.325
analysis 3 at 75%: efficacy if Z >= 2.359, futility if Z <= 1.291
analysis 4 at 100%: efficacy if Z >= 2.014, futility if Z <= 2.014
patients for an effect of 0.3 standard deviations: 127
expected share of the patients used: 0.59 with no effect, 0.73 with the planned effect
```

## Binary and survival endpoints

```python
binary = group_sequential_design(0.025, [1 / 3, 2 / 3, 1.0], spending="obrien-fleming")
print("patients, response 10% vs 12%, 80% power:",
      binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8))
print("events for a hazard ratio of 0.7, 80% power:", binary.max_events(hazard_ratio=0.7, power=0.8))
print(f"inflation factor over a single analysis: {binary.inflation_factor(0.8):.3f}")
```

```text
patients, response 10% vs 12%, 80% power: 7780
events for a hazard ratio of 0.7, 80% power: 250
inflation factor over a single analysis: 1.013
```

With O'Brien–Fleming spending, three analyses cost 1.3% more patients
than a single final analysis.

## Running the trial

```python
import random

from sequential_analysis.procedures import GroupSequentialProportions

n_max = binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8)
test = GroupSequentialProportions.from_design(binary, n_max)
state, rnd = test.initial_state(), random.Random(3)
for patient in range(n_max):
    arm = patient % 2                                         # 1 treatment, 0 control
    state, out = test.step(state, {"arm": arm, "y": int(rnd.random() < (0.12 if arm else 0.10))})
    if out.analysis:
        print(f"analysis {out.analysis} after {out.n} patients: Z = {out.z:.2f}, bound {out.bound:.2f}")
    if out.decision:
        print("decision:", out.decision)
        break
```

```text
analysis 1 after 2594 patients: Z = 2.14, bound 3.71
analysis 2 after 5187 patients: Z = 2.64, bound 2.51
decision: reject_h0
```

The trial stopped for efficacy at the second analysis, after two thirds
of the planned patients.

## When the analyses do not happen as planned

Data monitoring committees rarely meet exactly at 25% of the
information:

* `design.at(fractions)` recomputes the boundaries for the information
  actually reached. Alpha spending keeps the overall level.
* `GroupSequentialMonitor` takes any statistic you compute yourself (a
  Cox model, a mixed model) as a Z value and its information at each
  meeting.

## And if you want to look after every patient?

A group sequential design allows only the planned number of looks. To
monitor after every patient or event, use an anytime-valid procedure:
`AnytimeLogRankTest` for survival, `TwoProportionTest` for response
rates, `TMixtureSPRT` for a mean. They need more patients at the planned
effect. See [tutorial: survival trial](../tutorials/survival.md).

## Regulatory practice

Group sequential designs with alpha spending are the established
approach in confirmatory trials, described in the ICH E9 guideline and
the FDA guidance on adaptive designs (2019). This library computes the
designs and keeps an auditable, resumable record of each analysis (the
checkpoint and its history digest). It is not validated software in the
regulatory sense: a sponsor using it in a submission has to validate it
like any other tool.

More: [tutorial: group sequential trial](../tutorials/group-sequential.md),
which compares the numbers with rpact;
[reference: design and planning](../reference/design.md).
