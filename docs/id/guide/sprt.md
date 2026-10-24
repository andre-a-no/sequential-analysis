---
description: Cara menjalankan uji rasio probabilitas sekuensial (SPRT) Wald di Python dengan sequential-analysis. Tingkat galat, ukuran sampel rata-rata dibandingkan uji dengan sampel tetap, dan alternatif terpotong (2-SPRT, rencana optimal Kiefer–Weiss).
language: id
---

# Bagaimana menjalankan SPRT Wald di Python?

> Ini adalah terjemahan dari [halaman bahasa Inggris](../../guide/sprt.md). Terjemahan ini belum ditinjau oleh penutur asli; jika keduanya berbeda, halaman bahasa Inggris yang menjadi acuan.

**Jawaban singkat.** `SPRT(family, theta0, theta1, alpha, beta)` dari
`sequential_analysis.procedures` mengimplementasikan uji rasio probabilitas
sekuensial Wald (sequential probability ratio test, SPRT). Uji ini
memutuskan di antara dua hipotesis sederhana dengan rata-rata jumlah
observasi paling sedikit. Berikan observasi satu demi satu dan berhenti
pada keputusan pertama. Pada contoh di bawah, uji ini membutuhkan sekitar
separuh observasi dari uji dengan sampel tetap yang memiliki tingkat
galat yang sama: rata-rata 65–76 item, bukan 133. Jika Anda membutuhkan
ukuran sampel maksimum yang terjamin, gunakan `TwoSPRT` atau rencana dari
`kiefer_weiss_plan` sebagai gantinya.

## Contoh: apakah tingkat cacatnya 10% atau 20%?

Sebuah lot diterima jika tingkat cacatnya 10% dan ditolak jika 20%,
dengan kedua tingkat galat sebesar 5%:

```python
import random

from sequential_analysis.procedures import SPRT, Bernoulli

test = SPRT(Bernoulli(), theta0=0.10, theta1=0.20, alpha=0.05, beta=0.05)

def inspect_items(rate, seed):
    """Inspect items until the test decides; returns (decision, items inspected)."""
    rnd = random.Random(seed)
    state = test.initial_state()
    while state.decision is None:
        state, out = test.step(state, {"x": int(rnd.random() < rate)})
    return state.decision, state.n

decision, n = inspect_items(0.10, seed=1)
print(f"a good batch: {decision} after {n} items")
```

```text
a good batch: accept_h0 after 108 items
```

Seberapa baik kinerjanya atas banyak lot?

```python
for rate in (0.10, 0.20):
    results = [inspect_items(rate, seed) for seed in range(2000)]
    wrong = sum(d == ("reject_h0" if rate == 0.10 else "accept_h0") for d, _ in results) / len(results)
    average = sum(n for _, n in results) / len(results)
    longest = max(n for _, n in results)
    print(f"defect rate {rate:.0%}: wrong decision {wrong:.1%}, average {average:.0f} items, longest {longest}")
```

```text
defect rate 10%: wrong decision 3.5%, average 76 items, longest 370
defect rate 20%: wrong decision 4.3%, average 65 items, longest 315
```

Uji dengan sampel tetap yang memiliki tingkat galat yang sama memeriksa
sekitar 133 item pada setiap lot (hampiran normal). SPRT memeriksa rata-rata
43–51% lebih sedikit. Namun, ukuran sampelnya acak dan tidak memiliki
batas atas, dan beberapa lot memakan waktu jauh lebih lama daripada
rata-ratanya.

Ambang batasnya adalah ambang Wald: log((1 − β)/α) dan log(β/(1 − α)).
Ambang ini menjamin, untuk ukuran sampel berapa pun saat berhenti, bahwa
tingkat galat aktual α′ dan β′ memenuhi α′ ≤ α/(1 − β), β′ ≤ β/(1 − α),
dan α′ + β′ ≤ α + β. Rasio likelihood (likelihood ratio) melampaui ambang
saat berhenti, sehingga dalam praktik tingkat galatnya berada di bawah
nilai nominal, seperti di sini. Itulah makna `SPRT.guarantee == "exact"`.
Untuk tingkat galat yang dihitung secara eksak alih-alih dibatasi,
gunakan `operating_characteristic` pada sebuah rencana (lihat di bawah).

## Ketika Anda membutuhkan ukuran sampel maksimum

* `TwoSPRT` (2-SPRT Lorden) berhenti paling lambat pada horizon tetap dan
  hampir meminimalkan ukuran sampel harapan pada kasus terburuk.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  di `sequential_analysis.design` menghitung rencana optimal dengan ukuran
  sampel maksimum melalui induksi mundur (backward induction). `PlanTest`
  menjalankannya, dan `operating_characteristic` memberikan tingkat galat
  eksak serta ukuran sampel harapannya tanpa simulasi. Lihat
  `examples/07_design_kiefer_weiss.py`.
* Untuk beberapa kali melihat yang direncanakan alih-alih satu kali per
  observasi, gunakan
  [desain sekuensial kelompok](clinical-trials.md).

## Ketika SPRT bukan alat yang tepat

* **Hipotesisnya tidak sederhana.** "Tingkatnya 10%" melawan "tingkatnya
  berapa saja selain itu" adalah alternatif komposit. Gunakan SPRT
  campuran (`NormalMixtureSPRT`, `TMixtureSPRT`) atau uji lewat taruhan
  (`BettingMeanTest`), yang valid kapan saja (anytime-valid) terhadap
  setiap alternatif.
* **Nilai sebenarnya terletak di antara θ₀ dan θ₁.** Di situlah SPRT
  paling lambat, dan ukuran sampel harapannya dapat melebihi ukuran
  sampel tetap. Rencana Kiefer–Weiss dirancang tepat untuk kasus ini.

Keluarga distribusi yang tersedia untuk prosedur rasio likelihood:
`Gaussian` (variansi diketahui), `Bernoulli`, `Poisson`, `Exponential`.
