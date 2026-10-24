---
description: Python मध्ये सेन्सर वाचने, विलंब (latency) किंवा मेट्रिक्सच्या प्रवाहातील बदल कसा ओळखावा - CUSUM, Shiryaev–Roberts, अप्राचलिक (nonparametric) e-शोधक आणि बेझियन ऑनलाइन बदल-बिंदू शोध (change-point detection). खोटे इशारे सरासरी धाव लांबीद्वारे (ARL) नियंत्रित, sequential-analysis सह.
language: mr
---

# मोजमापांच्या प्रवाहात झालेला बदल कसा ओळखावा?

> हे [इंग्रजी पानाचे](../../guide/change-detection.md) भाषांतर आहे. मराठी मातृभाषक व्यक्तीने अद्याप त्याचे पुनरावलोकन केलेले नाही; दोन्हींमध्ये फरक आढळल्यास इंग्रजी पान अधिकृत मानावे.

**थोडक्यात उत्तर.** ऑनलाइन बदल-बिंदू शोधक (online change-point detector) वापरा.
तो प्रवाहावर लक्ष ठेवतो आणि वितरण बदललेले दिसताच इशारा (alarm) देतो. त्याचे
खोटे इशारे (false alarms) **सरासरी धाव लांबीद्वारे** (average run length, ARL)
नियंत्रित होतात: काहीही बदललेले नसताना खोट्या इशाऱ्यापर्यंत अपेक्षित
निरीक्षणांची संख्या. sequential-analysis मध्ये:

| बदलापूर्वी तुम्हाला काय माहीत आहे | कार्यपद्धती | हमी |
|---|---|---|
| दोन्ही वितरणे (उदा. सामान्य (normal), सरासरी 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| फक्त सरासरी, आणि मूल्यांच्या मर्यादा | `MeanEDetector` | अशा प्रत्येक वितरणासाठी exact |
| फक्त एक विभाजक (quantile) (उदा. विलंबाचे 95 वे शतमक (percentile)) | `QuantileEDetector` | प्रत्येक वितरणासाठी exact |
| बदलापूर्वी आणि नंतर अज्ञात प्राचलांसह (parameters) एक प्रतिमान | `BayesianChangePoint` | प्रतिमान आणि पूर्व वितरणाखाली (prior) |

## ज्याची सरासरी सरकते असा सेन्सर

एक तापमान सेन्सर 0.5 प्रमाण विचलन (standard deviation) असलेल्या गोंगाटासह
70.0 °C दाखवतो. 600 व्या वाचनापासून सरासरी 70.4 होते. log(1000) ≈ 6.9 उंबरठा
(threshold) असलेल्या CUSUM ची ARL किमान 1,000 वाचने आहे:

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

एका प्रमाण विचलनापेक्षा कमी सरकण कोणत्याही एका वाचनात डोळ्यांना दिसत नाही.
CUSUM पुरावा साठवत जाते आणि ती शोधून काढते.

## वाचने सामान्य वितरणाची नसतात तेव्हा

CUSUM ची ARL तेव्हाच टिकते जेव्हा वाचने तुम्ही दिलेल्या वितरणांनुसार असतात.
तिरप्या (skewed) डेटासाठी (कंपन आयाम, विलंब, रांगेची लांबी) ती नियोजितपेक्षा
कितीतरी जास्त वेळा खोटे इशारे देते. e-शोधकांना (e-detectors) खूप कमी गरज असते:

* `MeanEDetector` ला बदलापूर्वीची सरासरी आणि मूल्यांच्या मर्यादा लागतात.
* `QuantileEDetector` ला फक्त बदलापूर्वीचा एक विभाजक लागतो.

त्या सरासरी किंवा विभाजकाच्या **प्रत्येक** वितरणासाठी त्यांची ARL किमान लक्ष्याइतकी
असते:

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

व्यवहारात बदलापूर्वीचा विभाजक शांत कालावधीवरून अंदाजित केला जातो. मग हमी अंदाजे
टिकते, आणि तो कालावधी जितका लांब तितकी ती चांगली.

## ARL ची निवड

ARL खोटे इशारे आणि विलंब यांच्यात समतोल साधते. दर मिनिटाला एक वाचन असताना,
1,000 वाचनांची ARL म्हणजे सामान्य कार्यकाळात प्रति सेन्सर साधारण दर 17 तासांनी
एक खोटा इशारा. 50 सेन्सर असतील तर ते दिवसाला सुमारे 70 होतात. सर्व सेन्सर
मिळून दिवसाला किती खोटे इशारे तुम्हाला परवडतात त्यावरून ARL निवडा: इथे,
1,000,000 वाचनांची ARL 50 सेन्सरना सुमारे दर दोन आठवड्यांनी एका खोट्या
इशाऱ्यापर्यंत खाली आणते. याची किंमत वाटते त्यापेक्षा कमी आहे, कारण शोध विलंब
ARL च्या फक्त लॉगरिदमसोबत वाढतो. CUSUM साठी उंबरठा 6.9 वरून 13.8 होतो, आणि
विलंब साधारण दुप्पट होतो.

हे शोधक देखरेखीची साधने आहेत, सुरक्षा प्रणाली नव्हेत. प्रमाणित सुरक्षा
उपकरणीय प्रणालीच्या (safety instrumented system) जागी त्यांचा वापर करू नका.

अधिक: [ट्युटोरियल: प्रक्रिया देखरेख आणि बदल शोध](../../tutorials/monitoring.md),
[छुप्या Markov प्रतिमानांसह अवस्था (regimes)](../../tutorials/regimes.md),
[संदर्भ: बदल शोध](../../reference/detection.md).
