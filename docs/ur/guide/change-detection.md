---
description: Python میں سینسر ریڈنگز، لیٹنسی یا میٹرکس کی اسٹریم میں تبدیلی کا سراغ کیسے لگائیں، CUSUM، Shiryaev–Roberts، ناپیرامیٹرک e-detectors اور Bayesian آن لائن نقطۂ تبدیلی کے سراغ کے ساتھ۔ جھوٹے الارم اوسط رن لمبائی (ARL) کے ذریعے کنٹرول، sequential-analysis کے ساتھ۔
language: ur
---

# پیمائشوں کی اسٹریم میں تبدیلی کا سراغ کیسے لگائیں؟

> یہ [انگریزی صفحے](../../guide/change-detection.md) کا ترجمہ ہے۔ ابھی کسی اہلِ زبان نے اس کا جائزہ نہیں لیا؛ جہاں دونوں میں فرق ہو، وہاں انگریزی صفحہ ہی مستند ہے۔

**مختصر جواب۔** ایک آن لائن نقطۂ تبدیلی ڈیٹیکٹر (online change-point detector)
استعمال کریں۔ یہ اسٹریم پر نظر رکھتا ہے اور جیسے ہی تقسیم بدلی ہوئی نظر آئے، الارم
دیتا ہے۔ اس کے جھوٹے الارم (false alarms) **اوسط رن لمبائی (average run length,
ARL)** کے ذریعے کنٹرول ہوتے ہیں: جب کچھ نہ بدلا ہو تو جھوٹے الارم تک مشاہدات کی
متوقع تعداد۔ sequential-analysis میں:

| تبدیلی سے پہلے آپ کیا جانتے ہیں | طریقۂ کار | ضمانت |
|---|---|---|
| دونوں تقسیمیں (مثلاً normal، اوسط 70 → 71) | `CUSUM`، `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| صرف اوسط، اور قدروں کی حدیں | `MeanEDetector` | ایسی ہر تقسیم کے لیے exact |
| صرف ایک کوانٹائل (مثلاً لیٹنسی کا 95واں پرسنٹائل) | `QuantileEDetector` | ہر تقسیم کے لیے exact |
| نامعلوم پیرامیٹرز والا ماڈل، پہلے اور بعد میں | `BayesianChangePoint` | ماڈل اور prior کے تحت |

## ایک سینسر جس کا اوسط کھسکتا ہے

ایک درجۂ حرارت سینسر 70.0 °C پڑھتا ہے، جس میں شور (noise) کا معیاری انحراف
(standard deviation) 0.5 ہے۔ ریڈنگ 600 سے آگے اوسط 70.4 ہے۔ حدِ فیصلہ
(threshold) log(1000) ≈ 6.9 والے CUSUM کا ARL کم از کم 1,000 ریڈنگز ہے:

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

ایک معیاری انحراف سے کم کی تبدیلی کسی بھی ایک ریڈنگ میں آنکھ سے نظر نہیں آتی۔
CUSUM شواہد (evidence) جمع کرتا ہے اور اسے ڈھونڈ لیتا ہے۔

## جب ریڈنگز normal نہ ہوں

CUSUM کا ARL صرف اسی وقت برقرار رہتا ہے جب ریڈنگز ان تقسیموں کی پیروی کریں جو آپ
نے اسے دیں۔ ترچھے (skewed) ڈیٹا (ارتعاش کے حیطے، لیٹنسی، قطار کی لمبائی) کے لیے
یہ منصوبے سے کہیں زیادہ بار جھوٹے الارم دیتا ہے۔ e-detectors کو بہت کم درکار ہے:

* `MeanEDetector` کو تبدیلی سے پہلے کا اوسط اور قدروں کی حدیں درکار ہیں۔
* `QuantileEDetector` کو تبدیلی سے پہلے کا صرف ایک کوانٹائل درکار ہے۔

ان کا ARL اس اوسط یا کوانٹائل والی **ہر** تقسیم کے لیے کم از کم ہدف کے برابر ہے:

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

عملی طور پر تبدیلی سے پہلے کا کوانٹائل کسی پُرسکون دورانیے سے اندازہ لگایا جاتا
ہے۔ تب ضمانت تقریباً برقرار رہتی ہے، اور وہ دورانیہ جتنا لمبا ہو اتنی بہتر۔

## ARL کا انتخاب

ARL جھوٹے الارموں اور تاخیر کے درمیان توازن قائم کرتا ہے۔ فی منٹ ایک ریڈنگ پر،
1,000 ریڈنگز کے ARL کا مطلب ہے معمول کے آپریشن کے تقریباً ہر 17 گھنٹے میں ایک
جھوٹا الارم، فی سینسر۔ 50 سینسرز کے ساتھ یہ روزانہ تقریباً 70 بنتے ہیں۔ ARL اس
بنیاد پر منتخب کریں کہ تمام سینسرز کو ملا کر روزانہ آپ کتنے جھوٹے الارم برداشت
کر سکتے ہیں: یہاں، 1,000,000 ریڈنگز کا ARL 50 سینسرز کو تقریباً ہر دو ہفتے میں ایک
جھوٹے الارم تک لے آتا ہے۔ اس کی قیمت جتنی لگتی ہے اس سے کم ہے، کیونکہ سراغ کی
تاخیر ARL کے صرف لوگارتھم کے ساتھ بڑھتی ہے۔ CUSUM کے لیے حدِ فیصلہ 6.9 سے 13.8
ہو جاتی ہے، اور تاخیر تقریباً دگنی ہو جاتی ہے۔

یہ ڈیٹیکٹر مانیٹرنگ کے ٹولز ہیں، حفاظتی نظام نہیں۔ انہیں کسی سند یافتہ safety
instrumented system کی جگہ استعمال نہ کریں۔

مزید: [ٹیوٹوریل: پراسیس مانیٹرنگ اور تبدیلی کا سراغ](../../tutorials/monitoring.md)،
[hidden Markov ماڈلز کے ساتھ regimes](../../tutorials/regimes.md)،
[حوالہ: تبدیلی کا سراغ](../../reference/detection.md)۔
