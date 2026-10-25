---
description: Paano magpatakbo ng sequential statistics sa isang stream (Kafka, SQL, pandas, mga sensor) at magpatuloy pagkatapos ng crash nang eksakto kung saan ito huminto. Mga JSON checkpoint, deduplicated na delivery, history digest para sa audit, at ang parehong run na itinutuloy sa Python o TypeScript, gamit ang sequential-analysis.
language: tl
---

# Paano magpatakbo ng estadistika sa isang stream at magpatuloy pagkatapos ng crash?

> Ito ay salin ng [pahina sa Ingles](../../guide/streaming.md). Hindi pa ito nasusuri ng isang katutubong tagapagsalita ng wika; kung saan magkaiba ang dalawa, ang pahina sa Ingles ang masusunod.

**Maikling sagot.** Ibalot ang procedure sa isang `Run`. Pagkatapos:

1. Pakainin ito ng mga obserbasyon gamit ang `run_sync` (o `run_async`
   para sa mga sabay-sabay na producer).
2. I-save ang `run.checkpoint()` gaano man kadalas mo gusto. Isa itong
   simpleng JSON value na may state, random state, mga posisyon sa source
   at isang SHA-256 digest ng history.
3. Pagkatapos ng crash, nagpapatuloy nang eksakto ang
   `Run.restore(procedure, checkpoint)`, bit por bit. Sa
   `Delivery("sequence")`, itinatapon bilang duplicate ang mga obserbasyong
   muling naihatid pagkatapos ng restart.
4. Maaaring ituloy ng TypeScript executor ang parehong checkpoint sa
   JavaScript. Nagbibigay ito ng parehong mga desisyon at history digest,
   at mga numerong tumutugma hanggang sa mga huling bit: magkapareho sa 34
   sa 108 conformance case, at nasa loob ng 6·10⁻¹³ relative sa iba pa.

## Crash, restart, replay: parehong resulta

Naantala pagkatapos ng 120 ang isang monitoring run sa 300 reading.
Ini-replay ang source mula sa reading 100, gaya ng karaniwang pag-replay
ng isang message queue pagkatapos ng restart. Itinatapon ng na-restore na
run ang 20 reading na nakita na nito at nagtatapos nang eksakto kung saan
magtatapos ang isang run na hindi naantala:

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

Ang history digest ay isang hash chain sa bawat obserbasyong ginamit ng
run. Ang dalawang run na may parehong digest ay nakakita ng parehong datos
sa parehong pagkakasunod-sunod. Maaari itong kalkulahing muli ng isang
auditor mula sa observation log, ayon sa
[specification](../../spec.md).

## Saan nanggagaling ang mga obserbasyon

| Source | Function |
|---|---|
| isang list o generator ng mga halaga | `sources.from_values` |
| isang CSV file | `sources.from_csv` |
| isang pandas o polars DataFrame | `adapters.from_dataframe` |
| isang SQL query (anumang DB-API connection) | `adapters.from_sql` |
| mga Kafka message, na may committed offsets | `adapters.from_kafka`, `adapters.kafka_offsets` |
| ilang source nang sabay-sabay | `sources.interleave`, `sources.merge_ordered` |
| isang naitalang observation log | `sources.replay` |

Ang mga input mula sa iba't ibang source ay iniuugnay ng isang
**topology**. Pinagdurugtong ng `KeyJoin` ang assignment at outcome ayon sa
user, pinagtutugma ng `TimeAlign` ang dalawang sensor sa oras, at
ikinakabit ng `AsOfJoin` ang mga event sa mga bar na nakaaalam na sa mga
ito. Tingnan ang [mga data source](../../adapters.md).

## Kapag nagbago ang procedure

Itinatala ng checkpoint ang pangalan, bersiyon at configuration ng
procedure. Tinatanggihan ng `Run.restore` ang checkpoint na ginawa ng
ibang procedure, ibang configuration o bersiyong may ibang arithmetic, at
nagre-raise ito ng `IncompatibleCheckpoint`. Kaya hindi kailanman tahimik
na itinutuloy ang isang run gamit ang ibang mga numero.

Higit pa: [mga checkpoint, log at backend](../../checkpoints.md),
[TypeScript executor](../../typescript.md),
[specification ng mga format](../../spec.md).
