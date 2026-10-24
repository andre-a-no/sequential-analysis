---
description: Python'da bir A/B testini yanlış pozitifleri artırmadan erken durdurma. sequential-analysis ile dönüşüm ve sınırlı gelir için her an geçerli testler, örneklem oranı uyumsuzluğu kontrolü ve çok sayıda metrik üzerinde yanlış keşif oranı kontrolü.
language: tr
---

# Bir A/B testini yanlış pozitifleri artırmadan nasıl erken durdururum?

> Bu sayfa [İngilizce sayfanın](../../guide/ab-testing.md) çevirisidir. Henüz anadili Türkçe olan biri tarafından gözden geçirilmemiştir; iki metin arasında fark olduğunda İngilizce sayfa esas alınır.

**Kısa yanıt.** Her an geçerli (anytime-valid) bir test kullanın: bu
testin p-değeri ve güven aralığı, sonuca ne sıklıkla bakarsanız bakın
geçerli kalır; bu yüzden sonuç netleşir netleşmez durabilirsiniz.
sequential-analysis'te:

| Metrik | Prosedür | Garanti |
|---|---|---|
| dönüşüm oranı (0/1) | `TwoProportionTest` | exact |
| herhangi bir sınırlı metrik (üst sınırlı gelir, pay) | `BoundedABTest` | exact |
| maruz kalma birimi başına olay sayısı | `RateRatioTest` | Poisson sayımları için exact |
| oran metriği (oturum başına gelir) | `RatioABTest` | asymptotic |
| deney öncesi ortak değişkenli (covariate) ortalama (CUPED) | `ABTest` | asymptotic |
| trafik amaçlandığı gibi bölünüyor mu? | `SampleRatioMismatch` | exact |
| birlikte değerlendirilen birkaç metrik ya da kol | `MultipleTests` (e-BH) | yanlış keşif oranı, exact |

Her prosedüre kullanıcıları birer birer verin: `state, out = test.step(state, {...})`.
`out.decision` değerine göre istediğiniz zaman harekete geçin.

## Dönüşüm: veriler kesin sonuç verdiğinde durun

Kontrol grubu kullanıcıların %10'unu, deney grubu %12'sini dönüştürüyor.
Teste her kullanıcıdan sonra bakılıyor ve test ilk kararında duruyor:

```python
import random

from sequential_analysis.procedures import TwoProportionTest

def users(n, rates=(0.10, 0.12), seed=1):
    """(arm, converted) per user; arm 1 is the treatment."""
    rnd = random.Random(seed)
    for _ in range(n):
        arm = int(rnd.random() < 0.5)
        yield arm, int(rnd.random() < rates[arm])

test = TwoProportionTest(alpha=0.05)
state = test.initial_state()
for arm, converted in users(60_000):
    state, out = test.step(state, {"arm": arm, "y": converted})
    if out.decision is not None:
        break
print(f"stopped after {out.n} users: conversion {out.rates[0]:.4f} (treatment) vs {out.rates[1]:.4f}, "
      f"anytime-valid p = {out.p_value:.4f}, decision: {out.decision}")
```

```text
stopped after 16469 users: conversion 0.1259 (treatment) vs 0.1068, anytime-valid p = 0.0496, decision: reject_h0
```

Karşılaştırma için: bu artışı %80 güçle (power) yakalamak isteyen sabit
örneklemli bir test, kol başına yaklaşık 3.850, toplamda 7.700 kullanıcı
gerektirir ve sonucu yalnızca bir kez, sonunda okunabilir. Her an geçerli
test bu özgürlüğün bedelini öder: aynı güce ulaşmak için tek bir analizin
gerektirdiği kullanıcı sayısının 1,3–1,6 katına ihtiyaç duyar ve bu
çalıştırma bundan da fazlasını aldı. Buna karşılık önceden sabitlenecek
bir örneklem büyüklüğü yoktur; sonuca her gün bakabilir ve sonuç
netleşir netleşmez durabilirsiniz. Etki planlanandan büyük olduğunda bu
çok daha erken gerçekleşir.

## Gelir: sınırlı bir metrik için kesin bir aralık

`BoundedABTest` yalnızca metriğin sınırlarına ihtiyaç duyar. Geliri,
testten önce seçtiğiniz bir değerde (burada 30) üstten sınırlayın;
ortalamalar arasındaki fark için güven dizisi (confidence sequence) her
dağılım için kesindir:

