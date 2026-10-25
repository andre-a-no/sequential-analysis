---
description: sequential-analysis'in ardışık test, A/B testi, grup ardışık tasarımlar, değişim tespiti ve filtreleme için diğer Python ve R kütüphaneleriyle (statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn) karşılaştırması ve hangisinin ne zaman kullanılacağı.
language: tr
---

# Diğer kütüphanelerle karşılaştırıldığında nasıl?

> Bu sayfa [İngilizce sayfanın](../../guide/comparison.md) çevirisidir. Henüz anadili Türkçe olan biri tarafından gözden geçirilmemiştir; iki metin arasında fark olduğunda İngilizce sayfa esas alınır.

**Kısa yanıt.** Çoğu kütüphane tek bir yöntem ailesini iyi kapsar.
sequential-analysis, ardışık çıkarımın (sequential inference) başlıca
ailelerini tek bir arayüzün arkasında toplar:

* SPRT'ler ve optimal planlar;
* grup ardışık tasarımlar (group sequential designs);
* her an geçerli (anytime-valid) testler ve güven dizileri (confidence
  sequences);
* değişim tespiti;
* durum uzayı (state-space) filtreleri.

Yöntemlerin kendisinin ötesinde kattıkları:

* her prosedür kendi garantisini belirtir (`exact`, `asymptotic`, `model`,
  ...);
* her çalıştırma kontrol noktasına kaydedilip bit bit aynı biçimde
  sürdürülebilir;
* biçimler belirlenmiştir (specified) ve TypeScript'teki ikinci bir
  uygulama tarafından yürütülür;
* zorunlu bağımlılık yoktur.

Aşağıdaki yöntemlerden yalnızca birine ihtiyacınız varsa ve o konuda
uzmanlaşmış kütüphaneyi zaten kullanıyorsanız, o kütüphaneyi kullanmaya
devam edin. Tablo, her aracın nerede doğal seçim olduğunu gösterir.
Açıklamalar, Ekim 2026 itibarıyla her kütüphanenin ana amacına
ilişkindir; özelliklerinin eksiksiz bir listesi değildir.

| İhtiyaç | Doğal seçenekler | sequential-analysis'in sundukları |
|---|---|---|
| sabit örneklemli testler, regresyon, güç | scipy.stats, statsmodels | amacı bu değil |
| düzenleyici bir başvuru için grup ardışık tasarımlar | rpact, gsDesign (R) | aynı tasarımlar, test paketinde rpact ile doğrulanmış; araştırmayı kontrol noktalarıyla adım adım yürütür |
| güven dizileri, e-değerleri | confseq (Python), safestats (R) | ortalamalar, kantiller, regresyon katsayıları ve iki örneklem etkileri için güven dizileri; çok sayıda test için e-BH ve e-LOND |
| arayüzlü bir platform olarak A/B testleri | GrowthBook, Statsig, Eppo, Optimizely (platformlar) | gömülecek bir motor: dönüşüm, sınırlı ve oran metrikleri için kesin testler, SRM, metrikler üzerinde FDR |
| tamamlanmış bir serinin çevrim dışı değişim noktası bölütlemesi | ruptures (Python), changepoint (R) | veriler gelirken çevrim içi tespit: CUSUM, Shiryaev–Roberts, e-dedektörler, Bayesçi çevrim içi değişim noktaları |
| Kalman filtreleri | filterpy, statsmodels state space | Kalman, dayanıklı (robust) Kalman, parçacık ve HMM filtreleri; düzgünleştirme (smoothing) ve kontrol noktalarıyla |
| GARCH | arch | arch'ın maksimumuna göre uydurulan GARCH(1,1) ve GJR (testlerde doğrulanmış), ardından çevrim içi çalıştırılır |
| gizli Markov modelleri | hmmlearn | çevrim içi filtre, hmmlearn ile uyuşan Baum–Welch, çevrim içi EM |
| tahminleme | statsmodels, diğerleri | statsmodels ile uyuşan, çevrim içi öğrenilen, konformal (conformal) aralıklı ETS ve AR tahminleri |

## Başka bir aracın daha iyi olduğu durumlar

* **Bir düzenleyici kuruma başvuru.** rpact bu amaçla yaygın olarak
  kullanılır ve geliştiricileri doğrulama belgeleri sunar.
  sequential-analysis kapsadığı tasarımlarda onunla uyuşur, ancak bir
  sponsorun yine de onu doğrulaması gerekir.
* **Diziler üzerinde büyük çevrim dışı analizler.** numpy tabanlı
  kütüphaneler gözlem başına daha hızlıdır. sequential-analysis bir
  seferde tek bir gözlem için tasarlanmıştır; her prosedürün maliyeti
  için bkz. [Hız](../../performance.md).
* **Sahip olmadığı yöntemler.** Henüz iki örneklemli bir medyan testi,
  çok değişkenli Hawkes süreçleri ve hareketli ortalama terimli ARIMA
  modelleri yoktur. Neyin eklendiğini görmek için
  [değişiklik günlüğüne](../../changelog.md) bakın.
