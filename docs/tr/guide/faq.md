---
description: Ardışık testler ve her an geçerli çıkarım için Python kütüphanesi sequential-analysis hakkında sık sorulan sorular - kurulum, lisans ve ticari kullanım, üretimde A/B testleri, klinik araştırmalar, güç, hız, TypeScript, atıf.
language: tr
---

# Sık sorulan sorular

> Bu sayfa [İngilizce sayfanın](../../guide/faq.md) çevirisidir. Henüz anadili Türkçe olan biri tarafından gözden geçirilmemiştir; iki metin arasında fark olduğunda İngilizce sayfa esas alınır.

## Kütüphane hakkında

### sequential-analysis nedir?

Ardışık istatistiksel çıkarım (sequential inference) için bir Python
kütüphanesidir. Testleri, güven dizileri (confidence sequences) ve
dedektörleri her gözlemden sonra kontrol edilebilir ve hata
garantilerini kaybetmeden istenen her an durdurulabilir. İçerdikleri:

* SPRT'ler;
* grup ardışık tasarımlar (group sequential designs);
* her an geçerli (anytime-valid) A/B testleri;
* değişim noktası dedektörleri;
* Kalman, parçacık ve gizli Markov filtreleri;
* tahminleme ve GARCH.

Hepsi JSON kontrol noktalarıyla (checkpoints) tek bir arayüzün arkasında
çalışır. Novikov Laboratories LLC tarafından geliştirilmektedir.

### Nasıl kurulur? Nelere bağımlıdır?

`pip install sequential-analysis`. Python 3.8 ya da sonrasını gerektirir
(3.14'e kadar test edilmiştir), başka hiçbir şey gerektirmez.
`pip install "sequential-analysis[fast]"`, diziler üzerinde çalışan
prosedürler için numpy ekler. pandas, polars, Kafka istemcileri ve
matplotlib yalnızca bağdaştırıcıları (adapters) ya da çizim
fonksiyonlarını çağırırsanız kullanılır.

### Ticari kullanım için ücretsiz mi?

AGPL-3.0 ve ticari lisans altında çift lisanslıdır. Şu kullanımlar AGPL
altında ücretsizdir:

* araştırma ve öğretim;
* AGPL ya da GPL v3 altındaki açık kaynak projeler;
* bir kuruluş içinde dahili kullanım; başkalarına kopya verilmemesi ve
  kuruluş dışındaki kişilere ağ üzerinden erişim sağlanmaması koşuluyla.

Kapalı kaynaklı bir ürün ya da kaynak kodunu yayımlamadığınız bir ağ
hizmeti ticari lisans gerektirir. Hangi durumun hangisine girdiğini
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)
içindeki tablo belirler. Lisans sorguları: andrei@hobukob.ru.

### Nasıl atıf yapılır?

Depodaki [CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff)
dosyası atfı verir; GitHub'ın *Cite this repository* düğmesi onu BibTeX
ya da APA biçimine dönüştürür. Sürümler Zenodo'da bir DOI ile arşivlenir.
Yöntemler ve bunların doğrulamaları
[makalede](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf)
anlatılmaktadır.

## Kullanım

### Üretimde A/B testleri için kullanabilir miyim?

Evet, istatistiksel motor olarak. Şunlar için kesin testler sunar:

* dönüşüm (`TwoProportionTest`);
* sınırlı metrikler (`BoundedABTest`);
* oranlar (`RateRatioTest`);
* trafik bölünmesi (`SampleRatioMismatch`);
* yanlış keşif oranı (false discovery rate) kontrolüyle çok sayıda metrik
  (`MultipleTests`).

Saf Python'da dönüşüm testi kullanıcı başına yaklaşık 10 mikrosaniye,
bölünme kontrolü 4, oran testi 40 mikrosaniye sürer. Her birinin kontrol
noktası 2–4 kilobayt yer kaplar.
`BoundedABTest` bir ızgara tutar ve 0,1–0,5 ms sürer.

Kütüphane bir deney platformu değildir: atama, olay toplama ve panolar
sizin oluşturmanız ya da bir platformdan almanız gereken şeylerdir. Bkz.
[A/B testleri](ab-testing.md).

### Sonuçlara her gün göz atabilir miyim?

Evet, her an geçerli prosedürlerle: bunlar tam da bunun içindir. Grup
ardışık bir tasarımda yalnızca planlanan analizlere bakın. Klasik sabit
örneklemli bir testte bir kez bakın. Bkz. [gözetleme](peeking.md).

### Her an geçerli bir test, sabit örneklemli bir testten daha mı az güçlüdür?

