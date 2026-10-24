---
description: আস্থা অনুক্রম (confidence sequence) হলো এমন আস্থা ব্যবধান যা একসঙ্গে প্রতিটি নমুনার আকারে বৈধ থাকে, তাই এগুলো অবিরাম পর্যবেক্ষণ করা যায়। Python-এ সীমাবদ্ধ গড়, মধ্যমা বা কোয়ান্টাইল, এবং ভারী লেজযুক্ত (heavy-tailed) গড়ের জন্য এগুলো কীভাবে হিসাব করবেন, sequential-analysis দিয়ে।
language: bn
---

# বারবার দেখলেও বৈধ থাকে এমন আস্থা ব্যবধান কীভাবে পাব?

> এটি [ইংরেজি পৃষ্ঠার](../../guide/confidence-sequences.md) অনুবাদ। এটি এখনও কোনো বাংলাভাষী বিশেষজ্ঞ পর্যালোচনা করেননি; দুটির মধ্যে পার্থক্য থাকলে ইংরেজি পৃষ্ঠাটিই প্রামাণ্য।

**সংক্ষিপ্ত উত্তর।** একটি **আস্থা অনুক্রম** (confidence sequence) ব্যবহার করুন।
এটি ব্যবধানের একটি অনুক্রম, প্রতিটি পর্যবেক্ষণের পরে একটি করে, যা অন্তত 95%
সম্ভাবনায় সব নমুনার আকারে একই সঙ্গে প্রকৃত মানটি ধারণ করে। আপনি এর ওপর নজর
রাখতে পারেন, যথেষ্ট সরু হলে বা শূন্যকে বাদ দিলে থামতে পারেন, এবং যে ব্যবধানে
থেমেছেন সেটিই রিপোর্ট করতে পারেন। একটি সাধারণ 95% আস্থা ব্যবধান (confidence
interval) 95%-এর প্রতিশ্রুতি দেয় কেবল আগে থেকে স্থির করা একটি নমুনার আকারে।

| আপনি যা প্রাক্কলন করছেন | অনুমিতি (assumption) | পদ্ধতি | নিশ্চয়তা |
|---|---|---|---|
| সীমাবদ্ধ ডেটার গড় (হার, স্কোর, ঊর্ধ্বসীমা-বাঁধা আয়) | মানগুলো `[lower, upper]`-এর মধ্যে | `BettingConfidenceSequence` | exact |
| মধ্যমা, 90তম পার্সেন্টাইল, যেকোনো কোয়ান্টাইল | কিছুই না | `QuantileConfidenceSequence` | exact |
| ভারী লেজ বা বহিঃস্থ মানসহ (outlier) গড় | আদর্শ বিচ্যুতির একটি সীমা | `CatoniConfidenceSequence` | exact |
| normal ডেটার গড়, ভেদাঙ্ক (variance) অজানা | normality | `TMixtureSPRT` (`lower`, `upper`) | normality-র অধীনে exact |
| যেকোনো কিছুর গড়, দীর্ঘ রান | সসীম ভেদাঙ্ক | `AsymptoticConfidenceSequence` | asymptotic |
| দুই শাখার মধ্যে পার্থক্য | দেখুন [A/B পরীক্ষা](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## নজর রাখলে সাধারণ ব্যবধান ব্যর্থ হয়

গড় 0.3 বিশিষ্ট একটি 0/1 চলকের 500টি পর্যবেক্ষণ নিন, এবং 30তম থেকে শুরু করে
প্রত্যেকটির পরে পাঠ্যপুস্তকের 95% ব্যবধান হিসাব করুন: গড় ± 1.96 আদর্শ ত্রুটি
(standard error)। 100টি রানের কতগুলোতে ব্যবধানটি কোনো এক সময়ে প্রকৃত গড়কে
বাদ দেয়?

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

এর "95%" কেবল আগে থেকে স্থির করা একটি নমুনার আকারে বজায় থাকে। একই ডেটার
জন্য বাজি ধরার (betting) মাধ্যমে আস্থা অনুক্রম (Waudby-Smith and Ramdas 2024)
গঠনগতভাবেই সর্বোচ্চ 5% রানে কোনো এক n-এ প্রকৃত মান বাদ দেয়:

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

## লেটেন্সির মধ্যমা, কোনো অনুমিতি ছাড়াই

লেটেন্সি বিষম (skewed) ও ভারী লেজযুক্ত, তাই এদের জন্য গড় ± আদর্শ ত্রুটি
ব্যবধান বিশ্বাসযোগ্য নয়। `QuantileConfidenceSequence` যেকোনো বণ্টনের যেকোনো
কোয়ান্টাইল কভার করে, সমান মান (ties) সহ:

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

প্রকৃত মানগুলো 120 ms ও 258.8 ms। দুটি ব্যবধানই সব 2,000 নমুনার আকারে একই
সঙ্গে বজায় থাকে।

## সতর্কতা

* **সীমা ও ঊর্ধ্বসীমা অনুমিতির অংশ।** ডেটা দেখার আগে `lower` ও `upper` বেছে নিন।
  তাদের বাইরের কোনো মান প্রত্যাখ্যাত হয়।
* **যথেচ্ছ অসীমাবদ্ধ ডেটার গড়ের জন্য কোনো পদ্ধতিই যথাযথ আবরণ (coverage) দেয়
  না।** এমন ডেটার জন্য একটি কোয়ান্টাইল ব্যবহার করুন, মানগুলোর ঊর্ধ্বসীমা বেঁধে
  দিন, আদর্শ বিচ্যুতির একটি সীমা ধরে নিন (Catoni), অথবা একটি asymptotic
  অনুক্রম মেনে নিন।
* **একই নমুনার আকারে আস্থা অনুক্রম একক ব্যবধানের চেয়ে চওড়া।** এই চওড়া হওয়াটাই
  একসঙ্গে প্রতিটি নমুনার আকারে বৈধ থাকার মূল্য।

আরও: [কোন পদ্ধতি?](../../choosing.md),
[রেফারেন্স: যেকোনো-সময়-বৈধ ও অপ্যারামিতিক](../../reference/anytime.md)।
