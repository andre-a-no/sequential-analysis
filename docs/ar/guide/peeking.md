---
description: لماذا يضخّم فحص القيمة الاحتمالية كل يوم النتائج الإيجابية الكاذبة في اختبارات A/B والتجارب (مشكلة التلصّص على النتائج، peeking)، والعائلات الثلاث للطرق التتابعية التي تعالجها، في Python باستخدام sequential-analysis.
language: ar
---

# لماذا لا يجوز لي النظر إلى القيمة الاحتمالية كل يوم؟

> هذه ترجمة [للصفحة الإنجليزية](../../guide/peeking.md). لم يراجعها متحدث أصلي باللغة بعد؛ وحيثما اختلفت الصفحتان، فالصفحة الإنجليزية هي المرجع المعتمد.

**الإجابة المختصرة.** لا يَعِد الاختبار بحجم عينة ثابت (fixed-sample test)
بمعدل نتائج إيجابية كاذبة قدره 5% إلا إذا نظرت إلى النتيجة مرة واحدة، عند
حجم العينة المخطط له. فإذا نظرت مرارًا وتوقفت عند أول مرة تكون فيها
p < 0.05، فإنك تمنح نفسك فرصًا كثيرة للانخداع. ومع 20 نظرة يرتفع معدل
النتائج الإيجابية الكاذبة إلى نحو 25%. أما الطرق التتابعية فمبنية لكي
يُنظر فيها مرارًا. ومعها يبقى المعدل عند 5% أو أقل مهما تكرّر نظرك ومتى
توقفت.

## مشكلة التلصّص على النتائج، بالأرقام

ذراعان لهما معدل التحويل نفسه 10% (اختبار A/A)، و2,000 مستخدم، و200
تكرار. "التلصّص" (peeking) يجري اختبار z المعتاد لنسبتين بعد كل 100
مستخدم ويتوقف عند أول p < 0.05. أما `TwoProportionTest` التتابعي فيُفحص
بعد كل مستخدم على حدة:

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

النظرة الواحدة تفي بوعدها. وعشرون نظرة تجعل معدل الخطأ أكبر بنحو ست مرات.
أما الاختبار التتابعي، الذي يُنظر فيه بعد كل واحد من المستخدمين الـ
2,000، فيبقيه عند 5%. هذا هو الوعد: ضمانه **exact**
(`TwoProportionTest.guarantee == "exact"`)، أي معدل نتائج إيجابية كاذبة لا
يزيد على 5% عند كل حجم عينة، مهما تكرّر نظرك. ومع 200 تكرار، فإن 10 نتائج
إيجابية كاذبة هي ما يعطيه معدل دقيق قدره 5%.

## العائلات الثلاث للطرق التتابعية

| العائلة | متى يجوز لك النظر | الاستخدام النموذجي | في sequential-analysis |
|---|---|---|---|
| **اختبارات نسبة الاحتمال التتابعية** (sequential probability ratio tests) (Wald 1945) | بعد كل مشاهدة | فرضية بسيطة مقابل أخرى، بأقل عدد من المشاهدات في المتوسط: ضبط الجودة، المحاكاة، علم النفس الفيزيائي | `SPRT`، `TwoSPRT`، `kiefer_weiss_plan` |
| **التصاميم التتابعية الجماعية** (group sequential designs) (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | عند عدد قليل من التحليلات المرحلية المخطط لها | التجارب السريرية مع لجنة لمراقبة البيانات | `group_sequential_design`، `GroupSequentialTest`، `GroupSequentialProportions`، `GroupSequentialLogRank` |
| **الاستدلال الصالح في أي وقت** (anytime-valid inference): قيم e، متتاليات الثقة، SPRT المزيج (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | بعد كل مشاهدة، مع التوقف لأي سبب | اختبارات A/B عبر الإنترنت، لوحات المراقبة | `TwoProportionTest`، `BoundedABTest`، `NormalMixtureSPRT`، `BettingConfidenceSequence`، `MultipleTests` |

**ما الكلفة.** النظر بوتيرة أعلى يحتاج إلى بيانات أكثر عند الأثر الذي خطّطت
له:

* يحتاج التصميم التتابعي الجماعي بأربعة تحليلات إلى 1–20% مرضى أكثر من
  تحليل واحد؛
* يحتاج الاختبار الصالح في أي وقت لنسبتين إلى 1.3–1.6 ضعف عدد المستخدمين
  في تحليل واحد.

وفي المقابل، يوقف الأثر الكبير التجربة مبكرًا، ولا يضطر أحد إلى تحديد حجم
العينة مسبقًا.

## حين لا تكون هذه هي المشكلة

لا يضخّم التلصّص الأخطاء إلا حين يعتمد ما تفعله على ما رأيته. فإذا نظرت إلى
لوحة المتابعة لكنك تُكمل التجربة دائمًا حتى حجمها المخطط له وتختبر مرة
واحدة، فإن الاختبار بحجم عينة ثابت صالح. وهو كذلك الخيار الأكفأ في تلك
الحالة.

التالي: [أوقف اختبار A/B مبكرًا](ab-testing.md)،
[متتاليات الثقة](confidence-sequences.md)،
[مسرد المصطلحات](glossary.md).
