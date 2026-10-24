---
description: Cara menjalankan statistik sekuensial pada aliran data (Kafka, SQL, pandas, sensor) dan melanjutkannya setelah crash tepat di titik berhentinya. Checkpoint JSON, pengiriman tanpa duplikat, history digest untuk audit, dan proses yang sama dilanjutkan di Python atau TypeScript, dengan sequential-analysis.
language: id
---

# Bagaimana menjalankan statistik pada aliran data dan melanjutkannya setelah crash?

> Ini adalah terjemahan dari [halaman bahasa Inggris](../../guide/streaming.md). Terjemahan ini belum ditinjau oleh penutur asli; jika keduanya berbeda, halaman bahasa Inggris yang menjadi acuan.

**Jawaban singkat.** Bungkus prosedur dalam sebuah `Run`. Lalu:

1. Berikan observasi kepadanya dengan `run_sync` (atau `run_async` untuk
   produsen yang berjalan bersamaan).
2. Simpan `run.checkpoint()` sesering yang Anda mau. Ini adalah nilai JSON
   biasa yang berisi state, state pembangkit acak, posisi sumber, dan
   digest SHA-256 dari riwayatnya.
3. Setelah crash, `Run.restore(procedure, checkpoint)` melanjutkan secara
   persis, identik hingga tingkat bit. Dengan `Delivery("sequence")`,
   observasi yang dikirim ulang setelah restart dibuang sebagai duplikat.
4. Eksekutor TypeScript dapat melanjutkan checkpoint yang sama di
   JavaScript. Eksekutor ini memberikan keputusan dan history digest yang
   sama, serta angka yang cocok hingga bit-bit terakhir: identik pada 34
   dari 108 kasus kesesuaian (conformance), dan dalam batas relatif
   6·10⁻¹³ pada kasus lainnya.

## Crash, restart, putar ulang: hasil yang sama

Sebuah proses pemantauan atas 300 pembacaan terhenti setelah 120
pembacaan. Sumber diputar ulang mulai pembacaan ke-100, seperti yang
lazim dilakukan antrean pesan setelah restart. Proses yang dipulihkan
membuang 20 pembacaan yang sudah pernah dilihatnya dan berakhir tepat di
tempat proses tanpa gangguan akan berakhir:

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

History digest adalah rantai hash atas setiap observasi yang telah
digunakan proses tersebut. Dua proses dengan digest yang sama telah
melihat data yang sama dengan urutan yang sama. Seorang auditor dapat
menghitungnya ulang dari log observasi, mengikuti
[spesifikasinya](../../spec.md).

## Dari mana observasi berasal

| Sumber | Fungsi |
|---|---|
| daftar atau generator nilai | `sources.from_values` |
| berkas CSV | `sources.from_csv` |
| DataFrame pandas atau polars | `adapters.from_dataframe` |
| kueri SQL (koneksi DB-API apa pun) | `adapters.from_sql` |
| pesan Kafka, dengan offset yang di-commit | `adapters.from_kafka`, `adapters.kafka_offsets` |
| beberapa sumber sekaligus | `sources.interleave`, `sources.merge_ordered` |
| log observasi yang terekam | `sources.replay` |

Masukan dari sumber yang berbeda dihubungkan oleh sebuah **topologi**.
`KeyJoin` menggabungkan penugasan dan hasil berdasarkan pengguna,
`TimeAlign` menyelaraskan dua sensor menurut waktu, dan `AsOfJoin`
melekatkan kejadian ke bar yang sudah mengetahuinya. Lihat
[sumber data](../../adapters.md).

## Ketika prosedurnya berubah

Sebuah checkpoint mencatat nama, versi, dan konfigurasi prosedur.
`Run.restore` menolak checkpoint yang dibuat oleh prosedur yang berbeda,
konfigurasi yang berbeda, atau versi dengan aritmetika yang berbeda, dan
memunculkan `IncompatibleCheckpoint`. Dengan demikian, sebuah proses
tidak pernah diam-diam dilanjutkan dengan angka yang lain.

Selengkapnya: [checkpoint, log, dan backend](../../checkpoints.md),
[eksekutor TypeScript](../../typescript.md),
[spesifikasi format](../../spec.md).
