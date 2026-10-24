---
description: Come eseguire statistiche sequenziali su un flusso (Kafka, SQL, pandas, sensori) e riprendere dopo un crash esattamente da dove si erano fermate. Checkpoint JSON, consegna deduplicata, digest della storia per l'audit e la stessa esecuzione proseguita in Python o in TypeScript, con sequential-analysis.
language: it
---

# Come fare statistica su un flusso e riprendere dopo un crash?

> Questa è una traduzione della [pagina in inglese](../../guide/streaming.md). Non è ancora stata rivista da un madrelingua; in caso di differenze, fa fede la pagina in inglese.

**Risposta breve.** Avvolgete la procedura in un `Run`. Poi:

1. Fornitele le osservazioni con `run_sync` (o `run_async` per
   produttori concorrenti).
2. Salvate `run.checkpoint()` tutte le volte che volete. È un semplice
   valore JSON con lo stato, lo stato del generatore casuale, le
   posizioni nelle sorgenti e un digest SHA-256 della storia (history
   digest).
3. Dopo un crash, `Run.restore(procedure, checkpoint)` riprende
   esattamente, bit per bit. Con `Delivery("sequence")`, le osservazioni
   consegnate di nuovo dopo il riavvio vengono scartate come duplicati.
4. L'esecutore TypeScript può proseguire lo stesso checkpoint in
   JavaScript. Fornisce le stesse decisioni e lo stesso digest della
   storia, e numeri che concordano fino agli ultimi bit: identici in 34
   dei 108 casi di conformità, entro 6·10⁻¹³ in termini relativi negli
   altri.

## Crash, riavvio, replay: lo stesso risultato

Un'esecuzione di monitoraggio su 300 letture viene interrotta dopo 120.
La sorgente viene riprodotta dalla lettura 100, come fa tipicamente una
coda di messaggi dopo un riavvio. L'esecuzione ripristinata scarta le
20 letture che ha già visto e termina esattamente dove terminerebbe
un'esecuzione senza interruzioni:

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

Il digest della storia è una catena di hash su ogni osservazione usata
dall'esecuzione. Due esecuzioni con lo stesso digest hanno visto gli
stessi dati nello stesso ordine. Un revisore può ricalcolarlo dal log
delle osservazioni, seguendo la [specifica](../../spec.md).

## Da dove arrivano le osservazioni

| Sorgente | Funzione |
|---|---|
| una lista o un generatore di valori | `sources.from_values` |
| un file CSV | `sources.from_csv` |
| un DataFrame pandas o polars | `adapters.from_dataframe` |
| una query SQL (qualsiasi connessione DB-API) | `adapters.from_sql` |
| messaggi Kafka, con offset confermati (committed) | `adapters.from_kafka`, `adapters.kafka_offsets` |
| più sorgenti insieme | `sources.interleave`, `sources.merge_ordered` |
| un log di osservazioni registrato | `sources.replay` |

Gli input provenienti da sorgenti diverse sono messi in relazione da una
**topologia**. `KeyJoin` unisce un'assegnazione e un esito per utente,
`TimeAlign` allinea due sensori nel tempo, e `AsOfJoin` associa gli
eventi alle barre che ne erano a conoscenza. Vedete
[sorgenti di dati](../../adapters.md).

## Quando la procedura cambia

Un checkpoint registra il nome, la versione e la configurazione della
procedura. `Run.restore` rifiuta un checkpoint creato da una procedura
diversa, da una configurazione diversa o da una versione con
un'aritmetica diversa, e solleva `IncompatibleCheckpoint`. Un'esecuzione
non viene quindi mai proseguita silenziosamente con numeri diversi.

Per approfondire: [checkpoint, log e backend](../../checkpoints.md),
[esecutore TypeScript](../../typescript.md),
[specifica dei formati](../../spec.md).
