---
description: Cara menghentikan uji A/B lebih awal tanpa menggelembungkan positif palsu di Python. Uji yang valid kapan saja untuk konversi dan pendapatan terbatas, pemeriksaan ketidaksesuaian rasio sampel, dan pengendalian tingkat penemuan palsu atas banyak metrik, dengan sequential-analysis.
language: id
---

# Bagaimana menghentikan uji A/B lebih awal tanpa menggelembungkan positif palsu?

> Ini adalah terjemahan dari [halaman bahasa Inggris](../../guide/ab-testing.md). Terjemahan ini belum ditinjau oleh penutur asli; jika keduanya berbeda, halaman bahasa Inggris yang menjadi acuan.

**Jawaban singkat.** Gunakan uji yang valid kapan saja (anytime-valid):
nilai p dan selang kepercayaannya tetap valid seberapa sering pun Anda
melihatnya, sehingga Anda boleh berhenti begitu hasilnya jelas. Di
sequential-analysis:

| Metrik | Prosedur | Jaminan |
|---|---|---|
| tingkat konversi (0/1) | `TwoProportionTest` | exact |
| metrik terbatas apa pun (pendapatan yang dibatasi, proporsi) | `BoundedABTest` | exact |
| kejadian per unit paparan | `RateRatioTest` | exact untuk cacahan Poisson |
| metrik rasio (pendapatan per sesi) | `RatioABTest` | asymptotic |
| rata-rata dengan kovariat pra-eksperimen (CUPED) | `ABTest` | asymptotic |
| apakah pembagian trafik sesuai rencana? | `SampleRatioMismatch` | exact |
| beberapa metrik atau lengan sekaligus | `MultipleTests` (e-BH) | tingkat penemuan palsu, exact |

Berikan data ke setiap prosedur satu pengguna demi satu pengguna: `state, out = test.step(state, {...})`.
Ambil tindakan berdasarkan `out.decision` kapan pun Anda mau.

## Konversi: berhenti ketika data sudah meyakinkan

Kelompok kontrol mengonversi 10% pengguna, kelompok perlakuan 12%. Uji
dilihat setelah setiap pengguna dan berhenti pada keputusan pertamanya:

```python
import random

from sequential_analysis.procedures import TwoProportionTest

def users(n, rates=(0.10, 0.12), seed=1):
    """(arm, converted) per user; arm 1 is the treatment."""
    rnd = random.Random(seed)
    for _ in range(n):
        arm = int(rnd.random() < 0.5)
        yield arm, int(rnd.random() < rates[arm])

test = TwoProportionTest(alpha=0.05)
state = test.initial_state()
for arm, converted in users(60_000):
    state, out = test.step(state, {"arm": arm, "y": converted})
    if out.decision is not None:
        break
print(f"stopped after {out.n} users: conversion {out.rates[0]:.4f} (treatment) vs {out.rates[1]:.4f}, "
      f"anytime-valid p = {out.p_value:.4f}, decision: {out.decision}")
```

```text
stopped after 16469 users: conversion 0.1259 (treatment) vs 0.1068, anytime-valid p = 0.0496, decision: reject_h0
```

Sebagai pembanding, uji dengan sampel tetap yang memiliki kuasa (power)
80% untuk kenaikan ini membutuhkan sekitar 3.850 pengguna per lengan,
total 7.700, dan hanya boleh dibaca sekali, di akhir. Uji yang valid
kapan saja membayar kebebasannya: untuk mencapai kuasa yang sama, uji ini
membutuhkan 1,3–1,6 kali jumlah pengguna sebuah analisis tunggal, dan
proses ini bahkan memakan lebih dari itu. Sebagai gantinya, tidak ada
ukuran sampel yang harus ditetapkan di muka, dan Anda boleh melihat
hasilnya setiap hari dan berhenti begitu hasilnya jelas. Ketika efeknya
lebih besar dari yang direncanakan, hal itu terjadi jauh lebih awal.

## Pendapatan: selang eksak untuk metrik terbatas

`BoundedABTest` hanya membutuhkan batas-batas metrik. Batasi pendapatan
pada nilai yang Anda pilih sebelum uji (di sini 30), maka barisan
kepercayaan (confidence sequence) untuk selisih rata-rata bersifat eksak
untuk distribusi apa pun:

