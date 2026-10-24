---
description: كيف تُجري إحصاءً تتابعيًا على تدفق بيانات (Kafka، SQL، pandas، المستشعرات) وتستأنف بعد الانهيار من حيث توقفت بالضبط. نقاط حفظ JSON، وتسليم مع إزالة التكرار، وملخص سجل للتدقيق، ومتابعة التشغيل نفسه في Python أو TypeScript، باستخدام sequential-analysis.
language: ar
---

# كيف أجري الإحصاء على تدفق بيانات وأستأنف بعد الانهيار؟

> هذه ترجمة [للصفحة الإنجليزية](../../guide/streaming.md). لم يراجعها متحدث أصلي باللغة بعد؛ وحيثما اختلفت الصفحتان، فالصفحة الإنجليزية هي المرجع المعتمد.

**الإجابة المختصرة.** غلّف الإجراء في كائن `Run`. ثم:

1. غذِّه بالمشاهدات باستخدام `run_sync` (أو `run_async` للمنتجين
   المتزامنين).
2. احفظ `run.checkpoint()` بالوتيرة التي تشاء. وهي قيمة JSON عادية تتضمن
   الحالة، وحالة المولّد العشوائي، ومواضع المصادر، وملخص SHA-256 للسجل.
3. بعد الانهيار، يتابع `Run.restore(procedure, checkpoint)` بدقة تامة،
   مطابقًا بتًّا ببت. ومع `Delivery("sequence")`، تُسقَط المشاهدات التي
   تُسلَّم مرة أخرى بعد إعادة التشغيل بوصفها مكرّرات.
4. يستطيع المنفّذ المكتوب بلغة TypeScript متابعة نقطة الحفظ نفسها في
   JavaScript. فيعطي القرارات نفسها وملخص السجل نفسه، وأرقامًا تتفق حتى
   آخر البتات: متطابقة في 34 من حالات المطابقة الـ 108، وضمن فرق نسبي
   6·10⁻¹³ في البقية.

## انهيار، إعادة تشغيل، إعادة بث: النتيجة نفسها

يُقطع تشغيل مراقبة على 300 قراءة بعد 120 قراءة. ثم يُعاد بث المصدر من
القراءة 100، كما تفعل طوابير الرسائل عادةً بعد إعادة التشغيل. فيُسقط
التشغيل المُستعاد القراءات الـ 20 التي رآها من قبل وينتهي تمامًا حيث كان
سينتهي تشغيل غير منقطع:

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

ملخص السجل (history digest) سلسلة تجزئة على كل مشاهدة استخدمها التشغيل.
والتشغيلان اللذان لهما الملخص نفسه قد رأيا البيانات نفسها بالترتيب نفسه.
ويستطيع المدقّق إعادة حسابه من سجل المشاهدات، باتباع
[المواصفات](../../spec.md).

## من أين تأتي المشاهدات

| المصدر | الدالة |
|---|---|
| قائمة أو مولّد من القيم | `sources.from_values` |
| ملف CSV | `sources.from_csv` |
| إطار بيانات DataFrame في pandas أو polars | `adapters.from_dataframe` |
| استعلام SQL (أي اتصال DB-API) | `adapters.from_sql` |
| رسائل Kafka، مع إزاحات مُثبَّتة (committed offsets) | `adapters.from_kafka`، `adapters.kafka_offsets` |
| عدة مصادر في آن واحد | `sources.interleave`، `sources.merge_ordered` |
| سجل مشاهدات مُسجَّل | `sources.replay` |

تُربط المدخلات من مصادر مختلفة بواسطة **طوبولوجيا** (topology). فيربط
`KeyJoin` بين التخصيص والنتيجة بحسب المستخدم، ويحاذي `TimeAlign` بين
مستشعرين زمنيًا، ويُلحق `AsOfJoin` الأحداث بالأشرطة (bars) التي كانت على
علم بها. انظر [مصادر البيانات](../../adapters.md).

## حين يتغيّر الإجراء

تسجّل نقطة الحفظ اسم الإجراء وإصداره وإعداداته. ويرفض `Run.restore` نقطة
حفظ أنشأها إجراء مختلف، أو إعدادات مختلفة، أو إصدار بحساب مختلف، ويطلق
الاستثناء `IncompatibleCheckpoint`. وبذلك لا يُتابَع أي تشغيل أبدًا بأرقام
أخرى دون أن يُلاحَظ ذلك.

المزيد: [نقاط الحفظ والسجلات والواجهات الخلفية](../../checkpoints.md)،
[منفّذ TypeScript](../../typescript.md)،
[مواصفات الصيغ](../../spec.md).
