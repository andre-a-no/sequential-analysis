---
description: Python میں غلط مثبت نتائج بڑھائے بغیر A/B ٹیسٹ کو جلد کیسے روکیں۔ کنورژن اور محدود (bounded) آمدنی کے لیے anytime-valid ٹیسٹ، sample ratio mismatch کی جانچ اور متعدد میٹرکس پر false discovery rate کا کنٹرول، sequential-analysis کے ساتھ۔
language: ur
---

# غلط مثبت نتائج بڑھائے بغیر A/B ٹیسٹ کو جلد کیسے روکیں؟

> یہ [انگریزی صفحے](../../guide/ab-testing.md) کا ترجمہ ہے۔ ابھی کسی اہلِ زبان نے اس کا جائزہ نہیں لیا؛ جہاں دونوں میں فرق ہو، وہاں انگریزی صفحہ ہی مستند ہے۔

**مختصر جواب۔** ایسا ٹیسٹ استعمال کریں جو anytime-valid (کسی بھی وقت درست) ہو:
اس کا p-value اور وقفۂ اعتماد (confidence interval) درست رہتے ہیں چاہے آپ کتنی
ہی بار دیکھیں، اس لیے نتیجہ واضح ہوتے ہی آپ رک سکتے ہیں۔ sequential-analysis
میں:

| میٹرک | طریقۂ کار | ضمانت |
|---|---|---|
| کنورژن شرح (0/1) | `TwoProportionTest` | exact |
| کوئی بھی محدود (bounded) میٹرک (حد بند آمدنی، حصہ) | `BoundedABTest` | exact |
| ایکسپوژر کی فی اکائی واقعات (events) | `RateRatioTest` | Poisson گنتی کے لیے exact |
| تناسبی میٹرک (ratio metric) (فی سیشن آمدنی) | `RatioABTest` | asymptotic |
| تجربے سے پہلے کے covariate (CUPED) کے ساتھ اوسط | `ABTest` | asymptotic |
| کیا ٹریفک کی تقسیم ارادے کے مطابق ہے؟ | `SampleRatioMismatch` | exact |
| متعدد میٹرکس یا بازو ایک ساتھ | `MultipleTests` (e-BH) | غلط دریافت کی شرح (false discovery rate)، exact |

ہر طریقۂ کار کو ایک وقت میں ایک صارف دیں: `state, out = test.step(state, {...})`۔
جب چاہیں `out.decision` پر عمل کریں۔

## کنورژن: ڈیٹا فیصلہ کن ہوتے ہی رک جائیں

کنٹرول 10% صارفین کو کنورٹ کرتا ہے، ٹریٹمنٹ 12%۔ ٹیسٹ ہر صارف کے بعد دیکھا جاتا
ہے اور اپنے پہلے فیصلے پر رک جاتا ہے:

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

موازنے کے لیے، اس اضافے (lift) کے لیے 80% طاقت والے مقررہ نمونے کے ٹیسٹ کو فی بازو
تقریباً 3,850 صارفین درکار ہیں، کل 7,700، اور اسے صرف ایک بار، آخر میں، پڑھا جا
سکتا ہے۔ anytime-valid ٹیسٹ اپنی آزادی کی قیمت ادا کرتا ہے: وہی طاقت حاصل کرنے
کے لیے اسے ایک تجزیے کے 1.3–1.6 گنا صارفین درکار ہیں، اور اس رن میں اس سے بھی
زیادہ لگے۔ بدلے میں پہلے سے کوئی نمونے کا حجم مقرر نہیں کرنا پڑتا، اور آپ روزانہ
نتیجہ دیکھ سکتے ہیں اور واضح ہوتے ہی رک سکتے ہیں۔ جب اثر منصوبے سے بڑا ہو تو ایسا
بہت پہلے ہو جاتا ہے۔

## آمدنی: محدود میٹرک کے لیے exact وقفہ

`BoundedABTest` کو میٹرک کی صرف حدیں (bounds) درکار ہیں۔ آمدنی کو ٹیسٹ سے پہلے
اپنی منتخب کردہ قدر پر حد بند (cap) کریں (یہاں 30)، اور اوسطوں کے فرق کے لیے
سلسلۂ اعتماد (confidence sequence) کسی بھی تقسیم کے لیے exact ہے:

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

وقفہ 20,000 میں سے ہر بار دیکھنے پر بیک وقت درست ہے، صرف آخری بار نہیں۔ یہاں اس
میں ابھی بھی 0 شامل ہے: اتنی شور والی (noisy) میٹرک پر تقریباً 0.5 کا اضافہ ثابت
کرنے کے لیے 20,000 صارفین کافی نہیں ہیں، اس لیے تجربہ جاری رہتا ہے۔

## پہلے ٹریفک کی تقسیم جانچیں

Sample ratio mismatch کا مطلب ہے کہ تقسیم کنفیگر کی گئی تقسیم سے مختلف ہے، مثلاً
assignment یا logging میں کسی بگ کی وجہ سے۔ ایسے تجربے سے حاصل ہونے والے اثر کے
تخمینے قابلِ اعتماد نہیں ہوتے۔ 50/50 سے 52/48 کا mismatch تجربہ چلتے چلتے پکڑ لیا
جاتا ہے:

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

## ایک ساتھ متعدد میٹرکس

دس آزاد میٹرکس کو ہر ایک 5% پر ٹیسٹ کرنے سے کم از کم ایک غلط دریافت (false
discovery) کا تقریباً 40% امکان بنتا ہے۔ `MultipleTests` تمام ٹیسٹوں کے e-value
کو e-BH طریقۂ کار سے یکجا کرتا ہے، تاکہ غلط دریافت کی شرح کسی بھی رکنے کے وقت
(stopping time) پر `alpha` پر رہے:

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

## احتیاطیں

* **اسی اکائی کو رینڈمائز کریں جس کا آپ تجزیہ کرتے ہیں۔** اگر صارفین رینڈمائز کیے
  گئے ہیں تو فی صارف ایک ریکارڈ دیں، فی پیج ویو نہیں۔ فی سیشن میٹرکس کے لیے
  `RatioABTest` استعمال کریں، جو صارف کے مجموعوں پر کام کرتا ہے۔
* **محدود میٹرک کی حد ٹیسٹ سے پہلے مقرر کریں۔** ڈیٹا دیکھنے کے بعد اسے منتخب
  کرنا ضمانت کو کالعدم کر دیتا ہے۔
* **Asymptotic طریقوں کو بڑے نمونے درکار ہیں۔** `ABTest` اور `RatioABTest` کے لیے
  وقفہ لمبے رن میں صرف تقریباً درست ہے۔ جہاں موزوں ہوں، exact طریقوں کو ترجیح
  دیں۔
* **موافق ٹریفک تقسیم (adaptive traffic allocation)** (bandits) کے لیے ایسا ٹیسٹ
  درکار ہے جو اس وقت بھی درست رہے جب تقسیم نتائج پر منحصر ہو:
  `TwoProportionTest(method="universal")` یا
  `BoundedABTest(propensity_input=...)`۔ دیکھیں
  [ٹیوٹوریل §10](../../tutorials/ab-test.md)۔

مزید: [A/B ٹیسٹ ٹیوٹوریل](../../tutorials/ab-test.md) (CUPED، تناسبی میٹرکس، شرحیں،
دورانیے کی منصوبہ بندی) اور
[تجربات کا ایک پروگرام](../../tutorials/experiment-programme.md)
(متعدد تجربات پر غلط دریافت کی شرح)۔
