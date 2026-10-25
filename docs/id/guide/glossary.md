---
description: Glosarium istilah analisis sekuensial dan inferensi yang valid kapan saja - nilai-e, proses-e, barisan kepercayaan, nilai p yang selalu valid, mSPRT, pembelanjaan alfa, fraksi informasi, ARL, SRM, CUPED, e-BH - beserta sinonimnya dan prosedur sequential-analysis yang mengimplementasikan masing-masing.
language: id
---

# Glosarium

> Ini adalah terjemahan dari [halaman bahasa Inggris](../../guide/glossary.md). Terjemahan ini belum ditinjau oleh penutur asli; jika keduanya berbeda, halaman bahasa Inggris yang menjadi acuan.

Istilah yang digunakan dalam analisis sekuensial dan dalam pustaka ini.
Sinonim yang umum dipakai diberikan dalam tanda kurung.

**Analisis sekuensial** (sequential analysis; sequential testing,
sequential inference — pengujian sekuensial, inferensi sekuensial).
Statistika yang jumlah observasinya tidak ditetapkan di muka. Setelah
setiap observasi atau kelompok observasi, prosedur memutuskan apakah akan
berhenti atau berlanjut. Dirintis oleh Wald (1945).

**Mengintip hasil** (peeking; optional stopping, data peeking, continuous
monitoring — penghentian opsional, pemantauan berkelanjutan). Melihat uji
dengan sampel tetap berulang kali dan berhenti ketika hasilnya
signifikan. Hal ini menggelembungkan tingkat positif palsu; lihat
[mengintip hasil](peeking.md).

**SPRT** (sequential probability ratio test, uji rasio probabilitas
sekuensial, uji Wald). Uji ini mengakumulasi log rasio likelihood dari dua
hipotesis sederhana dan berhenti ketika nilainya keluar dari sebuah
selang. `SPRT`; versi terpotongnya `TwoSPRT` (2-SPRT Lorden) dan
`kiefer_weiss_plan`. Lihat [SPRT](sprt.md).

**Desain sekuensial kelompok** (group sequential design; interim
analyses, group sequential trial — analisis interim, uji klinis
sekuensial kelompok). Beberapa analisis yang direncanakan, masing-masing
dengan sebuah batas. Batas-batas itu dipilih sehingga galat tipe I
keseluruhan sama dengan alfa.
`group_sequential_design`. Lihat [uji klinis](clinical-trials.md).

**Fungsi pembelanjaan alfa** (alpha spending function; error spending,
Lan–DeMets — pembelanjaan galat). Fungsi ini menyatakan berapa banyak
galat tipe I yang boleh terpakai hingga setiap fraksi informasi.
Pembelanjaan tipe O'Brien–Fleming membelanjakan sedikit di awal,
pembelanjaan tipe Pocock membelanjakan secara merata.
`spending="obrien-fleming"`, `"pocock"`, ...

**Fraksi informasi** (information fraction). Bagian dari informasi
statistik yang direncanakan (pasien, kejadian) yang telah tercapai pada
suatu analisis.

**Batas kesia-siaan** (futility boundary; non-binding futility — batas
kesia-siaan tidak mengikat). Batas bawah: di bawahnya, penghentian karena
tidak adanya efek direkomendasikan. Batas yang tidak mengikat boleh
diabaikan tanpa menggelembungkan galat tipe I.

**Inferensi yang valid kapan saja** (anytime-valid inference;
always-valid inference, safe anytime-valid inference, SAVI — inferensi
yang selalu valid). Uji dan selang yang jaminannya berlaku pada setiap
ukuran sampel sekaligus, sehingga dapat dipantau terus-menerus dan
dihentikan dengan alasan apa pun.

**Nilai-e** (e-value; e-variable, betting score — variabel-e, skor
taruhan). Statistik nonnegatif yang nilai harapannya di bawah hipotesis
nol paling besar 1. Nilai-e yang besar merupakan bukti yang menentang
hipotesis nol: menolak ketika nilainya melampaui 1/alpha memiliki galat
tipe I paling besar alpha. Keluaran `log_e_value` dari banyak prosedur.

**Proses-e** (e-process; test martingale, test supermartingale, wealth
process — martingale uji, supermartingale uji, proses kekayaan). Barisan
nilai-e yang tetap valid pada waktu berhenti. Maksimum berjalannya
melampaui 1/alpha dengan peluang paling besar alpha di bawah hipotesis
nol (ketaksamaan Ville).

**Nilai p yang selalu valid** (always-valid p-value; anytime-valid
p-value, sequential p-value — nilai p yang valid kapan saja, nilai p
sekuensial). Nilai p yang valid pada waktu berhenti mana pun. Nilai ini
adalah kebalikan dari maksimum berjalan sebuah proses-e. Keluaran
`p_value` dari prosedur-prosedur yang valid kapan saja.

