---
description: Cara merencanakan dan menjalankan analisis interim uji klinis di Python, dengan desain sekuensial kelompok (O'Brien–Fleming, Pocock, pembelanjaan alfa Lan–DeMets, batas kesia-siaan), ukuran sampel untuk rata-rata, proporsi, dan kesintasan, diverifikasi terhadap rpact, dengan sequential-analysis.
language: id
---

# Bagaimana merencanakan analisis interim sebuah uji klinis?

> Ini adalah terjemahan dari [halaman bahasa Inggris](../../guide/clinical-trials.md). Terjemahan ini belum ditinjau oleh penutur asli; jika keduanya berbeda, halaman bahasa Inggris yang menjadi acuan.

**Jawaban singkat.** Gunakan desain sekuensial kelompok (group sequential
design). `group_sequential_design(alpha, fractions, spending=...)` dari
`sequential_analysis.group_sequential` menghitung:

* batas efikasi, dengan pembelanjaan alfa (alpha spending) Lan–DeMets
  (tipe O'Brien–Fleming, tipe Pocock, dan lainnya);
* batas kesia-siaan (futility boundary) yang tidak mengikat;
* kuasa dan ukuran sampel harapan;
* ukuran sampel maksimum untuk rata-rata dan proporsi, atau jumlah
  kejadian (event) untuk kesintasan.

Batas dan ukuran sampel tersebut sesuai dengan paket R rpact. Prosedur
uji (`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) kemudian
menjalankan uji klinisnya, pasien demi pasien atau kejadian demi
kejadian. Prosedur ini melakukan setiap analisis interim ketika fraksi
informasinya (information fraction) tercapai.

## Desain: empat analisis, pembelanjaan O'Brien–Fleming

α satu sisi = 0,025, analisis pada 25%, 50%, 75%, dan 100% pasien, kuasa
90%, dengan batas kesia-siaan:

```python
from sequential_analysis.group_sequential import group_sequential_design

design = group_sequential_design(0.025, [0.25, 0.5, 0.75, 1.0], spending="obrien-fleming",
                                 futility="obrien-fleming", power=0.9)
for k, (t, b, f) in enumerate(zip(design.fractions, design.bounds, design.futility), start=1):
    print(f"analysis {k} at {t:.0%}: efficacy if Z >= {b:.3f}, futility if Z <= {f:.3f}")
print("patients for an effect of 0.3 standard deviations:", design.max_sample_size(effect=0.3, sigma=1.0))
print(f"expected share of the patients used: {design.expected_fraction(0.0):.2f} with no effect, "
      f"{design.expected_fraction(design.drift):.2f} with the planned effect")
```

```text
analysis 1 at 25%: efficacy if Z >= 4.333, futility if Z <= -1.403
analysis 2 at 50%: efficacy if Z >= 2.963, futility if Z <= 0.325
analysis 3 at 75%: efficacy if Z >= 2.359, futility if Z <= 1.291
analysis 4 at 100%: efficacy if Z >= 2.014, futility if Z <= 2.014
patients for an effect of 0.3 standard deviations: 127
expected share of the patients used: 0.59 with no effect, 0.73 with the planned effect
```

## Titik akhir biner dan kesintasan

```python
binary = group_sequential_design(0.025, [1 / 3, 2 / 3, 1.0], spending="obrien-fleming")
print("patients, response 10% vs 12%, 80% power:",
      binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8))
print("events for a hazard ratio of 0.7, 80% power:", binary.max_events(hazard_ratio=0.7, power=0.8))
print(f"inflation factor over a single analysis: {binary.inflation_factor(0.8):.3f}")
```

```text
patients, response 10% vs 12%, 80% power: 7780
events for a hazard ratio of 0.7, 80% power: 250
inflation factor over a single analysis: 1.013
```

Dengan pembelanjaan O'Brien–Fleming, tiga analisis memerlukan 1,3% lebih
banyak pasien daripada satu analisis akhir tunggal.

## Menjalankan uji klinis

```python
import random

from sequential_analysis.procedures import GroupSequentialProportions

n_max = binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8)
test = GroupSequentialProportions.from_design(binary, n_max)
state, rnd = test.initial_state(), random.Random(3)
for patient in range(n_max):
    arm = patient % 2                                         # 1 treatment, 0 control
    state, out = test.step(state, {"arm": arm, "y": int(rnd.random() < (0.12 if arm else 0.10))})
    if out.analysis:
        print(f"analysis {out.analysis} after {out.n} patients: Z = {out.z:.2f}, bound {out.bound:.2f}")
    if out.decision:
        print("decision:", out.decision)
        break
```

```text
analysis 1 after 2594 patients: Z = 2.14, bound 3.71
analysis 2 after 5187 patients: Z = 2.64, bound 2.51
decision: reject_h0
```

Uji klinis dihentikan karena efikasi pada analisis kedua, setelah dua
pertiga dari pasien yang direncanakan.

## Ketika analisis tidak berlangsung sesuai rencana

Komite pemantau data jarang bertemu tepat pada 25% informasi:

* `design.at(fractions)` menghitung ulang batas untuk informasi yang
  benar-benar tercapai. Pembelanjaan alfa menjaga taraf keseluruhan.
* `GroupSequentialMonitor` menerima statistik apa pun yang Anda hitung
  sendiri (model Cox, model campuran) sebagai nilai Z beserta
  informasinya pada setiap pertemuan.

## Bagaimana jika Anda ingin melihat setelah setiap pasien?

Desain sekuensial kelompok hanya mengizinkan jumlah kali melihat yang
direncanakan. Untuk memantau setelah setiap pasien atau kejadian, gunakan
prosedur yang valid kapan saja (anytime-valid): `AnytimeLogRankTest`
untuk kesintasan, `TwoProportionTest` untuk tingkat respons,
`TMixtureSPRT` untuk rata-rata. Prosedur ini membutuhkan lebih banyak
pasien pada efek yang direncanakan. Lihat
[tutorial: uji klinis kesintasan](../../tutorials/survival.md).

## Praktik regulasi

Desain sekuensial kelompok dengan pembelanjaan alfa adalah pendekatan
yang mapan dalam uji konfirmatori, sebagaimana dijelaskan dalam pedoman
ICH E9 dan panduan FDA tentang desain adaptif (2019). Pustaka ini
menghitung desainnya dan menyimpan catatan setiap analisis yang dapat
diaudit dan dilanjutkan (checkpoint beserta history digest-nya). Pustaka
ini bukan perangkat lunak tervalidasi dalam pengertian regulasi: sponsor
yang menggunakannya dalam pengajuan harus memvalidasinya seperti alat
lainnya.

Selengkapnya: [tutorial: uji klinis sekuensial kelompok](../../tutorials/group-sequential.md),
yang membandingkan angka-angkanya dengan rpact;
[referensi: desain dan perencanaan](../../reference/design.md).
