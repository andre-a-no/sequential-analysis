---
description: Python లో తప్పుడు పాజిటివ్‌లను (false positive) పెంచకుండా A/B పరీక్షను ముందుగానే ఎలా ఆపాలి. కన్వర్షన్ మరియు పరిమిత ఆదాయం కోసం ఎప్పుడైనా-చెల్లుబాటయ్యే (anytime-valid) పరీక్షలు, నమూనా నిష్పత్తి అసమతుల్యత (sample ratio mismatch) తనిఖీ మరియు అనేక మెట్రిక్‌లపై తప్పుడు ఆవిష్కరణ రేటు (false discovery rate) నియంత్రణ, sequential-analysis తో.
language: te
---

# తప్పుడు పాజిటివ్‌లను పెంచకుండా A/B పరీక్షను ముందుగానే ఎలా ఆపాలి?

> ఇది [ఆంగ్ల పేజీ](../../guide/ab-testing.md)కి అనువాదం. దీనిని ఇంకా తెలుగు మాతృభాషీయులు ఎవరూ సమీక్షించలేదు; రెండింటి మధ్య తేడా ఉన్నచోట ఆంగ్ల పేజీయే ప్రామాణికం.

**సంక్షిప్త సమాధానం.** ఎప్పుడైనా-చెల్లుబాటయ్యే (anytime-valid) పరీక్షను
వాడండి: మీరు ఎన్నిసార్లు చూసినా దాని p-విలువ (p-value) మరియు విశ్వాస అంతరం
(confidence interval) చెల్లుబాటులోనే ఉంటాయి, కాబట్టి ఫలితం స్పష్టమైన వెంటనే
మీరు ఆపవచ్చు. sequential-analysis లో:

| మెట్రిక్ | విధానం | హామీ |
|---|---|---|
| కన్వర్షన్ రేటు (0/1) | `TwoProportionTest` | exact |
| ఏదైనా పరిమిత మెట్రిక్ (పరిమితి విధించిన ఆదాయం, వాటా) | `BoundedABTest` | exact |
| ఎక్స్‌పోజర్ యూనిట్‌కు సంఘటనలు | `RateRatioTest` | Poisson గణనలకు exact |
| నిష్పత్తి మెట్రిక్ (సెషన్‌కు ఆదాయం) | `RatioABTest` | asymptotic |
| ప్రయోగానికి-ముందు కోవేరియేట్‌తో సగటు (CUPED) | `ABTest` | asymptotic |
| ట్రాఫిక్ ఉద్దేశించినట్లు విభజించబడిందా? | `SampleRatioMismatch` | exact |
| అనేక మెట్రిక్‌లు లేదా శాఖలు (arm) కలిపి | `MultipleTests` (e-BH) | తప్పుడు ఆవిష్కరణ రేటు (false discovery rate), exact |

ప్రతి విధానానికి ఒకసారి ఒక వినియోగదారుని ఇవ్వండి: `state, out = test.step(state, {...})`.
మీకు ఎప్పుడు కావాలంటే అప్పుడు `out.decision` ఆధారంగా చర్య తీసుకోండి.

## కన్వర్షన్: డేటా నిర్ణయాత్మకమైనప్పుడు ఆపండి

నియంత్రణ (control) శాఖలో 10% వినియోగదారులు కన్వర్ట్ అవుతారు, ట్రీట్‌మెంట్ శాఖలో
12%. పరీక్షను ప్రతి వినియోగదారు తర్వాత చూస్తారు, అది తన మొదటి నిర్ణయం వద్ద
ఆగుతుంది:

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

పోలిక కోసం, ఈ పెరుగుదలకు (lift) 80% శక్తి (power) ఉన్న స్థిర-నమూనా పరీక్షకు
(fixed-sample test) ప్రతి శాఖకు సుమారు 3,850 మంది, మొత్తం 7,700 మంది
వినియోగదారులు కావాలి, దానిని చివరలో ఒక్కసారి మాత్రమే చదవవచ్చు.
ఎప్పుడైనా-చెల్లుబాటయ్యే పరీక్ష తన స్వేచ్ఛకు మూల్యం చెల్లిస్తుంది: అదే శక్తిని
చేరడానికి దానికి ఒకే విశ్లేషణ కంటే 1.3–1.6 రెట్లు వినియోగదారులు కావాలి, ఈ
రన్‌కు అంతకంటే ఎక్కువే పట్టింది. బదులుగా ముందుగా నిర్ణయించాల్సిన నమూనా
పరిమాణం ఉండదు, మీరు ప్రతిరోజూ ఫలితాన్ని చూసి అది స్పష్టమైన వెంటనే ఆపవచ్చు.
ప్రభావం (effect) ప్రణాళిక కంటే పెద్దదైనప్పుడు, అది చాలా ముందుగానే జరుగుతుంది.

