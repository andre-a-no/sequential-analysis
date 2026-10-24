---
description: A/B चाचण्या आणि वैद्यकीय चाचण्यांमध्ये रोज p-मूल्य तपासल्याने खोटे सकारात्मक निष्कर्ष का फुगतात (डोकावण्याची समस्या, peeking problem), आणि ती दूर करणारी अनुक्रमिक पद्धतींची तीन कुळे, Python मध्ये sequential-analysis सह.
language: mr
---

# मी रोज p-मूल्य का पाहू शकत नाही?

> हे [इंग्रजी पानाचे](../../guide/peeking.md) भाषांतर आहे. मराठी मातृभाषक व्यक्तीने अद्याप त्याचे पुनरावलोकन केलेले नाही; दोन्हींमध्ये फरक आढळल्यास इंग्रजी पान अधिकृत मानावे.

**थोडक्यात उत्तर.** स्थिर-नमुना चाचणी (fixed-sample test) 5% खोट्या सकारात्मकांच्या
दराचे (false-positive rate) वचन तेव्हाच देते जेव्हा तुम्ही निकाल एकदाच, नियोजित
नमुना आकारावर पाहता. तुम्ही वारंवार पाहिले आणि पहिल्यांदा p < 0.05 झाल्यावर
थांबलात, तर तुम्हाला फसण्याच्या अनेक संधी मिळतात. 20 पाहण्यांसह खोट्या
सकारात्मकांचा दर सुमारे 25% पर्यंत वाढतो. अनुक्रमिक पद्धती (sequential methods)
वारंवार पाहण्यासाठीच बनवलेल्या आहेत. त्यांच्यासह तुम्ही कितीही वेळा पाहिले आणि
केव्हाही थांबलात तरी दर 5% किंवा त्याहून कमी राहतो.

## डोकावण्याची समस्या, मोजलेली

समान 10% रूपांतरण दर (conversion rate) असलेल्या दोन शाखा (एक A/A चाचणी), 2,000
वापरकर्ते, 200 पुनरावृत्ती. "डोकावणे" (peeking) प्रत्येक 100 वापरकर्त्यांनंतर
नेहमीची दोन-प्रमाण z-चाचणी चालवते आणि पहिल्या p < 0.05 वर थांबते. अनुक्रमिक
`TwoProportionTest` प्रत्येक एकेका वापरकर्त्यानंतर तपासली जाते:

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

एकच पाहणी आपले वचन पाळते. वीस पाहण्या त्रुटी दर सुमारे सहा पट वाढवतात. 2,000
पैकी प्रत्येक वापरकर्त्यानंतर पाहिलेली अनुक्रमिक चाचणी तो 5% वर ठेवते. हेच वचन
आहे: तिची हमी **exact** आहे (`TwoProportionTest.guarantee == "exact"`), म्हणजे
तुम्ही कितीही वेळा पाहिले तरी प्रत्येक नमुना आकारावर जास्तीत जास्त 5% खोट्या
सकारात्मकांचा दर. 200 पुनरावृत्तींमध्ये, 10 खोटे सकारात्मक हेच अचूक 5% देते.

## अनुक्रमिक पद्धतींची तीन कुळे

| कूळ | तुम्ही केव्हा पाहू शकता | नेहमीचा वापर | sequential-analysis मध्ये |
|---|---|---|---|
| **अनुक्रमिक संभाव्यता गुणोत्तर चाचण्या** (sequential probability ratio tests) (Wald 1945) | प्रत्येक निरीक्षणानंतर | एका साध्या परिकल्पनेविरुद्ध दुसरी, सरासरीने सर्वात कमी निरीक्षणे: गुणवत्ता नियंत्रण, सिम्युलेशन, मनोभौतिकी (psychophysics) | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **गट अनुक्रमिक अभिकल्प** (group sequential designs) (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | काही नियोजित अंतरिम विश्लेषणांवर | डेटा देखरेख समितीसह वैद्यकीय चाचण्या | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **कधीही-वैध अनुमान** (anytime-valid inference): e-मूल्ये, विश्वास्यता अनुक्रम, मिश्रण SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | प्रत्येक निरीक्षणानंतर, कोणत्याही कारणाने थांबून | ऑनलाइन A/B चाचण्या, देखरेख डॅशबोर्ड | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**याची किंमत काय.** अधिक वेळा पाहण्यासाठी तुम्ही नियोजित केलेल्या परिणामावर अधिक
डेटा लागतो:

* चार विश्लेषणे असलेल्या गट अनुक्रमिक अभिकल्पाला एकाच विश्लेषणापेक्षा 1–20%
  अधिक रुग्ण लागतात;
* दोन प्रमाणांच्या कधीही-वैध चाचणीला एकाच विश्लेषणाच्या 1.3–1.6 पट वापरकर्ते
  लागतात.

त्याबदल्यात, मोठा परिणाम प्रयोग लवकर थांबवतो, आणि कोणालाही आधीपासून नमुना आकार
ठरवावा लागत नाही.

## ही समस्या केव्हा नसते

तुम्ही जे करता ते तुम्ही जे पाहिले त्यावर अवलंबून असेल तेव्हाच डोकावण्यामुळे
त्रुटी फुगतात. तुम्ही डॅशबोर्ड पाहत असलात पण प्रयोग नेहमी त्याच्या नियोजित
आकारापर्यंत चालवून एकदाच चाचणी करत असाल, तर स्थिर-नमुना चाचणी वैध आहे. त्या
परिस्थितीत ती सर्वात कार्यक्षम निवडही आहे.

पुढे: [A/B चाचणी लवकर थांबवा](ab-testing.md),
[विश्वास्यता अनुक्रम](confidence-sequences.md),
[शब्दसूची](glossary.md).
