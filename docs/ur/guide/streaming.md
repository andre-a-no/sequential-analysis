---
description: اسٹریم (Kafka، SQL، pandas، سینسرز) پر ترتیبی شماریات کیسے چلائیں اور کریش کے بعد بالکل وہیں سے دوبارہ کیسے شروع کریں جہاں وہ رکی تھی۔ JSON چیک پوائنٹس، ڈپلیکیٹ سے پاک ترسیل، آڈٹ کے لیے history digest، اور وہی رن Python یا TypeScript میں جاری، sequential-analysis کے ساتھ۔
language: ur
---

# اسٹریم پر شماریات کیسے چلائیں اور کریش کے بعد دوبارہ کیسے شروع کریں؟

> یہ [انگریزی صفحے](../../guide/streaming.md) کا ترجمہ ہے۔ ابھی کسی اہلِ زبان نے اس کا جائزہ نہیں لیا؛ جہاں دونوں میں فرق ہو، وہاں انگریزی صفحہ ہی مستند ہے۔

**مختصر جواب۔** طریقۂ کار کو ایک `Run` میں لپیٹیں۔ پھر:

1. `run_sync` کے ذریعے (یا بیک وقت چلنے والے producers کے لیے `run_async` کے
   ذریعے) اسے مشاہدات دیں۔
2. `run.checkpoint()` کو جتنی بار چاہیں محفوظ کریں۔ یہ ایک سادہ JSON قدر ہے جس میں
   اسٹیٹ، رینڈم اسٹیٹ، سورس کی پوزیشنز اور ہسٹری کا SHA-256 digest ہوتا ہے۔
3. کریش کے بعد، `Run.restore(procedure, checkpoint)` بالکل ٹھیک، بٹ بہ بٹ جاری
   رکھتا ہے۔ `Delivery("sequence")` کے ساتھ، ری اسٹارٹ کے بعد دوبارہ بھیجے گئے
   مشاہدات ڈپلیکیٹ سمجھ کر چھوڑ دیے جاتے ہیں۔
4. TypeScript ایگزیکیوٹر اسی چیک پوائنٹ کو JavaScript میں جاری رکھ سکتا ہے۔ یہ وہی
   فیصلے اور history digest دیتا ہے، اور ایسے اعداد جو آخری bits تک متفق ہیں: 108
   conformance کیسز میں سے 34 میں یکساں، باقی میں 6·10⁻¹³ نسبتی (relative) فرق
   کے اندر۔

## کریش، ری اسٹارٹ، ری پلے: وہی نتیجہ

300 ریڈنگز پر ایک مانیٹرنگ رن 120 کے بعد منقطع ہو جاتا ہے۔ سورس ریڈنگ 100 سے ری
پلے ہوتا ہے، جیسا کہ کوئی message queue عام طور پر ری اسٹارٹ کے بعد کرتی ہے۔ بحال
کیا گیا (restored) رن وہ 20 ریڈنگز چھوڑ دیتا ہے جو وہ پہلے دیکھ چکا ہے اور بالکل
وہیں ختم ہوتا ہے جہاں بلا تعطل رن ہوتا:

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

history digest رن کے استعمال کردہ ہر مشاہدے پر ایک ہیش چین ہے۔ ایک ہی digest والے
دو رنز نے ایک ہی ڈیٹا ایک ہی ترتیب میں دیکھا ہے۔ ایک آڈیٹر
[تفصیلی وضاحت (specification)](../../spec.md) پر عمل کرتے ہوئے مشاہدات کے لاگ سے
اس کا دوبارہ حساب لگا سکتا ہے۔

## مشاہدات کہاں سے آتے ہیں

| سورس | فنکشن |
|---|---|
| قدروں کی ایک فہرست یا جنریٹر | `sources.from_values` |
| ایک CSV فائل | `sources.from_csv` |
| ایک pandas یا polars DataFrame | `adapters.from_dataframe` |
| ایک SQL کوئری (کوئی بھی DB-API کنکشن) | `adapters.from_sql` |
| Kafka پیغامات، committed offsets کے ساتھ | `adapters.from_kafka`، `adapters.kafka_offsets` |
| ایک ساتھ کئی سورسز | `sources.interleave`، `sources.merge_ordered` |
| ریکارڈ کیا گیا مشاہدات کا لاگ | `sources.replay` |

مختلف سورسز کے inputs ایک **ٹوپولوجی (topology)** کے ذریعے جڑے ہوتے ہیں۔ `KeyJoin`
صارف کے لحاظ سے assignment اور نتیجے کو جوڑتا ہے، `TimeAlign` دو سینسرز کو وقت میں
ہم آہنگ کرتا ہے، اور `AsOfJoin` واقعات کو ان bars سے جوڑتا ہے جنہیں ان کا علم تھا۔
دیکھیں [ڈیٹا سورسز](../../adapters.md)۔

## جب طریقۂ کار بدل جائے

چیک پوائنٹ طریقۂ کار کا نام، ورژن اور کنفیگریشن درج کرتا ہے۔ `Run.restore` کسی
مختلف طریقۂ کار، مختلف کنفیگریشن یا مختلف حساب (arithmetic) والے ورژن کے بنائے
ہوئے چیک پوائنٹ کو رد کر دیتا ہے، اور `IncompatibleCheckpoint` raise کرتا ہے۔
اس لیے کوئی رن کبھی خاموشی سے دوسرے اعداد کے ساتھ جاری نہیں رہتا۔

مزید: [چیک پوائنٹس، لاگز اور بیک اینڈز](../../checkpoints.md)،
[TypeScript ایگزیکیوٹر](../../typescript.md)،
[فارمیٹس کی تفصیلی وضاحت](../../spec.md)۔
