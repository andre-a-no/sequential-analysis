---
description: كيف تنفّذ اختبار نسبة الاحتمال التتابعي لوالد (SPRT) في Python باستخدام sequential-analysis. معدلات الخطأ، ومتوسط حجم العينة مقارنةً باختبار بحجم عينة ثابت، والبدائل المقتطعة (2-SPRT، وخطط Kiefer–Weiss المثلى).
language: ar
---

# كيف أنفّذ اختبار SPRT لوالد في Python؟

> هذه ترجمة [للصفحة الإنجليزية](../../guide/sprt.md). لم يراجعها متحدث أصلي باللغة بعد؛ وحيثما اختلفت الصفحتان، فالصفحة الإنجليزية هي المرجع المعتمد.

**الإجابة المختصرة.** تطبّق `SPRT(family, theta0, theta1, alpha, beta)` من
`sequential_analysis.procedures` اختبار نسبة الاحتمال التتابعي لوالد
(sequential probability ratio test, SPRT). وهو يحسم بين فرضيتين بسيطتين
بأقل عدد من المشاهدات في المتوسط. غذِّه بمشاهدة واحدة في كل مرة وتوقف عند
أول قرار. في المثال أدناه يحتاج إلى نحو نصف مشاهدات اختبار بحجم عينة ثابت
بمعدلات الخطأ نفسها: 65–76 وحدة في المتوسط بدلًا من 133. وإذا كنت تحتاج
إلى حد أقصى مضمون لحجم العينة، فاستخدم بدلًا منه `TwoSPRT` أو خطة من
`kiefer_weiss_plan`.

## مثال: هل معدل العيوب 10% أم 20%؟

تُقبل الدفعة إذا كان معدل العيوب فيها 10% وتُرفض إذا كان 20%، مع معدلَي
خطأ قدر كل منهما 5%:

```python
import random

from sequential_analysis.procedures import SPRT, Bernoulli

test = SPRT(Bernoulli(), theta0=0.10, theta1=0.20, alpha=0.05, beta=0.05)

def inspect_items(rate, seed):
    """Inspect items until the test decides; returns (decision, items inspected)."""
    rnd = random.Random(seed)
    state = test.initial_state()
    while state.decision is None:
        state, out = test.step(state, {"x": int(rnd.random() < rate)})
    return state.decision, state.n

decision, n = inspect_items(0.10, seed=1)
print(f"a good batch: {decision} after {n} items")
```

```text
a good batch: accept_h0 after 108 items
```

ما مدى جودة أدائه على دفعات كثيرة؟

```python
for rate in (0.10, 0.20):
    results = [inspect_items(rate, seed) for seed in range(2000)]
    wrong = sum(d == ("reject_h0" if rate == 0.10 else "accept_h0") for d, _ in results) / len(results)
    average = sum(n for _, n in results) / len(results)
    longest = max(n for _, n in results)
    print(f"defect rate {rate:.0%}: wrong decision {wrong:.1%}, average {average:.0f} items, longest {longest}")
```

```text
defect rate 10%: wrong decision 3.5%, average 76 items, longest 370
defect rate 20%: wrong decision 4.3%, average 65 items, longest 315
```

يفحص اختبار بحجم عينة ثابت بمعدلات الخطأ نفسها نحو 133 وحدة في كل دفعة
(التقريب الطبيعي). أما SPRT فيفحص في المتوسط وحدات أقل بنسبة 43–51%. غير
أن حجم عينته عشوائي ولا حد أعلى له، وتستغرق بعض الدفعات وقتًا أطول بكثير
من المتوسط.

العتبتان هما عتبتا Wald: log((1 − β)/α) وlog(β/(1 − α)). وهما تضمنان،
لأي حجم عينة عند التوقف، أن يحقق معدلا الخطأ الفعليان α′ وβ′ المتباينات
α′ ≤ α/(1 − β) وβ′ ≤ β/(1 − α) وα′ + β′ ≤ α + β. وتتجاوز نسبة الإمكان
(likelihood ratio) العتبتين حين تتوقف، لذا يكون المعدلان عمليًا أقل من
القيمتين الاسميتين، كما هنا. وهذا هو معنى `SPRT.guarantee == "exact"`.
وللحصول على معدلات خطأ محسوبة بدقة لا محصورة بحدود، استخدم
`operating_characteristic` على خطة (انظر أدناه).

## حين تحتاج إلى حد أقصى لحجم العينة

* `TwoSPRT` (اختبار 2-SPRT لـ Lorden) يتوقف عند أفق ثابت ويقلّل تقريبًا
  إلى أدنى حد حجمَ العينة المتوقع في أسوأ الحالات.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  في `sequential_analysis.design` تحسب الخطة المثلى ذات الحد الأقصى لحجم
  العينة بالاستقراء العكسي (backward induction). وينفّذها `PlanTest`،
  وتعطي `operating_characteristic` معدلات الخطأ الدقيقة لها وحجم العينة
  المتوقع دون محاكاة. انظر
  `examples/07_design_kiefer_weiss.py`.
* لعدد قليل من النظرات المخطط لها بدلًا من نظرة بعد كل مشاهدة، استخدم
  [تصميمًا تتابعيًا جماعيًا](clinical-trials.md).

## حين يكون SPRT الأداة الخاطئة

* **الفرضيات ليست بسيطة.** "المعدل 10%" مقابل "المعدل أي قيمة أخرى" فرضية
  بديلة مركّبة. استخدم SPRT المزيج (`NormalMixtureSPRT`، `TMixtureSPRT`)
  أو اختبارًا بالمراهنة (`BettingMeanTest`)، وكلاهما صالح في أي وقت
  (anytime-valid) مقابل كل بديل.
* **القيمة الحقيقية تقع بين θ₀ وθ₁.** يكون SPRT حينئذ في أبطأ حالاته، وقد
  يتجاوز حجم العينة المتوقع حجم العينة الثابت. وخطة Kiefer–Weiss مبنية
  لهذه الحالة تحديدًا.

العائلات المتاحة لإجراءات نسبة الإمكان: `Gaussian` (تباين معلوم)،
`Bernoulli`، `Poisson`، `Exponential`.
