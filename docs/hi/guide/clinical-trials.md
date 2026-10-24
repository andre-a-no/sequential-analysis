---
description: Python में क्लिनिकल ट्रायल के अंतरिम विश्लेषणों (interim analyses) की योजना कैसे बनाएँ और उन्हें कैसे चलाएँ। समूह अनुक्रमिक डिज़ाइन (O'Brien–Fleming, Pocock, Lan–DeMets अल्फ़ा स्पेंडिंग, निरर्थकता सीमाएँ), माध्य, अनुपात और सर्वाइवल के लिए सैंपल साइज़, rpact से जाँचे गए, sequential-analysis के साथ।
language: hi
---

# क्लिनिकल ट्रायल के अंतरिम विश्लेषणों की योजना कैसे बनाएँ?

> यह [अंग्रेज़ी पृष्ठ](../../guide/clinical-trials.md) का अनुवाद है। इसकी समीक्षा अभी किसी मूल हिंदी भाषी ने नहीं की है; जहाँ दोनों में अंतर हो, वहाँ अंग्रेज़ी पृष्ठ ही प्रामाणिक है।

**संक्षिप्त उत्तर।** समूह अनुक्रमिक डिज़ाइन (group sequential design) इस्तेमाल
करें। `sequential_analysis.group_sequential` का
`group_sequential_design(alpha, fractions, spending=...)` गणना करता है:

* प्रभावकारिता सीमाएँ (efficacy boundaries), Lan–DeMets अल्फ़ा स्पेंडिंग (alpha
  spending) के साथ (O'Brien–Fleming प्रकार, Pocock प्रकार और अन्य);
* non-binding निरर्थकता सीमाएँ (futility boundaries);
* पावर और अपेक्षित सैंपल साइज़;
* माध्यों और अनुपातों के लिए अधिकतम सैंपल साइज़, या सर्वाइवल के लिए इवेंट्स
  की संख्या।

सीमाएँ और सैंपल साइज़ R पैकेज rpact से मेल खाते हैं। इसके बाद टेस्ट प्रक्रियाएँ
(`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) ट्रायल को चलाती हैं,
मरीज़-दर-मरीज़ या इवेंट-दर-इवेंट। हर अंतरिम विश्लेषण वे तब करती हैं जब उसका
सूचना अंश (information fraction) पूरा हो जाता है।

## डिज़ाइन: चार विश्लेषण, O'Brien–Fleming स्पेंडिंग

एकतरफ़ा (one-sided) α = 0.025, मरीज़ों के 25%, 50%, 75% और 100% पर विश्लेषण,
90% पावर, एक निरर्थकता सीमा के साथ:

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

## बाइनरी और सर्वाइवल एंडपॉइंट

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

O'Brien–Fleming स्पेंडिंग के साथ, तीन विश्लेषणों में एक अंतिम विश्लेषण की
तुलना में 1.3% अधिक मरीज़ लगते हैं।

## ट्रायल चलाना

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

ट्रायल दूसरे विश्लेषण पर, नियोजित मरीज़ों के दो-तिहाई के बाद, प्रभावकारिता
(efficacy) के लिए रुक गया।

## जब विश्लेषण योजना के अनुसार न हों

डेटा मॉनिटरिंग कमेटियाँ शायद ही कभी ठीक 25% सूचना पर मिलती हैं:

* `design.at(fractions)` वास्तव में पहुँची सूचना के लिए सीमाओं की फिर से
  गणना करता है। अल्फ़ा स्पेंडिंग समग्र स्तर (overall level) को बनाए रखती है।
* `GroupSequentialMonitor` हर बैठक पर आपके द्वारा स्वयं गणना की गई कोई भी
  सांख्यिकी (एक Cox मॉडल, एक mixed मॉडल) Z मान के रूप में और उसकी सूचना
  लेता है।

## और अगर आप हर मरीज़ के बाद देखना चाहें?

समूह अनुक्रमिक डिज़ाइन केवल नियोजित संख्या में देखने की अनुमति देता है। हर
मरीज़ या इवेंट के बाद मॉनिटर करने के लिए anytime-valid प्रक्रिया इस्तेमाल करें:
सर्वाइवल के लिए `AnytimeLogRankTest`, रिस्पॉन्स दरों के लिए `TwoProportionTest`,
माध्य के लिए `TMixtureSPRT`। इन्हें नियोजित प्रभाव पर अधिक मरीज़ चाहिए। देखें
[ट्यूटोरियल: सर्वाइवल ट्रायल](../../tutorials/survival.md)।

## नियामक व्यवहार (regulatory practice)

अल्फ़ा स्पेंडिंग वाले समूह अनुक्रमिक डिज़ाइन पुष्टिकारी (confirmatory) ट्रायलों
में स्थापित दृष्टिकोण हैं, जिनका वर्णन ICH E9 दिशानिर्देश और adaptive
designs पर FDA मार्गदर्शन (2019) में है। यह लाइब्रेरी डिज़ाइनों की गणना करती है
और हर विश्लेषण का एक ऑडिट-योग्य, फिर से शुरू किया जा सकने वाला रिकॉर्ड रखती है
(चेकपॉइंट और उसका history digest)। यह नियामक अर्थ में वैलिडेटेड सॉफ़्टवेयर
नहीं है: सबमिशन में इसका उपयोग करने वाले स्पॉन्सर को इसे किसी भी अन्य टूल की
तरह वैलिडेट करना होगा।

और: [ट्यूटोरियल: समूह अनुक्रमिक ट्रायल](../../tutorials/group-sequential.md),
जो संख्याओं की तुलना rpact से करता है;
[संदर्भ: डिज़ाइन और योजना](../../reference/design.md)।
