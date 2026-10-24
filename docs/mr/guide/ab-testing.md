---
description: Python मध्ये खोटे सकारात्मक निष्कर्ष (false positives) न वाढवता A/B चाचणी लवकर कशी थांबवावी. रूपांतरण दर आणि मर्यादित महसुलासाठी कधीही-वैध (anytime-valid) चाचण्या, नमुना गुणोत्तर विसंगती (SRM) तपासणी आणि अनेक मेट्रिक्सवर खोट्या शोधांच्या दराचे (FDR) नियंत्रण, sequential-analysis सह.
language: mr
---

# खोटे सकारात्मक निष्कर्ष न वाढवता A/B चाचणी लवकर कशी थांबवावी?

> हे [इंग्रजी पानाचे](../../guide/ab-testing.md) भाषांतर आहे. मराठी मातृभाषक व्यक्तीने अद्याप त्याचे पुनरावलोकन केलेले नाही; दोन्हींमध्ये फरक आढळल्यास इंग्रजी पान अधिकृत मानावे.

**थोडक्यात उत्तर.** कधीही-वैध (anytime-valid) चाचणी वापरा: तुम्ही कितीही वेळा
पाहिले तरी तिचे p-मूल्य (p-value) आणि विश्वास्यता अंतराल (confidence interval)
वैध राहतात, त्यामुळे निकाल स्पष्ट होताच तुम्ही थांबू शकता. sequential-analysis
मध्ये:

| मेट्रिक | कार्यपद्धती | हमी |
|---|---|---|
| रूपांतरण दर (conversion rate) (0/1) | `TwoProportionTest` | exact |
| कोणतेही मर्यादित मेट्रिक (कमाल मर्यादा लावलेला महसूल, हिस्सा) | `BoundedABTest` | exact |
| संपर्काच्या (exposure) प्रति एककातील घटना | `RateRatioTest` | Poisson गणनांसाठी exact |
| गुणोत्तर मेट्रिक (ratio metric) (प्रति सत्र महसूल) | `RatioABTest` | asymptotic |
| प्रयोगपूर्व सहचलासह (covariate) सरासरी (CUPED) | `ABTest` | asymptotic |
| ट्रॅफिकची विभागणी ठरल्याप्रमाणे आहे का? | `SampleRatioMismatch` | exact |
| अनेक मेट्रिक्स किंवा शाखा (arms) एकत्र | `MultipleTests` (e-BH) | खोट्या शोधांचा दर (false discovery rate), exact |

प्रत्येक कार्यपद्धतीला एका वेळी एक वापरकर्ता द्या: `state, out = test.step(state, {...})`.
`out.decision` नुसार तुम्हाला हवे तेव्हा कृती करा.

## रूपांतरण: डेटा निर्णायक होताच थांबा

नियंत्रण गटात (control) 10% वापरकर्ते रूपांतरित होतात, उपचार गटात (treatment)
12%. चाचणी प्रत्येक वापरकर्त्यानंतर पाहिली जाते आणि तिच्या पहिल्या निर्णयावर
थांबते:

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

तुलनेसाठी, या वाढीसाठी 80% सामर्थ्य (power) असलेल्या स्थिर-नमुना चाचणीला
(fixed-sample test) प्रति शाखा सुमारे 3,850, एकूण 7,700 वापरकर्ते लागतात,
आणि ती फक्त एकदाच, शेवटी वाचता येते. कधीही-वैध चाचणी आपल्या स्वातंत्र्याची
किंमत मोजते: तेवढेच सामर्थ्य गाठण्यासाठी तिला एकाच विश्लेषणाच्या 1.3–1.6 पट
वापरकर्ते लागतात, आणि या रनला त्यापेक्षाही जास्त लागले. त्याबदल्यात आधीपासून
कोणताही नमुना आकार ठरवावा लागत नाही, आणि तुम्ही निकाल रोज पाहू शकता आणि तो
स्पष्ट होताच थांबू शकता. परिणाम नियोजितपेक्षा मोठा असेल तेव्हा हे खूप लवकर घडते.

