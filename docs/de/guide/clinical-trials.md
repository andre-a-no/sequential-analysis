---
description: Wie man Zwischenanalysen einer klinischen Studie in Python plant und durchführt, mit gruppensequentiellen Designs (O'Brien–Fleming, Pocock, Alpha-Spending nach Lan–DeMets, Futility-Grenzen) und Fallzahlen für Mittelwerte, Anteile und Überlebenszeiten, abgeglichen mit rpact, mit sequential-analysis.
language: de
---

# Wie plane ich Zwischenanalysen einer klinischen Studie?

> Dies ist eine Übersetzung der [englischen Seite](../../guide/clinical-trials.md). Sie wurde noch nicht von einer Muttersprachlerin oder einem Muttersprachler geprüft; wo die beiden voneinander abweichen, ist die englische Seite maßgeblich.

**Kurze Antwort.** Verwenden Sie ein gruppensequentielles Design (group
sequential design). `group_sequential_design(alpha, fractions, spending=...)`
aus `sequential_analysis.group_sequential` berechnet:

* die Wirksamkeitsgrenzen mit Alpha-Spending (alpha spending) nach
  Lan–DeMets (vom Typ O'Brien–Fleming, vom Typ Pocock und weitere);
* nicht bindende Futility-Grenzen (non-binding futility boundaries);
* Power und erwarteten Stichprobenumfang;
* die maximale Fallzahl für Mittelwerte und Anteile bzw. die Zahl der
  Ereignisse für Überlebenszeiten.

Die Grenzen und Fallzahlen stimmen mit dem R-Paket rpact überein. Die
Testprozeduren (`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) führen dann die
Studie durch, Patient für Patient oder Ereignis für Ereignis. Jede
Zwischenanalyse führen sie aus, sobald ihr Informationsanteil (information
fraction) erreicht ist.

## Design: vier Analysen, Spending nach O'Brien–Fleming

Einseitiges α = 0,025, Analysen bei 25 %, 50 %, 75 % und 100 % der
Patienten, 90 % Power, mit einer Futility-Grenze:

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

## Binäre Endpunkte und Überlebenszeit-Endpunkte

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

Mit Spending nach O'Brien–Fleming kosten drei Analysen 1,3 % mehr Patienten
als eine einzige abschließende Analyse.

## Durchführung der Studie

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

Die Studie wurde bei der zweiten Analyse wegen Wirksamkeit beendet, nach
zwei Dritteln der geplanten Patienten.

## Wenn die Analysen nicht wie geplant stattfinden

Data Monitoring Committees tagen selten genau bei 25 % der Information:

* `design.at(fractions)` berechnet die Grenzen für die tatsächlich
  erreichte Information neu. Das Alpha-Spending hält das Gesamtniveau ein.
* `GroupSequentialMonitor` nimmt jede Statistik, die Sie selbst berechnen
  (ein Cox-Modell, ein gemischtes Modell), als Z-Wert samt ihrer
  Information bei jeder Sitzung entgegen.

## Und wenn Sie nach jedem Patienten hinschauen wollen?

Ein gruppensequentielles Design erlaubt nur die geplante Zahl von Blicken.
Um nach jedem Patienten oder Ereignis zu überwachen, verwenden Sie eine
jederzeit gültige Prozedur (anytime-valid): `AnytimeLogRankTest` für
Überlebenszeiten, `TwoProportionTest` für Ansprechraten, `TMixtureSPRT` für
einen Mittelwert. Beim geplanten Effekt brauchen sie mehr Patienten. Siehe
[Tutorial: Überlebenszeitstudie](../../tutorials/survival.md).

## Regulatorische Praxis

Gruppensequentielle Designs mit Alpha-Spending sind der etablierte Ansatz
in konfirmatorischen Studien, beschrieben in der Leitlinie ICH E9 und in
der FDA-Guidance zu adaptiven Designs (2019). Diese Bibliothek berechnet die
Designs und führt eine prüfbare, fortsetzbare Aufzeichnung jeder Analyse
(den Checkpoint und seinen History-Digest). Sie ist keine validierte
Software im regulatorischen Sinn: Ein Sponsor, der sie in einer Einreichung
verwendet, muss sie wie jedes andere Werkzeug validieren.

Mehr: [Tutorial: gruppensequentielle Studie](../../tutorials/group-sequential.md),
das die Zahlen mit rpact vergleicht;
[Referenz: Design und Planung](../../reference/design.md).
