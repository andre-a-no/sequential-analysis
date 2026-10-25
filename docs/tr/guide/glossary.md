---
description: Ardışık analiz ve her an geçerli çıkarım terimleri sözlüğü - e-değeri, e-süreç, güven dizisi, her zaman geçerli p-değeri, mSPRT, alfa harcama, bilgi oranı, ARL, SRM, CUPED, e-BH - eş anlamlılarıyla ve her birini uygulayan sequential-analysis prosedürleriyle.
language: tr
---

# Sözlük

> Bu sayfa [İngilizce sayfanın](../../guide/glossary.md) çevirisidir. Henüz anadili Türkçe olan biri tarafından gözden geçirilmemiştir; iki metin arasında fark olduğunda İngilizce sayfa esas alınır.

Ardışık analizde ve bu kütüphanede kullanılan terimler. Yaygın olarak
kullanılan eş anlamlılar parantez içinde verilmiştir.

**Ardışık analiz** (sequential analysis; sequential testing, sequential
inference — ardışık test, ardışık çıkarım). Gözlem sayısının önceden
sabitlenmediği istatistik. Her gözlemden ya da gözlem grubundan sonra
prosedür durmaya ya da devam etmeye karar verir. Wald (1945) tarafından
kurulmuştur.

**Gözetleme** (peeking; optional stopping, data peeking, continuous
monitoring — isteğe bağlı durdurma, sürekli izleme). Sabit örneklemli
bir teste tekrar tekrar bakmak ve anlamlı çıktığında durmak. Yanlış
pozitif oranını artırır; bkz. [gözetleme](peeking.md).

**SPRT** (sequential probability ratio test, ardışık olasılık oranı
testi, Wald testi). İki basit hipotezin log olabilirlik oranını
biriktirir ve bu oran bir aralığın dışına çıktığında durur. `SPRT`;
kesilmiş (truncated) sürümleri `TwoSPRT` (Lorden'ın 2-SPRT'si) ve
`kiefer_weiss_plan`. Bkz. [SPRT](sprt.md).

**Grup ardışık tasarım** (group sequential design; interim analyses,
group sequential trial — ara analizler, grup ardışık araştırma).
Her biri bir sınıra sahip, önceden planlanmış birkaç analiz. Sınırlar,
genel I. tip hata alfa olacak biçimde seçilir.
`group_sequential_design`. Bkz. [klinik araştırmalar](clinical-trials.md).

**Alfa harcama fonksiyonu** (alpha spending function; error spending,
Lan–DeMets — hata harcama). I. tip hatanın her bilgi oranına kadar ne
kadarının kullanılabileceğini belirtir. O'Brien–Fleming tipi harcama
başlangıçta az harcar, Pocock tipi harcama eşit dağıtır.
`spending="obrien-fleming"`, `"pocock"`, ...

**Bilgi oranı** (information fraction). Bir analizde ulaşılan, planlanan
istatistiksel bilginin (hastalar, olaylar) payı.

**Yararsızlık sınırı** (futility boundary; non-binding futility —
bağlayıcı olmayan yararsızlık). Bir alt sınır: bunun altında, etki
yokluğu nedeniyle durmak önerilir. Bağlayıcı olmayan bir sınır, I. tip
hatayı artırmadan göz ardı edilebilir.

**Her an geçerli çıkarım** (anytime-valid inference; always-valid
inference, safe anytime-valid inference, SAVI — her zaman geçerli
çıkarım). Garantileri her örneklem büyüklüğünde aynı anda geçerli olan
testler ve aralıklar; böylece sürekli izlenebilir ve herhangi bir
nedenle durdurulabilirler.

**E-değeri** (e-value; e-variable, betting score — e-değişkeni, bahis
skoru). Sıfır hipotezi altında beklenen değeri en fazla 1 olan, negatif
olmayan bir istatistik. Büyük bir e-değeri sıfır hipotezine karşı
kanıttır: 1/alpha'yı aştığında reddetmek, en fazla alpha'lık bir I. tip
hataya sahiptir. Pek çok prosedürün `log_e_value` çıktısı.

**E-süreç** (e-process; test martingale, test supermartingale, wealth
process — test martingali, test süpermartingali, servet süreci). Durma
zamanlarında geçerli kalan bir e-değerleri dizisi. Sıfır hipotezi
altında, birikimli maksimumu en fazla alpha olasılıkla 1/alpha'yı aşar
(Ville eşitsizliği).

**Her zaman geçerli p-değeri** (always-valid p-value; anytime-valid
p-value, sequential p-value — her an geçerli p-değeri, ardışık
p-değeri). Herhangi bir durma zamanında geçerli olan bir p-değeri. Bir
e-sürecin birikimli maksimumunun tersidir. Her an geçerli prosedürlerin
`p_value` çıktısı.

