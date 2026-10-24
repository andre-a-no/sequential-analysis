---
description: একটি প্রবাহের (Kafka, SQL, pandas, সেন্সর) ওপর কীভাবে ক্রমিক পরিসংখ্যান চালাবেন এবং ক্র্যাশের পরে ঠিক যেখানে থেমেছিল সেখান থেকে আবার শুরু করবেন। JSON চেকপয়েন্ট (checkpoint), ডুপ্লিকেট-মুক্ত সরবরাহ, নিরীক্ষার জন্য ইতিহাস ডাইজেস্ট (history digest), এবং একই রান Python বা TypeScript-এ চালিয়ে যাওয়া, sequential-analysis দিয়ে।
language: bn
---

# একটি প্রবাহের ওপর পরিসংখ্যান চালিয়ে ক্র্যাশের পরে কীভাবে আবার শুরু করব?

> এটি [ইংরেজি পৃষ্ঠার](../../guide/streaming.md) অনুবাদ। এটি এখনও কোনো বাংলাভাষী বিশেষজ্ঞ পর্যালোচনা করেননি; দুটির মধ্যে পার্থক্য থাকলে ইংরেজি পৃষ্ঠাটিই প্রামাণ্য।

**সংক্ষিপ্ত উত্তর।** পদ্ধতিটিকে একটি `Run`-এ মুড়ে দিন। তারপর:

1. `run_sync` (অথবা সমান্তরাল উৎপাদকদের (concurrent producer) জন্য `run_async`)
   দিয়ে একে পর্যবেক্ষণ দিন।
2. যত ঘন ঘন খুশি `run.checkpoint()` সংরক্ষণ করুন। এটি একটি সাধারণ JSON
   মান, যাতে থাকে অবস্থা (state), দৈব অবস্থা (random state), উৎসের অবস্থান এবং
   ইতিহাসের একটি SHA-256 ডাইজেস্ট।
3. ক্র্যাশের পরে `Run.restore(procedure, checkpoint)` হুবহু, বিট-বাই-বিট
   চালিয়ে যায়। `Delivery("sequence")`-সহ, পুনরারম্ভের পরে আবার সরবরাহ করা
   পর্যবেক্ষণগুলো ডুপ্লিকেট হিসেবে বাদ দেওয়া হয়।
4. TypeScript নির্বাহক (executor) একই চেকপয়েন্ট JavaScript-এ চালিয়ে যেতে
   পারে। এটি একই সিদ্ধান্ত ও ইতিহাস ডাইজেস্ট দেয়, এবং এমন সংখ্যা যা শেষ বিটগুলো
   পর্যন্ত মেলে: 108টি সামঞ্জস্য (conformance) ক্ষেত্রের 34টিতে হুবহু এক, বাকিগুলোতে
   আপেক্ষিকভাবে 6·10⁻¹³-এর মধ্যে।

## ক্র্যাশ, পুনরারম্ভ, পুনঃপ্রেরণ: একই ফলাফল

300টি পাঠের ওপর একটি পর্যবেক্ষণ রান 120টির পরে বাধাপ্রাপ্ত হয়। উৎসটি 100তম
পাঠ থেকে পুনরায় প্রেরিত (replay) হয়, যেমন একটি বার্তা সারি (message queue)
সাধারণত পুনরারম্ভের পরে করে। পুনরুদ্ধার করা রান ইতিমধ্যে দেখা 20টি পাঠ বাদ
দেয় এবং ঠিক সেখানে শেষ হয় যেখানে একটি নিরবচ্ছিন্ন রান শেষ হতো:

```python
import json
import random

from sequential_analysis import Delivery, Observation, Run, run_sync
from sequential_analysis.procedures import BettingConfidenceSequence

rnd = random.Random(5)
readings = [Observation("x", rnd.betavariate(2, 5), seq=i, source="sensor-7") for i in range(300)]

def procedure():
    return BettingConfidenceSequence(lower=0.0, upper=1.0, grid=200)

run = Run(procedure(), delivery=Delivery("sequence"), run_id="sensor-7")
run_sync(run, readings[:120])
saved = json.dumps(run.checkpoint())        # to a file, a database, object storage
del run                                     # the process dies

run = Run.restore(procedure(), json.loads(saved), delivery=Delivery("sequence"))
run_sync(run, readings[100:])               # the source replays from reading 100
print(f"resumed run: {run.t} readings, {run.delivery.duplicates} duplicates dropped")

uninterrupted = Run(procedure(), delivery=Delivery("sequence"), run_id="sensor-7")
run_sync(uninterrupted, readings)
print("same state as an uninterrupted run:", run.state == uninterrupted.state)
print("same history digest:", run.checkpoint()["history_digest"] == uninterrupted.checkpoint()["history_digest"])
print(f"checkpoint size: {len(saved)} bytes")
```

```text
resumed run: 300 readings, 20 duplicates dropped
same state as an uninterrupted run: True
same history digest: True
checkpoint size: 9606 bytes
```

ইতিহাস ডাইজেস্ট হলো রানটি যে প্রতিটি পর্যবেক্ষণ ব্যবহার করেছে তার ওপর একটি
হ্যাশ শৃঙ্খল (hash chain)। একই ডাইজেস্টসহ দুটি রান একই ক্রমে একই ডেটা দেখেছে।
একজন নিরীক্ষক [স্পেসিফিকেশন](../../spec.md) অনুসরণ করে পর্যবেক্ষণ লগ থেকে
এটি পুনরায় হিসাব করতে পারেন।

## পর্যবেক্ষণগুলো কোথা থেকে আসে

| উৎস | ফাংশন |
|---|---|
| মানের একটি তালিকা বা জেনারেটর | `sources.from_values` |
| একটি CSV ফাইল | `sources.from_csv` |
| একটি pandas বা polars DataFrame | `adapters.from_dataframe` |
| একটি SQL কোয়েরি (যেকোনো DB-API সংযোগ) | `adapters.from_sql` |
| Kafka বার্তা, কমিট করা অফসেটসহ | `adapters.from_kafka`, `adapters.kafka_offsets` |
| একসঙ্গে কয়েকটি উৎস | `sources.interleave`, `sources.merge_ordered` |
| একটি রেকর্ড করা পর্যবেক্ষণ লগ | `sources.replay` |

বিভিন্ন উৎসের ইনপুট একটি **টপোলজি** (topology) দিয়ে সম্পর্কিত হয়। `KeyJoin`
ব্যবহারকারী ধরে একটি বরাদ্দ ও একটি ফলাফল যুক্ত করে, `TimeAlign` দুটি সেন্সরকে
সময়ে সারিবদ্ধ করে, এবং `AsOfJoin` ঘটনাগুলোকে সেই বারগুলোর সঙ্গে জুড়ে দেয়
যেগুলো তাদের সম্পর্কে জানত। দেখুন [ডেটা উৎস](../../adapters.md)।

## যখন পদ্ধতি বদলায়

একটি চেকপয়েন্ট পদ্ধতির নাম, সংস্করণ ও কনফিগারেশন রেকর্ড করে।
`Run.restore` ভিন্ন পদ্ধতি, ভিন্ন কনফিগারেশন বা ভিন্ন পাটিগণিতসহ (arithmetic)
কোনো সংস্করণের তৈরি চেকপয়েন্ট প্রত্যাখ্যান করে এবং `IncompatibleCheckpoint`
উত্থাপন করে। তাই একটি রান কখনও নীরবে অন্য সংখ্যা নিয়ে চালিয়ে যাওয়া হয় না।

আরও: [চেকপয়েন্ট, লগ ও ব্যাকএন্ড](../../checkpoints.md),
[TypeScript নির্বাহক](../../typescript.md),
[ফরম্যাটগুলোর স্পেসিফিকেশন](../../spec.md)।
