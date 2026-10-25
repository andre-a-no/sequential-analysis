---
description: Comment arrêter un test A/B plus tôt sans gonfler les faux positifs, en Python. Tests valides à tout instant (anytime-valid) pour la conversion et un revenu borné, contrôle du déséquilibre de répartition (SRM) et du taux de fausses découvertes sur plusieurs métriques, avec sequential-analysis.
language: fr
---

# Comment arrêter un test A/B plus tôt sans gonfler les faux positifs ?

> Ceci est une traduction de la [page en anglais](../../guide/ab-testing.md). Elle n'a pas encore été relue par un locuteur natif ; en cas de divergence, la page en anglais fait foi.

**Réponse courte.** Utilisez un test valide à tout instant
(anytime-valid) : sa p-valeur et son intervalle de confiance restent
valides quelle que soit la fréquence à laquelle vous regardez, si bien
que vous pouvez arrêter dès que le résultat est net. Dans
sequential-analysis :

| Métrique | Procédure | Garantie |
|---|---|---|
| taux de conversion (0/1) | `TwoProportionTest` | exact |
| toute métrique bornée (revenu plafonné, part) | `BoundedABTest` | exact |
| événements par unité d'exposition | `RateRatioTest` | exact pour des comptages de Poisson |
| métrique de ratio (revenu par session) | `RatioABTest` | asymptotic |
| moyenne avec une covariable pré-expérience (CUPED) | `ABTest` | asymptotic |
| le trafic est-il réparti comme prévu ? | `SampleRatioMismatch` | exact |
| plusieurs métriques ou bras à la fois | `MultipleTests` (e-BH) | taux de fausses découvertes (false discovery rate), exact |

Alimentez chaque procédure un utilisateur à la fois : `state, out = test.step(state, {...})`.
Agissez sur `out.decision` quand vous le souhaitez.

## Conversion : arrêter quand les données sont concluantes

Le groupe témoin convertit 10 % des utilisateurs, le groupe traité 12 %.
Le test est consulté après chaque utilisateur et s'arrête à sa première
décision :

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

À titre de comparaison, un test à échantillon fixe ayant une puissance
de 80 % pour cette hausse nécessite environ 3 850 utilisateurs par bras,
7 700 au total, et ne peut être lu qu'une fois, à la fin. Le test valide
à tout instant paie sa liberté : pour atteindre la même puissance, il
lui faut 1,3 à 1,6 fois les utilisateurs d'une analyse unique, et cette
exécution en a pris davantage. En échange, il n'y a aucune taille
d'échantillon à fixer à l'avance, et vous pouvez regarder le résultat
chaque jour et arrêter dès qu'il est net. Lorsque l'effet est plus grand
que prévu, cela arrive bien plus tôt.

## Revenu : un intervalle exact pour une métrique bornée

`BoundedABTest` n'a besoin que de bornes sur la métrique. Plafonnez le
revenu à une valeur choisie avant le test (ici 30), et la suite de
confiance (confidence sequence) pour la différence des moyennes est
exacte pour toute distribution :

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

L'intervalle est valide simultanément à chacun des 20 000 regards, et
pas seulement au dernier. Ici, il contient encore 0 : 20 000
utilisateurs ne suffisent pas à établir une hausse d'environ 0,5 sur une
métrique aussi bruitée, donc l'expérience continue.

## Vérifier d'abord la répartition du trafic

Un déséquilibre de répartition (sample ratio mismatch) signifie que la
répartition diffère de celle qui a été configurée, par exemple à cause
d'un bogue dans l'affectation ou dans la journalisation. Les estimations
d'effet issues d'une telle expérience ne sont pas fiables. Un écart de
50/50 à 52/48 est détecté pendant que l'expérience tourne :

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

## Plusieurs métriques à la fois

Tester dix métriques indépendantes à 5 % chacune donne environ 40 % de
chances d'au moins une fausse découverte. `MultipleTests` combine les
e-valeurs (e-values) de tous les tests par la procédure e-BH, de sorte
que le taux de fausses découvertes reste à `alpha` à tout temps d'arrêt :

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

## Pièges

* **Randomisez l'unité que vous analysez.** Si ce sont les utilisateurs
  qui sont randomisés, fournissez un enregistrement par utilisateur, et
  non par page vue. Pour les métriques par session, utilisez
  `RatioABTest`, qui travaille sur les totaux par utilisateur.
* **Fixez le plafond d'une métrique bornée avant le test.** Le choisir
  après avoir vu les données annule la garantie.
* **Les procédures asymptotiques demandent de grands échantillons.**
  Pour `ABTest` et `RatioABTest`, l'intervalle n'est
  qu'approximativement valide sur de longues exécutions. Préférez les
  procédures exactes lorsqu'elles conviennent.
* **L'allocation adaptative du trafic** (bandits) exige un test qui
  reste valide quand la répartition dépend des résultats :
  `TwoProportionTest(method="universal")` ou
  `BoundedABTest(propensity_input=...)`. Voir le
  [tutoriel, §10](../../tutorials/ab-test.md).

Pour aller plus loin : le [tutoriel sur les tests A/B](../../tutorials/ab-test.md)
(CUPED, métriques de ratio, taux, planification de la durée) et
[un programme d'expériences](../../tutorials/experiment-programme.md)
(taux de fausses découvertes sur de nombreuses expériences).
