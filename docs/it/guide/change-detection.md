---
description: Come rilevare un cambiamento in un flusso di letture di sensori, latenze o metriche in Python, con CUSUM, Shiryaev–Roberts, e-detector non parametrici e rilevamento bayesiano online dei punti di cambiamento. Falsi allarmi controllati tramite la lunghezza media della sequenza (ARL), con sequential-analysis.
language: it
---

# Come rilevare un cambiamento in un flusso di misure?

> Questa è una traduzione della [pagina in inglese](../../guide/change-detection.md). Non è ancora stata rivista da un madrelingua; in caso di differenze, fa fede la pagina in inglese.

**Risposta breve.** Usate un rilevatore online di punti di cambiamento
(online change-point detector). Sorveglia il flusso e lancia un allarme
non appena la distribuzione sembra cambiata. I suoi falsi allarmi sono
controllati dalla **lunghezza media della sequenza** (average run
length, ARL): il numero atteso di osservazioni fino a un falso allarme
finché nulla è cambiato. In sequential-analysis:

| Che cosa sapete prima del cambiamento | Procedura | Garanzia |
|---|---|---|
| entrambe le distribuzioni (ad es. normale, media 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| solo la media, e limiti sui valori | `MeanEDetector` | exact per ogni distribuzione di questo tipo |
| solo un quantile (ad es. il 95° percentile della latenza) | `QuantileEDetector` | exact per ogni distribuzione |
| un modello con parametri ignoti, prima e dopo | `BayesianChangePoint` | sotto il modello e la distribuzione a priori |

## Un sensore la cui media si sposta

Un sensore di temperatura legge 70,0 °C con un rumore di deviazione
standard 0,5. Dalla lettura 600 in poi la media è 70,4. CUSUM con soglia
log(1000) ≈ 6,9 ha un'ARL di almeno 1.000 letture:

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

Uno spostamento inferiore a una deviazione standard è invisibile a
occhio in ogni singola lettura. CUSUM accumula l'evidenza e lo trova.

## Quando le letture non sono normali

L'ARL di CUSUM vale solo se le letture seguono le distribuzioni che gli
avete indicato. Per dati asimmetrici (ampiezze di vibrazione, latenze,
lunghezze di code) lancia falsi allarmi molto più spesso del previsto.
Gli e-detector richiedono molto meno:

* `MeanEDetector` ha bisogno della media prima del cambiamento e di
  limiti sui valori.
* `QuantileEDetector` ha bisogno solo di un quantile prima del
  cambiamento.

La loro ARL è almeno pari all'obiettivo per **ogni** distribuzione con
quella media o quel quantile:

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

In pratica il quantile prima del cambiamento si stima da un periodo
tranquillo. La garanzia vale allora approssimativamente, tanto meglio
quanto più lungo è quel periodo.

## Scegliere l'ARL

L'ARL bilancia falsi allarmi e ritardo. Con una lettura al minuto,
un'ARL di 1.000 letture significa un falso allarme ogni 17 ore circa di
funzionamento normale, per sensore. Con 50 sensori sono circa 70 al
giorno. Scegliete l'ARL in base al numero di falsi allarmi al giorno che
potete permettervi sull'insieme dei sensori: qui un'ARL di 1.000.000 di
letture porta i 50 sensori a circa un falso allarme ogni due settimane.
Costa meno di quanto sembri, perché il ritardo di rilevamento cresce
solo con il logaritmo dell'ARL. Per CUSUM la soglia passa da 6,9 a 13,8
e il ritardo all'incirca raddoppia.

Questi rilevatori sono strumenti di monitoraggio, non sistemi di
sicurezza. Non usateli al posto di un sistema strumentato di sicurezza
certificato.

Per approfondire: [tutorial: monitoraggio di processo e rilevamento di cambiamenti](../../tutorials/monitoring.md),
[regimi con modelli di Markov nascosti](../../tutorials/regimes.md),
[riferimento: rilevamento di cambiamenti](../../reference/detection.md).
