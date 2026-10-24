---
description: Kung bakit lumalaki ang false positives sa mga A/B test at trial kapag tinitingnan ang p-value araw-araw (ang peeking problem), at ang tatlong pamilya ng mga sequential method na lumulutas dito, sa Python gamit ang sequential-analysis.
language: tl
---

# Bakit hindi ko puwedeng tingnan ang p-value araw-araw?

> Ito ay salin ng [pahina sa Ingles](../../guide/peeking.md). Hindi pa ito nasusuri ng isang katutubong tagapagsalita ng wika; kung saan magkaiba ang dalawa, ang pahina sa Ingles ang masusunod.

**Maikling sagot.** Ang isang fixed-sample test ay nangangako ng 5% na
false-positive rate kung titingnan mo lamang ang resulta nang isang beses,
sa planadong sample size. Kung paulit-ulit kang titingin at hihinto sa
unang pagkakataong p < 0.05, marami kang pagkakataong malinlang. Sa 20 na
pagtingin, tumataas ang false-positive rate sa mga 25%. Ang mga sequential
method ay ginawa para tingnan nang paulit-ulit. Sa mga ito, nananatili ang
rate sa 5% o mas mababa gaano man kadalas ka tumingin at kailan ka man
huminto.

## Ang peeking problem, sinukat

Dalawang arm na may parehong 10% na conversion rate (isang A/A test), 2,000
user, 200 ulit. Ang "pagsilip" (peeking) ay ang pagpapatakbo ng karaniwang
two-proportion z-test pagkatapos ng bawat 100 user at paghinto sa unang
p < 0.05. Ang sequential na `TwoProportionTest` naman ay sinusuri
pagkatapos ng bawat isang user:

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

Tinutupad ng iisang pagtingin ang pangako nito. Ang dalawampung pagtingin
ay nagpaparami ng error rate nang mga anim na beses. Ang sequential test,
na tinitingnan pagkatapos ng bawat isa sa 2,000 user, ay pinananatili ito
sa 5%. Iyan ang pangako: ang garantiya (guarantee) nito ay **exact**
(`TwoProportionTest.guarantee == "exact"`), isang false-positive rate na
hindi hihigit sa 5% sa bawat sample size, gaano man kadalas ka tumingin.
Sa 200 ulit, 10 false positive ang inaasahang ibigay ng isang eksaktong
5%.

## Ang tatlong pamilya ng mga sequential method

| Pamilya | Kailan puwedeng tumingin | Karaniwang gamit | Sa sequential-analysis |
|---|---|---|---|
| **Sequential probability ratio test** (Wald 1945) | pagkatapos ng bawat obserbasyon | isang simpleng hypothesis laban sa isa pa, sa pinakakaunting obserbasyon sa karaniwan: quality control, simulation, psychophysics | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Group sequential design** (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | sa ilang planadong interim analysis | mga clinical trial na may data monitoring committee | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Anytime-valid inference**: mga e-value, confidence sequence, mixture SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | pagkatapos ng bawat obserbasyon, humihinto sa anumang dahilan | mga online A/B test, mga monitoring dashboard | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**Ano ang kapalit.** Ang mas madalas na pagtingin ay nangangailangan ng
mas maraming datos sa effect na pinlano mo:

* ang isang group sequential design na may apat na analysis ay
  nangangailangan ng 1–20% na mas maraming pasyente kaysa sa iisang
  analysis;
* ang isang anytime-valid test ng dalawang proporsiyon ay nangangailangan
  ng 1.3–1.6 na beses ng mga user ng iisang analysis.

Bilang kapalit, pinahihinto nang maaga ng malaking effect ang experiment,
at walang kailangang magtakda ng sample size nang maaga.

## Kapag hindi ito ang problema

Lumalaki lamang ang mga error dahil sa pagsilip kapag nakadepende ang
ginagawa mo sa nakita mo. Kung tinitingnan mo ang dashboard pero palagi
mong pinatatakbo ang experiment hanggang sa planadong laki nito at
isang beses lamang nagte-test, valid ang fixed-sample test. Ito rin ang
pinakaepisyenteng pagpipilian sa ganoong kaso.

Susunod: [ihinto nang maaga ang isang A/B test](ab-testing.md),
[mga confidence sequence](confidence-sequences.md),
[ang glosaryo](glossary.md).