## महसूल: मर्यादित मेट्रिकसाठी अचूक अंतराल

`BoundedABTest` ला फक्त मेट्रिकच्या मर्यादा लागतात. चाचणीपूर्वी तुम्ही निवडलेल्या
मूल्यावर (इथे 30) महसुलाची कमाल मर्यादा लावा, आणि सरासरींमधील फरकासाठीचा
विश्वास्यता अनुक्रम (confidence sequence) कोणत्याही वितरणासाठी अचूक असतो:

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

हा अंतराल फक्त शेवटच्या नव्हे, तर 20,000 पैकी प्रत्येक पाहणीवर एकाच वेळी टिकून
राहतो. इथे त्यात अजूनही 0 आहे: एवढ्या गोंगाटयुक्त (noisy) मेट्रिकवर सुमारे 0.5
ची वाढ सिद्ध करण्यासाठी 20,000 वापरकर्ते पुरेसे नाहीत, त्यामुळे प्रयोग सुरू राहतो.

## आधी ट्रॅफिकची विभागणी तपासा

नमुना गुणोत्तर विसंगती (sample ratio mismatch) म्हणजे विभागणी कॉन्फिगर
केलेल्यापेक्षा वेगळी आहे, उदाहरणार्थ वाटपात (assignment) किंवा लॉगिंगमधील
बगमुळे. अशा प्रयोगातून मिळालेले परिणामाचे अंदाज विश्वासार्ह नसतात. 50/50 ऐवजी
52/48 अशी विसंगती प्रयोग चालू असतानाच पकडली जाते:

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

## एकाच वेळी अनेक मेट्रिक्स

दहा स्वतंत्र मेट्रिक्सची प्रत्येकी 5% वर चाचणी केल्यास किमान एक खोटा शोध (false
discovery) होण्याची सुमारे 40% शक्यता असते. `MultipleTests` सर्व चाचण्यांची
e-मूल्ये (e-values) e-BH कार्यपद्धतीने एकत्र करते, त्यामुळे कोणत्याही थांबण्याच्या
वेळी (stopping time) खोट्या शोधांचा दर `alpha` वर राहतो:

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

## सापळे

* **तुम्ही ज्या एककाचे विश्लेषण करता त्याचेच यादृच्छिकीकरण (randomisation) करा.**
  वापरकर्त्यांचे यादृच्छिकीकरण केले असेल तर प्रति वापरकर्ता एक नोंद द्या, प्रति
  पृष्ठदृश्य (page view) नव्हे. प्रति सत्र मेट्रिक्ससाठी `RatioABTest` वापरा, जी
  वापरकर्त्यांच्या बेरजांवर काम करते.
* **मर्यादित मेट्रिकची कमाल मर्यादा चाचणीपूर्वी ठरवा.** डेटा पाहिल्यानंतर ती
  निवडल्यास हमी रद्द होते.
* **asymptotic कार्यपद्धतींना मोठे नमुने लागतात.** `ABTest` आणि `RatioABTest`
  साठी अंतराल फक्त लांब रनमध्ये अंदाजे वैध असतो. जिथे अचूक कार्यपद्धती लागू
  होतात तिथे त्यांना प्राधान्य द्या.
* **अनुकूली ट्रॅफिक वाटपासाठी (adaptive traffic allocation)** (बँडिट्स) अशी चाचणी
  लागते जी विभागणी निकालांवर अवलंबून असतानाही वैध राहते:
  `TwoProportionTest(method="universal")` किंवा
  `BoundedABTest(propensity_input=...)`. पाहा
  [ट्युटोरियल §10](../../tutorials/ab-test.md).

अधिक: [A/B चाचणी ट्युटोरियल](../../tutorials/ab-test.md) (CUPED, गुणोत्तर मेट्रिक्स,
दर, कालावधीचे नियोजन) आणि
[प्रयोगांचा कार्यक्रम](../../tutorials/experiment-programme.md)
(अनेक प्रयोगांवरील खोट्या शोधांचा दर).
