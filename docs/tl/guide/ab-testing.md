---
description: Paano ihinto nang maaga ang isang A/B test nang hindi lumalaki ang false positives, sa Python. Mga anytime-valid test para sa conversion at bounded na revenue, pagsusuri ng sample ratio mismatch at kontrol sa false discovery rate sa maraming metric, gamit ang sequential-analysis.
language: tl
---

# Paano ihinto nang maaga ang isang A/B test nang hindi lumalaki ang false positives?

> Ito ay salin ng [pahina sa Ingles](../../guide/ab-testing.md). Hindi pa ito nasusuri ng isang katutubong tagapagsalita ng wika; kung saan magkaiba ang dalawa, ang pahina sa Ingles ang masusunod.

**Maikling sagot.** Gumamit ng test na anytime-valid: nananatiling valid
ang p-value at confidence interval nito gaano man kadalas ka tumingin,
kaya puwede kang huminto sa sandaling malinaw na ang resulta. Sa
sequential-analysis:

| Metric | Procedure | Garantiya |
|---|---|---|
| conversion rate (0/1) | `TwoProportionTest` | exact |
| anumang bounded na metric (revenue na may cap, share) | `BoundedABTest` | exact |
| mga event bawat unit ng exposure | `RateRatioTest` | exact para sa mga Poisson count |
| ratio metric (revenue bawat session) | `RatioABTest` | asymptotic |
| mean na may pre-experiment covariate (CUPED) | `ABTest` | asymptotic |
| nahahati ba ang traffic ayon sa balak? | `SampleRatioMismatch` | exact |
| ilang metric o arm nang sabay-sabay | `MultipleTests` (e-BH) | false discovery rate, exact |

Pakainin ang bawat procedure ng isang user sa bawat pagkakataon:
`state, out = test.step(state, {...})`. Kumilos batay sa `out.decision`
kailan mo man gusto.

## Conversion: huminto kapag tiyak na ang datos

Ang control ay nagko-convert ng 10% ng mga user, ang treatment ay 12%.
Tinitingnan ang test pagkatapos ng bawat user at humihinto ito sa una
nitong desisyon:

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

Para sa paghahambing, ang isang fixed-sample test na may 80% na power para
sa lift na ito ay nangangailangan ng mga 3,850 user bawat arm, 7,700 lahat,
at puwede lamang basahin nang isang beses, sa dulo. May bayad ang kalayaan
ng anytime-valid test: para maabot ang parehong power, kailangan nito ng
1.3–1.6 na beses ng mga user ng iisang analysis, at lumampas pa roon ang
run na ito. Bilang kapalit, walang sample size na kailangang itakda nang
maaga, at puwede mong tingnan ang resulta araw-araw at huminto sa sandaling
malinaw na ito. Kapag mas malaki ang effect kaysa sa pinlano, mas maaga
itong nangyayari.

## Revenue: isang eksaktong interval para sa bounded na metric

Ang kailangan lamang ng `BoundedABTest` ay mga bound sa metric. Lagyan ng
cap ang revenue sa halagang pipiliin mo bago ang test (dito, 30), at
eksakto ang confidence sequence para sa pagkakaiba ng mga mean, anuman ang
distribution:

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

Nananatili ang interval sa lahat ng 20,000 pagtingin nang sabay-sabay, hindi
lamang sa huli. Dito, naglalaman pa rin ito ng 0: hindi sapat ang 20,000
user para patunayan ang lift na mga 0.5 sa ganito kaingay na metric, kaya
nagpapatuloy ang experiment.

## Suriin muna ang paghahati ng traffic

Ang sample ratio mismatch (SRM) ay nangangahulugang iba ang paghahati sa
naka-configure, halimbawa dahil sa bug sa assignment o sa logging. Hindi
mapagkakatiwalaan ang mga effect estimate mula sa ganitong experiment. Ang
paglihis mula 50/50 patungong 52/48 ay nahuhuli habang tumatakbo ang
experiment:

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

## Maraming metric nang sabay-sabay

Ang pag-test ng sampung independiyenteng metric sa 5% bawat isa ay
nagbibigay ng mga 40% na tsansa ng kahit isang false discovery.
Pinagsasama ng `MultipleTests` ang mga e-value ng lahat ng test gamit ang
e-BH procedure, kaya nananatili ang false discovery rate sa `alpha` sa
anumang stopping time:

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

## Mga dapat iwasan

* **I-randomise ang unit na ina-analyse mo.** Kung mga user ang
  nira-randomise, magpasok ng isang record bawat user, hindi bawat page
  view. Para sa mga per-session metric, gamitin ang `RatioABTest`, na
  gumagana sa mga kabuuan bawat user.
* **Itakda ang cap ng bounded na metric bago ang test.** Kapag pinili ito
  pagkatapos makita ang datos, nawawalan ng bisa ang garantiya.
* **Kailangan ng malalaking sample ang mga asymptotic na procedure.** Para
  sa `ABTest` at `RatioABTest`, approximately valid lamang ang interval sa
  mahahabang run. Mas piliin ang mga eksaktong procedure kapag angkop ang
  mga ito.
* **Ang adaptive traffic allocation** (mga bandit) ay nangangailangan ng
  test na nananatiling valid kapag nakadepende ang paghahati sa mga
  resulta: `TwoProportionTest(method="universal")` o
  `BoundedABTest(propensity_input=...)`. Tingnan ang
  [tutorial §10](../../tutorials/ab-test.md).

Higit pa: ang [tutorial sa A/B test](../../tutorials/ab-test.md) (CUPED,
mga ratio metric, mga rate, pagpaplano ng tagal) at
[isang programa ng mga experiment](../../tutorials/experiment-programme.md)
(false discovery rate sa maraming experiment).
