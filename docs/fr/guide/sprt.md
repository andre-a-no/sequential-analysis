---
description: Comment exécuter le test séquentiel du rapport de vraisemblance de Wald (SPRT) en Python avec sequential-analysis. Taux d'erreur, taille d'échantillon moyenne comparée à un test à échantillon fixe, et les variantes tronquées (2-SPRT, plans optimaux de Kiefer–Weiss).
language: fr
---

# Comment exécuter le SPRT de Wald en Python ?

> Ceci est une traduction de la [page en anglais](../../guide/sprt.md). Elle n'a pas encore été relue par un locuteur natif ; en cas de divergence, la page en anglais fait foi.

**Réponse courte.** `SPRT(family, theta0, theta1, alpha, beta)` de
`sequential_analysis.procedures` implémente le test séquentiel du
rapport de vraisemblance (sequential probability ratio test, SPRT) de
Wald. Il tranche entre deux hypothèses simples avec, en moyenne, le
moins d'observations possible. Fournissez-lui une observation à la fois
et arrêtez à la première décision. Dans l'exemple ci-dessous, il lui
faut environ la moitié des observations d'un test à échantillon fixe
ayant les mêmes taux d'erreur : 65 à 76 articles en moyenne au lieu de
133. Si vous avez besoin d'une taille d'échantillon maximale garantie,
utilisez plutôt `TwoSPRT` ou un plan issu de `kiefer_weiss_plan`.

## Exemple : le taux de défauts est-il de 10 % ou de 20 % ?

Un lot est accepté si son taux de défauts est de 10 % et rejeté s'il est
de 20 %, avec les deux taux d'erreur à 5 % :

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

Comment se comporte-t-il sur de nombreux lots ?

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

Un test à échantillon fixe ayant les mêmes taux d'erreur inspecte
environ 133 articles dans chaque lot (approximation normale). Le SPRT en
inspecte en moyenne 43 à 51 % de moins. Sa taille d'échantillon est
toutefois aléatoire et n'a pas de limite supérieure, et quelques lots
prennent bien plus longtemps que la moyenne.

Les seuils sont ceux de Wald : log((1 − β)/α) et log(β/(1 − α)). Ils
garantissent, quelle que soit la taille d'échantillon à l'arrêt, que les
taux d'erreur effectifs α′ et β′ vérifient α′ ≤ α/(1 − β),
β′ ≤ β/(1 − α) et α′ + β′ ≤ α + β. Le rapport de vraisemblance dépasse
les seuils au moment de l'arrêt, si bien qu'en pratique les taux sont
inférieurs aux taux nominaux, comme ici. C'est le sens de
`SPRT.guarantee == "exact"`. Pour des taux d'erreur calculés exactement
plutôt que bornés, utilisez `operating_characteristic` sur un plan
(voir ci-dessous).

## Quand il vous faut une taille d'échantillon maximale

* `TwoSPRT` (le 2-SPRT de Lorden) s'arrête avant un horizon fixé et
  minimise presque l'espérance de la taille d'échantillon dans le pire
  cas.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  dans `sequential_analysis.design` calcule par induction rétrograde le
  plan optimal avec une taille d'échantillon maximale. `PlanTest`
  l'exécute, et `operating_characteristic` donne ses taux d'erreur
  exacts et l'espérance de sa taille d'échantillon sans simulation.
  Voir `examples/07_design_kiefer_weiss.py`.
* Pour quelques regards prévus au lieu d'un par observation, utilisez un
  [plan séquentiel groupé](clinical-trials.md).

## Quand le SPRT n'est pas le bon outil

* **Les hypothèses ne sont pas simples.** « Le taux est de 10 % » contre
  « le taux est n'importe quoi d'autre » est une alternative composite.
  Utilisez un SPRT de mélange (`NormalMixtureSPRT`, `TMixtureSPRT`) ou
  un test par pari (`BettingMeanTest`), qui sont valides à tout instant
  (anytime-valid) contre toute alternative.
* **La vraie valeur se situe entre θ₀ et θ₁.** Le SPRT est alors le plus
  lent, et l'espérance de sa taille d'échantillon peut dépasser la
  taille d'échantillon fixe. Le plan de Kiefer–Weiss est conçu
  précisément pour ce cas.

Familles disponibles pour les procédures fondées sur le rapport de
vraisemblance : `Gaussian` (variance connue), `Bernoulli`, `Poisson`,
`Exponential`.
