---
description: Wie man in Python eine Änderung in einem Strom von Sensormesswerten, Latenzen oder Metriken erkennt, mit CUSUM, Shiryaev–Roberts, nichtparametrischen E-Detektoren und bayesscher Online-Change-Point-Erkennung. Fehlalarme werden über die mittlere Lauflänge (ARL) kontrolliert, mit sequential-analysis.
language: de
---

# Wie erkenne ich eine Änderung in einem Strom von Messwerten?

> Dies ist eine Übersetzung der [englischen Seite](../../guide/change-detection.md). Sie wurde noch nicht von einer Muttersprachlerin oder einem Muttersprachler geprüft; wo die beiden voneinander abweichen, ist die englische Seite maßgeblich.

**Kurze Antwort.** Verwenden Sie einen Online-Detektor für Change Points
(Strukturbrüche; change-point detector). Er beobachtet den Strom und löst
einen Alarm aus, sobald sich die Verteilung offenbar geändert hat. Seine
Fehlalarme werden über die **mittlere Lauflänge** (average run length, ARL)
kontrolliert: die erwartete Zahl von Beobachtungen bis zu einem Fehlalarm,
solange sich nichts geändert hat. In sequential-analysis:

| Was Sie vor der Änderung wissen | Prozedur | Garantie |
|---|---|---|
| beide Verteilungen (z. B. normal, Mittelwert 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| nur den Mittelwert und Schranken für die Werte | `MeanEDetector` | exact für jede solche Verteilung |
| nur ein Quantil (z. B. das 95. Perzentil der Latenz) | `QuantileEDetector` | exact für jede Verteilung |
| ein Modell mit unbekannten Parametern, vorher und nachher | `BayesianChangePoint` | unter dem Modell und der Prior-Verteilung |

## Ein Sensor, dessen Mittelwert sich verschiebt

Ein Temperatursensor misst 70,0 °C mit einem Rauschen mit
Standardabweichung 0,5. Ab Messwert 600 beträgt der Mittelwert 70,4. CUSUM
mit der Schwelle log(1000) ≈ 6,9 hat eine ARL von mindestens 1.000
Messwerten:

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

Eine Verschiebung um weniger als eine Standardabweichung ist mit bloßem
Auge in keinem einzelnen Messwert sichtbar. CUSUM sammelt die Evidenz an
und findet sie.

## Wenn die Messwerte nicht normalverteilt sind

Die ARL von CUSUM gilt nur, wenn die Messwerte den Verteilungen folgen, die
Sie ihm vorgegeben haben. Bei schiefen Daten (Schwingungsamplituden,
Latenzen, Warteschlangenlängen) löst es weit häufiger Fehlalarme aus als
geplant. Die E-Detektoren (e-detectors) brauchen viel weniger:

* `MeanEDetector` braucht den Mittelwert vor der Änderung und Schranken für
  die Werte.
* `QuantileEDetector` braucht nur ein Quantil vor der Änderung.

Ihre ARL liegt für **jede** Verteilung mit diesem Mittelwert bzw. Quantil
mindestens beim Zielwert:

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

In der Praxis wird das Quantil vor der Änderung aus einer ruhigen Phase
geschätzt. Die Garantie gilt dann näherungsweise, und zwar umso besser, je
länger diese Phase ist.

## Die Wahl der ARL

Die ARL wägt Fehlalarme gegen Verzögerung ab. Bei einem Messwert pro Minute
bedeutet eine ARL von 1.000 Messwerten etwa alle 17 Stunden Normalbetrieb
einen Fehlalarm, pro Sensor. Bei 50 Sensoren sind das etwa 70 pro Tag.
Wählen Sie die ARL nach der Zahl der Fehlalarme pro Tag, die Sie sich über
alle Sensoren zusammen leisten können: Hier bringt eine ARL von 1.000.000
Messwerten die 50 Sensoren auf etwa einen Fehlalarm alle zwei Wochen. Das
kostet weniger, als es scheint, denn die Erkennungsverzögerung wächst nur
mit dem Logarithmus der ARL. Bei CUSUM steigt die Schwelle von 6,9 auf 13,8,
und die Verzögerung verdoppelt sich ungefähr.

Diese Detektoren sind Überwachungswerkzeuge, keine Sicherheitssysteme.
Verwenden Sie sie nicht anstelle eines zertifizierten sicherheitstechnischen
Systems (Safety Instrumented System).

Mehr: [Tutorial: Prozessüberwachung und Change-Point-Erkennung](../../tutorials/monitoring.md),
[Regime mit Hidden-Markov-Modellen](../../tutorials/regimes.md),
[Referenz: Änderungserkennung](../../reference/detection.md).
