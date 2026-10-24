---
description: Perbandingan sequential-analysis dengan pustaka Python dan R lain untuk pengujian sekuensial, uji A/B, desain sekuensial kelompok, deteksi perubahan, dan filtering (statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn), serta kapan memakai yang mana.
language: id
---

# Bagaimana perbandingannya dengan pustaka lain?

> Ini adalah terjemahan dari [halaman bahasa Inggris](../../guide/comparison.md). Terjemahan ini belum ditinjau oleh penutur asli; jika keduanya berbeda, halaman bahasa Inggris yang menjadi acuan.

**Jawaban singkat.** Sebagian besar pustaka mencakup satu keluarga metode
dengan baik. sequential-analysis menempatkan keluarga-keluarga utama
inferensi sekuensial (sequential inference) di balik satu antarmuka:

* SPRT dan rencana optimal;
* desain sekuensial kelompok (group sequential design);
* uji yang valid kapan saja (anytime-valid) dan barisan kepercayaan
  (confidence sequence);
* deteksi perubahan;
* filter ruang keadaan (state-space).

Yang ditambahkannya di luar metode itu sendiri:

* setiap prosedur menyatakan jaminannya (`exact`, `asymptotic`, `model`,
  ...);
* setiap proses dapat disimpan sebagai checkpoint dan dilanjutkan secara
  identik hingga tingkat bit;
* format-formatnya dispesifikasikan dan dijalankan oleh implementasi kedua
  dalam TypeScript;
* tidak ada dependensi wajib.

Jika Anda hanya membutuhkan salah satu metode di bawah dan sudah memakai
pustaka yang mengkhususkan diri pada metode tersebut, teruslah memakai
pustaka itu. Tabel berikut menunjukkan di mana setiap alat merupakan
pilihan alami. Deskripsinya mengenai tujuan utama setiap pustaka per
Oktober 2026, dan bukan daftar lengkap fiturnya.

| Kebutuhan | Pilihan alami | Yang ditawarkan sequential-analysis |
|---|---|---|
| uji dengan sampel tetap, regresi, kuasa | scipy.stats, statsmodels | bukan tujuannya |
| desain sekuensial kelompok untuk pengajuan regulasi | rpact, gsDesign (R) | desain yang sama, diverifikasi terhadap rpact dalam rangkaian ujinya; menjalankan uji klinis langkah demi langkah dengan checkpoint |
| barisan kepercayaan, nilai-e | confseq (Python), safestats (R) | barisan kepercayaan untuk rata-rata, kuantil, koefisien regresi, efek dua sampel; e-BH dan e-LOND untuk banyak uji |
| uji A/B sebagai platform dengan UI | GrowthBook, Statsig, Eppo, Optimizely (platform) | mesin untuk disematkan: uji eksak untuk konversi, metrik terbatas dan metrik laju, SRM, FDR atas metrik |
| segmentasi titik perubahan secara luring atas deret yang sudah selesai | ruptures (Python), changepoint (R) | deteksi daring selagi data datang: CUSUM, Shiryaev–Roberts, e-detector, titik perubahan daring Bayesian |
| filter Kalman | filterpy, statsmodels state space | filter Kalman, Kalman robust, partikel, dan HMM, dengan smoothing dan checkpoint |
| GARCH | arch | GARCH(1,1) dan GJR yang di-fit hingga maksimum arch (diverifikasi dalam pengujian), lalu dijalankan secara daring |
| model Markov tersembunyi | hmmlearn | filter daring, Baum–Welch yang sesuai dengan hmmlearn, EM daring |
| peramalan | statsmodels, lainnya | ramalan ETS dan AR yang sesuai dengan statsmodels, dipelajari secara daring, dengan selang konformal (conformal) |

## Kasus ketika alat lain lebih baik

* **Pengajuan kepada regulator.** rpact banyak digunakan untuk tujuan
  itu, dan pengembangnya menyediakan dokumentasi validasi.
  sequential-analysis sesuai dengannya pada desain-desain yang
  dicakupnya, tetapi sponsor tetap harus memvalidasinya.
* **Analisis luring berskala besar atas array.** Pustaka berbasis numpy
  lebih cepat per observasi. sequential-analysis dibangun untuk satu
  observasi pada satu waktu; lihat [Kecepatan](../../performance.md) untuk
  biaya setiap prosedur.
* **Metode yang belum dimilikinya.** Pustaka ini belum memiliki uji
  median dua sampel, proses Hawkes multivariat, maupun model ARIMA dengan
  suku rata-rata bergerak. Lihat [changelog](../../changelog.md) untuk
  apa saja yang ditambahkan.
