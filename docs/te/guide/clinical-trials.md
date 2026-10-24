---
description: Python లో క్లినికల్ ట్రయల్ మధ్యంతర విశ్లేషణలను (interim analysis) ఎలా ప్రణాళిక చేసి నడపాలి, సమూహ అనుక్రమ రూపకల్పనలతో (group sequential design) (O'Brien–Fleming, Pocock, Lan–DeMets ఆల్ఫా వ్యయం, నిష్ఫలత సరిహద్దులు), సగటులు, నిష్పత్తులు మరియు మనుగడ (survival) కోసం నమూనా పరిమాణాలు, rpact తో సరిచూడబడినవి, sequential-analysis తో.
language: te
---

# క్లినికల్ ట్రయల్ మధ్యంతర విశ్లేషణలను ఎలా ప్రణాళిక చేయాలి?

> ఇది [ఆంగ్ల పేజీ](../../guide/clinical-trials.md)కి అనువాదం. దీనిని ఇంకా తెలుగు మాతృభాషీయులు ఎవరూ సమీక్షించలేదు; రెండింటి మధ్య తేడా ఉన్నచోట ఆంగ్ల పేజీయే ప్రామాణికం.

**సంక్షిప్త సమాధానం.** సమూహ అనుక్రమ రూపకల్పనను (group sequential design) వాడండి.
`sequential_analysis.group_sequential` నుండి
`group_sequential_design(alpha, fractions, spending=...)` లెక్కిస్తుంది:

* సమర్థత సరిహద్దులు (efficacy boundary), Lan–DeMets ఆల్ఫా వ్యయంతో (alpha
  spending) (O'Brien–Fleming రకం, Pocock రకం మరియు ఇతరాలు);
* బంధనరహిత (non-binding) నిష్ఫలత సరిహద్దులు (futility boundary);
* శక్తి (power) మరియు ఆశించిన నమూనా పరిమాణం;
* సగటులు మరియు నిష్పత్తులకు గరిష్ఠ నమూనా పరిమాణం, లేదా మనుగడ (survival)
  కోసం సంఘటనల (event) సంఖ్య.

సరిహద్దులు మరియు నమూనా పరిమాణాలు R ప్యాకేజీ rpact తో ఏకీభవిస్తాయి. తర్వాత
పరీక్షా విధానాలు (`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) ట్రయల్‌ను రోగి వారీగా
లేదా సంఘటన వారీగా నడుపుతాయి. ప్రతి మధ్యంతర విశ్లేషణను దాని సమాచార భిన్నం
(information fraction) చేరినప్పుడు అవి నిర్వహిస్తాయి.

## రూపకల్పన: నాలుగు విశ్లేషణలు, O'Brien–Fleming వ్యయం

ఏకపార్శ్వ (one-sided) α = 0.025, రోగులలో 25%, 50%, 75% మరియు 100% వద్ద
విశ్లేషణలు, 90% శక్తి, ఒక నిష్ఫలత సరిహద్దుతో:

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

## ద్వియాంశ (binary) మరియు మనుగడ ఎండ్‌పాయింట్‌లు (endpoint)

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

O'Brien–Fleming వ్యయంతో, మూడు విశ్లేషణలకు ఒకే తుది విశ్లేషణ కంటే 1.3% ఎక్కువ
రోగులు ఖర్చవుతారు.

## ట్రయల్‌ను నడపడం

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

ప్రణాళిక చేసిన రోగులలో మూడింట రెండు వంతుల తర్వాత, రెండవ విశ్లేషణ వద్ద
సమర్థత కారణంగా ట్రయల్ ఆగిపోయింది.

## విశ్లేషణలు ప్రణాళిక ప్రకారం జరగనప్పుడు

డేటా పర్యవేక్షణ కమిటీలు (data monitoring committee) అరుదుగా సరిగ్గా 25%
సమాచారం వద్ద సమావేశమవుతాయి:

* `design.at(fractions)` వాస్తవంగా చేరిన సమాచారానికి సరిహద్దులను మళ్లీ
  లెక్కిస్తుంది. ఆల్ఫా వ్యయం మొత్తం స్థాయిని (level) కాపాడుతుంది.
* `GroupSequentialMonitor` ప్రతి సమావేశంలో మీరే లెక్కించిన ఏ గణాంకాన్నైనా
  (ఒక Cox మోడల్, ఒక మిశ్రమ మోడల్ (mixed model)) Z విలువగా మరియు దాని
  సమాచారాన్ని తీసుకుంటుంది.

## మరి ప్రతి రోగి తర్వాత చూడాలనుకుంటే?

సమూహ అనుక్రమ రూపకల్పన ప్రణాళిక చేసిన సంఖ్యలో మాత్రమే చూపులను అనుమతిస్తుంది.
ప్రతి రోగి లేదా సంఘటన తర్వాత పర్యవేక్షించడానికి ఎప్పుడైనా-చెల్లుబాటయ్యే
(anytime-valid) విధానాన్ని వాడండి: మనుగడకు `AnytimeLogRankTest`, ప్రతిస్పందన
రేట్లకు `TwoProportionTest`, సగటుకు `TMixtureSPRT`. ప్రణాళిక చేసిన ప్రభావం వద్ద
వీటికి ఎక్కువ రోగులు కావాలి. చూడండి [ట్యుటోరియల్: మనుగడ ట్రయల్](../../tutorials/survival.md).

## నియంత్రణ ఆచరణ

ఆల్ఫా వ్యయంతో సమూహ అనుక్రమ రూపకల్పనలు నిర్ధారణాత్మక (confirmatory) ట్రయల్స్‌లో
స్థిరపడిన విధానం, ICH E9 మార్గదర్శకం మరియు అనుకూల రూపకల్పనలపై (adaptive design)
FDA మార్గదర్శనంలో (2019) వివరించబడింది. ఈ లైబ్రరీ రూపకల్పనలను లెక్కిస్తుంది
మరియు ప్రతి విశ్లేషణకు ఆడిట్ చేయదగిన, తిరిగి ప్రారంభించదగిన రికార్డును
ఉంచుతుంది (చెక్‌పాయింట్ మరియు దాని హిస్టరీ డైజెస్ట్ (history digest)). ఇది
నియంత్రణ అర్థంలో ధృవీకరించబడిన (validated) సాఫ్ట్‌వేర్ కాదు: సమర్పణలో
(submission) దీనిని వాడే స్పాన్సర్ ఇతర ఏ సాధనం లాగానే దీనిని ధృవీకరించాలి.

మరింత: [ట్యుటోరియల్: సమూహ అనుక్రమ ట్రయల్](../../tutorials/group-sequential.md),
ఇది సంఖ్యలను rpact తో పోలుస్తుంది;
[రిఫరెన్స్: రూపకల్పన మరియు ప్రణాళిక](../../reference/design.md).
