---
description: Python میں sequential-analysis کے ساتھ Wald کا ترتیبی احتمالی تناسب ٹیسٹ (SPRT) کیسے چلائیں۔ غلطی کی شرحیں، مقررہ نمونے کے ٹیسٹ کے مقابلے میں نمونے کا اوسط حجم، اور truncated متبادل (2-SPRT، Kiefer–Weiss کے بہترین منصوبے)۔
language: ur
---

# Python میں Wald کا SPRT کیسے چلائیں؟

> یہ [انگریزی صفحے](../../guide/sprt.md) کا ترجمہ ہے۔ ابھی کسی اہلِ زبان نے اس کا جائزہ نہیں لیا؛ جہاں دونوں میں فرق ہو، وہاں انگریزی صفحہ ہی مستند ہے۔

**مختصر جواب۔** `sequential_analysis.procedures` کا
`SPRT(family, theta0, theta1, alpha, beta)` Wald کے ترتیبی احتمالی تناسب ٹیسٹ
(sequential probability ratio test) کو نافذ کرتا ہے۔ یہ اوسطاً سب سے کم مشاہدات کے
ساتھ دو سادہ مفروضوں (simple hypotheses) کے درمیان فیصلہ کرتا ہے۔ اسے ایک وقت میں
ایک مشاہدہ دیں اور پہلے فیصلے پر رک جائیں۔ نیچے کی مثال میں اسے یکساں غلطی کی شرحوں
والے مقررہ نمونے کے ٹیسٹ کے تقریباً نصف مشاہدات درکار ہیں: 133 کے بجائے اوسطاً
65–76 اشیا۔ اگر آپ کو نمونے کا ضمانت شدہ زیادہ سے زیادہ حجم درکار ہے تو اس کے
بجائے `TwoSPRT` یا `kiefer_weiss_plan` سے حاصل منصوبہ استعمال کریں۔

## مثال: نقص کی شرح 10% ہے یا 20%؟

ایک بیچ قبول کیا جاتا ہے اگر اس کی نقص کی شرح (defect rate) 10% ہو اور رد کیا
جاتا ہے اگر 20% ہو، دونوں غلطی کی شرحیں 5%:

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

کئی بیچز پر یہ کیسی کارکردگی دکھاتا ہے؟

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

یکساں غلطی کی شرحوں والا مقررہ نمونے کا ٹیسٹ ہر بیچ میں تقریباً 133 اشیا جانچتا ہے
(normal تخمینہ)۔ SPRT اوسطاً 43–51% کم جانچتا ہے۔ تاہم اس کا نمونے کا حجم بے ترتیب
(random) ہے اور اس کی کوئی بالائی حد نہیں، اور چند بیچز اوسط سے کہیں زیادہ وقت لیتے
ہیں۔

حدیں (thresholds) Wald کی ہیں: log((1 − β)/α) اور log(β/(1 − α))۔ یہ رکنے پر
نمونے کے کسی بھی حجم کے لیے ضمانت دیتی ہیں کہ اصل غلطی کی شرحیں α′ اور β′ شرائط
α′ ≤ α/(1 − β)، β′ ≤ β/(1 − α) اور α′ + β′ ≤ α + β پوری کرتی ہیں۔ رکتے وقت امکانی
تناسب (likelihood ratio) حدوں سے آگے نکل جاتا ہے (overshoot)، اس لیے عملی طور پر
شرحیں اسمی (nominal) شرحوں سے کم ہوتی ہیں، جیسا کہ یہاں ہے۔
`SPRT.guarantee == "exact"` کا یہی مطلب ہے۔ صرف حد بندی کے بجائے بالکل ٹھیک حساب
کی گئی غلطی کی شرحوں کے لیے کسی منصوبے پر `operating_characteristic` استعمال کریں
(نیچے)۔

## جب آپ کو نمونے کا زیادہ سے زیادہ حجم درکار ہو

* `TwoSPRT` (Lorden's 2-SPRT) ایک مقررہ افق (horizon) تک رک جاتا ہے اور بدترین
  صورت (worst case) کے متوقع نمونے کے حجم کو تقریباً کم سے کم کرتا ہے۔
* `sequential_analysis.design` میں
  `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  backward induction کے ذریعے نمونے کے زیادہ سے زیادہ حجم والے بہترین منصوبے کا
  حساب لگاتا ہے۔ `PlanTest` اسے چلاتا ہے، اور `operating_characteristic` سمیولیشن
  کے بغیر اس کی exact غلطی کی شرحیں اور متوقع نمونے کا حجم دیتا ہے۔ دیکھیں
  `examples/07_design_kiefer_weiss.py`۔
* ہر مشاہدے پر ایک بار کے بجائے چند منصوبہ بند بار دیکھنے کے لیے
  [گروہی ترتیبی ڈیزائن](clinical-trials.md) استعمال کریں۔

## جب SPRT غلط ٹول ہے

* **مفروضے سادہ نہیں ہیں۔** "شرح 10% ہے" بمقابلہ "شرح کچھ اور ہے" ایک مرکب
  (composite) متبادل ہے۔ mixture SPRT (`NormalMixtureSPRT`، `TMixtureSPRT`) یا
  شرط کے ذریعے ٹیسٹ (`BettingMeanTest`) استعمال کریں، جو ہر متبادل کے خلاف
  anytime-valid ہیں۔
* **اصل قدر θ₀ اور θ₁ کے درمیان ہے۔** تب SPRT سب سے سست ہوتا ہے، اور اس کا متوقع
  نمونے کا حجم مقررہ نمونے کے حجم سے بڑھ سکتا ہے۔ Kiefer–Weiss منصوبہ بالکل اسی
  صورت کے لیے بنا ہے۔

امکانی تناسب والے طریقوں کے لیے دستیاب خاندان (families): `Gaussian` (معلوم
تغیر)، `Bernoulli`، `Poisson`، `Exponential`۔
