---
description: A/B testlerinde ve klinik araştırmalarda p-değerine her gün bakmanın yanlış pozitifleri neden artırdığı (gözetleme sorunu, peeking problem) ve bunu çözen üç ardışık yöntem ailesi, Python'da sequential-analysis ile.
language: tr
---

# p-değerine neden her gün bakamam?

> Bu sayfa [İngilizce sayfanın](../../guide/peeking.md) çevirisidir. Henüz anadili Türkçe olan biri tarafından gözden geçirilmemiştir; iki metin arasında fark olduğunda İngilizce sayfa esas alınır.

**Kısa yanıt.** Sabit örneklemli bir test, %5'lik yanlış pozitif oranını
ancak sonuca planlanan örneklem büyüklüğünde bir kez bakarsanız vaat
eder. Tekrar tekrar bakar ve p < 0,05 olduğu ilk anda durursanız,
yanılmak için pek çok fırsat yaratırsınız. 20 bakışta yanlış pozitif
oranı yaklaşık %25'e çıkar. Ardışık yöntemler ise tekrar tekrar bakılmak
üzere tasarlanmıştır. Bu yöntemlerle, ne sıklıkla bakarsanız bakın ve ne
zaman durursanız durun, oran %5'te ya da altında kalır.

## Gözetleme sorunu, ölçülmüş hâliyle

Dönüşüm oranı aynı (%10) olan iki kol (bir A/A testi), 2.000 kullanıcı,
200 tekrar. "Gözetleme" (peeking), alışılmış iki oran z-testini her 100
kullanıcıdan sonra çalıştırır ve ilk p < 0,05 değerinde durur. Ardışık
`TwoProportionTest` ise her bir kullanıcıdan sonra kontrol edilir:

```python
import math
import random

from sequential_analysis.procedures import TwoProportionTest

def a_a_test(seed, users=2000):
    """Alternating arms, both converting 10% of the time: any 'effect' is a false positive."""
    rnd = random.Random(seed)
    return [(user % 2, int(rnd.random() < 0.10)) for user in range(users)]

def peeking(data, looks):
    """The z-test for two proportions after every len(data) / looks users; True if it ever rejects."""
    successes, trials, every = [0, 0], [0, 0], len(data) // looks
    for i, (arm, y) in enumerate(data, start=1):
        successes[arm] += y
        trials[arm] += 1
        if i % every == 0:
            pooled = sum(successes) / sum(trials)
            se = math.sqrt(pooled * (1 - pooled) * (1 / trials[0] + 1 / trials[1]))
            if se > 0 and abs(successes[1] / trials[1] - successes[0] / trials[0]) / se > 1.96:
                return True
    return False

def sequential(data):
    """The anytime-valid test, looked at after every user; True if it ever rejects."""
    test = TwoProportionTest(alpha=0.05)
    state = test.initial_state()
    for arm, y in data:
        state, out = test.step(state, {"arm": arm, "y": y})
        if out.decision is not None:
            return True
    return False

runs = [a_a_test(seed) for seed in range(200)]
print(f"z-test, one look at the end:   {sum(peeking(r, 1) for r in runs) / len(runs):.1%} false positives")
print(f"z-test, 20 looks:              {sum(peeking(r, 20) for r in runs) / len(runs):.1%}")
print(f"TwoProportionTest, 2000 looks: {sum(sequential(r) for r in runs) / len(runs):.1%}")
```

```text
z-test, one look at the end:   4.5% false positives
z-test, 20 looks:              28.0%
TwoProportionTest, 2000 looks: 5.0%
```

Tek bakış vaadini tutar. Yirmi bakış hata oranını yaklaşık altı katına
çıkarır. Ardışık test ise 2.000 kullanıcının her birinden sonra
bakılmasına rağmen oranı %5'te tutar. Vaat budur: garantisi **exact**
(kesin) düzeydedir (`TwoProportionTest.guarantee == "exact"`), yani ne
sıklıkla bakarsanız bakın her örneklem büyüklüğünde en fazla %5'lik bir
yanlış pozitif oranı. 200 tekrarda 10 yanlış pozitif, kesin bir %5'in
vereceği sonuçtur.

## Ardışık yöntemlerin üç ailesi

| Aile | Ne zaman bakabilirsiniz | Tipik kullanım | sequential-analysis'te |
|---|---|---|---|
| **Ardışık olasılık oranı testleri** (sequential probability ratio tests) (Wald 1945) | her gözlemden sonra | bir basit hipoteze karşı bir başkası, ortalamada en az gözlemle: kalite kontrol, simülasyon, psikofizik | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Grup ardışık tasarımlar** (group sequential designs) (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | önceden planlanmış birkaç ara analizde | veri izleme komitesi olan klinik araştırmalar | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Her an geçerli çıkarım** (anytime-valid inference): e-değerleri, güven dizileri, karışım SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | her gözlemden sonra, herhangi bir nedenle durarak | çevrim içi A/B testleri, izleme panoları | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**Bedeli nedir?** Daha sık bakmak, planlanan etki düzeyinde daha fazla
veri gerektirir:

* dört analizli bir grup ardışık tasarım, tek bir analize göre %1–20
  daha fazla hasta gerektirir;
* iki oranın her an geçerli bir testi, tek bir analizin gerektirdiği
  kullanıcı sayısının 1,3–1,6 katına ihtiyaç duyar.

Buna karşılık büyük bir etki deneyi erken durdurur ve kimsenin örneklem
büyüklüğünü önceden sabitlemesi gerekmez.

## Sorunun bu olmadığı durumlar

Gözetleme, hataları yalnızca yaptığınız şey gördüğünüze bağlı olduğunda
artırır. Panoya bakıyor ama deneyi her zaman planlanan büyüklüğüne kadar
sürdürüp tek bir kez test ediyorsanız, sabit örneklemli test geçerlidir.
Bu durumda en verimli seçenek de odur.

Sonraki: [bir A/B testini erken durdurmak](ab-testing.md),
[güven dizileri](confidence-sequences.md),
[sözlük](glossary.md).
