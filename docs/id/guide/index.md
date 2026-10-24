---
description: Panduan pengguna sequential-analysis, pustaka Python untuk pengujian sekuensial dan inferensi yang valid kapan saja (anytime-valid). Setiap halaman menjawab satu pertanyaan secara langsung, dengan kode yang dapat dijalankan beserta keluarannya.
language: id
---

# Panduan pengguna

> Ini adalah terjemahan dari [halaman bahasa Inggris](../../guide/index.md). Terjemahan ini belum ditinjau oleh penutur asli; jika keduanya berbeda, halaman bahasa Inggris yang menjadi acuan.

Panduan ini disusun berdasarkan pertanyaan yang biasa diajukan orang.
Setiap halaman dibuka dengan jawaban langsung, lalu menyajikan program
singkat yang dapat dijalankan apa adanya, keluarannya, jaminan yang
mendasari jawaban tersebut, serta kasus-kasus ketika metode itu tidak
berlaku. [Tutorial](../../tutorials/ab-test.md) membahas setiap topik
lebih mendalam.

## Pustaka ini dalam satu paragraf

**sequential-analysis** adalah pustaka Python untuk inferensi statistik
pada data yang datang satu observasi demi satu observasi. Uji, selang
kepercayaan, dan detektornya boleh dilihat setelah setiap observasi dan
dihentikan kapan saja, dan tingkat galatnya tetap terjaga. Cakupannya:

* SPRT Wald (sequential probability ratio test) dan rencana sekuensial
  optimal;
* desain sekuensial kelompok (group sequential design) untuk uji klinis
  (fungsi pembelanjaan O'Brien–Fleming dan Pocock, batas kesia-siaan);
* uji A/B yang valid kapan saja (anytime-valid) dengan nilai-e (e-value)
  dan barisan kepercayaan (confidence sequence);
* deteksi titik perubahan (change-point detection);
* filter Kalman, filter partikel, dan filter Markov tersembunyi;
* peramalan (forecasting) dan volatilitas GARCH.

Setiap proses dapat disimpan sebagai checkpoint JSON lalu dilanjutkan
secara identik hingga tingkat bit di Python, atau diteruskan di eksekutor
TypeScript-nya dengan keputusan yang sama.

| | |
|---|---|
| Instalasi | `pip install sequential-analysis` |
| Impor | `import sequential_analysis` |
| Python | 3.8 hingga 3.14, tanpa dependensi wajib (numpy opsional) |
| Lisensi | AGPL-3.0, atau lisensi komersial dari Novikov Laboratories LLC |
| Kode sumber | <https://github.com/andre-a-no/sequential-analysis> |
| Dokumentasi | <https://andre-a-no.github.io/sequential-analysis/> |

## Pertanyaan

**Konsep**

* [Mengapa saya tidak boleh melihat nilai p setiap hari?](peeking.md)
  Masalah mengintip hasil (peeking) dan tiga keluarga metode sekuensial.
* [Glosarium](glossary.md): nilai-e, barisan kepercayaan, pembelanjaan
  alfa, ARL, dan istilah lainnya, beserta sinonimnya.

**Tugas**

* [Bagaimana menghentikan uji A/B lebih awal tanpa menggelembungkan positif palsu?](ab-testing.md)
* [Bagaimana mendapatkan selang kepercayaan yang tetap valid meskipun saya terus melihatnya?](confidence-sequences.md)
* [Bagaimana menjalankan SPRT Wald di Python?](sprt.md)
* [Bagaimana merencanakan analisis interim sebuah uji klinis?](clinical-trials.md)
* [Bagaimana mendeteksi perubahan dalam aliran data pengukuran?](change-detection.md)
* [Bagaimana menjalankan statistik pada aliran data dan melanjutkannya setelah crash?](streaming.md)

**Memilih**

* [Metode mana untuk pertanyaan saya?](../../choosing.md): tabel lengkapnya.
* [Bagaimana perbandingannya dengan pustaka lain?](comparison.md)
* [Pertanyaan yang sering diajukan](faq.md)

## Cara membaca jaminan

Setiap prosedur memiliki atribut `guarantee`. Panduan ini mengutipnya
pada setiap jawaban:

* **exact (eksak):** tingkat galat terjaga pada setiap ukuran sampel di
  bawah asumsi yang dinyatakan.
* **asymptotic (asimtotik):** terjaga secara hampiran, dan makin baik
  untuk sampel yang makin besar.
* **model:** peluangnya eksak di bawah model yang dinyatakan, tetapi
  tidak ada klaim apa pun di luar model itu.
* **approximate (hampiran):** sebuah hampiran, bahkan di bawah model.
* **none (tidak ada):** prosedur hanya mentransformasi data dan tidak
  membuat klaim apa pun.
