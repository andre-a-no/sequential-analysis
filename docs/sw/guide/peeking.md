---
description: Kwa nini kukagua thamani-p kila siku kunaongeza chanya za uongo katika majaribio ya A/B na majaribio ya kliniki (tatizo la kuchungulia, peeking problem), na familia tatu za mbinu za mfuatano zinazolitatua, katika Python kwa sequential-analysis.
language: sw
---

# Kwa nini siwezi kutazama thamani-p kila siku?

> Hii ni tafsiri ya [ukurasa wa Kiingereza](../../guide/peeking.md). Bado haijakaguliwa na mzungumzaji mzawa; pale ambapo hizi mbili zinatofautiana, ukurasa wa Kiingereza ndio wenye mamlaka.

**Jibu fupi.** Jaribio la sampuli isiyobadilika (fixed-sample test)
linaahidi kiwango cha chanya za uongo (false positives) cha 5% ikiwa tu
utatazama matokeo mara moja, katika ukubwa wa sampuli uliopangwa. Ukitazama
mara kwa mara na kusimama mara ya kwanza p < 0.05, unapata nafasi nyingi
za kudanganyika. Kwa matazamo 20, kiwango cha chanya za uongo kinapanda
hadi takriban 25%. Mbinu za mfuatano (sequential methods) zimejengwa ili
zitazamwe mara kwa mara. Kwazo, kiwango kinabaki kwenye 5% au chini yake
hata ukitazama mara ngapi na wakati wowote utakaposimama.

## Tatizo la kuchungulia, likipimwa

Makundi mawili yenye kiwango sawa cha ubadilishaji cha 10% (jaribio la
A/A), watumiaji 2,000, marudio 200. "Kuchungulia" (peeking) kunaendesha
jaribio-z la kawaida la uwiano miwili baada ya kila watumiaji 100 na
kusimama kwenye p < 0.05 ya kwanza. `TwoProportionTest` ya mfuatano
inakaguliwa baada ya kila mtumiaji mmoja mmoja:

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

Tazamo moja linatimiza ahadi yake. Matazamo ishirini yanazidisha kiwango
cha makosa takriban mara sita. Jaribio la mfuatano, likitazamwa baada ya
kila mmoja wa watumiaji 2,000, linakibakiza kwenye 5%. Hiyo ndiyo ahadi:
hakikisho lake ni **exact** (`TwoProportionTest.guarantee == "exact"`),
kiwango cha chanya za uongo kisichozidi 5% katika kila ukubwa wa sampuli,
hata ukitazama mara ngapi. Kwa marudio 200, chanya za uongo 10 ndizo
zinazotolewa na kiwango kamili cha 5%.

## Familia tatu za mbinu za mfuatano

| Familia | Unaweza kutazama | Matumizi ya kawaida | Katika sequential-analysis |
|---|---|---|---|
| **Majaribio ya mfuatano ya uwiano wa uwezekano** (sequential probability ratio tests) (Wald 1945) | baada ya kila kipimo | nadharia tete sahili moja dhidi ya nyingine, kwa wastani wa vipimo vichache zaidi: udhibiti wa ubora, uigaji, saikofizikia | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Miundo ya mfuatano wa vikundi** (group sequential designs) (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | katika chambuzi chache za kati zilizopangwa | majaribio ya kliniki yenye kamati ya ufuatiliaji wa data | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Makisio halali wakati wowote** (anytime-valid inference): thamani-e, mifuatano ya uhakika, SPRT ya mchanganyiko (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | baada ya kila kipimo, kusimama kwa sababu yoyote | majaribio ya A/B mtandaoni, dashibodi za ufuatiliaji | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**Gharama yake.** Kutazama mara nyingi zaidi kunahitaji data zaidi katika
athari uliyoipangia:

* muundo wa mfuatano wa vikundi wenye chambuzi nne unahitaji wagonjwa
  1–20% zaidi kuliko uchambuzi mmoja;
* jaribio halali wakati wowote la uwiano miwili linahitaji mara 1.3–1.6
  ya watumiaji wa uchambuzi mmoja.

Kwa malipo yake, athari kubwa inasimamisha jaribio mapema, na hakuna
anayelazimika kuweka ukubwa wa sampuli mapema.

## Wakati hili si tatizo

Kuchungulia kunaongeza makosa tu pale unachokifanya kinapotegemea
ulichokiona. Ukitazama dashibodi lakini kila mara ukaendesha jaribio hadi
ukubwa wake uliopangwa na kujaribu mara moja, jaribio la sampuli
isiyobadilika ni halali. Pia ndilo chaguo lenye ufanisi zaidi katika hali
hiyo.

Inayofuata: [simamisha jaribio la A/B mapema](ab-testing.md),
[mifuatano ya uhakika](confidence-sequences.md),
[faharasa](glossary.md).
