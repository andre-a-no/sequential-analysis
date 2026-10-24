---
description: Python లో సెన్సార్ రీడింగ్‌లు, లేటెన్సీలు లేదా మెట్రిక్‌ల ప్రవాహంలో మార్పును ఎలా గుర్తించాలి, CUSUM, Shiryaev–Roberts, అపరామితీయ e-డిటెక్టర్లు (e-detector) మరియు బేయేసియన్ ఆన్‌లైన్ మార్పు-బిందువు గుర్తింపు (change-point detection) తో. సగటు రన్ పొడవు (average run length, ARL) ద్వారా తప్పుడు అలారాలు నియంత్రించబడతాయి, sequential-analysis తో.
language: te
---

# కొలతల ప్రవాహంలో మార్పును ఎలా గుర్తించాలి?

> ఇది [ఆంగ్ల పేజీ](../../guide/change-detection.md)కి అనువాదం. దీనిని ఇంకా తెలుగు మాతృభాషీయులు ఎవరూ సమీక్షించలేదు; రెండింటి మధ్య తేడా ఉన్నచోట ఆంగ్ల పేజీయే ప్రామాణికం.

**సంక్షిప్త సమాధానం.** ఆన్‌లైన్ మార్పు-బిందువు డిటెక్టర్‌ను (change-point
detector) వాడండి. అది ప్రవాహాన్ని గమనిస్తూ, విభాజనం (distribution) మారినట్లు
కనిపించిన వెంటనే అలారం ఇస్తుంది. దాని తప్పుడు అలారాలు (false alarm) **సగటు
రన్ పొడవు** (average run length, ARL) ద్వారా నియంత్రించబడతాయి: ఏదీ మారనప్పుడు
ఒక తప్పుడు అలారం వరకు ఆశించిన పరిశీలనల సంఖ్య. sequential-analysis లో:

