---
description: Pertanyaan yang sering diajukan tentang sequential-analysis, pustaka Python untuk pengujian sekuensial dan inferensi yang valid kapan saja - instalasi, lisensi dan penggunaan komersial, uji A/B di produksi, uji klinis, kuasa uji, kecepatan, TypeScript, sitasi.
language: id
---

# Pertanyaan yang sering diajukan

> Ini adalah terjemahan dari [halaman bahasa Inggris](../../guide/faq.md). Terjemahan ini belum ditinjau oleh penutur asli; jika keduanya berbeda, halaman bahasa Inggris yang menjadi acuan.

## Tentang pustaka ini

### Apa itu sequential-analysis?

Pustaka Python untuk inferensi statistik sekuensial (sequential
inference). Uji, barisan kepercayaan (confidence sequence), dan
detektornya boleh diperiksa setelah setiap observasi dan dihentikan kapan
saja, tanpa kehilangan jaminan galatnya. Isinya:

* SPRT;
* desain sekuensial kelompok (group sequential design);
* uji A/B yang valid kapan saja (anytime-valid);
* detektor titik perubahan;
* filter Kalman, filter partikel, dan filter Markov tersembunyi;
* peramalan dan GARCH.

Semuanya berjalan di balik satu antarmuka dengan checkpoint JSON. Pustaka
ini dikembangkan oleh Novikov Laboratories LLC.

### Bagaimana cara memasangnya? Apa dependensinya?

`pip install sequential-analysis`. Pustaka ini membutuhkan Python 3.8 atau
yang lebih baru (diuji hingga 3.14) dan tidak membutuhkan apa pun selain
itu. `pip install "sequential-analysis[fast]"` menambahkan numpy untuk
prosedur yang bekerja pada array. pandas, polars, klien Kafka, dan
matplotlib hanya digunakan jika Anda memanggil adaptor atau fungsi
plotting.

### Apakah gratis untuk penggunaan komersial?

Pustaka ini berlisensi ganda, di bawah AGPL-3.0 dan lisensi komersial.
Penggunaan berikut gratis di bawah AGPL:

* riset dan pengajaran;
* proyek sumber terbuka di bawah AGPL atau GPL v3;
* penggunaan internal dalam suatu organisasi, tanpa memberikan salinan
  kepada pihak lain dan tanpa akses melalui jaringan bagi orang di luar
  organisasi tersebut.

Produk sumber tertutup, atau layanan jaringan yang kode sumbernya tidak
Anda publikasikan, memerlukan lisensi komersial. Tabel di
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)
menentukan kasus-kasusnya. Pertanyaan tentang lisensi: andrei@hobukob.ru.

### Bagaimana cara mengutipnya?

[CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff)
di repositori memberikan sitasinya, dan tombol *Cite this repository* di
GitHub mengubahnya menjadi BibTeX atau APA. Setiap rilis diarsipkan di
Zenodo dengan DOI. Metode-metodenya dan verifikasinya dijelaskan dalam
[makalah](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf).

## Penggunaan

### Bisakah saya menggunakannya untuk uji A/B di produksi?

Ya, sebagai mesin statistiknya. Pustaka ini menyediakan uji eksak untuk:

* konversi (`TwoProportionTest`);
* metrik terbatas (`BoundedABTest`);
* laju (`RateRatioTest`);
* pembagian trafik (`SampleRatioMismatch`);
* banyak metrik dengan pengendalian tingkat penemuan palsu (false
  discovery rate) (`MultipleTests`).

Dalam Python murni, uji konversi memerlukan sekitar 10 mikrodetik per
pengguna, pemeriksaan pembagian trafik 4, dan uji laju 40. Checkpoint
masing-masing berukuran 2–4 kilobyte.
`BoundedABTest` menyimpan sebuah grid dan memerlukan 0,1–0,5 ms.

Pustaka ini bukan platform eksperimen: penugasan, pengumpulan kejadian,
dan dasbor harus Anda bangun sendiri atau ambil dari sebuah platform.
Lihat [uji A/B](ab-testing.md).

### Bolehkah saya mengintip hasilnya setiap hari?

Ya, dengan prosedur yang valid kapan saja: memang untuk itulah prosedur
tersebut dibuat. Dengan desain sekuensial kelompok, lihat hanya pada
analisis yang direncanakan. Dengan uji klasik bersampel tetap, lihat
sekali saja. Lihat [mengintip hasil](peeking.md).

### Apakah uji yang valid kapan saja kurang kuat dibandingkan uji dengan sampel tetap?

