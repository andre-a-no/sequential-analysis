---
description: Bir klinik araştırmanın ara analizlerini Python'da sequential-analysis ile planlama ve yürütme. Grup ardışık tasarımlar (O'Brien–Fleming, Pocock, Lan–DeMets alfa harcama, yararsızlık sınırları), ortalamalar, oranlar ve sağkalım için örneklem büyüklükleri, rpact ile doğrulanmış.
language: tr
---

# Bir klinik araştırmanın ara analizlerini nasıl planlarım?

> Bu sayfa [İngilizce sayfanın](../../guide/clinical-trials.md) çevirisidir. Henüz anadili Türkçe olan biri tarafından gözden geçirilmemiştir; iki metin arasında fark olduğunda İngilizce sayfa esas alınır.

**Kısa yanıt.** Bir grup ardışık tasarım (group sequential design)
kullanın. `sequential_analysis.group_sequential` içindeki
`group_sequential_design(alpha, fractions, spending=...)` şunları hesaplar:

* Lan–DeMets alfa harcama (alpha spending) ile etkililik sınırları
  (O'Brien–Fleming tipi, Pocock tipi ve diğerleri);
* bağlayıcı olmayan yararsızlık sınırları (non-binding futility
  boundaries);
* güç ve beklenen örneklem büyüklüğü;
* ortalamalar ve oranlar için azami örneklem büyüklüğü ya da sağkalım
  için olay sayısı.

Sınırlar ve örneklem büyüklükleri R paketi rpact ile uyuşur. Ardından
test prosedürleri (`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) araştırmayı hasta
hasta ya da olay olay yürütür. Her ara analizi (interim analysis), ilgili
bilgi oranına (information fraction) ulaşıldığında gerçekleştirirler.

## Tasarım: dört analiz, O'Brien–Fleming harcaması

Tek yönlü α = 0,025, hastaların %25'i, %50'si, %75'i ve %100'ünde
analizler, %90 güç ve bir yararsızlık sınırı:

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

## İkili ve sağkalım sonlanım noktaları

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

O'Brien–Fleming harcamasıyla üç analiz, tek bir son analize göre %1,3
daha fazla hasta gerektirir.

## Araştırmanın yürütülmesi

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

Araştırma, planlanan hastaların üçte ikisinden sonra, ikinci analizde
etkililik nedeniyle durdu.

## Analizler planlandığı gibi gerçekleşmediğinde

Veri izleme komiteleri nadiren bilginin tam %25'inde toplanır:

* `design.at(fractions)`, sınırları gerçekte ulaşılan bilgi için yeniden
  hesaplar. Alfa harcama genel düzeyi korur.
* `GroupSequentialMonitor`, kendi hesapladığınız herhangi bir
  istatistiği (bir Cox modeli, bir karma model) her toplantıda bir Z
  değeri ve onun bilgisi olarak alır.

## Peki her hastadan sonra bakmak isterseniz?

Grup ardışık bir tasarım yalnızca planlanan sayıda bakışa izin verir.
Her hastadan ya da olaydan sonra izlemek için her an geçerli
(anytime-valid) bir prosedür kullanın: sağkalım için `AnytimeLogRankTest`,
yanıt oranları için `TwoProportionTest`, bir ortalama için
`TMixtureSPRT`. Bunlar, planlanan etki düzeyinde daha fazla hasta
gerektirir. Bkz. [eğitim: sağkalım araştırması](../../tutorials/survival.md).

## Düzenleyici uygulama

Alfa harcamalı grup ardışık tasarımlar, doğrulayıcı (confirmatory)
araştırmalarda yerleşik yaklaşımdır ve ICH E9 kılavuzunda ve FDA'nın
uyarlamalı tasarımlara ilişkin rehberinde (2019) tarif edilmiştir. Bu
kütüphane tasarımları hesaplar ve her analizin denetlenebilir,
sürdürülebilir bir kaydını (kontrol noktası ve onun geçmiş özeti) tutar.
Düzenleyici anlamda doğrulanmış (validated) bir yazılım değildir: onu
bir başvuruda kullanan bir sponsor, diğer her araç gibi onu da
doğrulamak zorundadır.

Daha fazlası: sayıları rpact ile karşılaştıran
[eğitim: grup ardışık araştırma](../../tutorials/group-sequential.md);
[başvuru: tasarım ve planlama](../../reference/design.md).
