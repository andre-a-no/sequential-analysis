---
description: ఒక ప్రవాహంపై (Kafka, SQL, pandas, సెన్సార్లు) అనుక్రమ గణాంకాలను ఎలా నడపాలి, క్రాష్ తర్వాత సరిగ్గా ఆగిన చోట నుండి ఎలా తిరిగి ప్రారంభించాలి. JSON చెక్‌పాయింట్‌లు (checkpoint), నకళ్లు తొలగించిన డెలివరీ, ఆడిట్ కోసం హిస్టరీ డైజెస్ట్ (history digest), మరియు అదే రన్‌ను Python లేదా TypeScript లో కొనసాగించడం, sequential-analysis తో.
language: te
---

# ఒక ప్రవాహంపై గణాంకాలను నడిపి, క్రాష్ తర్వాత ఎలా తిరిగి ప్రారంభించాలి?

> ఇది [ఆంగ్ల పేజీ](../../guide/streaming.md)కి అనువాదం. దీనిని ఇంకా తెలుగు మాతృభాషీయులు ఎవరూ సమీక్షించలేదు; రెండింటి మధ్య తేడా ఉన్నచోట ఆంగ్ల పేజీయే ప్రామాణికం.

**సంక్షిప్త సమాధానం.** విధానాన్ని ఒక `Run` లో చుట్టండి. తర్వాత:

1. `run_sync` (లేదా ఏకకాల ఉత్పాదకుల (concurrent producer) కోసం `run_async`)
   తో దానికి పరిశీలనలను ఇవ్వండి.
2. మీకు నచ్చినంత తరచుగా `run.checkpoint()` ను భద్రపరచండి. ఇది ఒక సాధారణ JSON
   విలువ, ఇందులో స్థితి (state), యాదృచ్ఛిక స్థితి (random state), మూల స్థానాలు
   మరియు చరిత్ర యొక్క SHA-256 డైజెస్ట్ ఉంటాయి.
3. క్రాష్ తర్వాత, `Run.restore(procedure, checkpoint)` ఖచ్చితంగా, బిట్-బై-బిట్
   కొనసాగుతుంది. `Delivery("sequence")` తో, పునఃప్రారంభం తర్వాత మళ్లీ అందించబడిన
   పరిశీలనలు నకళ్లుగా (duplicate) వదిలివేయబడతాయి.
4. TypeScript ఎగ్జిక్యూటర్ (executor) అదే చెక్‌పాయింట్‌ను JavaScript లో
   కొనసాగించగలదు. ఇది అవే నిర్ణయాలు మరియు హిస్టరీ డైజెస్ట్‌ను ఇస్తుంది, మరియు
   చివరి బిట్‌ల వరకు ఏకీభవించే సంఖ్యలను: 108 అనుగుణ్యత (conformance) కేసులలో 34
   లో ఒకేలా, మిగిలిన వాటిలో సాపేక్షంగా 6·10⁻¹³ లోపల.

## క్రాష్, పునఃప్రారంభం, మళ్లీ ప్రసారం: అదే ఫలితం

300 రీడింగ్‌లపై ఒక పర్యవేక్షణ రన్ 120 తర్వాత అంతరాయం చెందుతుంది. మూలం 100వ
రీడింగ్ నుండి మళ్లీ ప్రసారం (replay) చేయబడుతుంది, పునఃప్రారంభం తర్వాత సందేశ
క్యూ (message queue) సాధారణంగా చేసినట్లే. పునరుద్ధరించిన రన్ ఇప్పటికే చూసిన 20
రీడింగ్‌లను వదిలివేసి, అంతరాయం లేని రన్ ఎక్కడ ముగుస్తుందో సరిగ్గా అక్కడే
ముగుస్తుంది:

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

హిస్టరీ డైజెస్ట్ అనేది రన్ వాడిన ప్రతి పరిశీలనపై ఒక హ్యాష్ గొలుసు (hash chain).
ఒకే డైజెస్ట్ ఉన్న రెండు రన్‌లు అదే డేటాను అదే క్రమంలో చూశాయి. ఒక ఆడిటర్
[స్పెసిఫికేషన్](../../spec.md) ను అనుసరించి పరిశీలన లాగ్ నుండి దానిని మళ్లీ
లెక్కించగలరు.

## పరిశీలనలు ఎక్కడి నుండి వస్తాయి

| మూలం | ఫంక్షన్ |
|---|---|
| విలువల జాబితా లేదా జనరేటర్ | `sources.from_values` |
| ఒక CSV ఫైల్ | `sources.from_csv` |
| ఒక pandas లేదా polars DataFrame | `adapters.from_dataframe` |
| ఒక SQL క్వెరీ (ఏదైనా DB-API కనెక్షన్) | `adapters.from_sql` |
| Kafka సందేశాలు, కమిట్ చేసిన ఆఫ్‌సెట్‌లతో | `adapters.from_kafka`, `adapters.kafka_offsets` |
| ఒకేసారి అనేక మూలాలు | `sources.interleave`, `sources.merge_ordered` |
| రికార్డ్ చేసిన పరిశీలన లాగ్ | `sources.replay` |

వేర్వేరు మూలాల నుండి వచ్చే ఇన్‌పుట్‌లు ఒక **టోపాలజీ** (topology) ద్వారా
సంబంధించబడతాయి. `KeyJoin` ఒక కేటాయింపును మరియు ఒక ఫలితాన్ని వినియోగదారు వారీగా
కలుపుతుంది, `TimeAlign` రెండు సెన్సార్లను సమయంలో సమలేఖనం చేస్తుంది, మరియు
`AsOfJoin` సంఘటనలను వాటి గురించి తెలిసిన బార్‌లకు జోడిస్తుంది. చూడండి
[డేటా మూలాలు](../../adapters.md).

## విధానం మారినప్పుడు

చెక్‌పాయింట్ విధానం యొక్క పేరు, వెర్షన్ మరియు కాన్ఫిగరేషన్‌ను నమోదు చేస్తుంది.
`Run.restore` వేరే విధానం, వేరే కాన్ఫిగరేషన్ లేదా వేరే అంకగణితం (arithmetic)
ఉన్న వెర్షన్ చేసిన చెక్‌పాయింట్‌ను తిరస్కరిస్తుంది, మరియు `IncompatibleCheckpoint`
ను రేకెత్తిస్తుంది. కాబట్టి ఒక రన్ ఎప్పుడూ నిశ్శబ్దంగా వేరే సంఖ్యలతో
కొనసాగించబడదు.

మరింత: [చెక్‌పాయింట్‌లు, లాగ్‌లు మరియు బ్యాకెండ్‌లు](../../checkpoints.md),
[TypeScript ఎగ్జిక్యూటర్](../../typescript.md),
[ఫార్మాట్‌ల స్పెసిఫికేషన్](../../spec.md).
