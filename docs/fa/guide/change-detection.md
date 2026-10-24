---
description: چگونه تغییر را در جریانی از خوانش‌های حسگر، تأخیرها یا معیارها در Python تشخیص دهیم، با CUSUM، Shiryaev–Roberts، آشکارسازهای ناپارامتری e و تشخیص بیزی برخط نقطهٔ تغییر. هشدارهای کاذب از طریق متوسط طول اجرا (ARL) کنترل می‌شوند، با sequential-analysis.
language: fa
---

# چگونه تغییر را در جریانی از اندازه‌گیری‌ها تشخیص دهم؟

> این صفحه ترجمه‌ای از [صفحهٔ انگلیسی](../../guide/change-detection.md) است. این ترجمه هنوز توسط یک گویشور بومی بازبینی نشده است؛ هر جا این دو با هم تفاوت داشته باشند، صفحهٔ انگلیسی معتبر است.

**پاسخ کوتاه.** از یک آشکارساز برخط نقطهٔ تغییر (online change-point
detector) استفاده کنید. این آشکارساز جریان را زیر نظر می‌گیرد و به‌محض آنکه
به نظر برسد توزیع تغییر کرده است، هشدار می‌دهد. هشدارهای کاذب آن با **متوسط
طول اجرا** (average run length, ARL) کنترل می‌شوند: تعداد مورد انتظار
مشاهدات تا یک هشدار کاذب، تا زمانی که هیچ چیز تغییر نکرده است. در
sequential-analysis:

| آنچه پیش از تغییر می‌دانید | روال | تضمین |
|---|---|---|
| هر دو توزیع (مثلاً نرمال، میانگین 70 → 71) | `CUSUM`، `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| فقط میانگین، و کران‌های مقادیر | `MeanEDetector` | exact برای هر توزیعی از این دست |
| فقط یک چندک (مثلاً صدک 95ام تأخیر) | `QuantileEDetector` | exact برای هر توزیع |
| مدلی با پارامترهای نامعلوم، پیش و پس از تغییر | `BayesianChangePoint` | تحت مدل و توزیع پیشین |

## حسگری که میانگینش جابه‌جا می‌شود

یک حسگر دما 70.0 °C را با نوفه‌ای با انحراف معیار 0.5 می‌خواند. از خوانش 600
به بعد میانگین 70.4 است. CUSUM با آستانهٔ log(1000) ≈ 6.9 دارای ARL دست‌کم
1,000 خوانش است:

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

جابه‌جایی کمتر از یک انحراف معیار در هیچ خوانش منفردی با چشم دیده نمی‌شود.
CUSUM شواهد را انباشته می‌کند و آن را پیدا می‌کند.

## وقتی خوانش‌ها نرمال نیستند

ARL روش CUSUM فقط وقتی برقرار است که خوانش‌ها از توزیع‌هایی که به آن داده‌اید
پیروی کنند. برای داده‌های چوله (دامنهٔ ارتعاش، تأخیرها، طول صف‌ها) هشدارهای
کاذب آن بسیار بیشتر از برنامه رخ می‌دهد. آشکارسازهای e (e-detectors) به
اطلاعات بسیار کمتری نیاز دارند:

* `MeanEDetector` به میانگین پیش از تغییر و کران‌های مقادیر نیاز دارد.
* `QuantileEDetector` فقط به یک چندک پیش از تغییر نیاز دارد.

ARL آن‌ها برای **هر** توزیعی با آن میانگین یا چندک دست‌کم برابر هدف است:

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

در عمل چندکِ پیش از تغییر از یک دورهٔ آرام برآورد می‌شود. در این صورت تضمین
به‌طور تقریبی برقرار است، و هرچه آن دوره طولانی‌تر باشد بهتر.

## انتخاب ARL

ARL میان هشدارهای کاذب و تأخیر توازن برقرار می‌کند. با یک خوانش در دقیقه،
ARL برابر 1,000 خوانش یعنی تقریباً هر 17 ساعت کارکرد عادی یک هشدار کاذب،
برای هر حسگر. با 50 حسگر این حدود 70 هشدار در روز می‌شود. ARL را بر اساس
تعداد هشدارهای کاذب روزانه‌ای انتخاب کنید که برای همهٔ حسگرها روی هم قابل
تحمل است: اینجا، ARL برابر 1,000,000 خوانش، 50 حسگر را به حدود یک هشدار
کاذب در هر دو هفته می‌رساند. هزینهٔ این کار کمتر از آن است که به نظر می‌رسد،
چون تأخیر تشخیص فقط با لگاریتم ARL رشد می‌کند. برای CUSUM آستانه از 6.9 به
13.8 می‌رسد و تأخیر تقریباً دو برابر می‌شود.

این آشکارسازها ابزار پایش‌اند، نه سامانهٔ ایمنی. از آن‌ها به جای یک سامانهٔ
ابزاردقیق ایمنی (safety instrumented system) گواهی‌شده استفاده نکنید.

بیشتر: [آموزش: پایش فرایند و تشخیص تغییر](../../tutorials/monitoring.md)،
[رژیم‌ها (regimes) با مدل‌های مارکوف پنهان](../../tutorials/regimes.md)،
[مرجع: تشخیص تغییر](../../reference/detection.md).
