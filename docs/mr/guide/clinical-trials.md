---
description: Python मध्ये वैद्यकीय चाचणीच्या (clinical trial) अंतरिम विश्लेषणांचे नियोजन आणि अंमलबजावणी कशी करावी - गट अनुक्रमिक अभिकल्प (O'Brien–Fleming, Pocock, Lan–DeMets अल्फा व्यय, निष्फळता सीमा), सरासरी, प्रमाणे आणि उत्तरजीविता (survival) यांसाठी नमुना आकार, rpact शी पडताळलेले, sequential-analysis सह.
language: mr
---

# वैद्यकीय चाचणीच्या अंतरिम विश्लेषणांचे नियोजन कसे करावे?

> हे [इंग्रजी पानाचे](../../guide/clinical-trials.md) भाषांतर आहे. मराठी मातृभाषक व्यक्तीने अद्याप त्याचे पुनरावलोकन केलेले नाही; दोन्हींमध्ये फरक आढळल्यास इंग्रजी पान अधिकृत मानावे.

**थोडक्यात उत्तर.** गट अनुक्रमिक अभिकल्प (group sequential design) वापरा.
`sequential_analysis.group_sequential` मधील
`group_sequential_design(alpha, fractions, spending=...)` हे गणन करते:

* परिणामकारकतेच्या सीमा (efficacy boundaries), Lan–DeMets अल्फा व्ययासह (alpha
  spending) (O'Brien–Fleming प्रकार, Pocock प्रकार आणि इतर);
* अबंधनकारक (non-binding) निष्फळता सीमा (futility boundaries);
* सामर्थ्य (power) आणि अपेक्षित नमुना आकार;
* सरासरी आणि प्रमाणांसाठी कमाल नमुना आकार, किंवा उत्तरजीविता (survival)
  विश्लेषणासाठी घटनांची संख्या.

सीमा आणि नमुना आकार R पॅकेज rpact शी जुळतात. त्यानंतर चाचणी कार्यपद्धती
(`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) चाचणी रुग्ण-दर-रुग्ण
किंवा घटना-दर-घटना चालवतात. प्रत्येक अंतरिम विश्लेषण (interim analysis) त्याचा
माहिती अंश (information fraction) गाठला गेल्यावर ते करतात.

## अभिकल्प: चार विश्लेषणे, O'Brien–Fleming व्यय

एकपुच्छी (one-sided) α = 0.025, रुग्णांच्या 25%, 50%, 75% आणि 100% वर विश्लेषणे,
90% सामर्थ्य, निष्फळता सीमेसह:

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

## द्विमानी (binary) आणि उत्तरजीविता अंतिम बिंदू (endpoints)

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

O'Brien–Fleming व्ययासह, तीन विश्लेषणांना एकाच अंतिम विश्लेषणापेक्षा 1.3% अधिक
रुग्ण लागतात.

## चाचणी चालवणे

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

चाचणी दुसऱ्या विश्लेषणात, नियोजित रुग्णांपैकी दोन तृतीयांश रुग्णांनंतर,
परिणामकारकतेसाठी (efficacy) थांबली.

## विश्लेषणे नियोजनानुसार होत नाहीत तेव्हा

डेटा देखरेख समित्या (data monitoring committees) क्वचितच माहितीच्या बरोबर 25% वर
भेटतात:

* `design.at(fractions)` प्रत्यक्ष गाठलेल्या माहितीसाठी सीमा पुन्हा गणन करते.
  अल्फा व्यय एकूण पातळी राखतो.
* `GroupSequentialMonitor` तुम्ही स्वतः गणन केलेली कोणतीही सांख्यिकी (Cox
  प्रतिमान, मिश्र प्रतिमान (mixed model)) प्रत्येक बैठकीत Z मूल्य आणि तिची माहिती
  म्हणून घेते.

## आणि प्रत्येक रुग्णानंतर पाहायचे असेल तर?

गट अनुक्रमिक अभिकल्प फक्त नियोजित संख्येइतक्याच पाहण्यांना परवानगी देतो.
प्रत्येक रुग्ण किंवा घटनेनंतर देखरेख करण्यासाठी कधीही-वैध (anytime-valid)
कार्यपद्धती वापरा: उत्तरजीवितेसाठी `AnytimeLogRankTest`, प्रतिसाद दरांसाठी
`TwoProportionTest`, सरासरीसाठी `TMixtureSPRT`. नियोजित परिणामावर त्यांना अधिक
रुग्ण लागतात. पाहा [ट्युटोरियल: उत्तरजीविता चाचणी](../../tutorials/survival.md).

## नियामक प्रथा

अल्फा व्ययासह गट अनुक्रमिक अभिकल्प हा पुष्टीकारक (confirmatory) चाचण्यांमधील
प्रस्थापित दृष्टिकोन आहे, ज्याचे वर्णन ICH E9 मार्गदर्शक तत्त्वात आणि अनुकूली
अभिकल्पांवरील (adaptive designs) FDA मार्गदर्शनात (2019) आहे. ही लायब्ररी
अभिकल्पांचे गणन करते आणि प्रत्येक विश्लेषणाची लेखापरीक्षणयोग्य, पुन्हा सुरू
करता येणारी नोंद ठेवते (चेकपॉइंट आणि त्याचा इतिहास डायजेस्ट (history digest)).
नियामक अर्थाने हे प्रमाणित (validated) सॉफ्टवेअर नाही: सादरीकरणात (submission)
ती वापरणाऱ्या प्रायोजकाला (sponsor) इतर कोणत्याही साधनाप्रमाणे तिचे प्रमाणीकरण
करावे लागते.

अधिक: [ट्युटोरियल: गट अनुक्रमिक चाचणी](../../tutorials/group-sequential.md),
जे आकड्यांची rpact शी तुलना करते;
[संदर्भ: अभिकल्प आणि नियोजन](../../reference/design.md).
