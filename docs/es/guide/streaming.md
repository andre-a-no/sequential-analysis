---
description: Cómo ejecutar estadística secuencial sobre un flujo de datos (Kafka, SQL, pandas, sensores) y reanudarla tras una caída exactamente donde se detuvo. Puntos de control (checkpoints) en JSON, entrega sin duplicados, una huella del historial para auditoría y la misma ejecución continuada en Python o TypeScript, con sequential-analysis.
language: es
---

# ¿Cómo ejecuto estadísticas sobre un flujo de datos y las reanudo tras una caída?

> Esta es una traducción de la [página en inglés](../../guide/streaming.md). Aún no ha sido revisada por un hablante nativo; donde ambas difieran, prevalece la página en inglés.

**Respuesta breve.** Envuelva el procedimiento en un `Run`. Después:

1. Aliméntelo con observaciones mediante `run_sync` (o `run_async` para
   productores concurrentes).
2. Guarde `run.checkpoint()` tan a menudo como quiera. Es un valor JSON
   simple con el estado, el estado del generador aleatorio, las
   posiciones en las fuentes y una huella (digest) SHA-256 del
   historial.
3. Tras una caída, `Run.restore(procedure, checkpoint)` continúa de
   forma exacta, bit a bit. Con `Delivery("sequence")`, las
   observaciones que se vuelven a entregar tras el reinicio se descartan
   como duplicados.
4. El ejecutor de TypeScript puede continuar el mismo punto de control
   (checkpoint) en JavaScript. Da las mismas decisiones y la misma
   huella del historial, y números que coinciden hasta los últimos
   bits: idénticos en 34 de los 108 casos de conformidad, y con una
   diferencia relativa de como mucho 6·10⁻¹³ en los demás.

## Caída, reinicio, reproducción: el mismo resultado

Una ejecución de monitoreo sobre 300 lecturas se interrumpe tras 120. La
fuente se reproduce desde la lectura 100, como suele hacer una cola de
mensajes tras un reinicio. La ejecución restaurada descarta las 20
lecturas que ya ha visto y termina exactamente donde terminaría una
ejecución sin interrupciones:

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

La huella del historial (history digest) es una cadena de hashes sobre
todas las observaciones que ha usado la ejecución. Dos ejecuciones con
la misma huella han visto los mismos datos en el mismo orden. Un auditor
puede recalcularla a partir del registro de observaciones, siguiendo la
[especificación](../../spec.md).

## De dónde vienen las observaciones

| Fuente | Función |
|---|---|
| una lista o un generador de valores | `sources.from_values` |
| un archivo CSV | `sources.from_csv` |
| un DataFrame de pandas o polars | `adapters.from_dataframe` |
| una consulta SQL (cualquier conexión DB-API) | `adapters.from_sql` |
| mensajes de Kafka, con offsets confirmados | `adapters.from_kafka`, `adapters.kafka_offsets` |
| varias fuentes a la vez | `sources.interleave`, `sources.merge_ordered` |
| un registro de observaciones grabado | `sources.replay` |

Las entradas de distintas fuentes se relacionan mediante una
**topología**. `KeyJoin` une una asignación y un resultado por usuario,
`TimeAlign` alinea dos sensores en el tiempo y `AsOfJoin` asocia los
eventos a las barras que ya los conocían. Véase
[fuentes de datos](../../adapters.md).

## Cuando el procedimiento cambia

Un punto de control registra el nombre, la versión y la configuración
del procedimiento. `Run.restore` rechaza un punto de control creado por
otro procedimiento, con otra configuración o con una versión de
aritmética diferente, y lanza `IncompatibleCheckpoint`. Así, una
ejecución nunca continúa en silencio con otros números.

Más: [puntos de control, registros y backends](../../checkpoints.md),
[ejecutor de TypeScript](../../typescript.md),
[especificación de los formatos](../../spec.md).
