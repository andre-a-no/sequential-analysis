---
description: Как вести последовательную статистику на потоке данных (Kafka, SQL, pandas, датчики) и после сбоя продолжить ровно с того места, где она остановилась. Контрольные точки в JSON, доставка с устранением дубликатов, дайджест истории для аудита и продолжение того же запуска в Python или TypeScript, с sequential-analysis.
language: ru
---

# Как вести статистику на потоке данных и продолжить после сбоя?

> Это перевод [страницы на английском языке](../../guide/streaming.md). Перевод ещё не проверен носителем языка; если тексты расходятся, верной считается английская страница.

**Коротко.** Оберните процедуру в `Run`. Затем:

1. Подавайте наблюдения через `run_sync` (или `run_async` для параллельных
   источников).
2. Сохраняйте `run.checkpoint()` так часто, как хотите. Это обычное
   значение JSON с состоянием, состоянием генератора случайных чисел,
   позициями в источниках и дайджестом истории SHA-256.
3. После сбоя `Run.restore(procedure, checkpoint)` продолжает работу точно,
   бит в бит. С `Delivery("sequence")` наблюдения, доставленные повторно
   после перезапуска, отбрасываются как дубликаты.
4. Исполнитель на TypeScript может продолжить ту же контрольную точку
   (checkpoint) в JavaScript. Он даёт те же решения и тот же дайджест
   истории, а числа совпадают до последних битов: идентичны в 34 из 108
   тестов соответствия, в остальных — с относительной точностью 6·10⁻¹³.

## Сбой, перезапуск, повторное воспроизведение: тот же результат

Запуск мониторинга на 300 показаниях прерывается после 120-го. Источник
воспроизводится заново с показания 100, как обычно делает очередь сообщений
после перезапуска. Восстановленный запуск отбрасывает 20 уже виденных
показаний и заканчивается ровно там же, где закончился бы непрерывный:

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

Дайджест истории (history digest) — это хеш-цепочка по всем наблюдениям,
которые использовал запуск. Два запуска с одинаковым дайджестом видели одни
и те же данные в одном и том же порядке. Аудитор может пересчитать его по
журналу наблюдений, следуя [спецификации](../../spec.md).

## Откуда берутся наблюдения

| Источник | Функция |
|---|---|
| список или генератор значений | `sources.from_values` |
| файл CSV | `sources.from_csv` |
| DataFrame pandas или polars | `adapters.from_dataframe` |
| SQL-запрос (любое подключение DB-API) | `adapters.from_sql` |
| сообщения Kafka с зафиксированными смещениями | `adapters.from_kafka`, `adapters.kafka_offsets` |
| несколько источников одновременно | `sources.interleave`, `sources.merge_ordered` |
| записанный журнал наблюдений | `sources.replay` |

Входные данные из разных источников связываются **топологией**. `KeyJoin`
соединяет назначение группы и исход по пользователю, `TimeAlign`
выравнивает два датчика по времени, а `AsOfJoin` привязывает события к
барам, которым они уже были известны. См. [источники данных](../../adapters.md).

## Когда процедура меняется

Контрольная точка хранит имя процедуры, её версию и конфигурацию.
`Run.restore` отклоняет контрольную точку, созданную другой процедурой, с
другой конфигурацией или версией с другой арифметикой, и выбрасывает
`IncompatibleCheckpoint`. Поэтому запуск никогда не продолжается молча с
другими числами.

Подробнее: [контрольные точки, журналы и бэкенды](../../checkpoints.md),
[исполнитель на TypeScript](../../typescript.md),
[спецификация форматов](../../spec.md).
