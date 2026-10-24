---
description: Paano magplano at magpatakbo ng mga interim analysis ng isang clinical trial sa Python, gamit ang mga group sequential design (O'Brien–Fleming, Pocock, Lan–DeMets alpha spending, mga futility bound), mga sample size para sa mean, proporsiyon at survival, na sinuri laban sa rpact, gamit ang sequential-analysis.
language: tl
---

# Paano magplano ng mga interim analysis ng isang clinical trial?

> Ito ay salin ng [pahina sa Ingles](../../guide/clinical-trials.md). Hindi pa ito nasusuri ng isang katutubong tagapagsalita ng wika; kung saan magkaiba ang dalawa, ang pahina sa Ingles ang masusunod.

**Maikling sagot.** Gumamit ng group sequential design.
Kinakalkula ng `group_sequential_design(alpha, fractions, spending=...)`
mula sa `sequential_analysis.group_sequential` ang:

* mga efficacy boundary, gamit ang Lan–DeMets alpha spending (uring
  O'Brien–Fleming, uring Pocock at iba pa);
* mga non-binding na futility boundary;
* power at expected sample size;
* ang maximum sample size para sa mga mean at proporsiyon, o ang bilang
  ng mga event para sa survival.

Tumutugma ang mga boundary at sample size sa R package na rpact. Ang mga
test procedure (`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) naman ang
nagpapatakbo ng trial, pasyente kada pasyente o event kada event.
Isinasagawa nila ang bawat interim analysis kapag naabot na ang
information fraction nito.

## Design: apat na analysis, O'Brien–Fleming spending

One-sided α = 0.025, mga analysis sa 25%, 50%, 75% at 100% ng mga
pasyente, 90% na power, na may futility boundary:

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

## Binary at survival na endpoint

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

Sa O'Brien–Fleming spending, ang tatlong analysis ay nangangailangan ng
1.3% na mas maraming pasyente kaysa sa iisang final analysis.

## Pagpapatakbo ng trial

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

Huminto ang trial dahil sa efficacy sa ikalawang analysis, pagkatapos ng
dalawang-katlo ng mga planadong pasyente.

## Kapag hindi nangyari ang mga analysis ayon sa plano

Bihirang magpulong ang mga data monitoring committee nang eksakto sa 25%
ng information:

* Muling kinakalkula ng `design.at(fractions)` ang mga boundary para sa
  information na talagang naabot. Pinananatili ng alpha spending ang
  kabuuang level.
* Tumatanggap ang `GroupSequentialMonitor` ng anumang statistic na ikaw
  mismo ang nagkalkula (isang Cox model, isang mixed model) bilang Z value
  at ng information nito sa bawat pulong.

## Paano kung gusto mong tumingin pagkatapos ng bawat pasyente?

Ang group sequential design ay nagpapahintulot lamang ng planadong bilang
ng pagtingin. Para mag-monitor pagkatapos ng bawat pasyente o event,
gumamit ng anytime-valid na procedure: `AnytimeLogRankTest` para sa
survival, `TwoProportionTest` para sa mga response rate, `TMixtureSPRT`
para sa mean. Nangangailangan ang mga ito ng mas maraming pasyente sa
planadong effect. Tingnan ang [tutorial: survival trial](../../tutorials/survival.md).

## Praktikang regulatoryo

Ang mga group sequential design na may alpha spending ang itinatag na
pamamaraan sa mga confirmatory trial, na inilalarawan sa ICH E9 guideline
at sa FDA guidance on adaptive designs (2019). Kinakalkula ng library na
ito ang mga design at nagtatabi ng auditable at resumable na record ng
bawat analysis (ang checkpoint at ang history digest nito). Hindi ito
validated software sa regulatoryong kahulugan: ang isang sponsor na
gagamit nito sa isang submission ay kailangang mag-validate nito gaya ng
anumang ibang tool.

Higit pa: [tutorial: group sequential trial](../../tutorials/group-sequential.md),
na inihahambing ang mga numero sa rpact;
[reference: design at pagpaplano](../../reference/design.md).
