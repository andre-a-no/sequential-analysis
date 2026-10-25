---
description: دنباله‌های اطمینان (confidence sequences) بازه‌های اطمینانی‌اند که در همهٔ اندازه‌های نمونه به‌طور هم‌زمان معتبر می‌مانند، پس می‌توان آن‌ها را پیوسته پایش کرد. نحوهٔ محاسبهٔ آن‌ها در Python برای میانگین کران‌دار، میانه یا چندک، و میانگین با دم‌های سنگین، با sequential-analysis.
language: fa
---

# چگونه بازهٔ اطمینانی بگیرم که با نگاه‌های مکرر معتبر بماند؟

> این صفحه ترجمه‌ای از [صفحهٔ انگلیسی](../../guide/confidence-sequences.md) است. این ترجمه هنوز توسط یک گویشور بومی بازبینی نشده است؛ هر جا این دو با هم تفاوت داشته باشند، صفحهٔ انگلیسی معتبر است.

**پاسخ کوتاه.** از یک **دنبالهٔ اطمینان** (confidence sequence) استفاده
کنید. دنبالهٔ اطمینان دنباله‌ای از بازه‌هاست، یک بازه پس از هر مشاهده، که با
احتمال دست‌کم 95% مقدار واقعی را در همهٔ اندازه‌های نمونه به‌طور هم‌زمان در
بر دارد. می‌توانید آن را زیر نظر بگیرید، وقتی به اندازهٔ کافی باریک شد یا صفر
را کنار گذاشت متوقف شوید، و بازه‌ای را که در آن متوقف شدید گزارش کنید. یک
بازهٔ اطمینان معمولی 95% فقط در یک اندازهٔ نمونهٔ از پیش تعیین‌شده وعدهٔ 95%
می‌دهد.

| آنچه برآورد می‌کنید | فرض | روال | تضمین |
|---|---|---|---|
| میانگین داده‌های کران‌دار (نرخ‌ها، امتیازها، درآمد با سقف) | مقادیر در `[lower, upper]` | `BettingConfidenceSequence` | exact |
| میانه، صدک 90ام، هر چندکی | هیچ | `QuantileConfidenceSequence` | exact |
| میانگین با دم‌های سنگین یا داده‌های پرت | کرانی برای انحراف معیار | `CatoniConfidenceSequence` | exact |
| میانگین داده‌های نرمال، واریانس نامعلوم | نرمال بودن | `TMixtureSPRT` (`lower`، `upper`) | exact تحت نرمال بودن |
| میانگین هر چیزی، اجراهای طولانی | واریانس متناهی | `AsymptoticConfidenceSequence` | asymptotic |
| تفاوت میان دو بازو | ببینید [آزمون‌های A/B](ab-testing.md) | `BoundedABTest`، `ABTest` | exact / asymptotic |

## بازهٔ معمولی وقتی زیر نظر باشد شکست می‌خورد

500 مشاهده از یک متغیر 0/1 با میانگین 0.3 بگیرید و از مشاهدهٔ سی‌ام به بعد،
پس از هر مشاهده بازهٔ 95% کتاب‌های درسی را حساب کنید: میانگین ± 1.96 خطای
معیار. در چند اجرا از 100 اجرا، بازه در لحظه‌ای میانگین واقعی را از دست
می‌دهد؟

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

«95%» آن فقط در یک اندازهٔ نمونهٔ از پیش تعیین‌شده برقرار است. دنبالهٔ اطمینان
برای همین داده‌ها، ساخته‌شده به روش شرط‌بندی (betting) (Waudby-Smith and
Ramdas 2024)، بنا به ساختارش حداکثر در 5% اجراها در n ای مقدار واقعی را از
دست می‌دهد:

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

## میانهٔ تأخیر، بدون هیچ فرضی

تأخیرها چوله و دم‌سنگین‌اند، پس بازهٔ «میانگین ± خطای معیار» برای آن‌ها قابل
اعتماد نیست. `QuantileConfidenceSequence` هر چندک (quantile) از هر توزیعی را،
با احتساب مقادیر گره‌خورده (ties)، پوشش می‌دهد:

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

مقادیر واقعی 120 ms و 258.8 ms هستند. هر دو بازه در همهٔ 2,000 اندازهٔ نمونه
به‌طور هم‌زمان برقرارند.

## دام‌ها

* **کران‌ها و سقف‌ها بخشی از فرض‌اند.** `lower` و `upper` را پیش از دیدن
  داده‌ها انتخاب کنید. مقداری بیرون از آن‌ها پذیرفته نمی‌شود.
* **هیچ روشی برای میانگین داده‌های بی‌کران دلخواه پوشش دقیق به دست
  نمی‌دهد.** برای چنین داده‌هایی از یک چندک استفاده کنید، برای مقادیر سقف
  بگذارید، کرانی برای انحراف معیار فرض کنید (Catoni)، یا یک دنبالهٔ مجانبی
  را بپذیرید.
* **دنباله‌های اطمینان در اندازهٔ نمونهٔ یکسان از یک بازهٔ منفرد پهن‌ترند.**
  این پهنا بهای معتبر بودن در همهٔ اندازه‌های نمونه به‌طور هم‌زمان است.

بیشتر: [کدام روش؟](../../choosing.md)،
[مرجع: روش‌های معتبر در هر زمان و ناپارامتری](../../reference/anytime.md).
