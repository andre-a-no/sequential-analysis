---
description: Les suites de confiance (confidence sequences) sont des intervalles de confiance valides simultanément pour toutes les tailles d'échantillon, que l'on peut donc surveiller en continu. Comment les calculer en Python pour une moyenne bornée, une médiane ou un quantile, et une moyenne à queues lourdes, avec sequential-analysis.
language: fr
---

# Comment obtenir un intervalle de confiance qui reste valide quand on continue à regarder ?

> Ceci est une traduction de la [page en anglais](../../guide/confidence-sequences.md). Elle n'a pas encore été relue par un locuteur natif ; en cas de divergence, la page en anglais fait foi.

**Réponse courte.** Utilisez une **suite de confiance** (confidence
sequence). C'est une suite d'intervalles, un après chaque observation,
qui contient la vraie valeur pour toutes les tailles d'échantillon
simultanément avec une probabilité d'au moins 95 %. Vous pouvez la
suivre, arrêter quand elle est assez étroite ou exclut zéro, et
rapporter l'intervalle auquel vous vous êtes arrêté. Un intervalle de
confiance à 95 % habituel ne promet 95 % que pour une seule taille
d'échantillon fixée à l'avance.

| Ce que vous estimez | Hypothèse | Procédure | Garantie |
|---|---|---|---|
| moyenne de données bornées (taux, scores, revenu plafonné) | valeurs dans `[lower, upper]` | `BettingConfidenceSequence` | exact |
| médiane, 90e centile, tout quantile | aucune | `QuantileConfidenceSequence` | exact |
| moyenne avec queues lourdes ou valeurs aberrantes | une borne sur l'écart-type | `CatoniConfidenceSequence` | exact |
| moyenne de données normales, variance inconnue | normalité | `TMixtureSPRT` (`lower`, `upper`) | exact sous normalité |
| moyenne de n'importe quoi, longues exécutions | variance finie | `AsymptoticConfidenceSequence` | asymptotic |
| différence entre deux bras | voir [tests A/B](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## L'intervalle habituel échoue quand on le surveille

Tirez 500 observations d'une variable 0/1 de moyenne 0,3 et, à partir
de la 30e, calculez après chacune l'intervalle à 95 % des manuels : la
moyenne ± 1,96 erreur type. Dans combien des 100 exécutions l'intervalle
manque-t-il la vraie moyenne à un moment ou à un autre ?

```python
import math
import random

def stream(seed, n=500, p=0.3):
    rnd = random.Random(seed)
    return [float(rnd.random() < p) for _ in range(n)]

def textbook_ever_misses(xs, truth=0.3):
    total = total2 = 0.0
    for n, x in enumerate(xs, start=1):
        total, total2 = total + x, total2 + x * x
        if n >= 30:
            mean = total / n
            se = math.sqrt(max(total2 / n - mean * mean, 1e-12) / n)
            if abs(mean - truth) > 1.96 * se:
                return True
    return False

runs = [stream(seed) for seed in range(100)]
print(f"textbook interval misses the truth at some n in {sum(map(textbook_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
textbook interval misses the truth at some n in 28% of runs
```

Ses « 95 % » ne valent que pour une taille d'échantillon fixée à
l'avance. La suite de confiance pour les mêmes données, construite par
pari (Waudby-Smith and Ramdas 2024), manque la vraie valeur pour un
certain n dans au plus 5 % des exécutions, par construction :

```python
from sequential_analysis.procedures import BettingConfidenceSequence

def sequence_ever_misses(xs, truth=0.3):
    cs = BettingConfidenceSequence(lower=0.0, upper=1.0, alpha=0.05, grid=100)
    state = cs.initial_state()
    for x in xs:
        state, out = cs.step(state, {"x": x})
        if not out.lower <= truth <= out.upper:
            return True
    return False

print(f"confidence sequence misses the truth at some n in {sum(map(sequence_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
confidence sequence misses the truth at some n in 1% of runs
```

## Une latence médiane, sans aucune hypothèse

Les latences sont asymétriques et à queues lourdes, si bien qu'un
intervalle moyenne ± erreur type n'est pas fiable pour elles.
`QuantileConfidenceSequence` couvre n'importe quel quantile de n'importe
quelle distribution, ex-æquo compris :

```python
from sequential_analysis.procedures import QuantileConfidenceSequence

rnd = random.Random(7)
median = QuantileConfidenceSequence(p=0.5, alpha=0.05)
p90 = QuantileConfidenceSequence(p=0.9, alpha=0.05)
m_state, q_state = median.initial_state(), p90.initial_state()
for _ in range(2000):
    latency = rnd.lognormvariate(math.log(120.0), 0.6)   # milliseconds; true median 120
    m_state, m = median.step(m_state, {"x": latency})
    q_state, q = p90.step(q_state, {"x": latency})
print(f"median: {m.estimate:.1f} ms, 95% confidence sequence [{m.lower:.1f}, {m.upper:.1f}]")
print(f"90th percentile: {q.estimate:.1f} ms, [{q.lower:.1f}, {q.upper:.1f}]")
```

```text
median: 117.3 ms, 95% confidence sequence [111.3, 122.6]
90th percentile: 252.7 ms, [237.9, 272.5]
```

Les vraies valeurs sont 120 ms et 258,8 ms. Les deux intervalles sont
valides simultanément pour les 2 000 tailles d'échantillon.

## Pièges

* **Les bornes et les plafonds font partie de l'hypothèse.** Choisissez
  `lower` et `upper` avant de voir les données. Une valeur en dehors est
  refusée.
* **Aucune méthode ne donne une couverture exacte pour la moyenne de
  données non bornées quelconques.** Pour de telles données, utilisez un
  quantile, plafonnez les valeurs, supposez une borne sur l'écart-type
  (Catoni) ou acceptez une suite asymptotique.
* **Les suites de confiance sont plus larges qu'un intervalle unique**
  à taille d'échantillon égale. Cette largeur est le prix de la validité
  simultanée pour toutes les tailles d'échantillon.

Pour aller plus loin : [Quelle méthode ?](../../choosing.md),
[référence : inférence valide à tout instant et non paramétrique](../../reference/anytime.md).
