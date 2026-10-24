---
description: چرا بررسی روزانهٔ مقدار p در آزمون‌های A/B و کارآزمایی‌ها مثبت‌های کاذب را افزایش می‌دهد (مسئلهٔ سرک کشیدن یا peeking)، و سه خانوادهٔ روش‌های دنباله‌ای که آن را حل می‌کنند، در Python با sequential-analysis.
language: fa
---

# چرا نمی‌توانم هر روز به مقدار p نگاه کنم؟

> این صفحه ترجمه‌ای از [صفحهٔ انگلیسی](../../guide/peeking.md) است. این ترجمه هنوز توسط یک گویشور بومی بازبینی نشده است؛ هر جا این دو با هم تفاوت داشته باشند، صفحهٔ انگلیسی معتبر است.

**پاسخ کوتاه.** یک آزمون با اندازهٔ نمونهٔ ثابت (fixed-sample test) فقط وقتی
نرخ مثبت کاذب 5% را وعده می‌دهد که یک بار، در اندازهٔ نمونهٔ برنامه‌ریزی‌شده،
به نتیجه نگاه کنید. اگر مکرراً نگاه کنید و نخستین باری که p < 0.05 شد متوقف
شوید، فرصت‌های زیادی برای فریب خوردن خواهید داشت. با 20 نگاه، نرخ مثبت کاذب
به حدود 25% می‌رسد. روش‌های دنباله‌ای برای نگاه‌های مکرر ساخته شده‌اند. با آن‌ها
این نرخ، هر چند بار که نگاه کنید و هر زمان که متوقف شوید، در 5% یا کمتر
می‌ماند.

## مسئلهٔ سرک کشیدن، با عدد و رقم

دو بازو با نرخ تبدیل یکسان 10% (یک آزمون A/A)، 2,000 کاربر، 200 تکرار.
«سرک کشیدن» (peeking) آزمون z معمول دو نسبت را پس از هر 100 کاربر اجرا
می‌کند و در نخستین p < 0.05 متوقف می‌شود. `TwoProportionTest` دنباله‌ای پس از
تک‌تک کاربران بررسی می‌شود:

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

نگاه واحد به وعده‌اش وفا می‌کند. بیست نگاه نرخ خطا را حدود شش برابر می‌کند.
آزمون دنباله‌ای، که پس از تک‌تک 2,000 کاربر به آن نگاه می‌شود، آن را در 5%
نگه می‌دارد. وعده همین است: تضمین آن **exact** است
(`TwoProportionTest.guarantee == "exact"`)، یعنی نرخ مثبت کاذب حداکثر 5% در
هر اندازهٔ نمونه، هر چند بار که نگاه کنید. با 200 تکرار، 10 مثبت کاذب همان
چیزی است که یک نرخ دقیق 5% به دست می‌دهد.

## سه خانوادهٔ روش‌های دنباله‌ای

| خانواده | کی می‌توانید نگاه کنید | کاربرد رایج | در sequential-analysis |
|---|---|---|---|
| **آزمون‌های نسبت احتمال دنباله‌ای** (sequential probability ratio tests) (Wald 1945) | پس از هر مشاهده | یک فرض ساده در برابر فرضی دیگر، با کمترین تعداد مشاهدات به‌طور میانگین: کنترل کیفیت، شبیه‌سازی، روان‌فیزیک | `SPRT`، `TwoSPRT`، `kiefer_weiss_plan` |
| **طرح‌های دنباله‌ای گروهی** (group sequential designs) (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | در چند تحلیل میانی برنامه‌ریزی‌شده | کارآزمایی‌های بالینی با کمیتهٔ پایش داده‌ها | `group_sequential_design`، `GroupSequentialTest`، `GroupSequentialProportions`، `GroupSequentialLogRank` |
| **استنباط معتبر در هر زمان** (anytime-valid inference): مقادیر e، دنباله‌های اطمینان، SPRT آمیخته (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | پس از هر مشاهده، با توقف به هر دلیلی | آزمون‌های A/B آنلاین، داشبوردهای پایش | `TwoProportionTest`، `BoundedABTest`، `NormalMixtureSPRT`، `BettingConfidenceSequence`، `MultipleTests` |

**هزینه‌اش چیست.** نگاه کردن مکررتر در اثری که برایش برنامه‌ریزی کرده‌اید به
داده‌های بیشتری نیاز دارد:

* یک طرح دنباله‌ای گروهی با چهار تحلیل 1–20% بیمار بیشتر از یک تحلیل واحد
  لازم دارد؛
* یک آزمون معتبر در هر زمان برای دو نسبت به 1.3–1.6 برابر کاربرانِ یک تحلیل
  واحد نیاز دارد.

در عوض، یک اثر بزرگ آزمایش را زود متوقف می‌کند، و هیچ‌کس مجبور نیست اندازهٔ
نمونه را از پیش تعیین کند.

## وقتی مشکل این نیست

سرک کشیدن فقط وقتی خطاها را افزایش می‌دهد که کاری که می‌کنید به آنچه دیده‌اید
بستگی داشته باشد. اگر به داشبورد نگاه می‌کنید اما همیشه آزمایش را تا اندازهٔ
برنامه‌ریزی‌شده‌اش ادامه می‌دهید و یک بار آزمون می‌کنید، آزمون با اندازهٔ نمونهٔ
ثابت معتبر است. در این حالت کاراترین انتخاب هم همان است.

بعدی: [توقف زودهنگام آزمون A/B](ab-testing.md)،
[دنباله‌های اطمینان](confidence-sequences.md)،
[واژه‌نامه](glossary.md).
