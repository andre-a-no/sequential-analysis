---
description: Wald'ın ardışık olasılık oranı testini (SPRT) Python'da sequential-analysis ile çalıştırma. Hata oranları, sabit örneklemli bir teste kıyasla ortalama örneklem büyüklüğü ve kesilmiş alternatifler (2-SPRT, Kiefer–Weiss optimal planları).
language: tr
---

# Wald'ın SPRT'sini Python'da nasıl çalıştırırım?

> Bu sayfa [İngilizce sayfanın](../../guide/sprt.md) çevirisidir. Henüz anadili Türkçe olan biri tarafından gözden geçirilmemiştir; iki metin arasında fark olduğunda İngilizce sayfa esas alınır.

**Kısa yanıt.** `sequential_analysis.procedures` içindeki
`SPRT(family, theta0, theta1, alpha, beta)`, Wald'ın ardışık olasılık
oranı testini (sequential probability ratio test, SPRT) uygular. Test,
iki basit hipotez arasında ortalamada en az gözlemle karar verir. Teste
gözlemleri birer birer verin ve ilk kararda durun. Aşağıdaki örnekte
test, aynı hata oranlarına sahip sabit örneklemli bir testin
gerektirdiği gözlemlerin yaklaşık yarısıyla yetinir: 133 yerine
ortalamada 65–76 parça. Garantili bir azami örneklem büyüklüğüne
ihtiyacınız varsa bunun yerine `TwoSPRT` ya da `kiefer_weiss_plan`
ile elde edilen bir plan kullanın.

## Örnek: kusur oranı %10 mu, %20 mi?

Bir parti, kusur oranı %10 ise kabul, %20 ise reddedilir; her iki hata
oranı da %5'tir:

```python
import random

from sequential_analysis.procedures import SPRT, Bernoulli

test = SPRT(Bernoulli(), theta0=0.10, theta1=0.20, alpha=0.05, beta=0.05)

def inspect_items(rate, seed):
    """Inspect items until the test decides; returns (decision, items inspected)."""
    rnd = random.Random(seed)
    state = test.initial_state()
    while state.decision is None:
        state, out = test.step(state, {"x": int(rnd.random() < rate)})
    return state.decision, state.n

decision, n = inspect_items(0.10, seed=1)
print(f"a good batch: {decision} after {n} items")
```

```text
a good batch: accept_h0 after 108 items
```

Çok sayıda partide ne kadar iyi sonuç veriyor?

```python
for rate in (0.10, 0.20):
    results = [inspect_items(rate, seed) for seed in range(2000)]
    wrong = sum(d == ("reject_h0" if rate == 0.10 else "accept_h0") for d, _ in results) / len(results)
    average = sum(n for _, n in results) / len(results)
    longest = max(n for _, n in results)
    print(f"defect rate {rate:.0%}: wrong decision {wrong:.1%}, average {average:.0f} items, longest {longest}")
```

```text
defect rate 10%: wrong decision 3.5%, average 76 items, longest 370
defect rate 20%: wrong decision 4.3%, average 65 items, longest 315
```

Aynı hata oranlarına sahip sabit örneklemli bir test, her partide
yaklaşık 133 parçayı inceler (normal yaklaşım). SPRT ise ortalamada
%43–51 daha az parça inceler. Ancak örneklem büyüklüğü rastgeledir ve
bir üst sınırı yoktur; birkaç parti ortalamadan çok daha uzun sürer.

Eşikler Wald'ın eşikleridir: log((1 − β)/α) ve log(β/(1 − α)). Bu eşikler,
durma anındaki her örneklem büyüklüğü için gerçek hata oranları α′ ve
β′'nün α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) ve α′ + β′ ≤ α + β koşullarını
sağlamasını garanti eder. Olabilirlik oranı (likelihood ratio) durduğu
anda eşikleri aşar; bu yüzden pratikte oranlar, buradaki gibi, nominal
değerlerin altında kalır. `SPRT.guarantee == "exact"` ifadesinin anlamı
budur. Hata oranlarını sınırlamak yerine kesin olarak hesaplamak için
bir plan üzerinde `operating_characteristic` kullanın (aşağıya bakın).

## Azami bir örneklem büyüklüğüne ihtiyacınız olduğunda

* `TwoSPRT` (Lorden'ın 2-SPRT'si) sabit bir ufukta durur ve en kötü
  durumdaki beklenen örneklem büyüklüğünü neredeyse en aza indirir.
* `sequential_analysis.design` içindeki
  `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`,
  azami örneklem büyüklüğüne sahip optimal planı geriye doğru tümevarımla
  (backward induction) hesaplar. `PlanTest` bu planı yürütür;
  `operating_characteristic` ise planın kesin hata oranlarını ve beklenen
  örneklem büyüklüğünü simülasyon yapmadan verir. Bkz.
  `examples/07_design_kiefer_weiss.py`.
* Her gözlemde bir bakış yerine önceden planlanmış birkaç bakış için
  bir [grup ardışık tasarım](clinical-trials.md) kullanın.

## SPRT'nin yanlış araç olduğu durumlar

* **Hipotezler basit değilse.** "Oran %10'dur" hipotezine karşı "oran
  başka herhangi bir değerdir" hipotezi bileşik (composite) bir
  alternatiftir. Her alternatife karşı her an geçerli (anytime-valid)
  olan bir karışım SPRT (`NormalMixtureSPRT`, `TMixtureSPRT`) ya da bahis
  yoluyla bir test (`BettingMeanTest`) kullanın.
* **Gerçek değer θ₀ ile θ₁ arasındaysa.** Bu durumda SPRT en yavaş
  hâlindedir ve beklenen örneklem büyüklüğü sabit örneklem büyüklüğünü
  aşabilir. Kiefer–Weiss planı tam olarak bu durum için tasarlanmıştır.

Olabilirlik oranı prosedürleri için kullanılabilen aileler: `Gaussian`
(varyansı bilinen), `Bernoulli`, `Poisson`, `Exponential`.
