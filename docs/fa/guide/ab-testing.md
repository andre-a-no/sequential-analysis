---
description: چگونه یک آزمون A/B را در Python زودتر متوقف کنیم بی‌آنکه مثبت‌های کاذب افزایش یابد. آزمون‌های معتبر در هر زمان برای نرخ تبدیل و درآمد کران‌دار، بررسی عدم تطابق نسبت نمونه (SRM) و کنترل نرخ کشف کاذب روی معیارهای متعدد، با sequential-analysis.
language: fa
---

# چگونه یک آزمون A/B را زودتر متوقف کنم بی‌آنکه مثبت‌های کاذب افزایش یابد؟

> این صفحه ترجمه‌ای از [صفحهٔ انگلیسی](../../guide/ab-testing.md) است. این ترجمه هنوز توسط یک گویشور بومی بازبینی نشده است؛ هر جا این دو با هم تفاوت داشته باشند، صفحهٔ انگلیسی معتبر است.

**پاسخ کوتاه.** از آزمونی استفاده کنید که در هر زمان معتبر (anytime-valid)
باشد: مقدار p (p-value) و بازهٔ اطمینان آن هر چند بار هم که نگاه کنید معتبر
می‌مانند، پس می‌توانید به‌محض روشن شدن نتیجه متوقف شوید. در
sequential-analysis:

| معیار | روال | تضمین |
|---|---|---|
| نرخ تبدیل (0/1) | `TwoProportionTest` | exact |
| هر معیار کران‌دار (درآمد با سقف، سهم) | `BoundedABTest` | exact |
| رویداد به ازای هر واحد مواجهه | `RateRatioTest` | exact برای شمارش‌های Poisson |
| معیار نسبتی (درآمد به ازای هر نشست) | `RatioABTest` | asymptotic |
| میانگین با یک متغیر کمکی پیش از آزمایش (CUPED) | `ABTest` | asymptotic |
| آیا تقسیم ترافیک همان است که در نظر بود؟ | `SampleRatioMismatch` | exact |
| چند معیار یا چند بازو با هم | `MultipleTests` (e-BH) | نرخ کشف کاذب، exact |

به هر روال کاربران را یکی‌یکی بدهید: `state, out = test.step(state, {...})`.
و هر وقت خواستید بر اساس `out.decision` عمل کنید.

## نرخ تبدیل: وقتی داده‌ها قاطع شدند متوقف شوید

گروه کنترل 10% کاربران را تبدیل می‌کند و گروه آزمایش 12%. آزمون پس از هر
کاربر بررسی می‌شود و در نخستین تصمیمش متوقف می‌شود:

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

برای مقایسه، یک آزمون با اندازهٔ نمونهٔ ثابت با توان 80% برای این افزایش به
حدود 3,850 کاربر در هر بازو، یعنی در مجموع 7,700، نیاز دارد و فقط یک بار،
در پایان، می‌توان آن را خواند. آزمون معتبر در هر زمان بهای آزادی‌اش را
می‌پردازد: برای رسیدن به همان توان به 1.3–1.6 برابر کاربرانِ یک تحلیل واحد
نیاز دارد، و این اجرا بیش از آن طول کشید. در عوض لازم نیست اندازهٔ نمونه از
پیش تعیین شود، و می‌توانید هر روز به نتیجه نگاه کنید و به‌محض روشن شدن آن
متوقف شوید. وقتی اثر از مقدار برنامه‌ریزی‌شده بزرگ‌تر باشد، این اتفاق خیلی
زودتر می‌افتد.

## درآمد: بازه‌ای دقیق برای یک معیار کران‌دار

`BoundedABTest` فقط به کران‌های معیار نیاز دارد. برای درآمد سقفی بگذارید که
پیش از آزمون انتخاب می‌کنید (اینجا 30)، تا دنبالهٔ اطمینان (confidence
sequence) برای تفاوت میانگین‌ها برای هر توزیعی دقیق باشد:

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

این بازه در تک‌تک 20,000 نگاه به‌طور هم‌زمان برقرار است، نه فقط در آخری.
اینجا هنوز 0 را در بر دارد: 20,000 کاربر برای اثبات افزایشی در حدود 0.5 در
معیاری با این میزان نوفه کافی نیست، پس آزمایش ادامه می‌یابد.

## اول تقسیم ترافیک را بررسی کنید

عدم تطابق نسبت نمونه (sample ratio mismatch) یعنی تقسیم با آنچه پیکربندی
شده بود فرق دارد، مثلاً به دلیل یک باگ در تخصیص یا در ثبت رویدادها. برآورد
اثر از چنین آزمایشی قابل اعتماد نیست. انحراف از 50/50 به 52/48 در حین
اجرای آزمایش شناسایی می‌شود:

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

## چندین معیار به‌طور هم‌زمان

آزمودن ده معیار مستقل هر یک در سطح 5% حدود 40% احتمال دست‌کم یک کشف کاذب
به دست می‌دهد. `MultipleTests` مقادیر e (e-values) همهٔ آزمون‌ها را با روال
e-BH ترکیب می‌کند، تا نرخ کشف کاذب (false discovery rate) در هر زمان توقف
در سطح `alpha` بماند:

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

## دام‌ها

* **واحدی را تصادفی‌سازی کنید که تحلیل می‌کنید.** اگر کاربران تصادفی‌سازی
  شده‌اند، برای هر کاربر یک رکورد بدهید، نه برای هر بازدید صفحه. برای
  معیارهای مبتنی بر نشست از `RatioABTest` استفاده کنید که روی مجموع‌های هر
  کاربر کار می‌کند.
* **سقف معیار کران‌دار را پیش از آزمون تعیین کنید.** انتخاب آن پس از دیدن
  داده‌ها تضمین را باطل می‌کند.
* **روال‌های مجانبی به نمونه‌های بزرگ نیاز دارند.** برای `ABTest` و
  `RatioABTest` بازه فقط به‌طور تقریبی و در اجراهای طولانی معتبر است.
  هر جا روال‌های دقیق مناسب‌اند، آن‌ها را ترجیح دهید.
* **تخصیص تطبیقی ترافیک** (الگوریتم‌های bandit) به آزمونی نیاز دارد که
  وقتی تقسیم به نتایج وابسته است معتبر بماند:
  `TwoProportionTest(method="universal")` یا
  `BoundedABTest(propensity_input=...)`. ببینید
  [آموزش §10](../../tutorials/ab-test.md).

بیشتر: [آموزش آزمون A/B](../../tutorials/ab-test.md) (CUPED، معیارهای
نسبتی، نرخ‌ها، برنامه‌ریزی مدت) و
[برنامه‌ای از آزمایش‌ها](../../tutorials/experiment-programme.md)
(نرخ کشف کاذب روی آزمایش‌های متعدد).