Pada efek yang menjadi dasar perencanaan uji dengan sampel tetap, ya.
Untuk mencapai kuasa yang sama, uji dua proporsi yang valid kapan saja
membutuhkan 1,3–1,6 kali jumlah pengguna. Sebagai gantinya, Anda boleh
berhenti lebih awal ketika efeknya lebih besar, dan Anda tidak
memerlukan ukuran sampel yang ditetapkan di muka. Desain sekuensial
kelompok dengan beberapa kali melihat yang direncanakan hanya memerlukan
1–20% lebih banyak daripada satu analisis tunggal.

### Sekuensial kelompok atau valid kapan saja: mana yang sebaiknya saya pakai?

* **Sekuensial kelompok** jika analisisnya sedikit dan direncanakan,
  seperti dengan komite pemantau data atau siklus rilis, dan terutama
  untuk uji klinis konfirmatori.
* **Valid kapan saja** jika Anda ingin melihat terus-menerus, atau tidak
  dapat memastikan di muka kapan Anda akan melihat atau berhenti.

### Apakah pustaka ini mendukung uji A/B Bayesian?

Uji A/B-nya bersifat frekuentis, dengan jaminan atas tingkat galat.
Komponen Bayesian tersedia di tempat yang sesuai:

* `ThompsonAllocation` mengirim trafik berdasarkan peluang posterior
  bahwa setiap lengan adalah yang terbaik, dengan aturan kerugian harapan
  (expected loss) untuk peluncuran;
* `BayesianChangePoint` mendeteksi titik perubahan;
* model peramalan mempelajari parameternya melalui pembaruan Bayesian.

### Apakah pustaka ini tervalidasi untuk uji klinis?

Desain sekuensial kelompoknya (batas, kuasa, ukuran sampel, jumlah
kejadian) diverifikasi terhadap rpact dan paket survival R dalam
rangkaian ujinya. Pustaka ini bukan perangkat lunak tervalidasi dalam
pengertian regulasi. Sponsor yang menggunakannya untuk pengajuan
memvalidasinya seperti alat lainnya. Lihat [uji klinis](clinical-trials.md).

### Metrik saya berekor berat (pendapatan, latensi). Apa yang sebaiknya saya pakai?

* Untuk kuantil (median, persentil ke-90), gunakan `QuantileTest` atau
  `QuantileConfidenceSequence`, yang tidak memerlukan asumsi apa pun.
* Untuk rata-rata, batasi nilainya pada level yang ditetapkan di muka dan
  gunakan `BoundedABTest` atau `BettingConfidenceSequence` (eksak).
* Sebagai alternatif, asumsikan batas atas simpangan baku dan gunakan
  `CatoniConfidenceSequence`.

Uji median dua sampel belum ada di pustaka ini.

### Seberapa cepat?

Prosedur yang paling sederhana memerlukan 1–10 mikrodetik per observasi
dalam Python murni: SPRT, CUSUM, uji sekuensial kelompok dan uji campuran,
GARCH. Prosedur yang menyimpan grid atau seluruh sampel memerlukan
0,1–10 ms. Contohnya adalah barisan kepercayaan berbasis taruhan dan
Catoni, uji kernel, dan model peramalan yang belajar.
[Kecepatan](../../performance.md) mencantumkan biaya dan ukuran checkpoint
setiap prosedur.

### Bisakah saya menjalankannya di JavaScript atau di peramban?

Ya. Eksekutor TypeScript di `ts/` menjalankan prosedur-prosedurnya dan
melanjutkan checkpoint Python. History digest dan keputusannya identik,
dan angkanya cocok hingga bit-bit terakhir. Lihat
[eksekutor TypeScript](../../typescript.md).

### Bisakah sebuah proses bertahan dari crash?

Ya. `run.checkpoint()` adalah JSON biasa, dan `Run.restore` melanjutkan
secara identik hingga tingkat bit. Observasi yang dikirim ulang dibuang.
Lihat [aliran data](streaming.md).

### Apa arti "exact" dan "asymptotic" dalam dokumentasi?

Atribut `guarantee` setiap prosedur menyatakan janjinya:

* `exact`: tingkat galat terjaga pada setiap ukuran sampel di bawah
  asumsi yang dinyatakan;
* `asymptotic`: secara hampiran, pada proses yang panjang;
* `model`: eksak di bawah model yang dinyatakan;
* `approximate`;
* `none`.

Dokumentasi menganjurkan prosedur eksak bila ada yang sesuai. Lihat
[Metode mana?](../../choosing.md).
