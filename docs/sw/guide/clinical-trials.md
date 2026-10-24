---
description: Jinsi ya kupanga na kuendesha uchambuzi wa kati wa jaribio la kliniki katika Python, kwa miundo ya mfuatano wa vikundi (O'Brien–Fleming, Pocock, matumizi ya alfa ya Lan–DeMets, mipaka ya kutofaa), ukubwa wa sampuli kwa wastani, uwiano na muda wa kuishi, uliokaguliwa dhidi ya rpact, kwa sequential-analysis.
language: sw
---

# Ninapangaje uchambuzi wa kati wa jaribio la kliniki?

> Hii ni tafsiri ya [ukurasa wa Kiingereza](../../guide/clinical-trials.md). Bado haijakaguliwa na mzungumzaji mzawa; pale ambapo hizi mbili zinatofautiana, ukurasa wa Kiingereza ndio wenye mamlaka.

**Jibu fupi.** Tumia muundo wa mfuatano wa vikundi (group sequential
design). `group_sequential_design(alpha, fractions, spending=...)` kutoka
`sequential_analysis.group_sequential` inakokotoa:

* mipaka ya ufanisi (efficacy boundaries), kwa matumizi ya alfa (alpha
  spending) ya Lan–DeMets (aina ya O'Brien–Fleming, aina ya Pocock na
  nyinginezo);
* mipaka ya kutofaa (futility boundaries) isiyolazimisha;
* nguvu (power) na ukubwa wa sampuli unaotarajiwa;
* ukubwa wa juu wa sampuli kwa wastani na uwiano, au idadi ya matukio
  kwa uchambuzi wa muda wa kuishi (survival).

Mipaka na ukubwa wa sampuli vinakubaliana na kifurushi cha R rpact.
Taratibu za majaribio (`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) kisha zinaendesha
jaribio, mgonjwa kwa mgonjwa au tukio kwa tukio. Zinafanya kila uchambuzi
wa kati (interim analysis) sehemu yake ya taarifa (information fraction)
inapofikiwa.

## Muundo: chambuzi nne, matumizi ya O'Brien–Fleming

α ya upande mmoja = 0.025, chambuzi katika 25%, 50%, 75% na 100% ya
wagonjwa, nguvu ya 90%, pamoja na mpaka wa kutofaa:

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

## Matokeo ya kipimo cha jozi (binary) na ya muda wa kuishi

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

Kwa matumizi ya O'Brien–Fleming, chambuzi tatu zinagharimu wagonjwa 1.3%
zaidi kuliko uchambuzi mmoja wa mwisho.

## Kuendesha jaribio

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

Jaribio lilisimamishwa kwa sababu ya ufanisi katika uchambuzi wa pili,
baada ya theluthi mbili ya wagonjwa waliopangwa.

## Chambuzi zisipofanyika kama zilivyopangwa

Kamati za ufuatiliaji wa data mara chache hukutana hasa katika 25% ya
taarifa:

* `design.at(fractions)` inakokotoa upya mipaka kwa taarifa iliyofikiwa
  kwa kweli. Matumizi ya alfa yanadumisha kiwango cha jumla.
* `GroupSequentialMonitor` inapokea takwimu yoyote unayoikokotoa mwenyewe
  (modeli ya Cox, modeli mchanganyiko) kama thamani ya Z pamoja na taarifa
  yake katika kila kikao.

## Na ikiwa unataka kutazama baada ya kila mgonjwa?

Muundo wa mfuatano wa vikundi unaruhusu idadi iliyopangwa ya matazamo
pekee. Ili kufuatilia baada ya kila mgonjwa au tukio, tumia utaratibu
halali wakati wowote (anytime-valid): `AnytimeLogRankTest` kwa muda wa
kuishi, `TwoProportionTest` kwa viwango vya mwitikio, `TMixtureSPRT` kwa
wastani. Zinahitaji wagonjwa zaidi katika athari iliyopangwa. Tazama
[mafunzo: jaribio la muda wa kuishi](../../tutorials/survival.md).

## Utaratibu wa kisheria (regulatory)

Miundo ya mfuatano wa vikundi yenye matumizi ya alfa ndiyo mbinu
iliyothibitika katika majaribio ya uthibitisho (confirmatory trials),
inayoelezwa katika mwongozo wa ICH E9 na mwongozo wa FDA kuhusu miundo
inayojirekebisha (2019). Maktaba hii inakokotoa miundo hiyo na kuhifadhi
rekodi ya kila uchambuzi inayoweza kukaguliwa na kuendelezwa (kituo cha
ukaguzi (checkpoint) na muhtasari wake wa historia (history digest)). Si
programu iliyothibitishwa kwa maana ya kisheria: mfadhili anayeitumia
katika uwasilishaji anapaswa kuithibitisha kama zana nyingine yoyote.

Zaidi: [mafunzo: jaribio la mfuatano wa vikundi](../../tutorials/group-sequential.md),
linalolinganisha namba na rpact;
[marejeo: muundo na upangaji](../../reference/design.md).