| మార్పుకు ముందు మీకు తెలిసినది | విధానం | హామీ |
|---|---|---|
| రెండు విభాజనాలూ (ఉదా. normal, సగటు 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| సగటు మాత్రమే, మరియు విలువల పరిమితులు | `MeanEDetector` | అలాంటి ప్రతి విభాజనానికీ exact |
| ఒక క్వాంటైల్ మాత్రమే (ఉదా. లేటెన్సీ యొక్క 95వ పర్సెంటైల్) | `QuantileEDetector` | ప్రతి విభాజనానికీ exact |
| మార్పుకు ముందు మరియు తర్వాత తెలియని పరామితులతో ఒక మోడల్ | `BayesianChangePoint` | మోడల్ మరియు పూర్వ విభాజనం (prior) కింద |

## సగటు జరిగే సెన్సార్

ఒక ఉష్ణోగ్రత సెన్సార్ 70.0 °C చూపిస్తుంది, దాని శబ్దం (noise) ప్రామాణిక విచలనం
(standard deviation) 0.5. 600వ రీడింగ్ నుండి సగటు 70.4. log(1000) ≈ 6.9 పరిమితి
(threshold) తో CUSUM కు ARL కనీసం 1,000 రీడింగ్‌లు:

```python
import math
import random

from sequential_analysis.procedures import CUSUM, Gaussian

rnd = random.Random(1)
readings = [rnd.gauss(70.0, 0.5) for _ in range(600)] + [rnd.gauss(70.4, 0.5) for _ in range(400)]

detector = CUSUM(Gaussian(sigma=0.5), theta0=70.0, theta1=70.4, threshold=math.log(1000))
state = detector.initial_state()
for t, x in enumerate(readings, start=1):
    state, out = detector.step(state, {"x": x})
    if out.alarm:
        print(f"alarm at reading {t}, {t - 600} readings after the shift")
        break
```

```text
alarm at reading 615, 15 readings after the shift
```

ఒక ప్రామాణిక విచలనం కంటే తక్కువ జరుగుదల ఏ ఒక్క రీడింగ్‌లోనూ కంటికి కనిపించదు.
CUSUM సాక్ష్యాన్ని పోగుచేసి దాన్ని కనుగొంటుంది.

## రీడింగ్‌లు normal కానప్పుడు

రీడింగ్‌లు మీరు ఇచ్చిన విభాజనాలను పాటిస్తేనే CUSUM యొక్క ARL నిలుస్తుంది. వక్ర
(skewed) డేటాకు (కంపన విస్తారాలు, లేటెన్సీలు, క్యూ పొడవులు) ఇది ప్రణాళిక కంటే
చాలా తరచుగా తప్పుడు అలారాలు ఇస్తుంది. e-డిటెక్టర్లకు (e-detector) చాలా తక్కువ
కావాలి:

* `MeanEDetector` కు మార్పుకు ముందు సగటు మరియు విలువల పరిమితులు కావాలి.
* `QuantileEDetector` కు మార్పుకు ముందు ఒక క్వాంటైల్ మాత్రమే కావాలి.

ఆ సగటు లేదా క్వాంటైల్ ఉన్న **ప్రతి** విభాజనానికీ వాటి ARL కనీసం లక్ష్యమంత
ఉంటుంది:

```python
from sequential_analysis.procedures import QuantileEDetector

rnd = random.Random(2)
vibration = [rnd.lognormvariate(0.0, 0.8) for _ in range(800)] + [rnd.lognormvariate(0.5, 0.8) for _ in range(400)]
q95 = math.exp(0.8 * 1.6449)          # the 95th percentile before the change
p95 = QuantileEDetector(q0=q95, p=0.95, arl=1000, direction="increase", statistic="cusum")
state = p95.initial_state()
for t, x in enumerate(vibration, start=1):
    state, out = p95.step(state, {"x": x})
    if out.alarm:
        print(f"the 95th percentile rose: alarm at reading {t}, {t - 800} readings after the change")
        break
```

```text
the 95th percentile rose: alarm at reading 887, 87 readings after the change
```

ఆచరణలో మార్పుకు ముందు క్వాంటైల్‌ను ఒక ప్రశాంత కాలం నుండి అంచనా వేస్తారు.
అప్పుడు హామీ సుమారుగా నిలుస్తుంది, ఆ కాలం ఎంత పొడవైతే అంత మెరుగ్గా.

## ARL ను ఎంచుకోవడం

ARL తప్పుడు అలారాలు మరియు ఆలస్యం మధ్య సమతుల్యం చేస్తుంది. నిమిషానికి ఒక
రీడింగ్ అయితే, 1,000 రీడింగ్‌ల ARL అంటే సాధారణ పనితీరులో ప్రతి సెన్సార్‌కు
సుమారు ప్రతి 17 గంటలకు ఒక తప్పుడు అలారం. 50 సెన్సార్లతో అది రోజుకు సుమారు 70.
అన్ని సెన్సార్లు కలిపి రోజుకు మీరు భరించగలిగే తప్పుడు అలారాల సంఖ్య నుండి ARL
ను ఎంచుకోండి: ఇక్కడ, 1,000,000 రీడింగ్‌ల ARL 50 సెన్సార్లను సుమారు ప్రతి రెండు
వారాలకు ఒక తప్పుడు అలారానికి తగ్గిస్తుంది. దీని ఖర్చు కనిపించేంత కాదు, ఎందుకంటే
గుర్తింపు ఆలస్యం ARL యొక్క సంవర్గమానంతో (logarithm) మాత్రమే పెరుగుతుంది.
CUSUM కు పరిమితి 6.9 నుండి 13.8 కి వెళ్తుంది, ఆలస్యం సుమారు రెట్టింపు అవుతుంది.

ఈ డిటెక్టర్లు పర్యవేక్షణ (monitoring) సాధనాలు, భద్రతా వ్యవస్థలు కావు. ధృవీకరించబడిన
భద్రతా సాధన వ్యవస్థ (safety instrumented system) స్థానంలో వీటిని వాడకండి.

మరింత: [ట్యుటోరియల్: ప్రక్రియ పర్యవేక్షణ మరియు మార్పు గుర్తింపు](../../tutorials/monitoring.md),
[దాగిన మార్కోవ్ మోడల్‌లతో రెజీమ్‌లు](../../tutorials/regimes.md),
[రిఫరెన్స్: మార్పు గుర్తింపు](../../reference/detection.md).
