---
description: Pourquoi consulter une p-valeur tous les jours gonfle les faux positifs dans les tests A/B et les essais (le problème des regards répétés, ou peeking), et les trois familles de méthodes séquentielles qui le résolvent, en Python avec sequential-analysis.
language: fr
---

# Pourquoi ne puis-je pas regarder une p-valeur tous les jours ?

> Ceci est une traduction de la [page en anglais](../../guide/peeking.md). Elle n'a pas encore été relue par un locuteur natif ; en cas de divergence, la page en anglais fait foi.

**Réponse courte.** Un test à échantillon fixe ne promet un taux de faux
positifs de 5 % que si vous regardez le résultat une seule fois, à la
taille d'échantillon prévue. Si vous regardez à plusieurs reprises et
arrêtez la première fois que p < 0,05, vous multipliez les occasions
d'être trompé. Avec 20 regards, le taux de faux positifs monte à environ
25 %. Les méthodes séquentielles sont conçues pour être consultées à
plusieurs reprises. Avec elles, le taux reste inférieur ou égal à 5 %,
quelle que soit la fréquence des regards et quel que soit le moment de
l'arrêt.

## Le problème des regards répétés (peeking), mesuré

Deux bras avec le même taux de conversion de 10 % (un test A/A), 2 000
utilisateurs, 200 répétitions. Le « peeking » applique le test z
habituel de deux proportions tous les 100 utilisateurs et s'arrête au
premier p < 0,05. Le `TwoProportionTest` séquentiel est consulté après
chaque utilisateur :

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

Le regard unique tient sa promesse. Vingt regards multiplient le taux
d'erreur par environ six. Le test séquentiel, consulté après chacun des
2 000 utilisateurs, le maintient à 5 %. C'est là sa promesse : sa
garantie est **exact** (`TwoProportionTest.guarantee == "exact"`), soit
un taux de faux positifs d'au plus 5 % pour toute taille d'échantillon,
quelle que soit la fréquence des regards. Avec 200 répétitions,
10 faux positifs sont ce que donne un taux exact de 5 %.

## Les trois familles de méthodes séquentielles

| Famille | Vous pouvez regarder | Usage typique | Dans sequential-analysis |
|---|---|---|---|
| **Tests séquentiels du rapport de vraisemblance** (sequential probability ratio tests, Wald 1945) | après chaque observation | une hypothèse simple contre une autre, le moins d'observations possible en moyenne : contrôle qualité, simulation, psychophysique | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Plans séquentiels groupés** (group sequential designs ; Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | lors de quelques analyses intermédiaires prévues | essais cliniques avec un comité de surveillance des données | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Inférence valide à tout instant** (anytime-valid inference) : e-valeurs, suites de confiance, SPRT de mélange (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | après chaque observation, arrêt pour n'importe quelle raison | tests A/B en ligne, tableaux de bord de suivi | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**Ce que cela coûte.** Regarder plus souvent demande davantage de
données à l'effet pour lequel on a planifié :

* un plan séquentiel groupé à quatre analyses demande 1 à 20 % de
  patients de plus qu'une analyse unique ;
* un test valide à tout instant de deux proportions demande 1,3 à 1,6
  fois les utilisateurs d'une analyse unique.

En échange, un effet important arrête l'expérience tôt, et personne n'a
à fixer la taille d'échantillon à l'avance.

## Quand ce n'est pas le problème

Les regards répétés ne gonflent les erreurs que lorsque ce que vous
faites dépend de ce que vous avez vu. Si vous regardez le tableau de
bord mais menez toujours l'expérience jusqu'à sa taille prévue et ne
testez qu'une fois, le test à échantillon fixe est valide. C'est aussi
le choix le plus efficace dans ce cas.

Ensuite : [arrêter un test A/B plus tôt](ab-testing.md),
[les suites de confiance](confidence-sequences.md),
[le glossaire](glossary.md).
