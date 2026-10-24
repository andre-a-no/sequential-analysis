---
description: چگونه آزمون نسبت احتمال دنباله‌ای والد (SPRT) را در Python با sequential-analysis اجرا کنیم. نرخ‌های خطا، میانگین اندازهٔ نمونه در مقایسه با آزمون با اندازهٔ نمونهٔ ثابت، و جایگزین‌های بریده‌شده (2-SPRT، طرح‌های بهینهٔ Kiefer–Weiss).
language: fa
---

# چگونه SPRT والد را در Python اجرا کنم؟

> این صفحه ترجمه‌ای از [صفحهٔ انگلیسی](../../guide/sprt.md) است. این ترجمه هنوز توسط یک گویشور بومی بازبینی نشده است؛ هر جا این دو با هم تفاوت داشته باشند، صفحهٔ انگلیسی معتبر است.

**پاسخ کوتاه.** `SPRT(family, theta0, theta1, alpha, beta)` از
`sequential_analysis.procedures` آزمون نسبت احتمال دنباله‌ای والد (sequential
probability ratio test, SPRT) را پیاده‌سازی می‌کند. این آزمون میان دو فرض ساده
با کمترین تعداد مشاهدات به‌طور میانگین تصمیم می‌گیرد. مشاهدات را یکی‌یکی به آن
بدهید و در نخستین تصمیم متوقف شوید. در مثال زیر، این آزمون به حدود نیمی از
مشاهداتِ یک آزمون با اندازهٔ نمونهٔ ثابت با همان نرخ‌های خطا نیاز دارد: به‌طور
میانگین 65–76 قطعه به جای 133. اگر به بیشینهٔ تضمین‌شده‌ای برای اندازهٔ نمونه
نیاز دارید، به جای آن از `TwoSPRT` یا طرحی از `kiefer_weiss_plan` استفاده
کنید.

## مثال: نرخ معیوبی 10% است یا 20%؟

یک محموله اگر نرخ معیوبی آن 10% باشد پذیرفته و اگر 20% باشد رد می‌شود، و هر
دو نرخ خطا 5% است:

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

روی محموله‌های بسیار چه عملکردی دارد؟

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

یک آزمون با اندازهٔ نمونهٔ ثابت با همان نرخ‌های خطا در هر محموله حدود 133
قطعه را بازرسی می‌کند (تقریب نرمال). SPRT به‌طور میانگین 43–51% کمتر بازرسی
می‌کند. با این حال اندازهٔ نمونهٔ آن تصادفی است و کران بالایی ندارد، و چند
محموله بسیار بیشتر از میانگین طول می‌کشند.

آستانه‌ها آستانه‌های والد هستند: log((1 − β)/α) و log(β/(1 − α)). این
آستانه‌ها، برای هر اندازهٔ نمونه‌ای در زمان توقف، تضمین می‌کنند که نرخ‌های خطای
واقعی α′ و β′ در روابط α′ ≤ α/(1 − β)، β′ ≤ β/(1 − α) و α′ + β′ ≤ α + β صدق
کنند. نسبت درست‌نمایی (likelihood ratio) هنگام توقف از آستانه‌ها فراتر
می‌رود، پس در عمل نرخ‌ها کمتر از مقادیر اسمی‌اند، همان‌طور که اینجا دیده
می‌شود. معنای `SPRT.guarantee == "exact"` همین است. برای نرخ‌های خطایی که به
جای کران‌دار شدن دقیقاً محاسبه شوند، از `operating_characteristic` روی یک طرح
استفاده کنید (پایین‌تر).

## وقتی به بیشینهٔ اندازهٔ نمونه نیاز دارید

* `TwoSPRT` (2-SPRT لوردن، Lorden) تا یک افق ثابت متوقف می‌شود و اندازهٔ
  نمونهٔ مورد انتظار در بدترین حالت را تقریباً کمینه می‌کند.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  در `sequential_analysis.design` طرح بهینه با بیشینهٔ اندازهٔ نمونه را با
  استقرای پسرو (backward induction) محاسبه می‌کند. `PlanTest` آن را اجرا
  می‌کند، و `operating_characteristic` نرخ‌های خطای دقیق و اندازهٔ نمونهٔ مورد
  انتظار آن را بدون شبیه‌سازی به دست می‌دهد. ببینید
  `examples/07_design_kiefer_weiss.py`.
* برای چند نگاه برنامه‌ریزی‌شده به جای یک نگاه پس از هر مشاهده، از یک
  [طرح دنباله‌ای گروهی](clinical-trials.md) استفاده کنید.

## وقتی SPRT ابزار نادرستی است

* **فرض‌ها ساده نیستند.** «نرخ 10% است» در برابر «نرخ هر مقدار دیگری است» یک
  فرض مقابل مرکب است. از SPRT آمیخته (`NormalMixtureSPRT`، `TMixtureSPRT`) یا
  آزمون از طریق شرط‌بندی (`BettingMeanTest`) استفاده کنید که در برابر هر فرض
  مقابلی معتبر در هر زمان (anytime-valid) هستند.
* **مقدار واقعی میان θ₀ و θ₁ قرار دارد.** در این حالت SPRT کندترین عملکرد خود
  را دارد و اندازهٔ نمونهٔ مورد انتظار آن می‌تواند از اندازهٔ نمونهٔ ثابت بیشتر
  شود. طرح Kiefer–Weiss دقیقاً برای همین حالت ساخته شده است.

خانواده‌های موجود برای روال‌های نسبت درست‌نمایی: `Gaussian` (واریانس معلوم)،
`Bernoulli`، `Poisson`، `Exponential`.
