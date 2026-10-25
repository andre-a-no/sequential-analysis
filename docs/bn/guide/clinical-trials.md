---
description: Python-এ ক্লিনিক্যাল ট্রায়ালের অন্তর্বর্তী বিশ্লেষণ (interim analysis) কীভাবে পরিকল্পনা ও পরিচালনা করবেন, গ্রুপ ক্রমিক নকশা (group sequential design) দিয়ে (O'Brien–Fleming, Pocock, Lan–DeMets আলফা ব্যয়, অসারতার সীমানা), গড়, অনুপাত ও উত্তরজীবিতার (survival) জন্য নমুনার আকার, rpact-এর সঙ্গে মিলিয়ে যাচাই করা, sequential-analysis দিয়ে।
language: bn
---

# ক্লিনিক্যাল ট্রায়ালের অন্তর্বর্তী বিশ্লেষণ কীভাবে পরিকল্পনা করব?

> এটি [ইংরেজি পৃষ্ঠার](../../guide/clinical-trials.md) অনুবাদ। এটি এখনও কোনো বাংলাভাষী বিশেষজ্ঞ পর্যালোচনা করেননি; দুটির মধ্যে পার্থক্য থাকলে ইংরেজি পৃষ্ঠাটিই প্রামাণ্য।

**সংক্ষিপ্ত উত্তর।** একটি গ্রুপ ক্রমিক নকশা (group sequential design) ব্যবহার করুন।
`sequential_analysis.group_sequential` থেকে
`group_sequential_design(alpha, fractions, spending=...)` হিসাব করে:

* কার্যকারিতার সীমানা (efficacy boundary), Lan–DeMets আলফা ব্যয় (alpha
  spending) সহ (O'Brien–Fleming ধরন, Pocock ধরন ও অন্যান্য);
* অবন্ধনকারী (non-binding) অসারতার সীমানা (futility boundary);
* ক্ষমতা (power) ও প্রত্যাশিত নমুনার আকার;
* গড় ও অনুপাতের জন্য সর্বোচ্চ নমুনার আকার, অথবা উত্তরজীবিতার (survival)
  জন্য ঘটনার (event) সংখ্যা।

সীমানা ও নমুনার আকারগুলো R প্যাকেজ rpact-এর সঙ্গে মেলে। তারপর পরীক্ষা
পদ্ধতিগুলো (`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) ট্রায়ালটি চালায়, রোগী
ধরে ধরে বা ঘটনা ধরে ধরে। প্রতিটি অন্তর্বর্তী বিশ্লেষণ তারা সম্পন্ন করে যখন
তার তথ্য-ভগ্নাংশ (information fraction) পৌঁছায়।

## নকশা: চারটি বিশ্লেষণ, O'Brien–Fleming ব্যয়

একপার্শ্বিক (one-sided) α = 0.025, রোগীদের 25%, 50%, 75% ও 100%-এ বিশ্লেষণ,
90% ক্ষমতা, একটি অসারতার সীমানাসহ:

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

## দ্বিমানিক (binary) ও উত্তরজীবিতা প্রান্তবিন্দু (endpoint)

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

O'Brien–Fleming ব্যয়ে তিনটি বিশ্লেষণের খরচ একটিমাত্র চূড়ান্ত বিশ্লেষণের চেয়ে
1.3% বেশি রোগী।

## ট্রায়াল পরিচালনা

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

ট্রায়ালটি দ্বিতীয় বিশ্লেষণে, পরিকল্পিত রোগীদের দুই-তৃতীয়াংশের পরে, কার্যকারিতার
কারণে থেমে গেছে।

## যখন বিশ্লেষণগুলো পরিকল্পনামতো হয় না

ডেটা পর্যবেক্ষণ কমিটি (data monitoring committee) কদাচিৎ ঠিক তথ্যের 25%-এ
বৈঠকে বসে:

* `design.at(fractions)` প্রকৃতপক্ষে পৌঁছানো তথ্যের জন্য সীমানাগুলো পুনরায়
  হিসাব করে। আলফা ব্যয় সামগ্রিক স্তর (level) বজায় রাখে।
* `GroupSequentialMonitor` প্রতিটি বৈঠকে আপনার নিজের হিসাব করা যেকোনো
  পরিসংখ্যান (একটি Cox মডেল, একটি মিশ্র মডেল (mixed model)) একটি Z মান হিসেবে
  এবং তার তথ্য গ্রহণ করে।

## আর যদি প্রত্যেক রোগীর পরে দেখতে চান?

একটি গ্রুপ ক্রমিক নকশা কেবল পরিকল্পিত সংখ্যক বার দেখার অনুমতি দেয়। প্রত্যেক
রোগী বা ঘটনার পরে পর্যবেক্ষণ করতে একটি যেকোনো-সময়-বৈধ (anytime-valid) পদ্ধতি
ব্যবহার করুন: উত্তরজীবিতার জন্য `AnytimeLogRankTest`, প্রতিক্রিয়ার হারের জন্য
`TwoProportionTest`, গড়ের জন্য `TMixtureSPRT`। পরিকল্পিত প্রভাবে এদের আরও বেশি
রোগী লাগে। দেখুন [টিউটোরিয়াল: উত্তরজীবিতা ট্রায়াল](../../tutorials/survival.md)।

## নিয়ন্ত্রক অনুশীলন

আলফা ব্যয়সহ গ্রুপ ক্রমিক নকশা নিশ্চিতকরণমূলক (confirmatory) ট্রায়ালে
প্রতিষ্ঠিত পদ্ধতি, যা ICH E9 নির্দেশিকা ও অভিযোজিত নকশা (adaptive design)
বিষয়ক FDA নির্দেশনায় (2019) বর্ণিত। এই লাইব্রেরি নকশাগুলো হিসাব করে এবং
প্রতিটি বিশ্লেষণের একটি নিরীক্ষাযোগ্য (auditable), পুনরারম্ভযোগ্য রেকর্ড রাখে
(চেকপয়েন্ট ও তার ইতিহাস ডাইজেস্ট (history digest))। এটি নিয়ন্ত্রক অর্থে
বৈধীকৃত (validated) সফটওয়্যার নয়: কোনো স্পনসর জমাদানে (submission) এটি
ব্যবহার করলে অন্য যেকোনো সরঞ্জামের মতোই তাকে এটি বৈধীকরণ করতে হবে।

আরও: [টিউটোরিয়াল: গ্রুপ ক্রমিক ট্রায়াল](../../tutorials/group-sequential.md),
যা সংখ্যাগুলো rpact-এর সঙ্গে তুলনা করে;
[রেফারেন্স: নকশা ও পরিকল্পনা](../../reference/design.md)।
