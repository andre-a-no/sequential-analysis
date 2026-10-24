---
description: Mengapa memeriksa nilai p setiap hari menggelembungkan positif palsu dalam uji A/B dan uji klinis (masalah peeking), dan tiga keluarga metode sekuensial yang mengatasinya, di Python dengan sequential-analysis.
language: id
---

# Mengapa saya tidak boleh melihat nilai p setiap hari?

> Ini adalah terjemahan dari [halaman bahasa Inggris](../../guide/peeking.md). Terjemahan ini belum ditinjau oleh penutur asli; jika keduanya berbeda, halaman bahasa Inggris yang menjadi acuan.

**Jawaban singkat.** Uji dengan sampel tetap menjanjikan tingkat positif
palsu 5% hanya jika Anda melihat hasilnya sekali, pada ukuran sampel yang
direncanakan. Jika Anda melihat berulang kali dan berhenti pada saat
pertama p < 0,05, Anda memberi diri sendiri banyak kesempatan untuk
tertipu. Dengan 20 kali melihat, tingkat positif palsu naik menjadi
sekitar 25%. Metode sekuensial dirancang untuk dilihat berulang kali.
Dengan metode ini, tingkat tersebut tetap pada atau di bawah 5% seberapa
sering pun Anda melihat dan kapan pun Anda berhenti.

## Masalah mengintip hasil, diukur

Dua lengan dengan tingkat konversi yang sama, 10% (uji A/A), 2.000
pengguna, 200 ulangan. "Mengintip" (peeking) menjalankan uji z dua
proporsi yang biasa setelah setiap 100 pengguna dan berhenti pada p < 0,05
yang pertama. `TwoProportionTest` yang sekuensial diperiksa setelah setiap
pengguna:

```python
import math
import random

from sequential_analysis.procedures import TwoProportionTest

def a_a_test(seed, users=2000):
    """Alternating arms, both converting 10% of the time: any 'effect' is a false positive."""
    rnd = random.Random(seed)
    return [(user % 2, int(rnd.random() < 0.10)) for user in range(users)]

def peeking(data, looks):
    """The z-test for two proportions after every len(data) / looks users; True if it ever rejects."""
    successes, trials, every = [0, 0], [0, 0], len(data) // looks
    for i, (arm, y) in enumerate(data, start=1):
        successes[arm] += y
        trials[arm] += 1
        if i % every == 0:
            pooled = sum(successes) / sum(trials)
            se = math.sqrt(pooled * (1 - pooled) * (1 / trials[0] + 1 / trials[1]))
            if se > 0 and abs(successes[1] / trials[1] - successes[0] / trials[0]) / se > 1.96:
                return True
    return False

def sequential(data):
    """The anytime-valid test, looked at after every user; True if it ever rejects."""
    test = TwoProportionTest(alpha=0.05)
    state = test.initial_state()
    for arm, y in data:
        state, out = test.step(state, {"arm": arm, "y": y})
        if out.decision is not None:
            return True
    return False

runs = [a_a_test(seed) for seed in range(200)]
print(f"z-test, one look at the end:   {sum(peeking(r, 1) for r in runs) / len(runs):.1%} false positives")
print(f"z-test, 20 looks:              {sum(peeking(r, 20) for r in runs) / len(runs):.1%}")
print(f"TwoProportionTest, 2000 looks: {sum(sequential(r) for r in runs) / len(runs):.1%}")
```

```text
z-test, one look at the end:   4.5% false positives
z-test, 20 looks:              28.0%
TwoProportionTest, 2000 looks: 5.0%
```

Satu kali melihat menepati janjinya. Dua puluh kali melihat melipatgandakan
tingkat galat sekitar enam kali. Uji sekuensial, yang dilihat setelah
setiap dari 2.000 pengguna, mempertahankannya pada 5%. Itulah janjinya:
jaminannya **exact** (eksak) (`TwoProportionTest.guarantee == "exact"`),
yaitu tingkat positif palsu paling tinggi 5% pada setiap ukuran sampel,
seberapa sering pun Anda melihat. Dengan 200 ulangan, 10 positif palsu
adalah hasil yang diberikan oleh 5% yang eksak.

## Tiga keluarga metode sekuensial

| Keluarga | Kapan Anda boleh melihat | Penggunaan umum | Di sequential-analysis |
|---|---|---|---|
| **Uji rasio probabilitas sekuensial** (sequential probability ratio test, SPRT) (Wald 1945) | setelah setiap observasi | satu hipotesis sederhana melawan hipotesis lain, dengan rata-rata observasi paling sedikit: pengendalian mutu, simulasi, psikofisika | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Desain sekuensial kelompok** (group sequential design) (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | pada beberapa analisis interim yang direncanakan | uji klinis dengan komite pemantau data | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Inferensi yang valid kapan saja** (anytime-valid inference): nilai-e, barisan kepercayaan, SPRT campuran (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | setelah setiap observasi, berhenti dengan alasan apa pun | uji A/B daring, dasbor pemantauan | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**Berapa biayanya.** Melihat lebih sering membutuhkan lebih banyak data
pada efek yang Anda rencanakan:

* desain sekuensial kelompok dengan empat analisis membutuhkan 1–20% lebih
  banyak pasien dibandingkan satu analisis tunggal;
* uji dua proporsi yang valid kapan saja membutuhkan 1,3–1,6 kali jumlah
  pengguna sebuah analisis tunggal.

Sebagai gantinya, efek yang besar menghentikan eksperimen lebih awal, dan
tidak ada yang perlu menetapkan ukuran sampel di muka.

## Ketika ini bukan masalahnya

Mengintip hanya menggelembungkan galat ketika tindakan Anda bergantung
pada apa yang Anda lihat. Jika Anda melihat dasbor tetapi selalu
menjalankan eksperimen sampai ukuran yang direncanakan dan menguji
sekali, uji dengan sampel tetap tetap valid. Dalam kasus itu, uji
tersebut juga merupakan pilihan yang paling efisien.

Berikutnya: [menghentikan uji A/B lebih awal](ab-testing.md),
[barisan kepercayaan](confidence-sequences.md),
[glosarium](glossary.md).
