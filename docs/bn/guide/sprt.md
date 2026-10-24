---
description: Python-এ sequential-analysis দিয়ে Wald-এর ক্রমিক সম্ভাবিতা অনুপাত পরীক্ষা (sequential probability ratio test, SPRT) কীভাবে চালাবেন। ত্রুটির হার, স্থির-নমুনা পরীক্ষার তুলনায় গড় নমুনার আকার, এবং খণ্ডিত বিকল্পগুলো (2-SPRT, Kiefer–Weiss সর্বোত্তম পরিকল্পনা)।
language: bn
---

# Python-এ Wald-এর SPRT কীভাবে চালাব?

> এটি [ইংরেজি পৃষ্ঠার](../../guide/sprt.md) অনুবাদ। এটি এখনও কোনো বাংলাভাষী বিশেষজ্ঞ পর্যালোচনা করেননি; দুটির মধ্যে পার্থক্য থাকলে ইংরেজি পৃষ্ঠাটিই প্রামাণ্য।

**সংক্ষিপ্ত উত্তর।** `sequential_analysis.procedures` থেকে
`SPRT(family, theta0, theta1, alpha, beta)` Wald-এর ক্রমিক সম্ভাবিতা অনুপাত
পরীক্ষা (sequential probability ratio test) বাস্তবায়ন করে। এটি গড়ে সবচেয়ে কম
পর্যবেক্ষণে দুটি সরল প্রকল্পের (simple hypothesis) মধ্যে সিদ্ধান্ত নেয়। একে
একবারে একটি পর্যবেক্ষণ দিন এবং প্রথম সিদ্ধান্তে থামুন। নিচের উদাহরণে একই
ত্রুটির হারসহ স্থির-নমুনা পরীক্ষার প্রায় অর্ধেক পর্যবেক্ষণ লাগে: 133-এর বদলে
গড়ে 65–76টি আইটেম। নিশ্চিত সর্বোচ্চ নমুনার আকার দরকার হলে এর বদলে `TwoSPRT`
বা `kiefer_weiss_plan` থেকে একটি পরিকল্পনা ব্যবহার করুন।

## উদাহরণ: ত্রুটিপূর্ণতার হার কি 10% না 20%?

একটি ব্যাচ গ্রহণ করা হয় যদি তার ত্রুটিপূর্ণতার হার 10% হয় এবং প্রত্যাখ্যাত হয়
যদি 20% হয়, দুই ধরনের ত্রুটির হারই 5%:

```python
import random

from sequential_analysis.procedures import SPRT, Bernoulli

test = SPRT(Bernoulli(), theta0=0.10, theta1=0.20, alpha=0.05, beta=0.05)

def inspect_items(rate, seed):
    """Inspect items until the test decides; returns (decision, items inspected)."""
    rnd = random.Random(seed)
    state = test.initial_state()
    while state.decision is None:
        state, out = test.step(state, {"x": int(rnd.random() < rate)})
    return state.decision, state.n

decision, n = inspect_items(0.10, seed=1)
print(f"a good batch: {decision} after {n} items")
```

```text
a good batch: accept_h0 after 108 items
```

অনেক ব্যাচজুড়ে এটি কেমন করে?

```python
for rate in (0.10, 0.20):
    results = [inspect_items(rate, seed) for seed in range(2000)]
    wrong = sum(d == ("reject_h0" if rate == 0.10 else "accept_h0") for d, _ in results) / len(results)
    average = sum(n for _, n in results) / len(results)
    longest = max(n for _, n in results)
    print(f"defect rate {rate:.0%}: wrong decision {wrong:.1%}, average {average:.0f} items, longest {longest}")
```

```text
defect rate 10%: wrong decision 3.5%, average 76 items, longest 370
defect rate 20%: wrong decision 4.3%, average 65 items, longest 315
```

একই ত্রুটির হারসহ একটি স্থির-নমুনা পরীক্ষা প্রতিটি ব্যাচে প্রায় 133টি আইটেম
পরিদর্শন করে (normal আসন্নীকরণ)। SPRT গড়ে 43–51% কম পরিদর্শন করে। তবে এর
নমুনার আকার দৈব এবং এর কোনো ঊর্ধ্বসীমা নেই, এবং কয়েকটি ব্যাচে গড়ের চেয়ে
অনেক বেশি সময় লাগে।

সীমাগুলো (threshold) Wald-এর: log((1 − β)/α) ও log(β/(1 − α))। এগুলো থামার সময়ে
যেকোনো নমুনার আকারের জন্য নিশ্চিত করে যে প্রকৃত ত্রুটির হার α′ ও β′
α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) এবং α′ + β′ ≤ α + β মেনে চলে। থামার সময়
সম্ভাবিতা অনুপাত সীমাগুলো ছাড়িয়ে যায় (overshoot), তাই বাস্তবে হারগুলো নামমাত্র
(nominal) হারের নিচে থাকে, যেমন এখানে। এটাই `SPRT.guarantee == "exact"`-এর
অর্থ। সীমাবদ্ধ করার বদলে যথাযথভাবে হিসাব করা ত্রুটির হারের জন্য একটি
পরিকল্পনার ওপর `operating_characteristic` ব্যবহার করুন (নিচে)।

## যখন আপনার সর্বোচ্চ নমুনার আকার দরকার

* `TwoSPRT` (Lorden's 2-SPRT) একটি স্থির দিগন্তের (horizon) মধ্যে থামে এবং
  সবচেয়ে খারাপ ক্ষেত্রের প্রত্যাশিত নমুনার আকার প্রায় সর্বনিম্ন করে।
* `sequential_analysis.design`-এর
  `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  পশ্চাৎমুখী আরোহের (backward induction) মাধ্যমে সর্বোচ্চ নমুনার আকারসহ
  সর্বোত্তম পরিকল্পনা হিসাব করে। `PlanTest` এটি নির্বাহ করে, এবং
  `operating_characteristic` সিমুলেশন ছাড়াই এর যথাযথ ত্রুটির হার ও প্রত্যাশিত
  নমুনার আকার দেয়। দেখুন `examples/07_design_kiefer_weiss.py`।
* প্রতি পর্যবেক্ষণে একবারের বদলে কয়েকটি পরিকল্পিত দেখার জন্য একটি
  [গ্রুপ ক্রমিক নকশা](clinical-trials.md) ব্যবহার করুন।

## যখন SPRT ভুল সরঞ্জাম

* **প্রকল্পগুলো সরল নয়।** "হার 10%" বনাম "হার অন্য যেকোনো কিছু" একটি
  যৌগিক বিকল্প (composite alternative)। একটি মিশ্রণ SPRT (`NormalMixtureSPRT`,
  `TMixtureSPRT`) বা বাজি ধরার মাধ্যমে পরীক্ষা (`BettingMeanTest`) ব্যবহার করুন,
  যেগুলো প্রতিটি বিকল্পের বিরুদ্ধে যেকোনো-সময়-বৈধ।
* **প্রকৃত মান θ₀ ও θ₁-এর মাঝে।** তখন SPRT সবচেয়ে ধীর, এবং এর প্রত্যাশিত
  নমুনার আকার স্থির নমুনার আকারকে ছাড়িয়ে যেতে পারে। Kiefer–Weiss পরিকল্পনা ঠিক
  এই ক্ষেত্রের জন্যই তৈরি।

সম্ভাবিতা-অনুপাত পদ্ধতির জন্য উপলব্ধ পরিবার (family): `Gaussian` (জানা
ভেদাঙ্ক), `Bernoulli`, `Poisson`, `Exponential`।
