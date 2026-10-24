---
description: How to run sequential statistics on a stream (Kafka, SQL, pandas, sensors) and resume after a crash exactly where it stopped. JSON checkpoints, deduplicated delivery, a history digest for audit, and the same run continued in Python or TypeScript, with sequential-analysis.
---

# How do I run statistics on a stream and resume after a crash?

**Short answer.** Wrap the procedure in a `Run`. Then:

1. Feed it observations with `run_sync` (or `run_async` for concurrent
   producers).
2. Save `run.checkpoint()` as often as you like. It is a plain JSON
   value with the state, the random state, the source positions and a
   SHA-256 digest of the history.
3. After a crash, `Run.restore(procedure, checkpoint)` continues
   exactly, bit for bit. With `Delivery("sequence")`, observations
   delivered again after the restart are dropped as duplicates.
4. The TypeScript executor can continue the same checkpoint in
   JavaScript. It gives the same decisions and history digest, and
   numbers that agree to the last bits: identical in 34 of the 108
   conformance cases, within 6·10⁻¹³ relative in the others.

## Crash, restart, replay: the same result

A monitoring run on 300 readings is interrupted after 120. The source
is replayed from reading 100, as a message queue typically replays
after a restart. The restored run drops the 20 readings it has already
seen and ends exactly where an uninterrupted run would:

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

The history digest is a hash chain over every observation the run has
used. Two runs with the same digest have seen the same data in the
same order. An auditor can recompute it from the observation log, following the
[specification](../spec.md).

## Where the observations come from

| Source | Function |
|---|---|
| a list or generator of values | `sources.from_values` |
| a CSV file | `sources.from_csv` |
| a pandas or polars DataFrame | `adapters.from_dataframe` |
| an SQL query (any DB-API connection) | `adapters.from_sql` |
| Kafka messages, with committed offsets | `adapters.from_kafka`, `adapters.kafka_offsets` |
| several sources at once | `sources.interleave`, `sources.merge_ordered` |
| a recorded observation log | `sources.replay` |

Inputs from different sources are related by a **topology**. `KeyJoin`
joins an assignment and an outcome by user, `TimeAlign` aligns two
sensors in time, and `AsOfJoin` attaches events to the bars that knew
about them. See [data sources](../adapters.md).

## When the procedure changes

A checkpoint records the procedure's name, version and configuration.
`Run.restore` refuses a checkpoint made by a different procedure, a
different configuration or a version with different arithmetic, and
raises `IncompatibleCheckpoint`. A run is therefore never silently
continued with other numbers.

More: [checkpoints, logs and backends](../checkpoints.md),
[TypeScript executor](../typescript.md),
[specification of the formats](../spec.md).