```python
from sequential_analysis.procedures import BoundedABTest

rnd = random.Random(2)
revenue = BoundedABTest(lower=0.0, upper=30.0, allocation=0.5, input="revenue", grid=300)
state = revenue.initial_state()
for _ in range(20_000):
    arm = int(rnd.random() < 0.5)
    spend = min(rnd.expovariate(1 / (5.0 if arm == 0 else 5.6)), 30.0)   # capped at 30
    state, out = revenue.step(state, {"arm": arm, "revenue": spend})
print(f"after {out.n} users: mean revenue {out.means[0]:.2f} (treatment) vs {out.means[1]:.2f}, "
      f"95% confidence sequence for the difference [{out.lower:.2f}, {out.upper:.2f}]")
```

```text
after 20000 users: mean revenue 5.47 (treatment) vs 4.99, 95% confidence sequence for the difference [-0.30, 1.30]
```

Selang ini berlaku pada setiap dari 20.000 kali melihat sekaligus, bukan
hanya pada yang terakhir. Di sini selang tersebut masih memuat 0: 20.000
pengguna belum cukup untuk memastikan kenaikan sekitar 0,5 pada metrik
yang seberisik ini, sehingga eksperimen berlanjut.

## Periksa pembagian trafik terlebih dahulu

Ketidaksesuaian rasio sampel (sample ratio mismatch) berarti pembagian
trafik berbeda dari yang dikonfigurasi, misalnya karena bug dalam
penugasan atau dalam pencatatan log. Estimasi efek dari eksperimen
seperti itu tidak dapat dipercaya. Pergeseran dari 50/50 ke 52/48
terdeteksi selagi eksperimen berjalan:

```python
from sequential_analysis.procedures import SampleRatioMismatch

srm = SampleRatioMismatch(weights=(0.5, 0.5), alpha=0.001)
state = srm.initial_state()
rnd = random.Random(3)
for _ in range(50_000):
    state, out = srm.step(state, {"arm": int(rnd.random() < 0.52)})
    if out.decision is not None:
        break
print(f"mismatch detected after {out.n} users: split {out.proportions[0]:.3f} / {out.proportions[1]:.3f}")
```

```text
mismatch detected after 4927 users: split 0.470 / 0.530
```

## Banyak metrik sekaligus

Menguji sepuluh metrik yang saling independen masing-masing pada taraf
5% memberikan peluang sekitar 40% untuk setidaknya satu penemuan palsu.
`MultipleTests` menggabungkan nilai-e (e-value) dari semua uji dengan
prosedur e-BH, sehingga tingkat penemuan palsu (false discovery rate)
tetap pada `alpha` pada waktu berhenti mana pun:

```python
from sequential_analysis.procedures import MultipleTests

metrics = MultipleTests({
    "conversion": TwoProportionTest(input="converted"),
    "revenue": BoundedABTest(lower=0.0, upper=30.0, input="revenue", grid=100),
    "traffic split": SampleRatioMismatch((0.5, 0.5)),
}, alpha=0.05)
state = metrics.initial_state()
rnd = random.Random(4)
for _ in range(15_000):
    arm = int(rnd.random() < 0.5)
    converted = int(rnd.random() < (0.10, 0.13)[arm])
    spend = min(rnd.expovariate(1 / 5.0), 30.0)                          # no effect on revenue
    state, out = metrics.step(state, {"arm": arm, "converted": converted, "revenue": spend})
print("discoveries:", out.rejected)
```

```text
discoveries: ('conversion',)
```

## Jebakan

* **Acak unit yang Anda analisis.** Jika yang diacak adalah pengguna,
  berikan satu catatan per pengguna, bukan per tampilan halaman. Untuk
  metrik per sesi, gunakan `RatioABTest`, yang bekerja pada total per
  pengguna.
* **Tetapkan batas atas metrik terbatas sebelum uji.** Memilihnya setelah
  melihat data membatalkan jaminannya.
* **Prosedur asimtotik membutuhkan sampel besar.** Untuk `ABTest` dan
  `RatioABTest`, selangnya hanya valid secara hampiran pada proses yang
  panjang. Utamakan prosedur eksak bila sesuai.
* **Alokasi trafik adaptif** (bandit) membutuhkan uji yang tetap valid
  ketika pembagian trafik bergantung pada hasil:
  `TwoProportionTest(method="universal")` atau
  `BoundedABTest(propensity_input=...)`. Lihat
  [tutorial §10](../../tutorials/ab-test.md).

Selengkapnya: [tutorial uji A/B](../../tutorials/ab-test.md) (CUPED,
metrik rasio, laju, perencanaan durasi) dan
[program eksperimen](../../tutorials/experiment-programme.md)
(tingkat penemuan palsu atas banyak eksperimen).
