---
description: كيف توقف اختبار A/B مبكرًا في Python دون تضخيم النتائج الإيجابية الكاذبة. اختبارات صالحة في أي وقت لمعدل التحويل وللإيرادات المحدودة، وفحص عدم تطابق نسبة العينة (SRM)، وضبط معدل الاكتشاف الخاطئ عبر مقاييس كثيرة، باستخدام sequential-analysis.
language: ar
---

# كيف أوقف اختبار A/B مبكرًا دون تضخيم النتائج الإيجابية الكاذبة؟

> هذه ترجمة [للصفحة الإنجليزية](../../guide/ab-testing.md). لم يراجعها متحدث أصلي باللغة بعد؛ وحيثما اختلفت الصفحتان، فالصفحة الإنجليزية هي المرجع المعتمد.

**الإجابة المختصرة.** استخدم اختبارًا صالحًا في أي وقت (anytime-valid):
تبقى قيمته الاحتمالية (p-value) وفترة الثقة الخاصة به صالحتين مهما
تكرّر نظرك إليهما، فيمكنك التوقف حالما تتضح النتيجة. في
sequential-analysis:

| المقياس | الإجراء | الضمان |
|---|---|---|
| معدل التحويل (0/1) | `TwoProportionTest` | exact |
| أي مقياس محدود (إيراد مقيّد بسقف، حصة) | `BoundedABTest` | exact |
| أحداث لكل وحدة تعرّض | `RateRatioTest` | exact لأعداد Poisson |
| مقياس نسبة (الإيراد لكل جلسة) | `RatioABTest` | asymptotic |
| متوسط مع متغيّر مصاحب سابق للتجربة (CUPED) | `ABTest` | asymptotic |
| هل توزيع الحركة كما هو مقصود؟ | `SampleRatioMismatch` | exact |
| عدة مقاييس أو أذرع معًا | `MultipleTests` (e-BH) | معدل الاكتشاف الخاطئ، exact |

غذِّ كل إجراء بمستخدم واحد في كل مرة: `state, out = test.step(state, {...})`.
وتصرّف بناءً على `out.decision` متى شئت.

## معدل التحويل: توقّف عندما تصبح البيانات حاسمة

تحوّل المجموعة الضابطة 10% من المستخدمين، والمعالجة 12%. يُنظر في
الاختبار بعد كل مستخدم ويتوقف عند أول قرار له:

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

للمقارنة، يحتاج اختبار بحجم عينة ثابت وقوة إحصائية 80% لهذا التحسّن
إلى نحو 3,850 مستخدمًا في كل ذراع، أي 7,700 إجمالًا، ولا يجوز قراءته إلا
مرة واحدة في النهاية. يدفع الاختبار الصالح في أي وقت ثمن حريته: فلكي
يبلغ القوة نفسها يحتاج إلى 1.3–1.6 ضعف عدد المستخدمين في تحليل واحد،
وقد استغرق هذا التشغيل أكثر من ذلك. وفي المقابل لا يلزم تحديد حجم عينة
مسبقًا، ويمكنك النظر في النتيجة يوميًا والتوقف حالما تتضح. وعندما يكون
الأثر أكبر من المخطط له، يحدث ذلك أبكر بكثير.

## الإيرادات: فترة دقيقة لمقياس محدود

لا يحتاج `BoundedABTest` إلا إلى حدود للمقياس. ضع سقفًا للإيراد بقيمة
تختارها قبل الاختبار (هنا 30)، فتكون متتالية الثقة (confidence sequence)
للفرق بين المتوسطين دقيقة لأي توزيع:

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

تصحّ الفترة عند كل واحدة من النظرات الـ 20,000 في آن واحد، لا عند
الأخيرة فقط. وهي هنا لا تزال تحتوي على 0: فـ 20,000 مستخدم لا يكفون
لإثبات تحسّن بنحو 0.5 في مقياس بهذا القدر من الضجيج، لذا تستمر التجربة.

## افحص توزيع الحركة أولًا

يعني عدم تطابق نسبة العينة (sample ratio mismatch) أن التوزيع يختلف عمّا
ضُبط، بسبب خطأ برمجي في التخصيص أو في التسجيل مثلًا. ولا يمكن الوثوق
بتقديرات الأثر من تجربة كهذه. ويُكتشف الانحراف من 50/50 إلى 52/48 أثناء
سير التجربة:

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

## مقاييس كثيرة في آن واحد

اختبار عشرة مقاييس مستقلة عند 5% لكل منها يعطي احتمالًا بنحو 40% لاكتشاف
خاطئ واحد على الأقل. يجمع `MultipleTests` قيم e (e-values) لكل الاختبارات
بإجراء e-BH، فيبقى معدل الاكتشاف الخاطئ (false discovery rate) عند `alpha`
عند أي زمن توقف:

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

## مزالق

* **اجعل التوزيع العشوائي على الوحدة التي تحلّلها.** إذا وُزِّع المستخدمون
  عشوائيًا، فغذِّ الاختبار بسجل واحد لكل مستخدم، لا لكل مشاهدة صفحة.
  ولمقاييس الجلسات استخدم `RatioABTest`، الذي يعمل على مجاميع المستخدمين.
* **ثبّت سقف المقياس المحدود قبل الاختبار.** اختياره بعد رؤية البيانات
  يُبطل الضمان.
* **الإجراءات التقاربية تحتاج إلى عينات كبيرة.** في `ABTest` و
  `RatioABTest` لا تكون الفترة صالحة إلا تقريبًا وفي التشغيلات الطويلة.
  فضّل الإجراءات الدقيقة حين تناسب.
* **التخصيص التكيّفي للحركة** (خوارزميات bandit) يحتاج إلى اختبار يبقى
  صالحًا حين يعتمد التوزيع على النتائج:
  `TwoProportionTest(method="universal")` أو
  `BoundedABTest(propensity_input=...)`. انظر
  [الدرس التعليمي §10](../../tutorials/ab-test.md).

المزيد: [الدرس التعليمي لاختبار A/B](../../tutorials/ab-test.md) (CUPED،
مقاييس النسبة، المعدلات، تخطيط المدة) و
[برنامج من التجارب](../../tutorials/experiment-programme.md)
(معدل الاكتشاف الخاطئ عبر تجارب كثيرة).
