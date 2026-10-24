---
description: Wie man sequentielle Statistik auf einem Datenstrom (Kafka, SQL, pandas, Sensoren) rechnet und nach einem Absturz genau dort fortsetzt, wo sie aufgehört hat. JSON-Checkpoints, deduplizierte Zustellung, ein History-Digest für Audits und derselbe Lauf, fortgesetzt in Python oder TypeScript, mit sequential-analysis.
language: de
---

# Wie rechne ich Statistik auf einem Datenstrom und setze nach einem Absturz fort?

> Dies ist eine Übersetzung der [englischen Seite](../../guide/streaming.md). Sie wurde noch nicht von einer Muttersprachlerin oder einem Muttersprachler geprüft; wo die beiden voneinander abweichen, ist die englische Seite maßgeblich.

**Kurze Antwort.** Verpacken Sie die Prozedur in einen `Run`. Dann:

1. Füttern Sie ihn mit `run_sync` mit Beobachtungen (oder mit `run_async`
   für nebenläufige Produzenten).
2. Speichern Sie `run.checkpoint()` so oft Sie wollen. Das ist ein
   einfacher JSON-Wert mit dem Zustand, dem Zufallszustand, den Positionen
   in den Quellen und einem SHA-256-Digest der Historie.
3. Nach einem Absturz setzt `Run.restore(procedure, checkpoint)` exakt und
   bitgenau fort. Mit `Delivery("sequence")` werden Beobachtungen, die nach
   dem Neustart erneut zugestellt werden, als Duplikate verworfen.
4. Der TypeScript-Executor kann denselben Checkpoint in JavaScript
   fortsetzen. Er liefert dieselben Entscheidungen und denselben
   History-Digest sowie Zahlen, die bis auf die letzten Bits übereinstimmen:
   identisch in 34 der 108 Konformitätsfälle, in den übrigen innerhalb von
   6·10⁻¹³ relativ.

## Absturz, Neustart, Wiedereinspielen: dasselbe Ergebnis

Ein Überwachungslauf über 300 Messwerte wird nach 120 unterbrochen. Die
Quelle wird ab Messwert 100 erneut eingespielt, wie es eine
Message-Queue nach einem Neustart typischerweise tut. Der
wiederhergestellte Lauf verwirft die 20 Messwerte, die er schon gesehen
hat, und endet genau dort, wo ein ununterbrochener Lauf enden würde:

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

Der History-Digest (history digest) ist eine Hash-Kette über alle
Beobachtungen, die der Lauf verwendet hat. Zwei Läufe mit demselben Digest
haben dieselben Daten in derselben Reihenfolge gesehen. Ein Prüfer kann ihn
aus dem Beobachtungsprotokoll nachrechnen, gemäß der
[Spezifikation](../../spec.md).

## Woher die Beobachtungen kommen

| Quelle | Funktion |
|---|---|
| eine Liste oder ein Generator von Werten | `sources.from_values` |
| eine CSV-Datei | `sources.from_csv` |
| ein pandas- oder polars-DataFrame | `adapters.from_dataframe` |
| eine SQL-Abfrage (jede DB-API-Verbindung) | `adapters.from_sql` |
| Kafka-Nachrichten mit committeten Offsets | `adapters.from_kafka`, `adapters.kafka_offsets` |
| mehrere Quellen gleichzeitig | `sources.interleave`, `sources.merge_ordered` |
| ein aufgezeichnetes Beobachtungsprotokoll | `sources.replay` |

Eingaben aus verschiedenen Quellen werden durch eine **Topologie**
verknüpft. `KeyJoin` verbindet eine Zuweisung und ein Ergebnis über den
Nutzer, `TimeAlign` richtet zwei Sensoren zeitlich aus, und `AsOfJoin`
ordnet Ereignisse den Bars zu, die bereits von ihnen wussten. Siehe
[Datenquellen](../../adapters.md).

## Wenn sich die Prozedur ändert

Ein Checkpoint hält Namen, Version und Konfiguration der Prozedur fest.
`Run.restore` weist einen Checkpoint zurück, der von einer anderen
Prozedur, mit einer anderen Konfiguration oder von einer Version mit
anderer Arithmetik erstellt wurde, und löst `IncompatibleCheckpoint` aus.
Ein Lauf wird daher nie stillschweigend mit anderen Zahlen fortgesetzt.

Mehr: [Checkpoints, Protokolle und Backends](../../checkpoints.md),
[TypeScript-Executor](../../typescript.md),
[Spezifikation der Formate](../../spec.md).
