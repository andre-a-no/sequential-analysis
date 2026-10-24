---
description: Python میں کلینیکل ٹرائل کے عبوری تجزیوں (interim analyses) کی منصوبہ بندی اور انہیں چلانے کا طریقہ۔ گروہی ترتیبی ڈیزائن (O'Brien–Fleming، Pocock، Lan–DeMets الفا اسپینڈنگ، لاحاصلی کی حدیں)، اوسط، تناسب اور سروائیول کے لیے نمونے کا حجم، rpact سے جانچا ہوا، sequential-analysis کے ساتھ۔
language: ur
---

# کلینیکل ٹرائل کے عبوری تجزیوں کی منصوبہ بندی کیسے کریں؟

> یہ [انگریزی صفحے](../../guide/clinical-trials.md) کا ترجمہ ہے۔ ابھی کسی اہلِ زبان نے اس کا جائزہ نہیں لیا؛ جہاں دونوں میں فرق ہو، وہاں انگریزی صفحہ ہی مستند ہے۔

**مختصر جواب۔** گروہی ترتیبی ڈیزائن (group sequential design) استعمال کریں۔
`sequential_analysis.group_sequential` کا
`group_sequential_design(alpha, fractions, spending=...)` حساب لگاتا ہے:

* افادیت کی حدیں (efficacy boundaries)، Lan–DeMets الفا اسپینڈنگ (alpha spending)
  کے ساتھ (O'Brien–Fleming قسم، Pocock قسم اور دیگر)؛
* non-binding لاحاصلی کی حدیں (futility boundaries)؛
* طاقت (power) اور متوقع نمونے کا حجم؛
* اوسط اور تناسب کے لیے نمونے کا زیادہ سے زیادہ حجم، یا سروائیول کے لیے واقعات
  (events) کی تعداد۔

حدیں اور نمونوں کے حجم R پیکیج rpact سے متفق ہیں۔ اس کے بعد ٹیسٹ کے طریقے
(`GroupSequentialTest`، `GroupSequentialTwoMeans`،
`GroupSequentialProportions`، `GroupSequentialLogRank`) ٹرائل چلاتے ہیں، مریض بہ
مریض یا واقعہ بہ واقعہ۔ ہر عبوری تجزیہ وہ اس وقت کرتے ہیں جب اس کا معلوماتی حصہ
(information fraction) پورا ہو جائے۔

## ڈیزائن: چار تجزیے، O'Brien–Fleming اسپینڈنگ

یک طرفہ (one-sided) α = 0.025، مریضوں کے 25%، 50%، 75% اور 100% پر تجزیے، 90%
طاقت، لاحاصلی کی حد کے ساتھ:

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

## ثنائی (binary) اور سروائیول اینڈ پوائنٹس

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

O'Brien–Fleming اسپینڈنگ کے ساتھ، تین تجزیوں پر ایک حتمی تجزیے کے مقابلے میں 1.3%
زیادہ مریض لگتے ہیں۔

## ٹرائل چلانا

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

ٹرائل دوسرے تجزیے پر، منصوبہ بند مریضوں کے دو تہائی کے بعد، افادیت (efficacy) کی
بنا پر رک گیا۔

## جب تجزیے منصوبے کے مطابق نہ ہوں

ڈیٹا مانیٹرنگ کمیٹیاں شاذ ہی کبھی ٹھیک 25% معلومات پر ملتی ہیں:

* `design.at(fractions)` اصل میں حاصل شدہ معلومات کے لیے حدوں کا دوبارہ حساب
  لگاتا ہے۔ الفا اسپینڈنگ مجموعی سطح (overall level) برقرار رکھتی ہے۔
* `GroupSequentialMonitor` ہر اجلاس پر آپ کا خود حساب کیا ہوا کوئی بھی شماریہ
  (ایک Cox ماڈل، ایک mixed ماڈل) Z قدر کے طور پر اور اس کی معلومات لیتا ہے۔

## اور اگر آپ ہر مریض کے بعد دیکھنا چاہیں؟

گروہی ترتیبی ڈیزائن صرف منصوبہ بند تعداد میں دیکھنے کی اجازت دیتا ہے۔ ہر مریض یا
واقعے کے بعد مانیٹر کرنے کے لیے anytime-valid طریقۂ کار استعمال کریں: سروائیول کے
لیے `AnytimeLogRankTest`، ردِعمل کی شرح (response rates) کے لیے
`TwoProportionTest`، اوسط کے لیے `TMixtureSPRT`۔ انہیں منصوبہ بند اثر پر زیادہ
مریض درکار ہوتے ہیں۔ دیکھیں [ٹیوٹوریل: سروائیول ٹرائل](../../tutorials/survival.md)۔

## ریگولیٹری عمل (regulatory practice)

الفا اسپینڈنگ والے گروہی ترتیبی ڈیزائن تصدیقی (confirmatory) ٹرائلز میں مسلّمہ
طریقہ ہیں، جن کی وضاحت ICH E9 رہنما اصول اور adaptive designs پر FDA کی رہنمائی
(2019) میں کی گئی ہے۔ یہ لائبریری ڈیزائنوں کا حساب لگاتی ہے اور ہر تجزیے کا ایک
قابلِ آڈٹ، دوبارہ شروع کیا جا سکنے والا ریکارڈ رکھتی ہے (چیک پوائنٹ اور اس کا
history digest)۔ یہ ریگولیٹری معنوں میں validated سافٹ ویئر نہیں ہے: جمع کرانے
(submission) میں اسے استعمال کرنے والے اسپانسر کو کسی بھی دوسرے ٹول کی طرح اس کی
توثیق کرنی ہوگی۔

مزید: [ٹیوٹوریل: گروہی ترتیبی ٹرائل](../../tutorials/group-sequential.md)، جو
اعداد کا rpact سے موازنہ کرتا ہے؛
[حوالہ: ڈیزائن اور منصوبہ بندی](../../reference/design.md)۔
