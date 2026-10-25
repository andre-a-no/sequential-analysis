---
description: Python-এ মিথ্যা পজিটিভ (false positive) না বাড়িয়ে কীভাবে A/B পরীক্ষা আগেভাগে থামাবেন। কনভার্শন ও সীমাবদ্ধ আয়ের জন্য যেকোনো-সময়-বৈধ (anytime-valid) পরীক্ষা, নমুনা অনুপাতের অমিল (sample ratio mismatch) যাচাই এবং বহু মেট্রিকে মিথ্যা আবিষ্কারের হার (false discovery rate) নিয়ন্ত্রণ, sequential-analysis দিয়ে।
language: bn
---

# মিথ্যা পজিটিভ না বাড়িয়ে কীভাবে A/B পরীক্ষা আগেভাগে থামাব?

> এটি [ইংরেজি পৃষ্ঠার](../../guide/ab-testing.md) অনুবাদ। এটি এখনও কোনো বাংলাভাষী বিশেষজ্ঞ পর্যালোচনা করেননি; দুটির মধ্যে পার্থক্য থাকলে ইংরেজি পৃষ্ঠাটিই প্রামাণ্য।

**সংক্ষিপ্ত উত্তর।** যেকোনো-সময়-বৈধ (anytime-valid) একটি পরীক্ষা ব্যবহার করুন:
এর p-মান (p-value) ও আস্থা ব্যবধান (confidence interval) আপনি যতবারই দেখুন
বৈধ থাকে, তাই ফলাফল স্পষ্ট হওয়া মাত্রই আপনি থামতে পারেন। sequential-analysis-এ:

| মেট্রিক | পদ্ধতি | নিশ্চয়তা |
|---|---|---|
| কনভার্শন হার (0/1) | `TwoProportionTest` | exact |
| যেকোনো সীমাবদ্ধ মেট্রিক (ঊর্ধ্বসীমা-বাঁধা আয়, অংশ) | `BoundedABTest` | exact |
| প্রতি একক এক্সপোজারে ঘটনার সংখ্যা | `RateRatioTest` | Poisson গণনার জন্য exact |
| অনুপাত মেট্রিক (প্রতি সেশনে আয়) | `RatioABTest` | asymptotic |
| পরীক্ষা-পূর্ব কোভেরিয়েটসহ গড় (CUPED) | `ABTest` | asymptotic |
| ট্রাফিক কি উদ্দেশ্য অনুযায়ী ভাগ হচ্ছে? | `SampleRatioMismatch` | exact |
| একসঙ্গে কয়েকটি মেট্রিক বা শাখা (arm) | `MultipleTests` (e-BH) | মিথ্যা আবিষ্কারের হার (false discovery rate), exact |

প্রতিটি পদ্ধতিকে একবারে একজন ব্যবহারকারী দিন: `state, out = test.step(state, {...})`।
যখন খুশি `out.decision` অনুযায়ী পদক্ষেপ নিন।

## কনভার্শন: ডেটা চূড়ান্ত হলে থামুন

নিয়ন্ত্রণ (control) শাখায় 10% ব্যবহারকারী কনভার্ট করে, ট্রিটমেন্ট শাখায় 12%।
পরীক্ষাটি প্রত্যেক ব্যবহারকারীর পরে দেখা হয় এবং প্রথম সিদ্ধান্তেই থামে:

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

তুলনার জন্য, এই বৃদ্ধির (lift) জন্য 80% ক্ষমতাসম্পন্ন (power) একটি
স্থির-নমুনা পরীক্ষার (fixed-sample test) প্রয়োজন প্রতি শাখায় প্রায় 3,850 জন,
মোট 7,700 জন ব্যবহারকারী, এবং তা কেবল একবারই, শেষে, পড়া যায়।
যেকোনো-সময়-বৈধ পরীক্ষা তার স্বাধীনতার মূল্য দেয়: একই ক্ষমতায় পৌঁছাতে এর
একক বিশ্লেষণের 1.3–1.6 গুণ ব্যবহারকারী লাগে, এবং এই রানে তার চেয়েও বেশি
লেগেছে। বিনিময়ে আগে থেকে কোনো নমুনার আকার স্থির করতে হয় না, এবং আপনি প্রতিদিন
ফলাফল দেখতে পারেন ও স্পষ্ট হওয়া মাত্রই থামতে পারেন। প্রভাব (effect) পরিকল্পনার
চেয়ে বড় হলে তা অনেক আগেই ঘটে।

