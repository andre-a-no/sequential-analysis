---
description: Güven dizileri (confidence sequences), aynı anda her örneklem büyüklüğünde geçerli kalan güven aralıklarıdır; bu yüzden sürekli izlenebilirler. Sınırlı bir ortalama, bir medyan ya da kantil ve ağır kuyruklu bir ortalama için Python'da sequential-analysis ile nasıl hesaplanırlar.
language: tr
---

# Bakmaya devam ettiğimde de geçerli kalan bir güven aralığını nasıl elde ederim?

> Bu sayfa [İngilizce sayfanın](../../guide/confidence-sequences.md) çevirisidir. Henüz anadili Türkçe olan biri tarafından gözden geçirilmemiştir; iki metin arasında fark olduğunda İngilizce sayfa esas alınır.

**Kısa yanıt.** Bir **güven dizisi** (confidence sequence) kullanın.
Güven dizisi, her gözlemden sonra bir tane olmak üzere, gerçek değeri en
az %95 olasılıkla tüm örneklem büyüklüklerinde aynı anda içeren bir
aralıklar dizisidir. Onu izleyebilir, yeterince daraldığında ya da sıfırı
dışladığında durabilir ve durduğunuz andaki aralığı raporlayabilirsiniz.
Alışılmış bir %95 güven aralığı ise %95'i yalnızca önceden sabitlenmiş tek
bir örneklem büyüklüğünde vaat eder.

| Neyi tahmin ediyorsunuz | Varsayım | Prosedür | Garanti |
|---|---|---|---|
| sınırlı verinin ortalaması (oranlar, puanlar, üst sınırlı gelir) | değerler `[lower, upper]` içinde | `BettingConfidenceSequence` | exact |
| medyan, 90. yüzdelik, herhangi bir kantil (quantile) | yok | `QuantileConfidenceSequence` | exact |
| ağır kuyruklu ya da aykırı değerli verinin ortalaması | standart sapma için bir üst sınır | `CatoniConfidenceSequence` | exact |
| varyansı bilinmeyen normal verinin ortalaması | normallik | `TMixtureSPRT` (`lower`, `upper`) | normallik altında exact |
| herhangi bir verinin ortalaması, uzun çalıştırmalar | sonlu varyans | `AsymptoticConfidenceSequence` | asymptotic |
| iki kol arasındaki fark | bkz. [A/B testleri](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## İzlendiğinde alışılmış aralık başarısız olur

Ortalaması 0,3 olan 0/1 değerli bir değişkenden 500 gözlem çekin ve
30. gözlemden itibaren her gözlemden sonra ders kitabındaki %95 aralığını
hesaplayın: ortalama ± 1,96 standart hata. 100 çalıştırmanın kaçında
aralık bir noktada gerçek ortalamayı ıskalar?

```python
import math
import random

def stream(seed, n=500, p=0.3):
    rnd = random.Random(seed)
    return [float(rnd.random() < p) for _ in range(n)]

def textbook_ever_misses(xs, truth=0.3):
    total = total2 = 0.0
    for n, x in enumerate(xs, start=1):
        total, total2 = total + x, total2 + x * x
        if n >= 30:
            mean = total / n
            se = math.sqrt(max(total2 / n - mean * mean, 1e-12) / n)
            if abs(mean - truth) > 1.96 * se:
                return True
    return False

runs = [stream(seed) for seed in range(100)]
print(f"textbook interval misses the truth at some n in {sum(map(textbook_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
textbook interval misses the truth at some n in 28% of runs
```

Bu aralığın "%95"i yalnızca önceden sabitlenmiş bir örneklem
büyüklüğünde geçerlidir. Aynı veri için bahis yoluyla (by betting)
kurulan güven dizisi (Waudby-Smith and Ramdas 2024) ise yapısı gereği
çalıştırmaların en fazla %5'inde herhangi bir n'de ıskalar:

```python
from sequential_analysis.procedures import BettingConfidenceSequence

def sequence_ever_misses(xs, truth=0.3):
    cs = BettingConfidenceSequence(lower=0.0, upper=1.0, alpha=0.05, grid=100)
    state = cs.initial_state()
    for x in xs:
        state, out = cs.step(state, {"x": x})
        if not out.lower <= truth <= out.upper:
            return True
    return False

print(f"confidence sequence misses the truth at some n in {sum(map(sequence_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
confidence sequence misses the truth at some n in 1% of runs
```

## Hiçbir varsayım olmadan medyan gecikme

Gecikme süreleri çarpık ve ağır kuyrukludur; bu yüzden ortalama ±
standart hata aralığı bu veriler için güvenilir değildir.
`QuantileConfidenceSequence`, eşit değerler dahil, herhangi bir
dağılımın herhangi bir kantilini kapsar:

```python
from sequential_analysis.procedures import QuantileConfidenceSequence

rnd = random.Random(7)
median = QuantileConfidenceSequence(p=0.5, alpha=0.05)
p90 = QuantileConfidenceSequence(p=0.9, alpha=0.05)
m_state, q_state = median.initial_state(), p90.initial_state()
for _ in range(2000):
    latency = rnd.lognormvariate(math.log(120.0), 0.6)   # milliseconds; true median 120
    m_state, m = median.step(m_state, {"x": latency})
    q_state, q = p90.step(q_state, {"x": latency})
print(f"median: {m.estimate:.1f} ms, 95% confidence sequence [{m.lower:.1f}, {m.upper:.1f}]")
print(f"90th percentile: {q.estimate:.1f} ms, [{q.lower:.1f}, {q.upper:.1f}]")
```

```text
median: 117.3 ms, 95% confidence sequence [111.3, 122.6]
90th percentile: 252.7 ms, [237.9, 272.5]
```

Gerçek değerler 120 ms ve 258,8 ms'dir. Her iki aralık da 2.000 örneklem
büyüklüğünün tümünde aynı anda geçerlidir.

## Tuzaklar

* **Sınırlar ve üst sınırlar varsayımın bir parçasıdır.** `lower` ve
  `upper` değerlerini veriyi görmeden seçin. Bunların dışındaki bir değer
  reddedilir.
* **Hiçbir yöntem, keyfi sınırsız verinin ortalaması için kesin kapsama
  vermez.** Böyle veriler için bir kantil kullanın, değerleri üstten
  sınırlayın, standart sapma için bir üst sınır varsayın (Catoni) ya da
  asimptotik bir diziyi kabul edin.
* **Güven dizileri, aynı örneklem büyüklüğündeki tek bir aralıktan
  daha geniştir.** Bu genişlik, her örneklem büyüklüğünde aynı anda
  geçerli olmanın bedelidir.

Daha fazlası: [Hangi yöntem?](../../choosing.md),
[başvuru: her an geçerli ve parametrik olmayan yöntemler](../../reference/anytime.md).
