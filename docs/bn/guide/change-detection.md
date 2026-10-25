---
description: Python-এ সেন্সরের পাঠ, লেটেন্সি বা মেট্রিকের প্রবাহে পরিবর্তন কীভাবে শনাক্ত করবেন, CUSUM, Shiryaev–Roberts, অপ্যারামিতিক e-শনাক্তকারী (e-detector) ও বেইজীয় অনলাইন পরিবর্তন-বিন্দু শনাক্তকরণ (change-point detection) দিয়ে। গড় রান দৈর্ঘ্যের (average run length, ARL) মাধ্যমে মিথ্যা সতর্কসংকেত নিয়ন্ত্রিত, sequential-analysis দিয়ে।
language: bn
---

# পরিমাপের একটি প্রবাহে পরিবর্তন কীভাবে শনাক্ত করব?

> এটি [ইংরেজি পৃষ্ঠার](../../guide/change-detection.md) অনুবাদ। এটি এখনও কোনো বাংলাভাষী বিশেষজ্ঞ পর্যালোচনা করেননি; দুটির মধ্যে পার্থক্য থাকলে ইংরেজি পৃষ্ঠাটিই প্রামাণ্য।

**সংক্ষিপ্ত উত্তর।** একটি অনলাইন পরিবর্তন-বিন্দু শনাক্তকারী (change-point
detector) ব্যবহার করুন। এটি প্রবাহের ওপর নজর রাখে এবং বণ্টন (distribution)
বদলেছে বলে মনে হওয়া মাত্রই সতর্কসংকেত (alarm) দেয়। এর মিথ্যা সতর্কসংকেত
(false alarm) নিয়ন্ত্রিত হয় **গড় রান দৈর্ঘ্য** (average run length, ARL)
দিয়ে: কিছুই না বদলালে একটি মিথ্যা সতর্কসংকেত পর্যন্ত পর্যবেক্ষণের প্রত্যাশিত
সংখ্যা। sequential-analysis-এ:

| পরিবর্তনের আগে আপনি জানেন | পদ্ধতি | নিশ্চয়তা |
|---|---|---|
| উভয় বণ্টন (যেমন normal, গড় 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| কেবল গড়, এবং মানগুলোর সীমা | `MeanEDetector` | এমন প্রতিটি বণ্টনের জন্য exact |
| কেবল একটি কোয়ান্টাইল (যেমন লেটেন্সির 95তম পার্সেন্টাইল) | `QuantileEDetector` | প্রতিটি বণ্টনের জন্য exact |
| পরিবর্তনের আগে ও পরে অজানা প্যারামিটারসহ একটি মডেল | `BayesianChangePoint` | মডেল ও পূর্ব-বণ্টনের (prior) অধীনে |

## একটি সেন্সর যার গড় সরে যায়

একটি তাপমাত্রা সেন্সর 70.0 °C পাঠ দেয়, যার নয়েজের আদর্শ বিচ্যুতি (standard
deviation) 0.5। 600তম পাঠ থেকে গড় হয় 70.4। log(1000) ≈ 6.9 সীমা (threshold)
সহ CUSUM-এর ARL অন্তত 1,000 পাঠ:

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

এক আদর্শ বিচ্যুতির চেয়ে কম সরণ কোনো একক পাঠে চোখে ধরা পড়ে না। CUSUM
প্রমাণ জমা করে এবং তা খুঁজে পায়।

## যখন পাঠগুলো normal নয়

CUSUM-এর ARL কেবল তখনই বজায় থাকে যখন পাঠগুলো আপনার দেওয়া বণ্টন মেনে চলে।
বিষম (skewed) ডেটার (কম্পনের বিস্তার, লেটেন্সি, সারির দৈর্ঘ্য) ক্ষেত্রে এটি
পরিকল্পনার চেয়ে অনেক বেশি ঘন ঘন মিথ্যা সতর্কসংকেত দেয়। e-শনাক্তকারীগুলোর
(e-detector) প্রয়োজন অনেক কম:

* `MeanEDetector`-এর দরকার পরিবর্তনের আগের গড় এবং মানগুলোর সীমা।
* `QuantileEDetector`-এর দরকার কেবল পরিবর্তনের আগের একটি কোয়ান্টাইল।

ওই গড় বা কোয়ান্টাইলসহ **প্রতিটি** বণ্টনের জন্য এদের ARL অন্তত লক্ষ্যমাত্রার
সমান:

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

বাস্তবে পরিবর্তনের আগের কোয়ান্টাইলটি একটি শান্ত সময়কাল থেকে প্রাক্কলন করা হয়।
তখন নিশ্চয়তা আনুমানিকভাবে বজায় থাকে, এবং সেই সময়কাল যত দীর্ঘ, তত ভালো।

## ARL বেছে নেওয়া

ARL মিথ্যা সতর্কসংকেত ও বিলম্বের মধ্যে ভারসাম্য করে। প্রতি মিনিটে একটি পাঠ
হলে, 1,000 পাঠের ARL মানে স্বাভাবিক কার্যক্রমে প্রতি সেন্সরে মোটামুটি প্রতি 17
ঘণ্টায় একটি মিথ্যা সতর্কসংকেত। 50টি সেন্সরে তা দিনে প্রায় 70টি। সব সেন্সর
মিলিয়ে দিনে কতগুলো মিথ্যা সতর্কসংকেত আপনি সামলাতে পারেন, তা থেকে ARL বেছে
নিন: এখানে 1,000,000 পাঠের ARL 50টি সেন্সরকে নামিয়ে আনে প্রায় প্রতি দুই সপ্তাহে
একটি মিথ্যা সতর্কসংকেতে। এর খরচ যতটা মনে হয় তার চেয়ে কম, কারণ শনাক্তকরণের
বিলম্ব কেবল ARL-এর লগারিদমের সঙ্গে বাড়ে। CUSUM-এর জন্য সীমা 6.9 থেকে 13.8-এ
যায়, এবং বিলম্ব মোটামুটি দ্বিগুণ হয়।

এই শনাক্তকারীগুলো পর্যবেক্ষণের (monitoring) সরঞ্জাম, নিরাপত্তা ব্যবস্থা নয়।
প্রত্যয়িত নিরাপত্তা যন্ত্রায়িত ব্যবস্থার (safety instrumented system) বদলে
এগুলো ব্যবহার করবেন না।

আরও: [টিউটোরিয়াল: প্রক্রিয়া পর্যবেক্ষণ ও পরিবর্তন শনাক্তকরণ](../../tutorials/monitoring.md),
[লুক্কায়িত মার্কভ মডেল দিয়ে রেজিম](../../tutorials/regimes.md),
[রেফারেন্স: পরিবর্তন শনাক্তকরণ](../../reference/detection.md)।