Sabit örneklemli testin planlandığı etki düzeyinde, evet. Aynı güce
ulaşmak için iki oranın her an geçerli bir testi 1,3–1,6 kat daha fazla
kullanıcıya ihtiyaç duyar. Buna karşılık etki daha büyük olduğunda erken
durabilirsiniz ve önceden sabitlenmiş bir örneklem büyüklüğüne
ihtiyacınız olmaz. Planlanmış birkaç bakışa sahip grup ardışık bir
tasarım, tek bir analize göre yalnızca %1–20 daha maliyetlidir.

### Grup ardışık mı, her an geçerli mi: hangisini kullanmalıyım?

* **Grup ardışık**: analizler az sayıda ve planlıysa, örneğin bir veri
  izleme komitesi ya da bir sürüm döngüsü söz konusuysa, özellikle de
  doğrulayıcı (confirmatory) bir klinik araştırma için.
* **Her an geçerli**: sürekli bakmak istiyorsanız ya da ne zaman
  bakacağınızı veya duracağınızı önceden söyleyemiyorsanız.

### Bayesçi A/B testi yapıyor mu?

A/B testleri frekansçıdır ve hata oranları üzerinde garantiler verir.
Bayesçi bileşenler uygun oldukları yerlerde mevcuttur:

* `ThompsonAllocation`, trafiği her kolun en iyi olmasının sonsal
  (posterior) olasılığına göre yönlendirir ve yayına alma için bir
  beklenen kayıp kuralı içerir;
* `BayesianChangePoint` değişim noktalarını tespit eder;
* tahminleyiciler parametrelerini Bayesçi güncellemeyle öğrenir.

### Klinik araştırmalar için doğrulanmış (validated) mı?

Grup ardışık tasarımları (sınırlar, güç, örneklem büyüklükleri, olay
sayıları), test paketinde rpact ve R'ın survival paketiyle
karşılaştırılarak doğrulanmıştır. Düzenleyici anlamda doğrulanmış bir
yazılım değildir. Onu bir başvuruda kullanan bir sponsor, diğer her araç
gibi onu da doğrular. Bkz. [klinik araştırmalar](clinical-trials.md).

### Metriğim ağır kuyruklu (gelir, gecikme). Ne kullanmalıyım?

* Bir kantil (medyan, 90. yüzdelik) için, hiçbir varsayım gerektirmeyen
  `QuantileTest` ya da `QuantileConfidenceSequence` kullanın.
* Bir ortalama için değerleri önceden sabitlenmiş bir düzeyde üstten
  sınırlayın ve `BoundedABTest` ya da `BettingConfidenceSequence`
  kullanın (exact).
* Alternatif olarak standart sapma için bir üst sınır varsayın ve
  `CatoniConfidenceSequence` kullanın.

İki örneklemli bir medyan testi henüz kütüphanede yoktur.

### Ne kadar hızlı?

En basit prosedürler saf Python'da gözlem başına 1–10 mikrosaniye sürer:
SPRT'ler, CUSUM, grup ardışık testler ve karışım testleri, GARCH. Bir
ızgara ya da tüm örneklemi tutanlar 0,1–10 ms sürer. Bahis ve Catoni
güven dizileri, çekirdek (kernel) testi ve öğrenen tahminleyiciler
bunlara örnektir.
[Hız](../../performance.md) sayfası her prosedürün maliyetini ve kontrol
noktası boyutunu listeler.

### JavaScript'te ya da tarayıcıda çalıştırabilir miyim?

Evet. `ts/` içindeki TypeScript yürütücüsü prosedürleri çalıştırır ve
Python kontrol noktalarını sürdürür. Geçmiş özetleri ve kararlar
aynıdır, sayılar son bitlere kadar uyuşur. Bkz.
[TypeScript yürütücüsü](../../typescript.md).

### Bir çalıştırma çökmeden sağ çıkabilir mi?

Evet. `run.checkpoint()` düz JSON'dur ve `Run.restore` bit bit aynı
biçimde devam eder. Tekrar teslim edilen gözlemler atılır. Bkz.
[veri akışları](streaming.md).

### Belgelerdeki "exact" ve "asymptotic" ne anlama gelir?

Her prosedürün `guarantee` özniteliği vaadini belirtir:

* `exact`: hata oranı, belirtilen varsayımlar altında her örneklem
  büyüklüğünde geçerlidir;
* `asymptotic`: uzun çalıştırmalarda yaklaşık olarak geçerlidir;
* `model`: belirtilen model altında kesindir;
* `approximate`;
* `none`.

Belgeler, uygun olduğu yerde kesin prosedürü önerir. Bkz.
[Hangi yöntem?](../../choosing.md).
