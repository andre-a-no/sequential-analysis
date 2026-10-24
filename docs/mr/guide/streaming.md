---
description: डेटा प्रवाहावर (Kafka, SQL, pandas, सेन्सर) अनुक्रमिक सांख्यिकी कशी चालवावी आणि क्रॅशनंतर नेमकी जिथे थांबली तिथून पुन्हा कशी सुरू करावी. JSON चेकपॉइंट (checkpoints), दुहेरी नोंदी वगळणारी डिलिव्हरी, लेखापरीक्षणासाठी इतिहास डायजेस्ट, आणि तोच रन Python किंवा TypeScript मध्ये पुढे चालू, sequential-analysis सह.
language: mr
---

# डेटा प्रवाहावर सांख्यिकी कशी चालवावी आणि क्रॅशनंतर पुन्हा कशी सुरू करावी?

> हे [इंग्रजी पानाचे](../../guide/streaming.md) भाषांतर आहे. मराठी मातृभाषक व्यक्तीने अद्याप त्याचे पुनरावलोकन केलेले नाही; दोन्हींमध्ये फरक आढळल्यास इंग्रजी पान अधिकृत मानावे.

**थोडक्यात उत्तर.** कार्यपद्धती एका `Run` मध्ये गुंडाळा. मग:

1. `run_sync` ने (किंवा समवर्ती उत्पादकांसाठी (concurrent producers) `run_async` ने)
   तिला निरीक्षणे द्या.
2. `run.checkpoint()` तुम्हाला हवे तितक्या वेळा जतन करा. हे साधे JSON मूल्य आहे,
   ज्यात अवस्था (state), यादृच्छिक अवस्था, स्रोतांची स्थाने आणि इतिहासाचा SHA-256
   डायजेस्ट असतो.
3. क्रॅशनंतर `Run.restore(procedure, checkpoint)` अचूकपणे, बिट-दर-बिट पुढे चालू
   ठेवते. `Delivery("sequence")` सह, पुन्हा सुरू झाल्यानंतर परत पोहोचवलेली
   निरीक्षणे दुहेरी (duplicates) म्हणून वगळली जातात.
4. TypeScript एक्झिक्युटर तोच चेकपॉइंट JavaScript मध्ये पुढे चालू ठेवू शकतो. तो
   तेच निर्णय आणि इतिहास डायजेस्ट देतो, आणि शेवटच्या बिट्सपर्यंत जुळणारे आकडे:
   108 पैकी 34 अनुरूपता प्रकरणांमध्ये (conformance cases) एकसारखे, उरलेल्यांमध्ये
   6·10⁻¹³ सापेक्ष फरकाच्या आत.

## क्रॅश, पुन्हा सुरुवात, पुनःप्रक्षेपण: तोच निकाल

300 वाचनांवरील देखरेख रन 120 नंतर खंडित होतो. संदेश रांग (message queue) सहसा
पुन्हा सुरू झाल्यानंतर करते तसे, स्रोत 100 व्या वाचनापासून पुन्हा प्रक्षेपित
(replay) केला जातो. पुनर्स्थापित रन आधीच पाहिलेली 20 वाचने वगळतो आणि अखंड रन
जिथे संपला असता नेमका तिथेच संपतो:

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

इतिहास डायजेस्ट (history digest) ही रनने वापरलेल्या प्रत्येक निरीक्षणावरील हॅश
साखळी आहे. समान डायजेस्ट असलेल्या दोन रननी समान डेटा समान क्रमाने पाहिलेला असतो.
लेखापरीक्षक (auditor) निरीक्षण लॉगवरून
[विनिर्देशाचे](../../spec.md) पालन करून तो पुन्हा गणन करू शकतो.

## निरीक्षणे कुठून येतात

| स्रोत | फंक्शन |
|---|---|
| मूल्यांची यादी किंवा जनरेटर | `sources.from_values` |
| CSV फाइल | `sources.from_csv` |
| pandas किंवा polars DataFrame | `adapters.from_dataframe` |
| SQL क्वेरी (कोणतेही DB-API कनेक्शन) | `adapters.from_sql` |
| Kafka संदेश, कमिट केलेल्या ऑफसेटसह | `adapters.from_kafka`, `adapters.kafka_offsets` |
| एकाच वेळी अनेक स्रोत | `sources.interleave`, `sources.merge_ordered` |
| नोंदवलेला निरीक्षण लॉग | `sources.replay` |

वेगवेगळ्या स्रोतांमधील इनपुट एका **टोपोलॉजीद्वारे** (topology) जोडले जातात.
`KeyJoin` वाटप आणि निकाल वापरकर्त्यानुसार जोडते, `TimeAlign` दोन सेन्सर वेळेत
संरेखित करते, आणि `AsOfJoin` घटनांना त्या घटनांची माहिती असलेल्या बारशी जोडते.
पाहा [डेटा स्रोत](../../adapters.md).

## कार्यपद्धती बदलते तेव्हा

चेकपॉइंट कार्यपद्धतीचे नाव, आवृत्ती आणि संरचना (configuration) नोंदवतो.
`Run.restore` वेगळ्या कार्यपद्धतीने, वेगळ्या संरचनेने किंवा वेगळे अंकगणित असलेल्या
आवृत्तीने बनवलेला चेकपॉइंट नाकारते, आणि `IncompatibleCheckpoint` उभारते. त्यामुळे
रन कधीही गुपचूप इतर आकड्यांसह पुढे चालू होत नाही.

अधिक: [चेकपॉइंट, लॉग आणि बॅकएंड](../../checkpoints.md),
[TypeScript एक्झिक्युटर](../../typescript.md),
[स्वरूपांचे विनिर्देश](../../spec.md).
