---
description: كيف تخطّط للتحليلات المرحلية في تجربة سريرية وتنفّذها في Python، بالتصاميم التتابعية الجماعية (O'Brien–Fleming وPocock وإنفاق ألفا Lan–DeMets وحدود عدم الجدوى)، وأحجام العينات للمتوسطات والنسب والبقاء، مع التحقق مقابل rpact، باستخدام sequential-analysis.
language: ar
---

# كيف أخطّط للتحليلات المرحلية في تجربة سريرية؟

> هذه ترجمة [للصفحة الإنجليزية](../../guide/clinical-trials.md). لم يراجعها متحدث أصلي باللغة بعد؛ وحيثما اختلفت الصفحتان، فالصفحة الإنجليزية هي المرجع المعتمد.

**الإجابة المختصرة.** استخدم تصميمًا تتابعيًا جماعيًا (group sequential
design). تحسب الدالة `group_sequential_design(alpha, fractions, spending=...)`
من `sequential_analysis.group_sequential`:

* حدود الفعالية (efficacy boundaries)، مع إنفاق ألفا (alpha spending) وفق
  Lan–DeMets (من نوع O'Brien–Fleming ونوع Pocock وغيرهما)؛
* حدود عدم الجدوى غير الملزِمة (non-binding futility boundaries)؛
* القوة الإحصائية وحجم العينة المتوقع؛
* الحد الأقصى لحجم العينة للمتوسطات والنسب، أو عدد الأحداث لتحليل البقاء.

تتطابق الحدود وأحجام العينات مع حزمة R المسماة rpact. ثم تتولى إجراءات
الاختبار (`GroupSequentialTest`، `GroupSequentialTwoMeans`،
`GroupSequentialProportions`، `GroupSequentialLogRank`) تنفيذ التجربة،
مريضًا بعد مريض أو حدثًا بعد حدث. وتُجري كل تحليل مرحلي (interim
analysis) عند بلوغ نسبة المعلومات (information fraction) الخاصة به.

## التصميم: أربعة تحليلات، إنفاق O'Brien–Fleming

α أحادية الجانب = 0.025، والتحليلات عند 25% و50% و75% و100% من
المرضى، وقوة إحصائية 90%، مع حدّ لعدم الجدوى:

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

## نقاط النهاية الثنائية ونقاط نهاية البقاء

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

مع إنفاق O'Brien–Fleming، تكلّف ثلاثة تحليلات 1.3% مرضى أكثر من تحليل
نهائي واحد.

## تنفيذ التجربة

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

توقفت التجربة لثبوت الفعالية عند التحليل الثاني، بعد ثلثي المرضى المخطط
لهم.

## حين لا تجري التحليلات كما خُطّط لها

نادرًا ما تجتمع لجان مراقبة البيانات عند 25% من المعلومات بالضبط:

* تعيد `design.at(fractions)` حساب الحدود للمعلومات التي بُلغت فعلًا.
  ويحافظ إنفاق ألفا على المستوى الكلي.
* يقبل `GroupSequentialMonitor` أي إحصاءة تحسبها بنفسك (نموذج Cox، نموذج
  مختلط) بوصفها قيمة Z مع معلوماتها عند كل اجتماع.

## وإذا أردت النظر بعد كل مريض؟

لا يسمح التصميم التتابعي الجماعي إلا بعدد النظرات المخطط له. للمراقبة بعد
كل مريض أو حدث، استخدم إجراءً صالحًا في أي وقت (anytime-valid):
`AnytimeLogRankTest` للبقاء، و`TwoProportionTest` لمعدلات الاستجابة،
و`TMixtureSPRT` للمتوسط. وهي تحتاج إلى مرضى أكثر عند الأثر المخطط له.
انظر [درس تعليمي: تجربة بقاء](../../tutorials/survival.md).

## الممارسة التنظيمية

التصاميم التتابعية الجماعية مع إنفاق ألفا هي النهج الراسخ في التجارب
التأكيدية، وهي موصوفة في الدليل الإرشادي ICH E9 وفي إرشادات FDA بشأن
التصاميم التكيفية (2019). تحسب هذه المكتبة التصاميم وتحتفظ بسجل قابل
للتدقيق والاستئناف لكل تحليل (نقطة الحفظ وملخص سجلها). وهي ليست برمجية
مُصادَقًا عليها بالمعنى التنظيمي: فالجهة الراعية التي تستخدمها في ملف
تقديم عليها أن تصادق عليها كأي أداة أخرى.

المزيد: [درس تعليمي: تجربة تتابعية جماعية](../../tutorials/group-sequential.md)،
الذي يقارن الأرقام مع rpact؛
[المرجع: التصميم والتخطيط](../../reference/design.md).
