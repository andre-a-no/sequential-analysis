---
description: متتاليات الثقة (confidence sequences) فترات ثقة تبقى صالحة عند كل أحجام العينة في آن واحد، فيمكن مراقبتها باستمرار. كيف تحسبها في Python لمتوسط محدود، ولوسيط أو كمّيّة، ولمتوسط ذي ذيول ثقيلة، باستخدام sequential-analysis.
language: ar
---

# كيف أحصل على فترة ثقة تبقى صالحة مهما واصلت النظر؟

> هذه ترجمة [للصفحة الإنجليزية](../../guide/confidence-sequences.md). لم يراجعها متحدث أصلي باللغة بعد؛ وحيثما اختلفت الصفحتان، فالصفحة الإنجليزية هي المرجع المعتمد.

**الإجابة المختصرة.** استخدم **متتالية ثقة** (confidence sequence). وهي
متتالية من الفترات، فترة بعد كل مشاهدة، تحتوي على القيمة الحقيقية عند
جميع أحجام العينة في آن واحد باحتمال لا يقل عن 95%. يمكنك مراقبتها،
والتوقف حين تصبح ضيقة بما يكفي أو حين تستبعد الصفر، والإبلاغ عن الفترة
التي توقفت عندها. أما فترة الثقة المعتادة بمستوى 95% فلا تَعِد بـ 95% إلا
عند حجم عينة واحد محدّد مسبقًا.

| ما تقدّره | الافتراض | الإجراء | الضمان |
|---|---|---|---|
| متوسط بيانات محدودة (معدلات، درجات، إيراد مقيّد بسقف) | القيم في `[lower, upper]` | `BettingConfidenceSequence` | exact |
| الوسيط، المئين الـ 90، أي كمّيّة | لا شيء | `QuantileConfidenceSequence` | exact |
| متوسط ذو ذيول ثقيلة أو قيم شاذة | حدّ أعلى للانحراف المعياري | `CatoniConfidenceSequence` | exact |
| متوسط بيانات طبيعية، التباين مجهول | التوزيع الطبيعي | `TMixtureSPRT` (`lower`، `upper`) | exact في ظل التوزيع الطبيعي |
| متوسط أي شيء، تشغيلات طويلة | تباين منتهٍ | `AsymptoticConfidenceSequence` | asymptotic |
| الفرق بين ذراعين | انظر [اختبارات A/B](ab-testing.md) | `BoundedABTest`، `ABTest` | exact / asymptotic |

## الفترة المعتادة تفشل حين تُراقَب

اسحب 500 مشاهدة لمتغيّر 0/1 متوسطه 0.3، وابتداءً من المشاهدة الثلاثين
احسب بعد كل واحدة فترة الكتب المدرسية بمستوى 95%: المتوسط ± 1.96 خطأ
معياري. في كم تشغيلًا من 100 تُخطئ الفترة المتوسط الحقيقي في لحظة ما؟

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

إن "95%" الخاصة بها لا تصحّ إلا عند حجم عينة محدّد مسبقًا. أما متتالية
الثقة للبيانات نفسها، المبنية بطريقة المراهنة (betting) (Waudby-Smith and
Ramdas 2024)، فتخطئ عند n ما في 5% على الأكثر من التشغيلات بحكم بنائها:

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

## وسيط زمن الاستجابة، بلا أي افتراض

أزمنة الاستجابة ملتوية وذات ذيول ثقيلة، لذا لا يمكن الوثوق بفترة "المتوسط ±
الخطأ المعياري" لها. تغطي `QuantileConfidenceSequence` أي كمّيّة (quantile)
لأي توزيع، بما في ذلك حالات التساوي:

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

القيمتان الحقيقيتان هما 120 ms و258.8 ms. وتصحّ الفترتان كلتاهما عند جميع
أحجام العينة الـ 2,000 في آن واحد.

## مزالق

* **الحدود والسقوف جزء من الافتراض.** اختر `lower` و`upper` قبل رؤية
  البيانات. وتُرفض أي قيمة خارجهما.
* **لا توجد طريقة تعطي تغطية دقيقة لمتوسط بيانات غير محدودة اعتباطية.**
  لمثل هذه البيانات استخدم كمّيّة، أو ضع سقفًا للقيم، أو افترض حدًّا أعلى
  للانحراف المعياري (Catoni)، أو اقبل بمتتالية تقاربية.
* **متتاليات الثقة أعرض من الفترة المنفردة** عند حجم العينة نفسه. والعرض
  هو ثمن الصلاحية عند كل أحجام العينة في آن واحد.

المزيد: [أي طريقة؟](../../choosing.md)،
[المرجع: الطرق الصالحة في أي وقت واللامعلمية](../../reference/anytime.md).