## আয়: সীমাবদ্ধ মেট্রিকের জন্য যথাযথ ব্যবধান

`BoundedABTest`-এর কেবল মেট্রিকের সীমা দরকার। পরীক্ষার আগে আপনার বেছে নেওয়া
একটি মানে (এখানে 30) আয়ের ঊর্ধ্বসীমা বেঁধে দিন, তাহলে গড়ের পার্থক্যের আস্থা
অনুক্রম (confidence sequence) যেকোনো বণ্টনের (distribution) জন্য যথাযথ (exact):

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

ব্যবধানটি কেবল শেষেরটিতে নয়, 20,000টি দেখার প্রতিটিতে একসঙ্গে বৈধ। এখানে এটি
এখনও 0 ধারণ করে: এত গোলমেলে (noisy) একটি মেট্রিকে প্রায় 0.5 বৃদ্ধি
প্রতিষ্ঠা করতে 20,000 ব্যবহারকারী যথেষ্ট নয়, তাই পরীক্ষা চলতে থাকে।

## আগে ট্রাফিকের ভাগ যাচাই করুন

নমুনা অনুপাতের অমিল (sample ratio mismatch) মানে ভাগটি কনফিগার করা ভাগ থেকে
আলাদা, যেমন বরাদ্দে (assignment) বা লগিংয়ে কোনো বাগের কারণে। এমন পরীক্ষা থেকে
পাওয়া প্রভাবের প্রাক্কলন (estimate) বিশ্বাসযোগ্য নয়। 50/50 থেকে 52/48-এ
অমিল পরীক্ষা চলার সময়েই ধরা পড়ে:

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

## একসঙ্গে অনেক মেট্রিক

দশটি স্বাধীন মেট্রিক প্রতিটি 5%-এ পরীক্ষা করলে অন্তত একটি মিথ্যা আবিষ্কারের
সম্ভাবনা প্রায় 40%। `MultipleTests` সব পরীক্ষার e-মান (e-value) e-BH পদ্ধতিতে
একত্র করে, ফলে যেকোনো থামার সময়ে (stopping time) মিথ্যা আবিষ্কারের হার
`alpha`-তে থাকে:

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

## সতর্কতা

* **যে এককটি বিশ্লেষণ করছেন সেটিকেই দৈবায়িত (randomise) করুন।** ব্যবহারকারীরা
  দৈবায়িত হলে প্রতি পৃষ্ঠা-দর্শন নয়, প্রতি ব্যবহারকারী একটি রেকর্ড দিন।
  প্রতি-সেশন মেট্রিকের জন্য `RatioABTest` ব্যবহার করুন, যা ব্যবহারকারীর মোট
  মানের ওপর কাজ করে।
* **সীমাবদ্ধ মেট্রিকের ঊর্ধ্বসীমা পরীক্ষার আগেই স্থির করুন।** ডেটা দেখার পরে
  তা বেছে নিলে নিশ্চয়তা বাতিল হয়ে যায়।
* **asymptotic পদ্ধতির জন্য বড় নমুনা দরকার।** `ABTest` ও `RatioABTest`-এর
  ব্যবধান কেবল দীর্ঘ রানে আনুমানিকভাবে বৈধ। যেখানে খাপ খায়, exact পদ্ধতিগুলোকে
  অগ্রাধিকার দিন।
* **অভিযোজিত ট্রাফিক বরাদ্দের (adaptive traffic allocation)** (bandit) জন্য
  এমন পরীক্ষা দরকার যা ভাগটি ফলাফলের ওপর নির্ভর করলেও বৈধ থাকে:
  `TwoProportionTest(method="universal")` অথবা
  `BoundedABTest(propensity_input=...)`। দেখুন
  [টিউটোরিয়াল §10](../../tutorials/ab-test.md)।

আরও: [A/B পরীক্ষার টিউটোরিয়াল](../../tutorials/ab-test.md) (CUPED, অনুপাত
মেট্রিক, হার, সময়কালের পরিকল্পনা) এবং
[পরীক্ষার একটি কর্মসূচি](../../tutorials/experiment-programme.md)
(বহু পরীক্ষাজুড়ে মিথ্যা আবিষ্কারের হার)।
