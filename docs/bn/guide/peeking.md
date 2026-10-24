---
description: A/B পরীক্ষা ও ট্রায়ালে প্রতিদিন p-মান যাচাই করলে কেন মিথ্যা পজিটিভ (false positive) বেড়ে যায় (উঁকি দেওয়ার সমস্যা, peeking problem), এবং ক্রমিক পদ্ধতির যে তিনটি পরিবার এর সমাধান করে, Python-এ sequential-analysis দিয়ে।
language: bn
---

# আমি কেন প্রতিদিন p-মান দেখতে পারি না?

> এটি [ইংরেজি পৃষ্ঠার](../../guide/peeking.md) অনুবাদ। এটি এখনও কোনো বাংলাভাষী বিশেষজ্ঞ পর্যালোচনা করেননি; দুটির মধ্যে পার্থক্য থাকলে ইংরেজি পৃষ্ঠাটিই প্রামাণ্য।

**সংক্ষিপ্ত উত্তর।** একটি স্থির-নমুনা পরীক্ষা (fixed-sample test) 5% মিথ্যা-পজিটিভ
হারের (false-positive rate) প্রতিশ্রুতি দেয় কেবল তখনই, যদি আপনি ফলাফলটি একবার,
পরিকল্পিত নমুনার আকারে, দেখেন। যদি আপনি বারবার দেখেন এবং প্রথম যখন p < 0.05
হয় তখনই থামেন, তাহলে আপনি প্রতারিত হওয়ার অনেক সুযোগ পান। 20 বার দেখলে
মিথ্যা-পজিটিভের হার প্রায় 25%-এ ওঠে। ক্রমিক পদ্ধতিগুলো (sequential methods)
বারবার দেখার জন্যই তৈরি। এগুলোর ক্ষেত্রে আপনি যতবারই দেখুন এবং যখনই থামুন,
হার 5% বা তার নিচে থাকে।

## উঁকি দেওয়ার সমস্যা, পরিমাপ করে

একই 10% কনভার্শন হারসহ দুটি শাখা (একটি A/A পরীক্ষা), 2,000 ব্যবহারকারী,
200 বার পুনরাবৃত্তি। "উঁকি দেওয়া" (peeking) প্রতি 100 ব্যবহারকারীর পরে প্রচলিত
দুই-অনুপাত z-পরীক্ষা চালায় এবং প্রথম p < 0.05-এ থামে। ক্রমিক
`TwoProportionTest` প্রত্যেক একক ব্যবহারকারীর পরে যাচাই করা হয়:

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

একবার দেখা তার প্রতিশ্রুতি রাখে। বিশবার দেখা ত্রুটির হারকে প্রায় ছয় গুণ বাড়িয়ে
দেয়। ক্রমিক পরীক্ষা, 2,000 ব্যবহারকারীর প্রত্যেকের পরে দেখা হলেও, তা 5%-এ
রাখে। এটাই প্রতিশ্রুতি: এর নিশ্চয়তা **exact**
(`TwoProportionTest.guarantee == "exact"`), অর্থাৎ যতবারই দেখুন, প্রতিটি নমুনার
আকারে মিথ্যা-পজিটিভের হার সর্বোচ্চ 5%। 200 বার পুনরাবৃত্তিতে 10টি মিথ্যা
পজিটিভ ঠিক সেটাই যা একটি exact 5% দেয়।

## ক্রমিক পদ্ধতির তিনটি পরিবার

| পরিবার | আপনি দেখতে পারেন | সাধারণ ব্যবহার | sequential-analysis-এ |
|---|---|---|---|
| **ক্রমিক সম্ভাবিতা অনুপাত পরীক্ষা (sequential probability ratio test)** (Wald 1945) | প্রতিটি পর্যবেক্ষণের পরে | একটি সরল প্রকল্পের বিপরীতে আরেকটি, গড়ে সবচেয়ে কম পর্যবেক্ষণ: মান নিয়ন্ত্রণ, সিমুলেশন, সাইকোফিজিক্স | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **গ্রুপ ক্রমিক নকশা (group sequential design)** (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | কয়েকটি পরিকল্পিত অন্তর্বর্তী বিশ্লেষণে | ডেটা পর্যবেক্ষণ কমিটিসহ ক্লিনিক্যাল ট্রায়াল | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **যেকোনো-সময়-বৈধ অনুমান (anytime-valid inference)**: e-মান, আস্থা অনুক্রম, মিশ্রণ SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | প্রতিটি পর্যবেক্ষণের পরে, যেকোনো কারণে থামা | অনলাইন A/B পরীক্ষা, পর্যবেক্ষণ ড্যাশবোর্ড | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**এর খরচ কত।** বেশি ঘন ঘন দেখলে পরিকল্পিত প্রভাবে বেশি ডেটা লাগে:

* চারটি বিশ্লেষণসহ একটি গ্রুপ ক্রমিক নকশার একক বিশ্লেষণের চেয়ে 1–20% বেশি
  রোগী লাগে;
* দুই অনুপাতের একটি যেকোনো-সময়-বৈধ পরীক্ষার একক বিশ্লেষণের 1.3–1.6 গুণ
  ব্যবহারকারী লাগে।

বিনিময়ে একটি বড় প্রভাব পরীক্ষাটিকে আগেভাগে থামিয়ে দেয়, এবং কাউকে আগে থেকে
নমুনার আকার স্থির করতে হয় না।

## যখন এটি সমস্যা নয়

উঁকি দেওয়া ত্রুটি কেবল তখনই বাড়ায় যখন আপনি যা করেন তা আপনি যা দেখেছেন তার
ওপর নির্ভর করে। আপনি যদি ড্যাশবোর্ড দেখেন কিন্তু সবসময় পরীক্ষাটি তার পরিকল্পিত
আকার পর্যন্ত চালান এবং একবার পরীক্ষা করেন, তবে স্থির-নমুনা পরীক্ষাটি বৈধ। সেই
ক্ষেত্রে এটিই সবচেয়ে দক্ষ পছন্দও।

এরপর: [A/B পরীক্ষা আগেভাগে থামান](ab-testing.md),
[আস্থা অনুক্রম](confidence-sequences.md),
[পরিভাষা](glossary.md)।
