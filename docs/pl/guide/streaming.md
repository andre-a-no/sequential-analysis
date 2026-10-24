---
description: Jak prowadzić sekwencyjne obliczenia statystyczne na strumieniu (Kafka, SQL, pandas, czujniki) i po awarii wznowić je dokładnie tam, gdzie się zatrzymały. Punkty kontrolne JSON, dostarczanie z deduplikacją, skrót historii do audytu i ten sam przebieg kontynuowany w Pythonie lub TypeScript, z sequential-analysis.
language: pl
---

# Jak prowadzić obliczenia statystyczne na strumieniu i wznowić je po awarii?

> To jest tłumaczenie [strony w języku angielskim](../../guide/streaming.md). Nie zostało jeszcze sprawdzone przez rodzimego użytkownika języka; w razie rozbieżności rozstrzyga wersja angielska.

**Krótka odpowiedź.** Opakuj procedurę w `Run`. Następnie:

1. Podawaj mu obserwacje za pomocą `run_sync` (lub `run_async` dla
   współbieżnych producentów).
2. Zapisuj `run.checkpoint()` tak często, jak chcesz. Jest to zwykła wartość
   JSON zawierająca stan, stan generatora losowego, pozycje w źródłach oraz
   skrót SHA-256 historii.
3. Po awarii `Run.restore(procedure, checkpoint)` kontynuuje dokładnie, bit
   w bit. Przy `Delivery("sequence")` obserwacje dostarczone ponownie po
   restarcie są odrzucane jako duplikaty.
4. Wykonawca TypeScript może kontynuować ten sam punkt kontrolny (checkpoint)
   w JavaScripcie. Daje te same decyzje i ten sam skrót historii (history
   digest), a liczby zgadzają się co do ostatnich bitów: są identyczne
   w 34 ze 108 przypadków zgodności, a w pozostałych różnią się względnie
   o nie więcej niż 6·10⁻¹³.

## Awaria, restart, odtworzenie: ten sam wynik

Przebieg monitorujący 300 odczytów zostaje przerwany po 120. Źródło jest
odtwarzane od odczytu 100, tak jak kolejka komunikatów zwykle odtwarza
wiadomości po restarcie. Przywrócony przebieg odrzuca 20 odczytów, które już
widział, i kończy dokładnie tam, gdzie zakończyłby przebieg nieprzerwany:

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

Skrót historii to łańcuch skrótów obejmujący każdą obserwację wykorzystaną
przez przebieg. Dwa przebiegi z tym samym skrótem widziały te same dane
w tej samej kolejności. Audytor może go odtworzyć z dziennika obserwacji,
postępując zgodnie ze [specyfikacją](../../spec.md).

## Skąd pochodzą obserwacje

| Źródło | Funkcja |
|---|---|
| lista lub generator wartości | `sources.from_values` |
| plik CSV | `sources.from_csv` |
| DataFrame pandas lub polars | `adapters.from_dataframe` |
| zapytanie SQL (dowolne połączenie DB-API) | `adapters.from_sql` |
| komunikaty Kafki z zatwierdzonymi offsetami | `adapters.from_kafka`, `adapters.kafka_offsets` |
| kilka źródeł naraz | `sources.interleave`, `sources.merge_ordered` |
| zapisany dziennik obserwacji | `sources.replay` |

Dane wejściowe z różnych źródeł wiąże **topologia**. `KeyJoin` łączy przydział
z wynikiem według użytkownika, `TimeAlign` wyrównuje w czasie dwa czujniki,
a `AsOfJoin` dołącza zdarzenia do świec (bars), w których czasie były już
znane. Zob. [źródła danych](../../adapters.md).

## Gdy procedura się zmienia

Punkt kontrolny zapisuje nazwę, wersję i konfigurację procedury.
`Run.restore` odrzuca punkt kontrolny utworzony przez inną procedurę, przy
innej konfiguracji lub w wersji z inną arytmetyką i zgłasza
`IncompatibleCheckpoint`. Dzięki temu przebieg nigdy nie jest po cichu
kontynuowany z innymi liczbami.

Więcej: [punkty kontrolne, dzienniki i backendy](../../checkpoints.md),
[wykonawca TypeScript](../../typescript.md),
[specyfikacja formatów](../../spec.md).
