---
description: ஒரு தரவுத் தொடரோட்டத்தில் (Kafka, SQL, pandas, உணரிகள்) தொடர்முறைப் புள்ளியியலை இயக்குவது எப்படி, செயலிழப்புக்குப் பின் நின்ற இடத்திலிருந்தே துல்லியமாகத் தொடர்வது எப்படி. JSON சோதனைப்புள்ளிகள் (checkpoints), நகல்நீக்கிய விநியோகம், தணிக்கைக்கான வரலாற்றுச் செரிமானம், அதே ஓட்டம் Python அல்லது TypeScript-இல் தொடர்தல், sequential-analysis உடன்.
language: ta
---

# தரவுத் தொடரோட்டத்தில் புள்ளியியலை இயக்கி, செயலிழப்புக்குப் பின் மீண்டும் தொடர்வது எப்படி?

> இது [ஆங்கிலப் பக்கத்தின்](../../guide/streaming.md) மொழிபெயர்ப்பு. தமிழைத் தாய்மொழியாகக் கொண்ட ஒருவர் இதை இன்னும் மதிப்பாய்வு செய்யவில்லை; இரண்டுக்கும் இடையே வேறுபாடு இருந்தால், ஆங்கிலப் பக்கமே அதிகாரப்பூர்வமானது.

**சுருக்கமான பதில்.** செயல்முறையை ஒரு `Run`-க்குள் பொதியுங்கள். பின்னர்:

1. `run_sync` மூலம் (அல்லது ஒருங்கியங்கும் உற்பத்தியாளர்களுக்கு (concurrent
   producers) `run_async` மூலம்) அதற்குக் கவனிப்புகளை வழங்குங்கள்.
2. `run.checkpoint()`-ஐ நீங்கள் விரும்பும் அளவுக்கு அடிக்கடி சேமியுங்கள். இது ஒரு
   சாதாரண JSON மதிப்பு; இதில் நிலை (state), சமவாய்ப்பு நிலை, மூலங்களின் நிலைகள்
   மற்றும் வரலாற்றின் SHA-256 செரிமானம் உள்ளன.
3. செயலிழப்புக்குப் பின், `Run.restore(procedure, checkpoint)` துல்லியமாக,
   பிட்டுக்குப் பிட் தொடர்கிறது. `Delivery("sequence")` உடன், மறுதொடக்கத்துக்குப்
   பின் மீண்டும் வழங்கப்படும் கவனிப்புகள் நகல்களாக (duplicates) கைவிடப்படுகின்றன.
4. TypeScript இயக்கி அதே சோதனைப்புள்ளியை JavaScript-இல் தொடர முடியும். அது அதே
   முடிவுகளையும் வரலாற்றுச் செரிமானத்தையும் தருகிறது; எண்கள் கடைசி பிட்டுகள் வரை
   ஒத்துப்போகின்றன: 108 இணக்கச் சூழல்களில் (conformance cases) 34-இல் ஒன்றேபோல்,
   மற்றவற்றில் 6·10⁻¹³ சார்பு வேறுபாட்டுக்குள்.

## செயலிழப்பு, மறுதொடக்கம், மறுஒளிபரப்பு: அதே முடிவு

300 அளவீடுகள் மீதான ஒரு கண்காணிப்பு ஓட்டம் 120-க்குப் பிறகு குறுக்கிடப்படுகிறது.
செய்தி வரிசை (message queue) மறுதொடக்கத்துக்குப் பின் வழக்கமாகச் செய்வது போல,
மூலம் 100-ஆவது அளவீட்டிலிருந்து மீண்டும் ஒளிபரப்பப்படுகிறது (replay). மீட்டமைக்கப்பட்ட
ஓட்டம் ஏற்கெனவே பார்த்த 20 அளவீடுகளைக் கைவிட்டு, குறுக்கீடு இல்லாத ஓட்டம் எங்கே
முடிந்திருக்குமோ சரியாக அங்கேயே முடிகிறது:

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

வரலாற்றுச் செரிமானம் (history digest) என்பது ஓட்டம் பயன்படுத்திய ஒவ்வொரு கவனிப்பின்
மீதான ஹாஷ் சங்கிலி. ஒரே செரிமானம் கொண்ட இரண்டு ஓட்டங்கள் ஒரே தரவை ஒரே வரிசையில்
பார்த்துள்ளன. ஒரு தணிக்கையாளர் (auditor) கவனிப்புப் பதிவிலிருந்து,
[விவரக்கூற்றைப்](../../spec.md) பின்பற்றி அதை மீண்டும் கணக்கிட முடியும்.

## கவனிப்புகள் எங்கிருந்து வருகின்றன

| மூலம் | செயல்பாடு |
|---|---|
| மதிப்புகளின் பட்டியல் அல்லது உருவாக்கி (generator) | `sources.from_values` |
| ஒரு CSV கோப்பு | `sources.from_csv` |
| ஒரு pandas அல்லது polars DataFrame | `adapters.from_dataframe` |
| ஒரு SQL வினவல் (எந்த DB-API இணைப்பும்) | `adapters.from_sql` |
| Kafka செய்திகள், உறுதிசெய்யப்பட்ட ஆஃப்செட்டுகளுடன் | `adapters.from_kafka`, `adapters.kafka_offsets` |
| ஒரே நேரத்தில் பல மூலங்கள் | `sources.interleave`, `sources.merge_ordered` |
| பதிவுசெய்யப்பட்ட கவனிப்புப் பதிவு | `sources.replay` |

வெவ்வேறு மூலங்களிலிருந்து வரும் உள்ளீடுகள் ஒரு **இடவியலால்** (topology)
தொடர்புபடுத்தப்படுகின்றன. `KeyJoin` ஒதுக்கீட்டையும் விளைவையும் பயனர் வாரியாக
இணைக்கிறது, `TimeAlign` இரண்டு உணரிகளை நேரத்தில் சீரமைக்கிறது, `AsOfJoin`
நிகழ்வுகளை அவற்றைப் பற்றி அறிந்திருந்த பார்களுடன் (bars) இணைக்கிறது. காண்க
[தரவு மூலங்கள்](../../adapters.md).

## செயல்முறை மாறும்போது

சோதனைப்புள்ளி செயல்முறையின் பெயர், பதிப்பு மற்றும் உள்ளமைவைப் (configuration)
பதிவுசெய்கிறது. வேறொரு செயல்முறை, வேறொரு உள்ளமைவு அல்லது வேறுபட்ட எண்கணிதம் கொண்ட
பதிப்பு உருவாக்கிய சோதனைப்புள்ளியை `Run.restore` மறுத்து,
`IncompatibleCheckpoint`-ஐ எழுப்புகிறது. எனவே ஓர் ஓட்டம் ஒருபோதும் வேறு எண்களுடன்
மௌனமாகத் தொடரப்படுவதில்லை.

மேலும்: [சோதனைப்புள்ளிகள், பதிவுகள் மற்றும் பின்தளங்கள்](../../checkpoints.md),
[TypeScript இயக்கி](../../typescript.md),
[வடிவங்களின் விவரக்கூற்று](../../spec.md).
