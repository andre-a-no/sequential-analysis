---
description: Cara mendeteksi perubahan dalam aliran pembacaan sensor, latensi, atau metrik di Python, dengan CUSUM, Shiryaev–Roberts, e-detector nonparametrik, dan deteksi titik perubahan daring Bayesian. Alarm palsu dikendalikan melalui panjang run rata-rata (ARL), dengan sequential-analysis.
language: id
---

# Bagaimana mendeteksi perubahan dalam aliran data pengukuran?

> Ini adalah terjemahan dari [halaman bahasa Inggris](../../guide/change-detection.md). Terjemahan ini belum ditinjau oleh penutur asli; jika keduanya berbeda, halaman bahasa Inggris yang menjadi acuan.

**Jawaban singkat.** Gunakan detektor titik perubahan daring (online
change-point detector). Detektor ini mengawasi aliran data dan membunyikan
alarm begitu distribusinya tampak telah berubah. Alarm palsunya
dikendalikan oleh **panjang run rata-rata** (average run length, ARL):
jumlah harapan observasi hingga terjadi alarm palsu ketika tidak ada yang
berubah. Di sequential-analysis:

| Yang Anda ketahui sebelum perubahan | Prosedur | Jaminan |
|---|---|---|
| kedua distribusi (mis. normal, rata-rata 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| hanya rata-rata, dan batas-batas nilainya | `MeanEDetector` | exact untuk setiap distribusi semacam itu |
| hanya sebuah kuantil (mis. persentil ke-95 latensi) | `QuantileEDetector` | exact untuk setiap distribusi |
| model dengan parameter tak diketahui, sebelum dan sesudah | `BayesianChangePoint` | di bawah model dan prior-nya |

## Sensor yang rata-ratanya bergeser

Sebuah sensor suhu membaca 70,0 °C dengan derau bersimpangan baku 0,5.
Mulai pembacaan ke-600, rata-ratanya menjadi 70,4. CUSUM dengan ambang
log(1000) ≈ 6,9 memiliki ARL setidaknya 1.000 pembacaan:

```python
import math
import random

from sequential_analysis.procedures import CUSUM, Gaussian

rnd = random.Random(1)
readings = [rnd.gauss(70.0, 0.5) for _ in range(600)] + [rnd.gauss(70.4, 0.5) for _ in range(400)]

detector = CUSUM(Gaussian(sigma=0.5), theta0=70.0, theta1=70.4, threshold=math.log(1000))
state = detector.initial_state()
for t, x in enumerate(readings, start=1):
    state, out = detector.step(state, {"x": x})
    if out.alarm:
        print(f"alarm at reading {t}, {t - 600} readings after the shift")
        break
```

```text
alarm at reading 615, 15 readings after the shift
```

Pergeseran kurang dari satu simpangan baku tidak terlihat oleh mata pada
pembacaan tunggal mana pun. CUSUM mengakumulasi bukti dan menemukannya.

## Ketika pembacaan tidak berdistribusi normal

ARL CUSUM hanya berlaku jika pembacaan mengikuti distribusi yang Anda
berikan kepadanya. Untuk data yang menceng (amplitudo getaran, latensi,
panjang antrean), CUSUM membunyikan alarm palsu jauh lebih sering daripada
yang direncanakan. E-detector membutuhkan jauh lebih sedikit:

* `MeanEDetector` membutuhkan rata-rata sebelum perubahan dan batas-batas
  nilainya.
* `QuantileEDetector` hanya membutuhkan sebuah kuantil sebelum perubahan.

ARL keduanya setidaknya sebesar target untuk **setiap** distribusi dengan
rata-rata atau kuantil tersebut:

```python
from sequential_analysis.procedures import QuantileEDetector

rnd = random.Random(2)
vibration = [rnd.lognormvariate(0.0, 0.8) for _ in range(800)] + [rnd.lognormvariate(0.5, 0.8) for _ in range(400)]
q95 = math.exp(0.8 * 1.6449)          # the 95th percentile before the change
p95 = QuantileEDetector(q0=q95, p=0.95, arl=1000, direction="increase", statistic="cusum")
state = p95.initial_state()
for t, x in enumerate(vibration, start=1):
    state, out = p95.step(state, {"x": x})
    if out.alarm:
        print(f"the 95th percentile rose: alarm at reading {t}, {t - 800} readings after the change")
        break
```

```text
the 95th percentile rose: alarm at reading 887, 87 readings after the change
```

Dalam praktik, kuantil sebelum perubahan diestimasi dari periode yang
tenang. Jaminannya kemudian berlaku secara hampiran, makin baik makin
panjang periode tersebut.

## Memilih ARL

ARL menukar alarm palsu dengan keterlambatan deteksi. Dengan satu
pembacaan per menit, ARL sebesar 1.000 pembacaan berarti satu alarm palsu
kira-kira setiap 17 jam operasi normal, per sensor. Dengan 50 sensor,
itu sekitar 70 per hari. Pilih ARL berdasarkan jumlah alarm palsu per
hari yang sanggup Anda tanggung untuk semua sensor bersama-sama: di sini,
ARL sebesar 1.000.000 pembacaan menurunkan 50 sensor itu menjadi sekitar
satu alarm palsu setiap dua minggu. Biayanya lebih kecil daripada
kelihatannya, karena keterlambatan deteksi hanya tumbuh sebanding dengan
logaritma ARL. Untuk CUSUM, ambangnya naik dari 6,9 menjadi 13,8, dan
keterlambatannya kira-kira menjadi dua kali lipat.

Detektor ini adalah alat pemantauan, bukan sistem keselamatan. Jangan
menggunakannya sebagai pengganti sistem instrumentasi keselamatan (safety
instrumented system) yang tersertifikasi.

Selengkapnya: [tutorial: pemantauan proses dan deteksi perubahan](../../tutorials/monitoring.md),
[rezim dengan model Markov tersembunyi](../../tutorials/regimes.md),
[referensi: deteksi perubahan](../../reference/detection.md).
