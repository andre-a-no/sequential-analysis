---
description: Jinsi ya kuendesha takwimu za mfuatano kwenye mkondo wa data (Kafka, SQL, pandas, vihisi) na kuendelea baada ya mfumo kuanguka pale pale ulipoachia. Vituo vya ukaguzi vya JSON, uwasilishaji usio na nakala rudufu, muhtasari wa historia kwa ukaguzi wa hesabu, na uendeshaji ule ule ukiendelezwa katika Python au TypeScript, kwa sequential-analysis.
language: sw
---

# Ninaendeshaje takwimu kwenye mkondo wa data na kuendelea baada ya mfumo kuanguka?

> Hii ni tafsiri ya [ukurasa wa Kiingereza](../../guide/streaming.md). Bado haijakaguliwa na mzungumzaji mzawa; pale ambapo hizi mbili zinatofautiana, ukurasa wa Kiingereza ndio wenye mamlaka.

**Jibu fupi.** Funika utaratibu ndani ya `Run`. Kisha:

1. Lilishe vipimo (observations) kwa `run_sync` (au `run_async` kwa
   wazalishaji wa data wanaofanya kazi sambamba).
2. Hifadhi `run.checkpoint()` mara nyingi kadiri unavyopenda. Ni thamani
   ya kawaida ya JSON yenye hali, hali ya nasibu, nafasi za vyanzo na
   muhtasari wa historia (history digest) wa SHA-256.
3. Baada ya mfumo kuanguka (crash), `Run.restore(procedure, checkpoint)`
   inaendelea kwa usahihi kamili, biti kwa biti. Kwa `Delivery("sequence")`,
   vipimo vinavyowasilishwa tena baada ya kuwasha upya vinatupwa kama
   nakala rudufu.
4. Kitekelezaji cha TypeScript kinaweza kuendeleza kituo cha ukaguzi
   (checkpoint) kile kile katika JavaScript. Kinatoa maamuzi na muhtasari
   wa historia ule ule, na namba zinazokubaliana hadi biti za mwisho:
   zinafanana kabisa katika kesi 34 kati ya 108 za ulinganifu
   (conformance), na ndani ya 6·10⁻¹³ kwa uwiano katika nyingine.

## Kuanguka, kuwasha upya, kurudia: matokeo yale yale

Uendeshaji wa ufuatiliaji wa vipimo 300 unakatizwa baada ya 120. Chanzo
kinarudiwa kuanzia kipimo cha 100, kama ambavyo foleni ya ujumbe kwa
kawaida hurudia baada ya kuwasha upya. Uendeshaji uliorejeshwa unatupa
vipimo 20 ambavyo tayari umeviona na unamalizikia pale pale ambapo
uendeshaji usiokatizwa ungemalizikia:

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

Muhtasari wa historia ni mnyororo wa hash juu ya kila kipimo ambacho
uendeshaji umetumia. Uendeshaji miwili yenye muhtasari ule ule imeona
data zile zile kwa mpangilio ule ule. Mkaguzi wa hesabu anaweza
kuukokotoa upya kutoka kwa kumbukumbu ya vipimo, akifuata
[vipimo rasmi (specification)](../../spec.md).

## Vipimo vinatoka wapi

| Chanzo | Kitendakazi |
|---|---|
| orodha au jenereta ya thamani | `sources.from_values` |
| faili ya CSV | `sources.from_csv` |
| DataFrame ya pandas au polars | `adapters.from_dataframe` |
| hoja ya SQL (muunganisho wowote wa DB-API) | `adapters.from_sql` |
| ujumbe wa Kafka, pamoja na offsets zilizothibitishwa (committed) | `adapters.from_kafka`, `adapters.kafka_offsets` |
| vyanzo kadhaa kwa wakati mmoja | `sources.interleave`, `sources.merge_ordered` |
| kumbukumbu ya vipimo iliyorekodiwa | `sources.replay` |

Ingizo kutoka vyanzo tofauti vinahusianishwa na **topolojia**. `KeyJoin`
inaunganisha ugawaji na matokeo kwa mtumiaji, `TimeAlign` inapanga vihisi
viwili kulingana na wakati, na `AsOfJoin` inaambatisha matukio kwenye
pau (bars) zilizoyajua. Tazama [vyanzo vya data](../../adapters.md).

## Utaratibu unapobadilika

Kituo cha ukaguzi kinarekodi jina, toleo na usanidi wa utaratibu.
`Run.restore` inakataa kituo cha ukaguzi kilichotengenezwa na utaratibu
tofauti, usanidi tofauti au toleo lenye hesabu tofauti, na inatoa
`IncompatibleCheckpoint`. Kwa hiyo uendeshaji hauendelezwi kamwe kimya
kimya kwa namba nyingine.

Zaidi: [vituo vya ukaguzi, kumbukumbu na mifumo ya nyuma (backends)](../../checkpoints.md),
[kitekelezaji cha TypeScript](../../typescript.md),
[vipimo rasmi vya fomati](../../spec.md).
