---
description: A/B పరీక్షలు మరియు ట్రయల్స్‌లో ప్రతిరోజూ p-విలువను తనిఖీ చేయడం తప్పుడు పాజిటివ్‌లను (false positive) ఎందుకు పెంచుతుంది (తొంగిచూసే సమస్య, peeking problem), మరియు దానిని సరిదిద్దే అనుక్రమ పద్ధతుల మూడు కుటుంబాలు, Python లో sequential-analysis తో.
language: te
---

# నేను ప్రతిరోజూ p-విలువను ఎందుకు చూడకూడదు?

> ఇది [ఆంగ్ల పేజీ](../../guide/peeking.md)కి అనువాదం. దీనిని ఇంకా తెలుగు మాతృభాషీయులు ఎవరూ సమీక్షించలేదు; రెండింటి మధ్య తేడా ఉన్నచోట ఆంగ్ల పేజీయే ప్రామాణికం.

**సంక్షిప్త సమాధానం.** స్థిర-నమూనా పరీక్ష (fixed-sample test) 5% తప్పుడు-పాజిటివ్
రేటును (false-positive rate) హామీ ఇచ్చేది మీరు ఫలితాన్ని ఒక్కసారి, ప్రణాళిక
చేసిన నమూనా పరిమాణం వద్ద చూసినప్పుడు మాత్రమే. మీరు పదే పదే చూసి, మొదటిసారి
p < 0.05 అయినప్పుడు ఆపితే, మోసపోవడానికి మీకు చాలా అవకాశాలు వస్తాయి. 20 చూపులతో
తప్పుడు-పాజిటివ్ రేటు సుమారు 25% కి పెరుగుతుంది. అనుక్రమ పద్ధతులు (sequential
methods) పదే పదే చూడటం కోసమే నిర్మించబడ్డాయి. వాటితో మీరు ఎన్నిసార్లు చూసినా,
ఎప్పుడు ఆపినా రేటు 5% వద్ద లేదా అంతకంటే తక్కువగా ఉంటుంది.

## తొంగిచూసే సమస్య, కొలిచి చూపితే

ఒకే 10% కన్వర్షన్ రేటుతో రెండు శాఖలు (ఒక A/A పరీక్ష), 2,000 వినియోగదారులు,
200 పునరావృత్తులు. "తొంగిచూడటం" (peeking) ప్రతి 100 వినియోగదారుల తర్వాత సాధారణ
రెండు-నిష్పత్తుల z-పరీక్షను నడిపి, మొదటి p < 0.05 వద్ద ఆగుతుంది. అనుక్రమ
`TwoProportionTest` ను ప్రతి ఒక్క వినియోగదారు తర్వాత తనిఖీ చేస్తారు:

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

ఒక్క చూపు తన వాగ్దానాన్ని నిలబెట్టుకుంటుంది. ఇరవై చూపులు దోష రేటును సుమారు
ఆరు రెట్లు పెంచుతాయి. అనుక్రమ పరీక్ష, 2,000 వినియోగదారులలో ప్రతి ఒక్కరి తర్వాత
చూసినా, దానిని 5% వద్ద ఉంచుతుంది. అదే వాగ్దానం: దాని హామీ **exact**
(`TwoProportionTest.guarantee == "exact"`), అంటే మీరు ఎన్నిసార్లు చూసినా, ప్రతి
నమూనా పరిమాణం వద్ద గరిష్ఠంగా 5% తప్పుడు-పాజిటివ్ రేటు. 200 పునరావృత్తులతో,
10 తప్పుడు పాజిటివ్‌లు exact 5% ఇచ్చేదే.

## అనుక్రమ పద్ధతుల మూడు కుటుంబాలు

| కుటుంబం | మీరు చూడవచ్చు | సాధారణ వినియోగం | sequential-analysis లో |
|---|---|---|---|
| **అనుక్రమ లైకలిహుడ్ నిష్పత్తి పరీక్షలు (sequential probability ratio test)** (Wald 1945) | ప్రతి పరిశీలన తర్వాత | ఒక సరళ పరికల్పనకు వ్యతిరేకంగా మరొకటి, సగటున అతి తక్కువ పరిశీలనలు: నాణ్యతా నియంత్రణ, సిమ్యులేషన్, సైకోఫిజిక్స్ | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **సమూహ అనుక్రమ రూపకల్పనలు (group sequential design)** (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | కొన్ని ప్రణాళిక చేసిన మధ్యంతర విశ్లేషణల వద్ద | డేటా పర్యవేక్షణ కమిటీతో క్లినికల్ ట్రయల్స్ | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **ఎప్పుడైనా-చెల్లుబాటయ్యే అనుమితి (anytime-valid inference)**: e-విలువలు, విశ్వాస శ్రేణులు, మిశ్రమ SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | ప్రతి పరిశీలన తర్వాత, ఏ కారణంతోనైనా ఆపడం | ఆన్‌లైన్ A/B పరీక్షలు, పర్యవేక్షణ డ్యాష్‌బోర్డ్‌లు | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**దీని ఖర్చు ఎంత.** ఎక్కువసార్లు చూడటానికి ప్రణాళిక చేసిన ప్రభావం వద్ద ఎక్కువ
డేటా కావాలి:

* నాలుగు విశ్లేషణలతో సమూహ అనుక్రమ రూపకల్పనకు ఒకే విశ్లేషణ కంటే 1–20% ఎక్కువ
  రోగులు కావాలి;
* రెండు నిష్పత్తుల ఎప్పుడైనా-చెల్లుబాటయ్యే పరీక్షకు ఒకే విశ్లేషణ కంటే 1.3–1.6
  రెట్లు వినియోగదారులు కావాలి.

బదులుగా, పెద్ద ప్రభావం ప్రయోగాన్ని ముందుగానే ఆపుతుంది, ఎవరూ నమూనా పరిమాణాన్ని
ముందుగా నిర్ణయించాల్సిన అవసరం లేదు.

## ఇది సమస్య కానప్పుడు

మీరు చేసేది మీరు చూసినదానిపై ఆధారపడినప్పుడు మాత్రమే తొంగిచూడటం దోషాలను పెంచుతుంది.
మీరు డ్యాష్‌బోర్డ్‌ను చూసినా ఎల్లప్పుడూ ప్రయోగాన్ని దాని ప్రణాళిక చేసిన పరిమాణం వరకు
నడిపి ఒక్కసారే పరీక్షిస్తే, స్థిర-నమూనా పరీక్ష చెల్లుబాటవుతుంది. ఆ సందర్భంలో
అదే అత్యంత సమర్థవంతమైన ఎంపిక కూడా.

తర్వాత: [A/B పరీక్షను ముందుగానే ఆపండి](ab-testing.md),
[విశ్వాస శ్రేణులు](confidence-sequences.md),
[పదకోశం](glossary.md).
