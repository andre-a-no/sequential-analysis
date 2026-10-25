---
description: విశ్వాస శ్రేణులు (confidence sequence) అనేవి అన్ని నమూనా పరిమాణాల వద్ద ఒకేసారి చెల్లుబాటయ్యే విశ్వాస అంతరాలు, కాబట్టి వాటిని నిరంతరం పర్యవేక్షించవచ్చు. Python లో పరిమిత సగటు, మధ్యగతం లేదా క్వాంటైల్, మరియు భారీ తోకలున్న (heavy-tailed) సగటు కోసం వాటిని ఎలా లెక్కించాలి, sequential-analysis తో.
language: te
---

# పదే పదే చూసినా చెల్లుబాటయ్యే విశ్వాస అంతరాన్ని ఎలా పొందాలి?

> ఇది [ఆంగ్ల పేజీ](../../guide/confidence-sequences.md)కి అనువాదం. దీనిని ఇంకా తెలుగు మాతృభాషీయులు ఎవరూ సమీక్షించలేదు; రెండింటి మధ్య తేడా ఉన్నచోట ఆంగ్ల పేజీయే ప్రామాణికం.

**సంక్షిప్త సమాధానం.** **విశ్వాస శ్రేణి** (confidence sequence) ని వాడండి. అది
అంతరాల శ్రేణి, ప్రతి పరిశీలన తర్వాత ఒకటి, ఇది కనీసం 95% సంభావ్యతతో అన్ని
నమూనా పరిమాణాల వద్ద ఏకకాలంలో నిజమైన విలువను కలిగి ఉంటుంది. మీరు దానిని
గమనించవచ్చు, అది తగినంత ఇరుకుగా అయినప్పుడు లేదా సున్నాను మినహాయించినప్పుడు
ఆపవచ్చు, మీరు ఆగిన అంతరాన్నే నివేదించవచ్చు. సాధారణ 95% విశ్వాస అంతరం
(confidence interval) ముందుగా నిర్ణయించిన ఒకే నమూనా పరిమాణం వద్ద మాత్రమే
95% ను హామీ ఇస్తుంది.

| మీరు అంచనా వేసేది | ఊహ (assumption) | విధానం | హామీ |
|---|---|---|---|
| పరిమిత డేటా సగటు (రేట్లు, స్కోర్లు, పరిమితి విధించిన ఆదాయం) | విలువలు `[lower, upper]` లో | `BettingConfidenceSequence` | exact |
| మధ్యగతం, 90వ పర్సెంటైల్, ఏదైనా క్వాంటైల్ | ఏదీ లేదు | `QuantileConfidenceSequence` | exact |
| భారీ తోకలు లేదా బాహ్య విలువలతో (outlier) సగటు | ప్రామాణిక విచలనంపై ఒక పరిమితి | `CatoniConfidenceSequence` | exact |
| normal డేటా సగటు, విస్తృతి (variance) తెలియదు | normality | `TMixtureSPRT` (`lower`, `upper`) | normality కింద exact |
| దేనిదైనా సగటు, దీర్ఘ రన్‌లు | పరిమిత విస్తృతి | `AsymptoticConfidenceSequence` | asymptotic |
| రెండు శాఖల మధ్య తేడా | చూడండి [A/B పరీక్షలు](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## గమనిస్తే సాధారణ అంతరం విఫలమవుతుంది

సగటు 0.3 ఉన్న 0/1 చరరాశి యొక్క 500 పరిశీలనలను తీసుకోండి, 30వ దాని నుండి
ప్రతి దాని తర్వాత పాఠ్యపుస్తక 95% అంతరాన్ని లెక్కించండి: సగటు ± 1.96
ప్రామాణిక దోషాలు (standard error). 100 రన్‌లలో ఎన్నింటిలో అంతరం ఏదో ఒక
సమయంలో నిజమైన సగటును తప్పిపోతుంది?

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

దీని "95%" ముందుగా నిర్ణయించిన నమూనా పరిమాణం వద్ద మాత్రమే నిలుస్తుంది. అదే
డేటాకు పందెం (betting) ద్వారా విశ్వాస శ్రేణి (Waudby-Smith and Ramdas 2024)
నిర్మాణం ద్వారానే గరిష్ఠంగా 5% రన్‌లలో ఏదో ఒక n వద్ద తప్పిపోతుంది:

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

## లేటెన్సీ మధ్యగతం, ఏ ఊహా లేకుండా

లేటెన్సీలు వక్రమైనవి (skewed) మరియు భారీ తోకలున్నవి, కాబట్టి వాటికి సగటు ±
ప్రామాణిక దోషం అంతరం నమ్మదగినది కాదు. `QuantileConfidenceSequence` ఏ
విభాజనానికైనా ఏ క్వాంటైల్‌నైనా కవర్ చేస్తుంది, సమాన విలువలు (ties) సహా:

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

నిజమైన విలువలు 120 ms మరియు 258.8 ms. రెండు అంతరాలూ 2,000 నమూనా పరిమాణాల
వద్ద ఒకేసారి నిలుస్తాయి.

## జాగ్రత్తలు

* **పరిమితులు ఊహలో భాగం.** డేటా చూడకముందే `lower` మరియు `upper` ఎంచుకోండి.
  వాటి వెలుపలి విలువ తిరస్కరించబడుతుంది.
* **ఏకపక్ష అపరిమిత డేటా సగటుకు ఏ పద్ధతీ ఖచ్చితమైన కవరేజీ (coverage)
  ఇవ్వదు.** అలాంటి డేటాకు ఒక క్వాంటైల్ వాడండి, విలువలకు పరిమితి విధించండి,
  ప్రామాణిక విచలనంపై ఒక పరిమితిని ఊహించండి (Catoni), లేదా asymptotic శ్రేణిని
  అంగీకరించండి.
* **ఒకే నమూనా పరిమాణం వద్ద విశ్వాస శ్రేణులు ఒకే అంతరం కంటే వెడల్పుగా ఉంటాయి.**
  ఆ వెడల్పే అన్ని నమూనా పరిమాణాల వద్ద ఒకేసారి చెల్లుబాటు కావడానికి మూల్యం.

మరింత: [ఏ పద్ధతి?](../../choosing.md),
[రిఫరెన్స్: ఎప్పుడైనా-చెల్లుబాటయ్యే మరియు అపరామితీయ](../../reference/anytime.md).
