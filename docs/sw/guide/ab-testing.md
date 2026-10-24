---
description: Jinsi ya kusimamisha jaribio la A/B mapema bila kuongeza chanya za uongo katika Python. Majaribio halali wakati wowote kwa kiwango cha ubadilishaji na mapato yenye mipaka, ukaguzi wa kutolingana kwa uwiano wa sampuli (SRM) na udhibiti wa kiwango cha ugunduzi wa uongo kwa vipimo vingi, kwa sequential-analysis.
language: sw
---

# Ninasimamishaje jaribio la A/B mapema bila kuongeza chanya za uongo?

> Hii ni tafsiri ya [ukurasa wa Kiingereza](../../guide/ab-testing.md). Bado haijakaguliwa na mzungumzaji mzawa; pale ambapo hizi mbili zinatofautiana, ukurasa wa Kiingereza ndio wenye mamlaka.

**Jibu fupi.** Tumia jaribio lililo halali wakati wowote (anytime-valid):
thamani-p (p-value) yake na kipindi cha uhakika (confidence interval)
hubaki halali hata ukitazama mara ngapi, kwa hiyo unaweza kusimama mara
tu matokeo yanapokuwa wazi. Katika sequential-analysis:

| Kipimo | Utaratibu | Hakikisho |
|---|---|---|
| kiwango cha ubadilishaji (conversion rate) (0/1) | `TwoProportionTest` | exact |
| kipimo chochote chenye mipaka (mapato yaliyowekewa kikomo, sehemu) | `BoundedABTest` | exact |
| matukio kwa kila kipimo cha mfichuo | `RateRatioTest` | exact kwa hesabu za Poisson |
| kipimo cha uwiano (mapato kwa kila kipindi cha matumizi) | `RatioABTest` | asymptotic |
| wastani pamoja na kigezo shirikishi cha kabla ya jaribio (CUPED) | `ABTest` | asymptotic |
| je, trafiki imegawanywa kama ilivyokusudiwa? | `SampleRatioMismatch` | exact |
| vipimo au makundi kadhaa kwa pamoja | `MultipleTests` (e-BH) | kiwango cha ugunduzi wa uongo (false discovery rate), exact |

Lisha kila utaratibu mtumiaji mmoja kwa wakati: `state, out = test.step(state, {...})`.
Chukua hatua kulingana na `out.decision` wakati wowote unapotaka.

## Ubadilishaji: simama data zinapokuwa thabiti

Kundi la udhibiti linabadilisha 10% ya watumiaji, kundi la tiba 12%.
Jaribio linatazamwa baada ya kila mtumiaji na linasimama kwenye uamuzi
wake wa kwanza:

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

Kwa kulinganisha, jaribio la sampuli isiyobadilika (fixed-sample test)
lenye nguvu ya 80% kwa ongezeko hili linahitaji takriban watumiaji 3,850
kwa kila kundi, 7,700 kwa jumla, na linaweza kusomwa mara moja tu,
mwishoni. Jaribio halali wakati wowote hulipia uhuru wake: ili kufikia
nguvu ile ile linahitaji mara 1.3–1.6 ya watumiaji wa uchambuzi mmoja,
na uendeshaji huu ulichukua zaidi ya hapo. Kwa malipo yake hakuna ukubwa
wa sampuli wa kuwekwa mapema, na unaweza kutazama matokeo kila siku na
kusimama mara tu yanapokuwa wazi. Athari inapokuwa kubwa kuliko
ilivyopangwa, hilo hutokea mapema zaidi sana.

## Mapato: kipindi kamili kwa kipimo chenye mipaka

`BoundedABTest` inahitaji mipaka ya kipimo pekee. Weka kikomo cha mapato
(revenue) kwenye thamani unayochagua kabla ya jaribio (hapa 30), na
mfuatano wa uhakika (confidence sequence) wa tofauti ya wastani ni kamili
kwa mgawanyo wowote:

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

Kipindi hiki kinashikilia katika kila moja ya matazamo 20,000 kwa
wakati mmoja, si katika la mwisho tu. Hapa bado kina 0: watumiaji 20,000
hawatoshi kuthibitisha ongezeko la takriban 0.5 kwenye kipimo chenye
kelele kiasi hiki, kwa hiyo jaribio linaendelea.

## Kagua mgawanyo wa trafiki kwanza

Kutolingana kwa uwiano wa sampuli (sample ratio mismatch) kunamaanisha
kwamba mgawanyo wa trafiki unatofautiana na ule uliosanidiwa, kwa mfano
kwa sababu ya hitilafu katika ugawaji au katika uandikaji wa kumbukumbu.
Makadirio ya athari kutoka kwa jaribio kama hilo hayaaminiki. Kutolingana
kutoka 50/50 hadi 52/48 kunagunduliwa wakati jaribio linaendelea:

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

## Vipimo vingi kwa wakati mmoja

Kujaribu vipimo kumi vinavyojitegemea kwa 5% kila kimoja kunatoa takriban
nafasi ya 40% ya angalau ugunduzi mmoja wa uongo. `MultipleTests`
inaunganisha thamani-e (e-values) za majaribio yote kwa utaratibu wa
e-BH, ili kiwango cha ugunduzi wa uongo kibaki kwenye `alpha` katika
wakati wowote wa kusimama:

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

## Mitego

* **Fanya ugawaji nasibu kwa kipimo unachochambua.** Ikiwa watumiaji ndio
  wamegawiwa nasibu, lisha rekodi moja kwa kila mtumiaji, si kwa kila
  ukurasa uliotazamwa. Kwa vipimo vya kila kipindi cha matumizi tumia
  `RatioABTest`, inayofanya kazi kwa jumla za kila mtumiaji.
* **Weka kikomo cha kipimo chenye mipaka kabla ya jaribio.** Kukichagua
  baada ya kuona data kunabatilisha hakikisho.
* **Taratibu za asymptotic zinahitaji sampuli kubwa.** Kwa `ABTest` na
  `RatioABTest` kipindi ni halali kwa ukaribu tu katika uendeshaji mrefu.
  Pendelea taratibu kamili zinapofaa.
* **Ugawaji wa trafiki unaojirekebisha** (bandits) unahitaji jaribio
  linalobaki halali mgawanyo unapotegemea matokeo:
  `TwoProportionTest(method="universal")` au
  `BoundedABTest(propensity_input=...)`. Tazama
  [mafunzo §10](../../tutorials/ab-test.md).

Zaidi: [mafunzo ya jaribio la A/B](../../tutorials/ab-test.md) (CUPED,
vipimo vya uwiano, viwango, kupanga muda) na
[programu ya majaribio](../../tutorials/experiment-programme.md)
(kiwango cha ugunduzi wa uongo kwa majaribio mengi).
