---
description: Python में फ़ॉल्स पॉज़िटिव बढ़ाए बिना A/B टेस्ट को जल्दी कैसे रोकें। कन्वर्ज़न और सीमित (bounded) रेवेन्यू के लिए anytime-valid टेस्ट, sample ratio mismatch की जाँच और कई मेट्रिक्स पर false discovery rate नियंत्रण, sequential-analysis के साथ।
language: hi
---

# फ़ॉल्स पॉज़िटिव बढ़ाए बिना A/B टेस्ट को जल्दी कैसे रोकें?

> यह [अंग्रेज़ी पृष्ठ](../../guide/ab-testing.md) का अनुवाद है। इसकी समीक्षा अभी किसी मूल हिंदी भाषी ने नहीं की है; जहाँ दोनों में अंतर हो, वहाँ अंग्रेज़ी पृष्ठ ही प्रामाणिक है।

**संक्षिप्त उत्तर।** ऐसा टेस्ट इस्तेमाल करें जो anytime-valid (किसी भी समय
वैध) हो: इसका p-value और विश्वास्यता अंतराल (confidence interval) वैध रहते
हैं चाहे आप कितनी भी बार देखें, इसलिए परिणाम स्पष्ट होते ही आप रुक सकते
हैं। sequential-analysis में:

| मेट्रिक | प्रक्रिया | गारंटी |
|---|---|---|
| कन्वर्ज़न दर (0/1) | `TwoProportionTest` | exact |
| कोई भी सीमित (bounded) मेट्रिक (कैप किया गया रेवेन्यू, हिस्सा) | `BoundedABTest` | exact |
| एक्सपोज़र की प्रति इकाई इवेंट | `RateRatioTest` | Poisson गणनाओं के लिए exact |
| अनुपात मेट्रिक (ratio metric) (प्रति सेशन रेवेन्यू) | `RatioABTest` | asymptotic |
| प्रयोग-पूर्व कोवेरिएट (CUPED) के साथ माध्य | `ABTest` | asymptotic |
| क्या ट्रैफ़िक का बँटवारा इच्छित अनुपात में है? | `SampleRatioMismatch` | exact |
| कई मेट्रिक्स या आर्म एक साथ | `MultipleTests` (e-BH) | मिथ्या खोज दर (false discovery rate), exact |

हर प्रक्रिया को एक बार में एक उपयोगकर्ता दें: `state, out = test.step(state, {...})`।
जब चाहें `out.decision` पर कार्रवाई करें।

## कन्वर्ज़न: डेटा निर्णायक होते ही रुकें

कंट्रोल 10% उपयोगकर्ताओं को कन्वर्ट करता है, ट्रीटमेंट 12%। टेस्ट हर
उपयोगकर्ता के बाद देखा जाता है और अपने पहले निर्णय पर रुक जाता है:

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

तुलना के लिए, इस बढ़ोतरी (lift) के लिए 80% पावर वाले निश्चित-सैंपल टेस्ट को
प्रति आर्म लगभग 3,850 उपयोगकर्ता चाहिए, कुल 7,700, और उसे सिर्फ़ एक बार,
अंत में, पढ़ा जा सकता है। anytime-valid टेस्ट अपनी स्वतंत्रता की कीमत चुकाता
है: वही पावर पाने के लिए उसे एक विश्लेषण के 1.3–1.6 गुना उपयोगकर्ता चाहिए,
और इस रन में उससे भी अधिक लगे। बदले में पहले से कोई सैंपल साइज़ तय नहीं
करना पड़ता, और आप हर दिन परिणाम देख सकते हैं और स्पष्ट होते ही रुक सकते
हैं। जब प्रभाव नियोजित से बड़ा हो, तो ऐसा बहुत पहले हो जाता है।

## रेवेन्यू: सीमित मेट्रिक के लिए exact अंतराल

`BoundedABTest` को मेट्रिक की केवल सीमाएँ (bounds) चाहिए। रेवेन्यू को टेस्ट
से पहले आपके चुने हुए मान पर कैप करें (यहाँ 30), और माध्यों के अंतर के लिए
विश्वास्यता अनुक्रम (confidence sequence) किसी भी वितरण के लिए exact है:

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

अंतराल 20,000 में से हर बार देखने पर एक साथ वैध है, सिर्फ़ आख़िरी बार नहीं।
यहाँ इसमें अभी भी 0 शामिल है: इतनी शोरभरी (noisy) मेट्रिक पर लगभग 0.5 की
बढ़ोतरी स्थापित करने के लिए 20,000 उपयोगकर्ता काफ़ी नहीं हैं, इसलिए प्रयोग
जारी रहता है।

## पहले ट्रैफ़िक का बँटवारा जाँचें

Sample ratio mismatch (SRM) का अर्थ है कि बँटवारा कॉन्फ़िगर किए गए अनुपात से
अलग है, उदाहरण के लिए असाइनमेंट या लॉगिंग में किसी बग के कारण। ऐसे प्रयोग
से मिले प्रभाव के अनुमान भरोसेमंद नहीं होते। 50/50 से 52/48 का mismatch
प्रयोग के चलते-चलते पकड़ लिया जाता है:

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

## एक साथ कई मेट्रिक्स

दस स्वतंत्र मेट्रिक्स को हर एक 5% पर टेस्ट करने से कम से कम एक मिथ्या खोज
(false discovery) की लगभग 40% संभावना बनती है। `MultipleTests` सभी टेस्टों के
e-value को e-BH प्रक्रिया से जोड़ता है, ताकि मिथ्या खोज दर किसी भी रुकने के
समय (stopping time) पर `alpha` पर रहे:

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

## सावधानियाँ

* **उसी इकाई को रैंडमाइज़ करें जिसका आप विश्लेषण करते हैं।** अगर उपयोगकर्ता
  रैंडमाइज़ किए गए हैं, तो प्रति उपयोगकर्ता एक रिकॉर्ड दें, प्रति पेज व्यू नहीं।
  प्रति-सेशन मेट्रिक्स के लिए `RatioABTest` इस्तेमाल करें, जो उपयोगकर्ता के
  कुल योग पर काम करता है।
* **सीमित मेट्रिक का कैप टेस्ट से पहले तय करें।** डेटा देखने के बाद इसे चुनना
  गारंटी को निरस्त कर देता है।
* **Asymptotic प्रक्रियाओं को बड़े सैंपल चाहिए।** `ABTest` और `RatioABTest` के
  लिए अंतराल लंबे रन में केवल लगभग वैध है। जहाँ फ़िट हों, exact प्रक्रियाओं को
  प्राथमिकता दें।
* **अनुकूली ट्रैफ़िक आवंटन (adaptive traffic allocation)** (bandits) के लिए
  ऐसा टेस्ट चाहिए जो तब भी वैध रहे जब बँटवारा परिणामों पर निर्भर हो:
  `TwoProportionTest(method="universal")` या
  `BoundedABTest(propensity_input=...)`। देखें
  [ट्यूटोरियल §10](../../tutorials/ab-test.md)।

और: [A/B टेस्ट ट्यूटोरियल](../../tutorials/ab-test.md) (CUPED, अनुपात
मेट्रिक्स, दरें, अवधि की योजना) और
[प्रयोगों का एक कार्यक्रम](../../tutorials/experiment-programme.md)
(कई प्रयोगों पर मिथ्या खोज दर)।
