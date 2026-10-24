---
description: Konfidenzfolgen (confidence sequences) sind Konfidenzintervalle, die bei allen Stichprobenumfängen zugleich gültig bleiben und sich daher laufend überwachen lassen. Wie man sie in Python für einen beschränkten Mittelwert, einen Median oder ein Quantil und einen Mittelwert mit schweren Rändern berechnet, mit sequential-analysis.
language: de
---

# Wie bekomme ich ein Konfidenzintervall, das gültig bleibt, wenn ich immer wieder hinschaue?

> Dies ist eine Übersetzung der [englischen Seite](../../guide/confidence-sequences.md). Sie wurde noch nicht von einer Muttersprachlerin oder einem Muttersprachler geprüft; wo die beiden voneinander abweichen, ist die englische Seite maßgeblich.

**Kurze Antwort.** Verwenden Sie eine **Konfidenzfolge (confidence
sequence)**. Das ist eine Folge von Intervallen, eines nach jeder
Beobachtung, die den wahren Wert mit einer Wahrscheinlichkeit von
mindestens 95 % bei allen Stichprobenumfängen gleichzeitig enthält. Sie
dürfen sie beobachten, aufhören, sobald sie schmal genug ist oder die Null
ausschließt, und das Intervall berichten, bei dem Sie aufgehört haben. Ein
gewöhnliches 95-%-Konfidenzintervall verspricht 95 % nur bei einem einzigen,
vorab festgelegten Stichprobenumfang.

| Was geschätzt wird | Annahme | Prozedur | Garantie |
|---|---|---|---|
| Mittelwert beschränkter Daten (Raten, Scores, gedeckelter Umsatz) | Werte in `[lower, upper]` | `BettingConfidenceSequence` | exact |
| Median, 90. Perzentil, beliebiges Quantil | keine | `QuantileConfidenceSequence` | exact |
| Mittelwert mit schweren Rändern oder Ausreißern | eine Schranke für die Standardabweichung | `CatoniConfidenceSequence` | exact |
| Mittelwert normalverteilter Daten, Varianz unbekannt | Normalverteilung | `TMixtureSPRT` (`lower`, `upper`) | exact unter Normalverteilung |
| Mittelwert beliebiger Daten, lange Läufe | endliche Varianz | `AsymptoticConfidenceSequence` | asymptotic |
| Differenz zwischen zwei Gruppen | siehe [A/B-Tests](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## Das übliche Intervall versagt unter Beobachtung

Ziehen Sie 500 Beobachtungen einer 0/1-Variablen mit Mittelwert 0,3 und
berechnen Sie ab der 30. nach jeder Beobachtung das 95-%-Intervall aus dem
Lehrbuch: Mittelwert ± 1,96 Standardfehler. In wie vielen von 100 Läufen
verfehlt das Intervall irgendwann den wahren Mittelwert?

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

Seine „95 %“ gelten nur bei einem vorab festgelegten Stichprobenumfang. Die
Konfidenzfolge für dieselben Daten, konstruiert über Wetten (betting;
Waudby-Smith and Ramdas 2024), verfehlt den wahren Wert konstruktionsbedingt
in höchstens 5 % der Läufe bei irgendeinem n:

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

## Eine Median-Latenz, ganz ohne Annahmen

Latenzen sind schief und haben schwere Ränder, deshalb ist ein Intervall
„Mittelwert ± Standardfehler“ für sie nicht vertrauenswürdig.
`QuantileConfidenceSequence` deckt jedes Quantil jeder Verteilung ab,
Bindungen eingeschlossen:

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

Die wahren Werte sind 120 ms und 258,8 ms. Beide Intervalle gelten bei allen
2.000 Stichprobenumfängen gleichzeitig.

## Fallstricke

* **Schranken und Deckelungen sind Teil der Annahme.** Wählen Sie `lower`
  und `upper`, bevor Sie die Daten sehen. Ein Wert außerhalb wird
  zurückgewiesen.
* **Keine Methode liefert exakte Überdeckung für den Mittelwert beliebiger
  unbeschränkter Daten.** Verwenden Sie für solche Daten ein Quantil,
  deckeln Sie die Werte, nehmen Sie eine Schranke für die
  Standardabweichung an (Catoni) oder akzeptieren Sie eine asymptotische
  Folge.
* **Konfidenzfolgen sind breiter als ein einzelnes Intervall** beim
  gleichen Stichprobenumfang. Die Breite ist der Preis dafür, bei allen
  Stichprobenumfängen zugleich gültig zu sein.

Mehr: [Welche Methode?](../../choosing.md),
[Referenz: jederzeit gültige und nichtparametrische Verfahren](../../reference/anytime.md).
