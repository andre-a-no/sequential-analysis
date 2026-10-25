---
description: स्ट्रीम (Kafka, SQL, pandas, सेंसर) पर अनुक्रमिक सांख्यिकी कैसे चलाएँ और क्रैश के बाद ठीक वहीं से कैसे फिर शुरू करें जहाँ वह रुकी थी। JSON चेकपॉइंट, डुप्लिकेट-रहित डिलीवरी, ऑडिट के लिए history digest, और वही रन Python या TypeScript में जारी, sequential-analysis के साथ।
language: hi
---

# स्ट्रीम पर सांख्यिकी कैसे चलाएँ और क्रैश के बाद फिर से कैसे शुरू करें?

> यह [अंग्रेज़ी पृष्ठ](../../guide/streaming.md) का अनुवाद है। इसकी समीक्षा अभी किसी मूल हिंदी भाषी ने नहीं की है; जहाँ दोनों में अंतर हो, वहाँ अंग्रेज़ी पृष्ठ ही प्रामाणिक है।

**संक्षिप्त उत्तर।** प्रक्रिया को एक `Run` में लपेटें। फिर:

1. `run_sync` से (या समवर्ती (concurrent) producers के लिए `run_async` से) इसे
   प्रेक्षण दें।
2. `run.checkpoint()` को जितनी बार चाहें सहेजें। यह एक सादा JSON मान है जिसमें
   स्टेट, रैंडम स्टेट, सोर्स की पोज़िशन और हिस्ट्री का SHA-256 digest होता है।
3. क्रैश के बाद, `Run.restore(procedure, checkpoint)` ठीक-ठीक, बिट-दर-बिट जारी
   रखता है। `Delivery("sequence")` के साथ, रीस्टार्ट के बाद दोबारा भेजे गए
   प्रेक्षण डुप्लिकेट मानकर छोड़ दिए जाते हैं।
4. TypeScript एक्ज़ीक्यूटर उसी चेकपॉइंट को JavaScript में जारी रख सकता है। यह
   वही निर्णय और history digest देता है, और ऐसी संख्याएँ जो आख़िरी बिट्स तक मेल
   खाती हैं: 108 conformance मामलों में से 34 में समान, बाकी में 6·10⁻¹³
   सापेक्ष (relative) के भीतर।

## क्रैश, रीस्टार्ट, रीप्ले: वही परिणाम

300 रीडिंग पर एक मॉनिटरिंग रन 120 के बाद बाधित हो जाता है। सोर्स रीडिंग 100 से
रीप्ले होता है, जैसा कोई message queue आम तौर पर रीस्टार्ट के बाद करती है।
बहाल किया गया (restored) रन वे 20 रीडिंग छोड़ देता है जो वह पहले देख चुका है और
ठीक वहीं ख़त्म होता है जहाँ बिना बाधा वाला रन होता:

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

history digest रन द्वारा उपयोग किए गए हर प्रेक्षण पर एक हैश चेन है। एक ही digest
वाले दो रन ने एक ही डेटा एक ही क्रम में देखा है। एक ऑडिटर
[विनिर्देश (specification)](../../spec.md) का पालन करते हुए प्रेक्षण लॉग से इसकी
फिर से गणना कर सकता है।

## प्रेक्षण कहाँ से आते हैं

| सोर्स | फ़ंक्शन |
|---|---|
| मानों की एक सूची या जनरेटर | `sources.from_values` |
| एक CSV फ़ाइल | `sources.from_csv` |
| एक pandas या polars DataFrame | `adapters.from_dataframe` |
| एक SQL क्वेरी (कोई भी DB-API कनेक्शन) | `adapters.from_sql` |
| Kafka संदेश, committed offsets के साथ | `adapters.from_kafka`, `adapters.kafka_offsets` |
| एक साथ कई सोर्स | `sources.interleave`, `sources.merge_ordered` |
| रिकॉर्ड किया गया प्रेक्षण लॉग | `sources.replay` |

अलग-अलग सोर्स के इनपुट एक **टोपोलॉजी (topology)** द्वारा जुड़े होते हैं। `KeyJoin`
उपयोगकर्ता के अनुसार असाइनमेंट और परिणाम को जोड़ता है, `TimeAlign` दो सेंसरों को
समय में संरेखित करता है, और `AsOfJoin` इवेंट्स को उन बार्स से जोड़ता है जिन्हें
उनकी जानकारी थी। देखें [डेटा सोर्स](../../adapters.md)।

## जब प्रक्रिया बदल जाए

चेकपॉइंट प्रक्रिया का नाम, संस्करण और कॉन्फ़िगरेशन दर्ज करता है। `Run.restore`
किसी अलग प्रक्रिया, अलग कॉन्फ़िगरेशन या अलग अंकगणित (arithmetic) वाले संस्करण
द्वारा बनाए गए चेकपॉइंट को अस्वीकार कर देता है, और `IncompatibleCheckpoint`
उठाता है। इसलिए कोई रन कभी भी चुपचाप अलग संख्याओं के साथ जारी नहीं रहता।

और: [चेकपॉइंट, लॉग और बैकएंड](../../checkpoints.md),
[TypeScript एक्ज़ीक्यूटर](../../typescript.md),
[फ़ॉर्मैट का विनिर्देश](../../spec.md)।
