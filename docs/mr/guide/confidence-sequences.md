---
description: विश्वास्यता अनुक्रम (confidence sequences) हे असे विश्वास्यता अंतराल आहेत जे एकाच वेळी प्रत्येक नमुना आकारावर वैध राहतात, त्यामुळे त्यांच्यावर सतत देखरेख करता येते. Python मध्ये मर्यादित सरासरी, मध्यका किंवा विभाजक (quantile), आणि जड पुच्छ असलेली सरासरी यांसाठी ते कसे गणन करावे, sequential-analysis सह.
language: mr
---

# वारंवार पाहत राहिले तरी वैध राहणारा विश्वास्यता अंतराल कसा मिळवावा?

> हे [इंग्रजी पानाचे](../../guide/confidence-sequences.md) भाषांतर आहे. मराठी मातृभाषक व्यक्तीने अद्याप त्याचे पुनरावलोकन केलेले नाही; दोन्हींमध्ये फरक आढळल्यास इंग्रजी पान अधिकृत मानावे.

**थोडक्यात उत्तर.** **विश्वास्यता अनुक्रम** (confidence sequence) वापरा. हा
अंतरालांचा अनुक्रम आहे, प्रत्येक निरीक्षणानंतर एक, ज्यात खरे मूल्य किमान 95%
संभाव्यतेने सर्व नमुना आकारांवर एकाच वेळी असते. तुम्ही त्यावर लक्ष ठेवू शकता,
तो पुरेसा अरुंद झाल्यावर किंवा शून्य वगळल्यावर थांबू शकता, आणि जिथे थांबलात तो
अंतराल नोंदवू शकता. नेहमीचा 95% विश्वास्यता अंतराल (confidence interval) 95% चे
वचन फक्त आधीपासून ठरवलेल्या एकाच नमुना आकारावर देतो.

| तुम्ही काय अंदाजता | गृहीतक | कार्यपद्धती | हमी |
|---|---|---|---|
| मर्यादित डेटाची सरासरी (दर, गुण, कमाल मर्यादा लावलेला महसूल) | मूल्ये `[lower, upper]` मध्ये | `BettingConfidenceSequence` | exact |
| मध्यका (median), 90 वे शतमक (percentile), कोणताही विभाजक (quantile) | काहीही नाही | `QuantileConfidenceSequence` | exact |
| जड पुच्छ (heavy tails) किंवा बहिःस्थ मूल्ये (outliers) असलेली सरासरी | प्रमाण विचलनावर एक मर्यादा | `CatoniConfidenceSequence` | exact |
| सामान्य (normal) डेटाची सरासरी, विचरण (variance) अज्ञात | सामान्यता | `TMixtureSPRT` (`lower`, `upper`) | सामान्यतेखाली exact |
| कशाचीही सरासरी, लांब रन | सांत विचरण | `AsymptoticConfidenceSequence` | asymptotic |
| दोन शाखांमधील फरक | पाहा [A/B चाचण्या](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## लक्ष ठेवल्यास नेहमीचा अंतराल अपयशी ठरतो

सरासरी 0.3 असलेल्या 0/1 चलाची 500 निरीक्षणे घ्या, आणि 30 व्यापासून पुढे
प्रत्येकानंतर पाठ्यपुस्तकी 95% अंतराल गणन करा: सरासरी ± 1.96 प्रमाण त्रुटी
(standard errors). 100 रनपैकी किती रनमध्ये अंतराल कधीतरी खरी सरासरी चुकवतो?

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

त्याचे "95%" फक्त आधीपासून ठरवलेल्या नमुना आकारावरच टिकते. त्याच डेटासाठी पैजेद्वारे
(by betting) मिळणारा विश्वास्यता अनुक्रम (Waudby-Smith and Ramdas 2024) रचनेनुसारच
जास्तीत जास्त 5% रनमध्ये कधीतरी n वर चुकतो:

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

## कोणत्याही गृहीतकाशिवाय मध्यका विलंब

विलंब (latencies) तिरपे आणि जड-पुच्छ असतात, त्यामुळे त्यांच्यासाठी सरासरी ±
प्रमाण त्रुटी हा अंतराल विश्वासार्ह नाही. `QuantileConfidenceSequence` कोणत्याही
वितरणाचा कोणताही विभाजक व्यापते, समान मूल्यांसह (ties):

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

खरी मूल्ये 120 ms आणि 258.8 ms आहेत. दोन्ही अंतराल सर्व 2,000 नमुना आकारांवर
एकाच वेळी टिकतात.

## सापळे

* **मर्यादा आणि कमाल मर्यादा गृहीतकाचा भाग आहेत.** `lower` आणि `upper` डेटा
  पाहण्यापूर्वी निवडा. त्यांच्या बाहेरील मूल्य नाकारले जाते.
* **अनियंत्रित अमर्यादित डेटाच्या सरासरीसाठी कोणतीही पद्धत अचूक व्याप्ती
  (coverage) देत नाही.** अशा डेटासाठी विभाजक वापरा, मूल्यांवर कमाल मर्यादा लावा,
  प्रमाण विचलनावर मर्यादा गृहीत धरा (Catoni), किंवा asymptotic अनुक्रम स्वीकारा.
* **त्याच नमुना आकारावर विश्वास्यता अनुक्रम एकाच अंतरालापेक्षा रुंद असतात.**
  ही रुंदी म्हणजे एकाच वेळी प्रत्येक नमुना आकारावर वैध असण्याची किंमत.

अधिक: [कोणती पद्धत?](../../choosing.md),
[संदर्भ: कधीही-वैध आणि अप्राचलिक (nonparametric)](../../reference/anytime.md).
