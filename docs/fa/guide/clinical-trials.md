---
description: چگونه تحلیل‌های میانی یک کارآزمایی بالینی را در Python برنامه‌ریزی و اجرا کنیم، با طرح‌های دنباله‌ای گروهی (O'Brien–Fleming، Pocock، مصرف آلفای Lan–DeMets، مرزهای بی‌فایدگی)، اندازهٔ نمونه برای میانگین‌ها، نسبت‌ها و بقا، بررسی‌شده در برابر rpact، با sequential-analysis.
language: fa
---

# چگونه تحلیل‌های میانی یک کارآزمایی بالینی را برنامه‌ریزی کنم؟

> این صفحه ترجمه‌ای از [صفحهٔ انگلیسی](../../guide/clinical-trials.md) است. این ترجمه هنوز توسط یک گویشور بومی بازبینی نشده است؛ هر جا این دو با هم تفاوت داشته باشند، صفحهٔ انگلیسی معتبر است.

**پاسخ کوتاه.** از یک طرح دنباله‌ای گروهی (group sequential design) استفاده
کنید. تابع `group_sequential_design(alpha, fractions, spending=...)` از
`sequential_analysis.group_sequential` این‌ها را محاسبه می‌کند:

* مرزهای اثربخشی (efficacy boundaries)، با مصرف آلفا (alpha spending) به
  روش Lan–DeMets (از نوع O'Brien–Fleming، از نوع Pocock و انواع دیگر)؛
* مرزهای بی‌فایدگی غیرالزام‌آور (non-binding futility boundaries)؛
* توان آزمون و اندازهٔ نمونهٔ مورد انتظار؛
* بیشینهٔ اندازهٔ نمونه برای میانگین‌ها و نسبت‌ها، یا تعداد رویدادها برای
  تحلیل بقا.

مرزها و اندازه‌های نمونه با بستهٔ R به نام rpact مطابقت دارند. سپس روال‌های
آزمون (`GroupSequentialTest`، `GroupSequentialTwoMeans`،
`GroupSequentialProportions`، `GroupSequentialLogRank`) کارآزمایی را، بیمار
به بیمار یا رویداد به رویداد، اجرا می‌کنند. آن‌ها هر تحلیل میانی (interim
analysis) را وقتی کسر اطلاعات (information fraction) مربوط به آن به دست آید
انجام می‌دهند.

## طراحی: چهار تحلیل، مصرف O'Brien–Fleming

α یک‌طرفه = 0.025، تحلیل‌ها در 25%، 50%، 75% و 100% بیماران، توان 90%،
همراه با یک مرز بی‌فایدگی:

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

## پیامدهای دودویی و پیامدهای بقا

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

با مصرف O'Brien–Fleming، سه تحلیل 1.3% بیمار بیشتر از یک تحلیل نهایی واحد
هزینه دارد.

## اجرای کارآزمایی

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

کارآزمایی در تحلیل دوم، پس از دو سوم بیماران برنامه‌ریزی‌شده، به دلیل
اثربخشی متوقف شد.

## وقتی تحلیل‌ها طبق برنامه انجام نمی‌شوند

کمیته‌های پایش داده‌ها به‌ندرت دقیقاً در 25% اطلاعات تشکیل جلسه می‌دهند:

* `design.at(fractions)` مرزها را برای اطلاعاتی که واقعاً به دست آمده
  دوباره محاسبه می‌کند. مصرف آلفا سطح کلی را حفظ می‌کند.
* `GroupSequentialMonitor` هر آماره‌ای را که خودتان محاسبه می‌کنید (یک مدل
  Cox، یک مدل آمیخته) به‌صورت یک مقدار Z همراه با اطلاعات آن در هر جلسه
  می‌پذیرد.

## و اگر بخواهید پس از هر بیمار نگاه کنید؟

طرح دنباله‌ای گروهی فقط تعداد نگاه‌های برنامه‌ریزی‌شده را مجاز می‌داند. برای
پایش پس از هر بیمار یا رویداد، از یک روال معتبر در هر زمان (anytime-valid)
استفاده کنید: `AnytimeLogRankTest` برای بقا، `TwoProportionTest` برای
نرخ‌های پاسخ، `TMixtureSPRT` برای میانگین. این روال‌ها در اثر
برنامه‌ریزی‌شده به بیماران بیشتری نیاز دارند. ببینید
[آموزش: کارآزمایی بقا](../../tutorials/survival.md).

## رویهٔ نظارتی

طرح‌های دنباله‌ای گروهی با مصرف آلفا رویکرد جاافتاده در کارآزمایی‌های
تأییدی‌اند و در رهنمود ICH E9 و راهنمای FDA دربارهٔ طرح‌های تطبیقی (2019)
توصیف شده‌اند. این کتابخانه طرح‌ها را محاسبه می‌کند و از هر تحلیل سابقه‌ای
قابل ممیزی و قابل ازسرگیری نگه می‌دارد (نقطهٔ بازیابی و چکیدهٔ تاریخچهٔ آن).
این کتابخانه نرم‌افزاری اعتبارسنجی‌شده به معنای نظارتی نیست: حامی‌ای
(sponsor) که در یک پروندهٔ ارسالی از آن استفاده می‌کند باید آن را مانند هر
ابزار دیگری اعتبارسنجی کند.

بیشتر: [آموزش: کارآزمایی دنباله‌ای گروهی](../../tutorials/group-sequential.md)،
که اعداد را با rpact مقایسه می‌کند؛
[مرجع: طراحی و برنامه‌ریزی](../../reference/design.md).
