---
description: Comment détecter un changement dans un flux de mesures de capteurs, de latences ou de métriques en Python, avec CUSUM, Shiryaev–Roberts, des e-détecteurs non paramétriques et la détection bayésienne en ligne de ruptures. Fausses alarmes contrôlées par la période opérationnelle moyenne (ARL), avec sequential-analysis.
language: fr
---

# Comment détecter un changement dans un flux de mesures ?

> Ceci est une traduction de la [page en anglais](../../guide/change-detection.md). Elle n'a pas encore été relue par un locuteur natif ; en cas de divergence, la page en anglais fait foi.

**Réponse courte.** Utilisez un détecteur de ruptures en ligne (online
change-point detector). Il surveille le flux et déclenche une alarme dès
que la distribution semble avoir changé. Ses fausses alarmes sont
contrôlées par la **période opérationnelle moyenne** (average run
length, ARL) : le nombre espéré d'observations avant une fausse alarme
tant que rien n'a changé. Dans sequential-analysis :

| Ce que vous savez avant le changement | Procédure | Garantie |
|---|---|---|
| les deux distributions (par ex. normale, moyenne 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact : ARL ≥ e^threshold |
| seulement la moyenne, et des bornes sur les valeurs | `MeanEDetector` | exact pour toute distribution de ce type |
| seulement un quantile (par ex. le 95e centile de la latence) | `QuantileEDetector` | exact pour toute distribution |
| un modèle à paramètres inconnus, avant et après | `BayesianChangePoint` | sous le modèle et la loi a priori |

## Un capteur dont la moyenne se décale

Un capteur de température indique 70,0 °C avec un bruit d'écart-type
0,5. À partir de la mesure 600, la moyenne vaut 70,4. CUSUM avec le
seuil log(1000) ≈ 6,9 a une ARL d'au moins 1 000 mesures :

```python
import math
import random

from sequential_analysis.procedures import CUSUM, Gaussian

rnd = random.Random(1)
readings = [rnd.gauss(70.0, 0.5) for _ in range(600)] + [rnd.gauss(70.4, 0.5) for _ in range(400)]

detector = CUSUM(Gaussian(sigma=0.5), theta0=70.0, theta1=70.4, threshold=math.log(1000))
state = detector.initial_state()
for t, x in enumerate(readings, start=1):
    state, out = detector.step(state, {"x": x})
    if out.alarm:
        print(f"alarm at reading {t}, {t - 600} readings after the shift")
        break
```

```text
alarm at reading 615, 15 readings after the shift
```

Un décalage de moins d'un écart-type est invisible à l'œil sur une
mesure isolée. CUSUM accumule les indices et le trouve.

## Quand les mesures ne sont pas normales

L'ARL de CUSUM n'est garantie que si les mesures suivent les
distributions que vous lui avez indiquées. Pour des données asymétriques
(amplitudes de vibration, latences, longueurs de file d'attente), il
déclenche des fausses alarmes bien plus souvent que prévu. Les
e-détecteurs (e-detectors) demandent beaucoup moins :

* `MeanEDetector` a besoin de la moyenne avant le changement et de
  bornes sur les valeurs.
* `QuantileEDetector` n'a besoin que d'un quantile avant le changement.

Leur ARL est au moins égale à la cible pour **toute** distribution
ayant cette moyenne ou ce quantile :

```python
from sequential_analysis.procedures import QuantileEDetector

rnd = random.Random(2)
vibration = [rnd.lognormvariate(0.0, 0.8) for _ in range(800)] + [rnd.lognormvariate(0.5, 0.8) for _ in range(400)]
q95 = math.exp(0.8 * 1.6449)          # the 95th percentile before the change
p95 = QuantileEDetector(q0=q95, p=0.95, arl=1000, direction="increase", statistic="cusum")
state = p95.initial_state()
for t, x in enumerate(vibration, start=1):
    state, out = p95.step(state, {"x": x})
    if out.alarm:
        print(f"the 95th percentile rose: alarm at reading {t}, {t - 800} readings after the change")
        break
```

```text
the 95th percentile rose: alarm at reading 887, 87 readings after the change
```

En pratique, le quantile avant le changement est estimé sur une période
calme. La garantie est alors approximative, d'autant meilleure que cette
période est longue.

## Choisir l'ARL

L'ARL arbitre entre fausses alarmes et délai. À raison d'une mesure par
minute, une ARL de 1 000 mesures signifie une fausse alarme toutes les
17 heures environ de fonctionnement normal, par capteur. Avec 50
capteurs, cela fait environ 70 par jour. Choisissez l'ARL à partir du
nombre de fausses alarmes par jour que vous pouvez vous permettre pour
l'ensemble des capteurs : ici, une ARL de 1 000 000 de mesures ramène
les 50 capteurs à environ une fausse alarme toutes les deux semaines.
Cela coûte moins qu'il n'y paraît, car le délai de détection ne croît
qu'avec le logarithme de l'ARL. Pour CUSUM, le seuil passe de 6,9 à
13,8, et le délai double à peu près.

Ces détecteurs sont des outils de surveillance, pas des systèmes de
sécurité. Ne les utilisez pas à la place d'un système instrumenté de
sécurité certifié.

Pour aller plus loin : [tutoriel : surveillance de procédés et détection de changements](../../tutorials/monitoring.md),
[régimes avec des modèles de Markov cachés](../../tutorials/regimes.md),
[référence : détection de changements](../../reference/detection.md).