## ఆదాయం: పరిమిత మెట్రిక్‌కు ఖచ్చితమైన అంతరం

`BoundedABTest` కు మెట్రిక్ పరిమితులు మాత్రమే కావాలి. పరీక్షకు ముందు మీరు
ఎంచుకున్న విలువ వద్ద (ఇక్కడ 30) ఆదాయానికి పరిమితి విధించండి, అప్పుడు సగటుల
తేడాకు విశ్వాస శ్రేణి (confidence sequence) ఏ విభాజనానికైనా (distribution)
ఖచ్చితమైనది (exact):

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

అంతరం చివరిదానిలోనే కాదు, 20,000 చూపుల్లో ప్రతిదానిలోనూ ఒకేసారి నిలుస్తుంది.
ఇక్కడ అది ఇంకా 0 ను కలిగి ఉంది: ఇంత శబ్దభరితమైన (noisy) మెట్రిక్‌పై సుమారు
0.5 పెరుగుదలను స్థాపించడానికి 20,000 వినియోగదారులు సరిపోరు, కాబట్టి ప్రయోగం
కొనసాగుతుంది.

## ముందుగా ట్రాఫిక్ విభజనను తనిఖీ చేయండి

నమూనా నిష్పత్తి అసమతుల్యత (sample ratio mismatch) అంటే విభజన కాన్ఫిగర్ చేసిన
దానికి భిన్నంగా ఉంది, ఉదాహరణకు కేటాయింపులో (assignment) లేదా లాగింగ్‌లో ఉన్న
బగ్ వల్ల. అలాంటి ప్రయోగం నుండి వచ్చే ప్రభావ అంచనాలు నమ్మదగినవి కావు.
50/50 నుండి 52/48 కి అసమతుల్యత ప్రయోగం నడుస్తుండగానే పట్టుబడుతుంది:

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

## ఒకేసారి అనేక మెట్రిక్‌లు

పది స్వతంత్ర మెట్రిక్‌లను ఒక్కొక్కటి 5% వద్ద పరీక్షిస్తే కనీసం ఒక తప్పుడు
ఆవిష్కరణకు సుమారు 40% అవకాశం ఉంటుంది. `MultipleTests` అన్ని పరీక్షల
e-విలువలను (e-value) e-BH విధానంతో కలుపుతుంది, కాబట్టి ఏ ఆపే సమయం (stopping
time) వద్దనైనా తప్పుడు ఆవిష్కరణ రేటు `alpha` వద్దే ఉంటుంది:

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

## జాగ్రత్తలు

* **మీరు విశ్లేషించే యూనిట్‌నే యాదృచ్ఛికీకరించండి (randomise).** వినియోగదారులు
  యాదృచ్ఛికీకరించబడితే, పేజీ వీక్షణకు కాకుండా వినియోగదారుకు ఒక రికార్డు ఇవ్వండి.
  సెషన్-వారీ మెట్రిక్‌లకు `RatioABTest` వాడండి, ఇది వినియోగదారు మొత్తాలపై
  పనిచేస్తుంది.
* **పరిమిత మెట్రిక్ పరిమితిని పరీక్షకు ముందే నిర్ణయించండి.** డేటా చూసిన తర్వాత
  దాన్ని ఎంచుకుంటే హామీ రద్దవుతుంది.
* **asymptotic విధానాలకు పెద్ద నమూనాలు కావాలి.** `ABTest` మరియు
  `RatioABTest` కు అంతరం దీర్ఘ రన్‌లలో మాత్రమే సుమారుగా చెల్లుబాటవుతుంది.
  సరిపోయినప్పుడు exact విధానాలకే ప్రాధాన్యం ఇవ్వండి.
* **అనుకూల ట్రాఫిక్ కేటాయింపుకు (adaptive traffic allocation)** (bandit) విభజన
  ఫలితాలపై ఆధారపడినా చెల్లుబాటయ్యే పరీక్ష కావాలి:
  `TwoProportionTest(method="universal")` లేదా
  `BoundedABTest(propensity_input=...)`. చూడండి
  [ట్యుటోరియల్ §10](../../tutorials/ab-test.md).

మరింత: [A/B పరీక్ష ట్యుటోరియల్](../../tutorials/ab-test.md) (CUPED, నిష్పత్తి
మెట్రిక్‌లు, రేట్లు, వ్యవధి ప్రణాళిక) మరియు
[ప్రయోగాల కార్యక్రమం](../../tutorials/experiment-programme.md)
(అనేక ప్రయోగాలపై తప్పుడు ఆవిష్కరణ రేటు).
