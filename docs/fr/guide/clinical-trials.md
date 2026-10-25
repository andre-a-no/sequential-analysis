---
description: Comment planifier et conduire les analyses intermédiaires d'un essai clinique en Python, avec des plans séquentiels groupés (O'Brien–Fleming, Pocock, dépense de l'alpha de Lan–DeMets, bornes de futilité), des tailles d'échantillon pour des moyennes, des proportions et la survie, vérifiées par rapport à rpact, avec sequential-analysis.
language: fr
---

# Comment planifier les analyses intermédiaires d'un essai clinique ?

> Ceci est une traduction de la [page en anglais](../../guide/clinical-trials.md). Elle n'a pas encore été relue par un locuteur natif ; en cas de divergence, la page en anglais fait foi.

**Réponse courte.** Utilisez un plan séquentiel groupé (group sequential
design). `group_sequential_design(alpha, fractions, spending=...)` de
`sequential_analysis.group_sequential` calcule :

* les bornes d'efficacité, avec la dépense de l'alpha (alpha spending)
  de Lan–DeMets (de type O'Brien–Fleming, de type Pocock et autres) ;
* des bornes de futilité (futility boundaries) non contraignantes ;
* la puissance et la taille d'échantillon espérée ;
* la taille d'échantillon maximale pour des moyennes et des proportions,
  ou le nombre d'événements pour la survie.

Les bornes et les tailles d'échantillon concordent avec le package R
rpact. Les procédures de test (`GroupSequentialTest`,
`GroupSequentialTwoMeans`, `GroupSequentialProportions`,
`GroupSequentialLogRank`) conduisent ensuite l'essai, patient par
patient ou événement par événement. Elles effectuent chaque analyse
intermédiaire (interim analysis) lorsque sa fraction d'information est
atteinte.

## Plan : quatre analyses, dépense d'O'Brien–Fleming

α unilatéral = 0,025, analyses à 25 %, 50 %, 75 % et 100 % des patients,
puissance de 90 %, avec une borne de futilité :

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

## Critères binaires et de survie

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

Avec la dépense d'O'Brien–Fleming, trois analyses coûtent 1,3 % de
patients de plus qu'une analyse finale unique.

## Conduire l'essai

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

L'essai s'est arrêté pour efficacité à la deuxième analyse, après les
deux tiers des patients prévus.

## Quand les analyses n'ont pas lieu comme prévu

Les comités de surveillance des données se réunissent rarement à
exactement 25 % de l'information :

* `design.at(fractions)` recalcule les bornes pour l'information
  effectivement atteinte. La dépense de l'alpha préserve le niveau
  global.
* `GroupSequentialMonitor` prend toute statistique que vous calculez
  vous-même (un modèle de Cox, un modèle mixte) sous forme de valeur Z,
  avec son information, à chaque réunion.

## Et si vous voulez regarder après chaque patient ?

Un plan séquentiel groupé ne permet que le nombre de regards prévu. Pour
surveiller après chaque patient ou chaque événement, utilisez une
procédure valide à tout instant (anytime-valid) : `AnytimeLogRankTest`
pour la survie, `TwoProportionTest` pour des taux de réponse,
`TMixtureSPRT` pour une moyenne. Elles demandent plus de patients à
l'effet prévu. Voir le [tutoriel : essai de survie](../../tutorials/survival.md).

## Pratique réglementaire

Les plans séquentiels groupés avec dépense de l'alpha sont l'approche
établie dans les essais confirmatoires, décrite dans la ligne directrice
ICH E9 et dans le guide de la FDA sur les plans adaptatifs (2019). Cette
bibliothèque calcule les plans et conserve un enregistrement auditable
et reprenable de chaque analyse (le point de reprise et l'empreinte de
son historique). Ce n'est pas un logiciel validé au sens réglementaire :
un promoteur qui l'utilise dans une soumission doit la valider comme
tout autre outil.

Pour aller plus loin : [tutoriel : essai séquentiel groupé](../../tutorials/group-sequential.md),
qui compare les chiffres avec rpact ;
[référence : conception et planification](../../reference/design.md).
