---
description: Python में सेंसर रीडिंग, लेटेंसी या मेट्रिक्स की स्ट्रीम में बदलाव का पता कैसे लगाएँ, CUSUM, Shiryaev–Roberts, नॉनपैरामेट्रिक e-detectors और Bayesian ऑनलाइन परिवर्तन-बिंदु पहचान के साथ। झूठे अलार्म औसत रन लंबाई (ARL) से नियंत्रित, sequential-analysis के साथ।
language: hi
---

# मापों की स्ट्रीम में बदलाव का पता कैसे लगाएँ?

> यह [अंग्रेज़ी पृष्ठ](../../guide/change-detection.md) का अनुवाद है। इसकी समीक्षा अभी किसी मूल हिंदी भाषी ने नहीं की है; जहाँ दोनों में अंतर हो, वहाँ अंग्रेज़ी पृष्ठ ही प्रामाणिक है।

**संक्षिप्त उत्तर।** एक ऑनलाइन परिवर्तन-बिंदु डिटेक्टर (online change-point
detector) इस्तेमाल करें। यह स्ट्रीम पर नज़र रखता है और जैसे ही वितरण बदला
हुआ लगता है, अलार्म देता है। इसके झूठे अलार्म (false alarms) **औसत रन लंबाई
(average run length, ARL)** से नियंत्रित होते हैं: जब कुछ नहीं बदला हो, तब
झूठे अलार्म तक प्रेक्षणों की अपेक्षित संख्या। sequential-analysis में:

| बदलाव से पहले आप क्या जानते हैं | प्रक्रिया | गारंटी |
|---|---|---|
| दोनों वितरण (जैसे normal, माध्य 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| केवल माध्य, और मानों की सीमाएँ | `MeanEDetector` | ऐसे हर वितरण के लिए exact |
| केवल एक क्वांटाइल (जैसे लेटेंसी का 95वाँ पर्सेंटाइल) | `QuantileEDetector` | हर वितरण के लिए exact |
| अज्ञात पैरामीटरों वाला मॉडल, पहले और बाद में | `BayesianChangePoint` | मॉडल और प्रायर (prior) के अंतर्गत |

## एक सेंसर जिसका माध्य खिसकता है

एक तापमान सेंसर 70.0 °C पढ़ता है, जिसमें शोर (noise) का मानक विचलन (standard
deviation) 0.5 है। रीडिंग 600 से आगे माध्य 70.4 है। थ्रेशोल्ड log(1000) ≈ 6.9
वाले CUSUM का ARL कम से कम 1,000 रीडिंग है:

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

एक मानक विचलन से कम का खिसकाव किसी भी एक रीडिंग में आँख से दिखाई नहीं देता।
CUSUM साक्ष्य (evidence) जमा करता है और उसे ढूँढ लेता है।

## जब रीडिंग normal न हों

CUSUM का ARL तभी बना रहता है जब रीडिंग उन वितरणों का पालन करें जो आपने उसे
दिए। तिरछे (skewed) डेटा (कंपन के आयाम, लेटेंसी, कतार की लंबाई) के लिए यह
योजना से कहीं अधिक बार झूठे अलार्म देता है। e-detectors को बहुत कम चाहिए:

* `MeanEDetector` को बदलाव से पहले का माध्य और मानों की सीमाएँ चाहिए।
* `QuantileEDetector` को बदलाव से पहले का केवल एक क्वांटाइल चाहिए।

उनका ARL उस माध्य या क्वांटाइल वाले **हर** वितरण के लिए कम से कम लक्ष्य जितना
है:

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

व्यवहार में बदलाव से पहले का क्वांटाइल किसी शांत अवधि से अनुमानित किया जाता
है। तब गारंटी लगभग बनी रहती है, और वह अवधि जितनी लंबी हो, उतनी बेहतर।

## ARL का चुनाव

ARL झूठे अलार्मों और देरी के बीच संतुलन बनाता है। प्रति मिनट एक रीडिंग पर,
1,000 रीडिंग के ARL का अर्थ है सामान्य संचालन के लगभग हर 17 घंटे में एक झूठा
अलार्म, प्रति सेंसर। 50 सेंसरों के साथ यह दिन में लगभग 70 होते हैं। ARL इस
आधार पर चुनें कि सभी सेंसरों को मिलाकर प्रति दिन आप कितने झूठे अलार्म सह
सकते हैं: यहाँ, 1,000,000 रीडिंग का ARL 50 सेंसरों को लगभग हर दो हफ़्ते में
एक झूठे अलार्म तक ले आता है। इसकी कीमत जितनी लगती है उससे कम है, क्योंकि
पहचान की देरी ARL के केवल लघुगणक (logarithm) के साथ बढ़ती है। CUSUM के लिए
थ्रेशोल्ड 6.9 से 13.8 हो जाता है, और देरी लगभग दोगुनी हो जाती है।

ये डिटेक्टर मॉनिटरिंग टूल हैं, सुरक्षा प्रणालियाँ नहीं। इन्हें किसी प्रमाणित
safety instrumented system की जगह इस्तेमाल न करें।

और: [ट्यूटोरियल: प्रोसेस मॉनिटरिंग और परिवर्तन पहचान](../../tutorials/monitoring.md),
[hidden Markov मॉडल के साथ रेजीम](../../tutorials/regimes.md),
[संदर्भ: परिवर्तन पहचान](../../reference/detection.md)।
