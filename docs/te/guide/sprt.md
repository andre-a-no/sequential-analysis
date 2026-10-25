---
description: Python లో sequential-analysis తో Wald అనుక్రమ లైకలిహుడ్ నిష్పత్తి పరీక్షను (sequential probability ratio test, SPRT) ఎలా నడపాలి. దోష రేట్లు, స్థిర-నమూనా పరీక్షతో పోలిస్తే సగటు నమూనా పరిమాణం, మరియు కత్తిరించిన ప్రత్యామ్నాయాలు (2-SPRT, Kiefer–Weiss అనుకూలతమ ప్రణాళికలు).
language: te
---

# Python లో Wald SPRT ను ఎలా నడపాలి?

> ఇది [ఆంగ్ల పేజీ](../../guide/sprt.md)కి అనువాదం. దీనిని ఇంకా తెలుగు మాతృభాషీయులు ఎవరూ సమీక్షించలేదు; రెండింటి మధ్య తేడా ఉన్నచోట ఆంగ్ల పేజీయే ప్రామాణికం.

**సంక్షిప్త సమాధానం.** `sequential_analysis.procedures` నుండి
`SPRT(family, theta0, theta1, alpha, beta)` Wald అనుక్రమ లైకలిహుడ్ నిష్పత్తి
పరీక్షను (sequential probability ratio test) అమలు చేస్తుంది. ఇది సగటున అతి
తక్కువ పరిశీలనలతో రెండు సరళ పరికల్పనల (simple hypothesis) మధ్య నిర్ణయిస్తుంది.
దానికి ఒకసారి ఒక పరిశీలన ఇచ్చి, మొదటి నిర్ణయం వద్ద ఆపండి. కింది ఉదాహరణలో అదే
దోష రేట్లతో స్థిర-నమూనా పరీక్షకు కావలసిన పరిశీలనలలో సుమారు సగం సరిపోతాయి:
133 కి బదులు సగటున 65–76 వస్తువులు. మీకు హామీ ఉన్న గరిష్ఠ నమూనా పరిమాణం
అవసరమైతే, బదులుగా `TwoSPRT` ను లేదా `kiefer_weiss_plan` నుండి ఒక ప్రణాళికను
వాడండి.

## ఉదాహరణ: లోపాల రేటు 10% ఆ లేక 20% ఆ?

ఒక బ్యాచ్ లోపాల రేటు 10% అయితే అంగీకరించబడుతుంది, 20% అయితే తిరస్కరించబడుతుంది,
రెండు దోష రేట్లూ 5%:

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

అనేక బ్యాచ్‌లపై ఇది ఎంత బాగా పనిచేస్తుంది?

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

అదే దోష రేట్లతో స్థిర-నమూనా పరీక్ష ప్రతి బ్యాచ్‌లో సుమారు 133 వస్తువులను
తనిఖీ చేస్తుంది (normal ఉజ్జాయింపు). SPRT సగటున 43–51% తక్కువ తనిఖీ చేస్తుంది.
అయితే దాని నమూనా పరిమాణం యాదృచ్ఛికమైనది మరియు దానికి ఎగువ పరిమితి లేదు,
కొన్ని బ్యాచ్‌లకు సగటు కంటే చాలా ఎక్కువ సమయం పడుతుంది.

పరిమితులు (threshold) Wald వి: log((1 − β)/α) మరియు log(β/(1 − α)). ఆపే సమయంలో
ఏ నమూనా పరిమాణానికైనా, వాస్తవ దోష రేట్లు α′ మరియు β′
α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) మరియు α′ + β′ ≤ α + β ను సంతృప్తిపరుస్తాయని అవి
హామీ ఇస్తాయి. ఆగినప్పుడు లైకలిహుడ్ నిష్పత్తి పరిమితులను దాటిపోతుంది (overshoot),
కాబట్టి ఆచరణలో రేట్లు నామమాత్ర (nominal) రేట్ల కంటే తక్కువగా ఉంటాయి, ఇక్కడ లాగానే.
`SPRT.guarantee == "exact"` యొక్క అర్థం అదే. పరిమితం చేయడం కాకుండా ఖచ్చితంగా
లెక్కించిన దోష రేట్ల కోసం, ఒక ప్రణాళికపై `operating_characteristic` వాడండి (కింద).

## మీకు గరిష్ఠ నమూనా పరిమాణం అవసరమైనప్పుడు

* `TwoSPRT` (Lorden's 2-SPRT) ఒక స్థిర క్షితిజం (horizon) లోపల ఆగుతుంది మరియు
  చెత్త-సందర్భ ఆశించిన నమూనా పరిమాణాన్ని దాదాపు కనిష్ఠం చేస్తుంది.
* `sequential_analysis.design` లోని
  `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  వెనుకబాటు ప్రేరణ (backward induction) ద్వారా గరిష్ఠ నమూనా పరిమాణంతో అనుకూలతమ
  ప్రణాళికను లెక్కిస్తుంది. `PlanTest` దానిని అమలు చేస్తుంది, మరియు
  `operating_characteristic` సిమ్యులేషన్ లేకుండా దాని ఖచ్చితమైన దోష రేట్లను
  మరియు ఆశించిన నమూనా పరిమాణాన్ని ఇస్తుంది. చూడండి
  `examples/07_design_kiefer_weiss.py`.
* ప్రతి పరిశీలనకు ఒక చూపు కాకుండా కొన్ని ప్రణాళిక చేసిన చూపుల కోసం,
  [సమూహ అనుక్రమ రూపకల్పన](clinical-trials.md) వాడండి.

## SPRT తప్పు సాధనం అయినప్పుడు

* **పరికల్పనలు సరళమైనవి కావు.** "రేటు 10%" కు వ్యతిరేకంగా "రేటు ఇంకేదైనా"
  అనేది సంయుక్త ప్రత్యామ్నాయం (composite alternative). మిశ్రమ SPRT
  (`NormalMixtureSPRT`, `TMixtureSPRT`) లేదా పందెం ద్వారా పరీక్ష (`BettingMeanTest`)
  వాడండి, ఇవి ప్రతి ప్రత్యామ్నాయానికి వ్యతిరేకంగా ఎప్పుడైనా-చెల్లుబాటయ్యేవి.
* **నిజమైన విలువ θ₀ మరియు θ₁ మధ్య ఉంది.** అప్పుడు SPRT అత్యంత నెమ్మదిగా
  ఉంటుంది, దాని ఆశించిన నమూనా పరిమాణం స్థిర-నమూనా పరిమాణాన్ని మించవచ్చు.
  Kiefer–Weiss ప్రణాళిక సరిగ్గా ఈ సందర్భం కోసమే నిర్మించబడింది.

లైకలిహుడ్-నిష్పత్తి విధానాలకు అందుబాటులో ఉన్న కుటుంబాలు (family): `Gaussian`
(తెలిసిన విస్తృతి), `Bernoulli`, `Poisson`, `Exponential`.