```python
from sequential_analysis.procedures import BoundedABTest

rnd = random.Random(2)
revenue = BoundedABTest(lower=0.0, upper=30.0, allocation=0.5, input="revenue", grid=300)
state = revenue.initial_state()
for _ in range(20_000):
    arm = int(rnd.random() < 0.5)
    spend = min(rnd.expovariate(1 / (5.0 if arm == 0 else 5.6)), 30.0)   # capped at 30
    state, out = revenue.step(state, {"arm": arm, "revenue": spend})
print(f"after {out.n} users: mean revenue {out.means[0]:.2f} (treatment) vs {out.means[1]:.2f}, "
      f"95% confidence sequence for the difference [{out.lower:.2f}, {out.upper:.2f}]")
```

```text
after 20000 users: mean revenue 5.47 (treatment) vs 4.99, 95% confidence sequence for the difference [-0.30, 1.30]
```

Aralık yalnızca sonuncusunda değil, 20.000 bakışın her birinde aynı anda
geçerlidir. Burada aralık hâlâ 0'ı içeriyor: bu kadar gürültülü bir
metrikte yaklaşık 0,5'lik bir artışı ortaya koymak için 20.000 kullanıcı
yeterli değildir, dolayısıyla deney sürer.

## Önce trafik bölünmesini kontrol edin

Örneklem oranı uyumsuzluğu (sample ratio mismatch), bölünmenin
yapılandırılandan farklı olması demektir; örneğin atamadaki ya da
kayıt tutmadaki bir hatadan kaynaklanabilir. Böyle bir deneyden elde
edilen etki tahminleri güvenilir değildir. 50/50'den 52/48'e bir sapma,
deney sürerken yakalanır:

```python
from sequential_analysis.procedures import SampleRatioMismatch

srm = SampleRatioMismatch(weights=(0.5, 0.5), alpha=0.001)
state = srm.initial_state()
rnd = random.Random(3)
for _ in range(50_000):
    state, out = srm.step(state, {"arm": int(rnd.random() < 0.52)})
    if out.decision is not None:
        break
print(f"mismatch detected after {out.n} users: split {out.proportions[0]:.3f} / {out.proportions[1]:.3f}")
```

```text
mismatch detected after 4927 users: split 0.470 / 0.530
```

## Aynı anda çok sayıda metrik

Birbirinden bağımsız on metriği her biri %5 düzeyinde test etmek, en az
bir yanlış keşif yapma olasılığını yaklaşık %40'a çıkarır.
`MultipleTests`, tüm testlerin e-değerlerini (e-values) e-BH prosedürüyle
birleştirir; böylece yanlış keşif oranı (false discovery rate) her durma
zamanında `alpha` düzeyinde kalır:

```python
from sequential_analysis.procedures import MultipleTests

metrics = MultipleTests({
    "conversion": TwoProportionTest(input="converted"),
    "revenue": BoundedABTest(lower=0.0, upper=30.0, input="revenue", grid=100),
    "traffic split": SampleRatioMismatch((0.5, 0.5)),
}, alpha=0.05)
state = metrics.initial_state()
rnd = random.Random(4)
for _ in range(15_000):
    arm = int(rnd.random() < 0.5)
    converted = int(rnd.random() < (0.10, 0.13)[arm])
    spend = min(rnd.expovariate(1 / 5.0), 30.0)                          # no effect on revenue
    state, out = metrics.step(state, {"arm": arm, "converted": converted, "revenue": spend})
print("discoveries:", out.rejected)
```

```text
discoveries: ('conversion',)
```

## Tuzaklar

* **Analiz ettiğiniz birimi rastgele atayın.** Kullanıcılar rastgele
  atanıyorsa sayfa görüntülemesi başına değil, kullanıcı başına bir kayıt
  verin. Oturum başına metrikler için kullanıcı toplamları üzerinde
  çalışan `RatioABTest` kullanın.
* **Sınırlı bir metriğin üst sınırını testten önce belirleyin.** Sınırı
  veriyi gördükten sonra seçmek garantiyi geçersiz kılar.
* **Asimptotik prosedürler büyük örneklem gerektirir.** `ABTest` ve
  `RatioABTest` için aralık yalnızca uzun çalıştırmalarda yaklaşık olarak
  geçerlidir. Uygun olduklarında kesin prosedürleri tercih edin.
* **Uyarlamalı trafik dağıtımı** (bandit'ler), bölünme sonuçlara bağlı
  olduğunda da geçerli kalan bir test gerektirir:
  `TwoProportionTest(method="universal")` ya da
  `BoundedABTest(propensity_input=...)`. Bkz.
  [eğitim §10](../../tutorials/ab-test.md).

Daha fazlası: [A/B testi eğitimi](../../tutorials/ab-test.md) (CUPED, oran
metrikleri, oranlar, sürenin planlanması) ve
[bir deney programı](../../tutorials/experiment-programme.md)
(çok sayıda deney üzerinde yanlış keşif oranı).
