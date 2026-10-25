---
description: سلسلۂ اعتماد (confidence sequences) ایسے وقفۂ اعتماد ہیں جو بیک وقت نمونے کے ہر حجم پر درست رہتے ہیں، اس لیے ان پر مسلسل نظر رکھی جا سکتی ہے۔ Python میں محدود اوسط، وسطانیہ یا کوانٹائل، اور بھاری دُم والے اوسط کے لیے ان کا حساب کیسے لگائیں، sequential-analysis کے ساتھ۔
language: ur
---

# ایسا وقفۂ اعتماد کیسے حاصل کریں جو بار بار دیکھنے پر بھی درست رہے؟

> یہ [انگریزی صفحے](../../guide/confidence-sequences.md) کا ترجمہ ہے۔ ابھی کسی اہلِ زبان نے اس کا جائزہ نہیں لیا؛ جہاں دونوں میں فرق ہو، وہاں انگریزی صفحہ ہی مستند ہے۔

**مختصر جواب۔** **سلسلۂ اعتماد (confidence sequence)** استعمال کریں۔ یہ وقفوں کا
ایک سلسلہ ہے، ہر مشاہدے کے بعد ایک، جس میں نمونے کے تمام حجموں پر بیک وقت اصل قدر
کم از کم 95% احتمال کے ساتھ شامل رہتی ہے۔ آپ اس پر نظر رکھ سکتے ہیں، جب یہ کافی تنگ
ہو جائے یا صفر کو خارج کر دے تب رک سکتے ہیں، اور جس وقفے پر رکے اسے رپورٹ کر سکتے
ہیں۔ عام 95% وقفۂ اعتماد (confidence interval) 95% کا وعدہ صرف پہلے سے مقرر
کیے گئے نمونے کے ایک حجم پر کرتا ہے۔

| آپ کس چیز کا تخمینہ لگاتے ہیں | مفروضہ | طریقۂ کار | ضمانت |
|---|---|---|---|
| محدود (bounded) ڈیٹا کا اوسط (شرحیں، اسکور، حد بند آمدنی) | قدریں `[lower, upper]` میں | `BettingConfidenceSequence` | exact |
| وسطانیہ (median)، 90واں پرسنٹائل، کوئی بھی کوانٹائل | کوئی نہیں | `QuantileConfidenceSequence` | exact |
| بھاری دُم (heavy tails) یا آؤٹ لائرز والا اوسط | معیاری انحراف پر ایک حد | `CatoniConfidenceSequence` | exact |
| normal ڈیٹا کا اوسط، تغیر (variance) نامعلوم | normality | `TMixtureSPRT` (`lower`، `upper`) | normality کے تحت exact |
| کسی بھی چیز کا اوسط، لمبے رن | متناہی تغیر | `AsymptoticConfidenceSequence` | asymptotic |
| دو بازوؤں کے درمیان فرق | دیکھیں [A/B ٹیسٹ](ab-testing.md) | `BoundedABTest`، `ABTest` | exact / asymptotic |

## دیکھتے رہنے پر عام وقفہ ناکام ہو جاتا ہے

اوسط 0.3 والے ایک 0/1 متغیر کے 500 مشاہدات لیں، اور 30ویں سے آگے ہر ایک کے بعد
درسی کتاب والا 95% وقفہ نکالیں: اوسط ± 1.96 معیاری غلطیاں (standard errors)۔ 100
رنز میں سے کتنے رنز میں وقفہ کسی نقطے پر اصل اوسط سے چوک جاتا ہے؟

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

اس کا "95%" صرف پہلے سے مقرر نمونے کے حجم پر لاگو ہوتا ہے۔ اسی ڈیٹا کے لیے شرط
(betting) کے ذریعے بنا سلسلۂ اعتماد (Waudby-Smith and Ramdas 2024) اپنی ساخت ہی سے
زیادہ سے زیادہ 5% رنز میں کسی n پر چوکتا ہے:

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

## وسطانی لیٹنسی، بغیر کسی مفروضے کے

لیٹنسی ترچھی (skewed) اور بھاری دُم والی ہوتی ہے، اس لیے اوسط ± معیاری غلطی والا
وقفہ اس کے لیے قابلِ اعتماد نہیں ہے۔ `QuantileConfidenceSequence` کسی بھی تقسیم کے
کسی بھی کوانٹائل کا احاطہ کرتا ہے، برابر قدروں (ties) سمیت:

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

اصل قدریں 120 ms اور 258.8 ms ہیں۔ دونوں وقفے نمونے کے تمام 2,000 حجموں پر بیک وقت
درست ہیں۔

## احتیاطیں

* **حدیں اور cap مفروضے کا حصہ ہیں۔** `lower` اور `upper` ڈیٹا دیکھنے سے پہلے
  منتخب کریں۔ ان سے باہر کی قدر رد کر دی جاتی ہے۔
* **کوئی بھی طریقہ من مانے غیر محدود (unbounded) ڈیٹا کے اوسط کے لیے exact
  احاطہ (coverage) نہیں دیتا۔** ایسے ڈیٹا کے لیے کوانٹائل استعمال کریں، قدروں کو
  حد بند کریں، معیاری انحراف پر ایک حد فرض کریں (Catoni)، یا asymptotic سلسلہ
  قبول کریں۔
* **سلسلۂ اعتماد ایک اکیلے وقفے سے چوڑا ہوتا ہے**، نمونے کے اسی حجم پر۔ یہ چوڑائی
  بیک وقت نمونے کے ہر حجم پر درست ہونے کی قیمت ہے۔

مزید: [کون سا طریقہ؟](../../choosing.md)،
[حوالہ: anytime-valid اور ناپیرامیٹرک](../../reference/anytime.md)۔
