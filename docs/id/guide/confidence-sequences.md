---
description: Barisan kepercayaan (confidence sequence) adalah selang kepercayaan yang tetap valid pada semua ukuran sampel sekaligus, sehingga dapat dipantau terus-menerus. Cara menghitungnya di Python untuk rata-rata terbatas, median atau kuantil, dan rata-rata berekor berat, dengan sequential-analysis.
language: id
---

# Bagaimana mendapatkan selang kepercayaan yang tetap valid meskipun saya terus melihatnya?

> Ini adalah terjemahan dari [halaman bahasa Inggris](../../guide/confidence-sequences.md). Terjemahan ini belum ditinjau oleh penutur asli; jika keduanya berbeda, halaman bahasa Inggris yang menjadi acuan.

**Jawaban singkat.** Gunakan **barisan kepercayaan** (confidence
sequence). Ini adalah barisan selang, satu setelah setiap observasi, yang
memuat nilai sebenarnya pada semua ukuran sampel secara serentak dengan
peluang setidaknya 95%. Anda boleh memantaunya, berhenti ketika selangnya
cukup sempit atau tidak lagi memuat nol, dan melaporkan selang pada saat
Anda berhenti. Selang kepercayaan 95% yang biasa hanya menjanjikan 95%
pada satu ukuran sampel yang ditetapkan di muka.

| Yang Anda estimasi | Asumsi | Prosedur | Jaminan |
|---|---|---|---|
| rata-rata data terbatas (proporsi, skor, pendapatan yang dibatasi) | nilai dalam `[lower, upper]` | `BettingConfidenceSequence` | exact |
| median, persentil ke-90, kuantil (quantile) apa pun | tidak ada | `QuantileConfidenceSequence` | exact |
| rata-rata dengan ekor berat atau pencilan | batas atas simpangan baku | `CatoniConfidenceSequence` | exact |
| rata-rata data normal, variansi tidak diketahui | normalitas | `TMixtureSPRT` (`lower`, `upper`) | exact di bawah normalitas |
| rata-rata data apa pun, proses panjang | variansi berhingga | `AsymptoticConfidenceSequence` | asymptotic |
| selisih antara dua lengan | lihat [uji A/B](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## Selang yang biasa gagal ketika dipantau

Ambil 500 observasi dari variabel 0/1 dengan rata-rata 0,3, dan mulai
dari observasi ke-30 hitung selang 95% versi buku teks setelah setiap
observasi: rata-rata ± 1,96 galat baku. Dalam berapa dari 100 proses
selang tersebut pada suatu saat meleset dari rata-rata sebenarnya?

```python
import math
import random

def stream(seed, n=500, p=0.3):
    rnd = random.Random(seed)
    return [float(rnd.random() < p) for _ in range(n)]

def textbook_ever_misses(xs, truth=0.3):
    total = total2 = 0.0
    for n, x in enumerate(xs, start=1):
        total, total2 = total + x, total2 + x * x
        if n >= 30:
            mean = total / n
            se = math.sqrt(max(total2 / n - mean * mean, 1e-12) / n)
            if abs(mean - truth) > 1.96 * se:
                return True
    return False

runs = [stream(seed) for seed in range(100)]
print(f"textbook interval misses the truth at some n in {sum(map(textbook_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
textbook interval misses the truth at some n in 28% of runs
```

"95%"-nya hanya berlaku pada ukuran sampel yang ditetapkan di muka.
Barisan kepercayaan untuk data yang sama, yang dibangun lewat taruhan
(betting) (Waudby-Smith and Ramdas 2024), meleset pada suatu n paling
banyak pada 5% proses, berdasarkan konstruksinya:

```python
from sequential_analysis.procedures import BettingConfidenceSequence

def sequence_ever_misses(xs, truth=0.3):
    cs = BettingConfidenceSequence(lower=0.0, upper=1.0, alpha=0.05, grid=100)
    state = cs.initial_state()
    for x in xs:
        state, out = cs.step(state, {"x": x})
        if not out.lower <= truth <= out.upper:
            return True
    return False

print(f"confidence sequence misses the truth at some n in {sum(map(sequence_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
confidence sequence misses the truth at some n in 1% of runs
```

## Median latensi, tanpa asumsi apa pun

Latensi bersifat menceng dan berekor berat, sehingga selang rata-rata ±
galat baku tidak dapat dipercaya untuknya. `QuantileConfidenceSequence`
mencakup kuantil apa pun dari distribusi apa pun, termasuk ketika ada
nilai kembar (ties):

```python
from sequential_analysis.procedures import QuantileConfidenceSequence

rnd = random.Random(7)
median = QuantileConfidenceSequence(p=0.5, alpha=0.05)
p90 = QuantileConfidenceSequence(p=0.9, alpha=0.05)
m_state, q_state = median.initial_state(), p90.initial_state()
for _ in range(2000):
    latency = rnd.lognormvariate(math.log(120.0), 0.6)   # milliseconds; true median 120
    m_state, m = median.step(m_state, {"x": latency})
    q_state, q = p90.step(q_state, {"x": latency})
print(f"median: {m.estimate:.1f} ms, 95% confidence sequence [{m.lower:.1f}, {m.upper:.1f}]")
print(f"90th percentile: {q.estimate:.1f} ms, [{q.lower:.1f}, {q.upper:.1f}]")
```

```text
median: 117.3 ms, 95% confidence sequence [111.3, 122.6]
90th percentile: 252.7 ms, [237.9, 272.5]
```

Nilai sebenarnya adalah 120 ms dan 258,8 ms. Kedua selang berlaku pada
semua 2.000 ukuran sampel sekaligus.

## Jebakan

* **Batas dan batas atas pemotongan adalah bagian dari asumsi.** Pilih
  `lower` dan `upper` sebelum melihat data. Nilai di luar keduanya akan
  ditolak.
* **Tidak ada metode yang memberikan cakupan eksak untuk rata-rata data
  tak terbatas yang sembarang.** Untuk data seperti itu, gunakan kuantil,
  batasi nilainya, asumsikan batas atas simpangan baku (Catoni), atau
  terima barisan asimtotik.
* **Barisan kepercayaan lebih lebar daripada satu selang tunggal** pada
  ukuran sampel yang sama. Lebar itu adalah harga untuk tetap valid pada
  setiap ukuran sampel sekaligus.

Selengkapnya: [Metode mana?](../../choosing.md),
[referensi: metode valid kapan saja dan nonparametrik](../../reference/anytime.md).