**Barisan kepercayaan** (confidence sequence; anytime-valid confidence
interval, always-valid confidence interval, time-uniform confidence
interval — selang kepercayaan yang valid kapan saja, selang kepercayaan
seragam-waktu). Barisan selang yang memuat nilai sebenarnya pada semua
ukuran sampel secara serentak dengan peluang setidaknya 1 − alpha.
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, serta keluaran
`lower` dan `upper` dari banyak uji. Lihat
[barisan kepercayaan](confidence-sequences.md).

**mSPRT** (mixture SPRT, SPRT campuran, campuran Robbins). SPRT yang
alternatifnya dirata-ratakan atas sebuah prior, sehingga valid kapan saja
terhadap setiap alternatif. `NormalMixtureSPRT` (variansi diketahui),
`TMixtureSPRT` (variansi tidak diketahui).

**Pengujian lewat taruhan** (testing by betting). Membangun proses-e
sebagai kekayaan seorang penjudi yang bertaruh melawan hipotesis nol.
`BettingMeanTest`, `BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal, optimal dalam laju pertumbuhan). Nilai-e
yang dipilih untuk memaksimalkan harapan pertumbuhan log bukti di bawah
hipotesis alternatif. `TwoProportionTest(method="grow")`.

**Inferensi universal** (universal inference). Nilai-e dari rasio
likelihood dengan alternatif yang diestimasi hanya dari data masa lalu.
Nilai ini tetap valid di bawah desain adaptif.
`TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). Mengendalikan tingkat penemuan palsu
(false discovery rate) atas banyak nilai-e, di bawah dependensi apa pun.
`MultipleTests`, `e_bh`.

**e-LOND, FDR daring** (online FDR). Pengendalian tingkat penemuan palsu
atas serangkaian hipotesis yang diputuskan satu per satu. `OnlineFDR`.

**SRM** (sample ratio mismatch, ketidaksesuaian rasio sampel). Pembagian
trafik antar-lengan yang teramati berbeda dari yang dikonfigurasi, sebuah
tanda adanya bug dalam eksperimen. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data; covariate
adjustment, regression adjustment — penyesuaian kovariat, penyesuaian
regresi). Mengurangi variansi efek A/B dengan kovariat yang diukur
sebelum eksperimen. `ABTest(covariate=True)`, `AnytimeLinearModel`.

**Metrik rasio** (ratio metric; delta method — metode delta). Metrik
yang merupakan rasio dari dua jumlah per pengguna, seperti pendapatan per
sesi. `RatioABTest`.

**Deteksi titik perubahan** (change-point detection; change detection,
quickest detection, online anomaly detection — deteksi perubahan, deteksi
tercepat, deteksi anomali daring). Membunyikan alarm segera setelah
distribusi sebuah aliran data berubah. `CUSUM`, `ShiryaevRoberts`,
`MeanEDetector`, `QuantileEDetector`, `BayesianChangePoint`. Lihat
[deteksi perubahan](change-detection.md).

**ARL** (average run length, panjang run rata-rata, ARL₀, waktu rata-rata
hingga alarm palsu). Jumlah harapan observasi hingga terjadi alarm palsu
ketika tidak ada yang berubah. Ukuran pengendalian alarm palsu pada
detektor perubahan.

**E-detector.** Detektor perubahan yang dibangun dari proses-e, satu
dimulai pada setiap kemungkinan waktu perubahan. ARL-nya dijamin di bawah
hipotesis nol nonparametrik. `MeanEDetector`, `QuantileEDetector`.

**Masalah Kiefer–Weiss.** Mencari uji sekuensial dengan ukuran sampel
maksimum yang meminimalkan ukuran sampel harapan terbesar.
`kiefer_weiss_plan`.

**Karakteristik operasi** (operating characteristic). Peluang galat dan
distribusi ukuran sampel sebuah rencana, sebagai fungsi dari parameter
sebenarnya. `operating_characteristic`.

**Checkpoint.** Nilai JSON yang menjadi titik dari mana sebuah proses
berlanjut secara persis. `Run.checkpoint`, `Run.restore`. Lihat
[aliran data](streaming.md).

**History digest** (digest riwayat). Rantai hash SHA-256 atas observasi
yang telah digunakan sebuah proses, disimpan di setiap checkpoint, untuk
keperluan audit.

**Jaminan** (guarantee; `exact`, `asymptotic`, `model`, `approximate`,
`none`). Atribut tempat setiap prosedur dalam pustaka ini menyatakan apa
yang dijanjikannya. Lihat [Metode mana?](../../choosing.md).