**Güven dizisi** (confidence sequence; anytime-valid confidence
interval, always-valid confidence interval, time-uniform confidence
interval — her an geçerli güven aralığı, zamana göre düzgün güven
aralığı). Gerçek değeri en az 1 − alpha olasılıkla tüm örneklem
büyüklüklerinde aynı anda içeren bir aralıklar dizisi.
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence` ve pek çok
testin `lower` ve `upper` çıktıları. Bkz.
[güven dizileri](confidence-sequences.md).

**mSPRT** (mixture SPRT, karışım SPRT, Robbins karışımı). Alternatifi bir
önsel dağılım (prior) üzerinden ortalanan ve bu sayede her alternatife
karşı her an geçerli olan bir SPRT. `NormalMixtureSPRT` (varyansı
bilinen), `TMixtureSPRT` (varyansı bilinmeyen).

**Bahis yoluyla test** (testing by betting). E-süreçleri, sıfır
hipotezine karşı bahis oynayan bir kumarbazın serveti olarak kurmak.
`BettingMeanTest`, `BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal, büyüme hızı açısından optimal).
Alternatif altında kanıtın beklenen log büyümesini en üst düzeye
çıkaracak biçimde seçilen bir e-değeri.
`TwoProportionTest(method="grow")`.

**Evrensel çıkarım** (universal inference). Alternatifin yalnızca geçmiş
verilerden tahmin edildiği bir olabilirlik oranından elde edilen bir
e-değeri. Uyarlamalı tasarımlar altında geçerli kalır.
`TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). Herhangi bir bağımlılık altında, çok
sayıda e-değeri üzerinde yanlış keşif oranını (false discovery rate)
kontrol eder. `MultipleTests`, `e_bh`.

**e-LOND, çevrim içi FDR** (online FDR). Birer birer karara bağlanan bir
hipotezler dizisi üzerinde yanlış keşif oranı kontrolü. `OnlineFDR`.

**SRM** (sample ratio mismatch, örneklem oranı uyumsuzluğu). Trafiğin
kollar arasında gözlenen bölünmesi yapılandırılandan farklıdır; bu,
deneydeki bir hatanın işaretidir. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data; covariate
adjustment, regression adjustment — ortak değişken düzeltmesi,
regresyon düzeltmesi). Deneyden önce ölçülen bir ortak değişkenle
(covariate) bir A/B etkisinin varyansını azaltır.
`ABTest(covariate=True)`, `AnytimeLinearModel`.

**Oran metriği** (ratio metric; delta method — delta yöntemi).
Oturum başına gelir gibi, kullanıcı başına iki toplamın oranı olan bir
metrik. `RatioABTest`.

**Değişim noktası tespiti** (change-point detection; change detection,
quickest detection, online anomaly detection — değişim tespiti, en
hızlı tespit, çevrim içi anomali tespiti). Bir akışın dağılımı
değiştikten kısa süre sonra alarm vermek. `CUSUM`, `ShiryaevRoberts`,
`MeanEDetector`, `QuantileEDetector`, `BayesianChangePoint`. Bkz.
[değişim tespiti](change-detection.md).

**ARL** (average run length, ortalama çalışma uzunluğu, ARL₀, yanlış
alarma kadar ortalama süre). Hiçbir şey değişmemişken yanlış bir alarma
kadar beklenen gözlem sayısı. Değişim dedektörlerinin yanlış alarm
kontrolü.

**E-dedektör** (e-detector). Her olası değişim anında bir tane başlatılan
e-süreçlerden kurulan bir değişim dedektörü. ARL'si parametrik olmayan
bir sıfır hipotezi altında garanti edilir. `MeanEDetector`,
`QuantileEDetector`.

**Kiefer–Weiss problemi.** Azami bir örneklem büyüklüğüne sahip olup en
büyük beklenen örneklem büyüklüğünü en aza indiren ardışık testi bulmak.
`kiefer_weiss_plan`.

**İşletim karakteristiği** (operating characteristic). Bir planın hata
olasılıkları ve örneklem büyüklüğünün dağılımı, gerçek parametrenin
fonksiyonları olarak. `operating_characteristic`.

**Kontrol noktası** (checkpoint). Bir çalıştırmanın tam olarak kaldığı
yerden devam ettiği bir JSON değeri. `Run.checkpoint`, `Run.restore`.
Bkz. [veri akışları](streaming.md).

**Geçmiş özeti** (history digest). Bir çalıştırmanın kullandığı
gözlemler üzerinde kurulan, her kontrol noktasında tutulan, denetim
amaçlı bir SHA-256 özet zinciri.

**Garanti** (guarantee; `exact`, `asymptotic`, `model`, `approximate`,
`none`). Bu kütüphanedeki her prosedürün neyi vaat ettiğini belirttiği
öznitelik. Bkz. [Hangi yöntem?](../../choosing.md).
