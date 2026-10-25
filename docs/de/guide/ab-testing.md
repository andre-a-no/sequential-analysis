---
description: Wie man einen A/B-Test in Python vorzeitig beendet, ohne die falsch-positiven Ergebnisse zu erhöhen. Jederzeit gültige Tests (anytime-valid) für Konversion und beschränkten Umsatz, eine Prüfung auf Sample Ratio Mismatch und Kontrolle der False Discovery Rate über viele Metriken, mit sequential-analysis.
language: de
---

# Wie beende ich einen A/B-Test vorzeitig, ohne die falsch-positiven Ergebnisse zu erhöhen?

> Dies ist eine Übersetzung der [englischen Seite](../../guide/ab-testing.md). Sie wurde noch nicht von einer Muttersprachlerin oder einem Muttersprachler geprüft; wo die beiden voneinander abweichen, ist die englische Seite maßgeblich.

**Kurze Antwort.** Verwenden Sie einen jederzeit gültigen Test
(anytime-valid): Sein p-Wert und sein Konfidenzintervall bleiben gültig, wie
oft Sie auch hinschauen, sodass Sie aufhören dürfen, sobald das Ergebnis
klar ist. In sequential-analysis:

| Metrik | Prozedur | Garantie |
|---|---|---|
| Konversionsrate (0/1) | `TwoProportionTest` | exact |
| jede beschränkte Metrik (gedeckelter Umsatz, Anteil) | `BoundedABTest` | exact |
| Ereignisse pro Expositionseinheit | `RateRatioTest` | exact für Poisson-Zählungen |
| Quotientenmetrik (Umsatz pro Sitzung) | `RatioABTest` | asymptotic |
| Mittelwert mit einer Kovariate aus der Zeit vor dem Experiment (CUPED) | `ABTest` | asymptotic |
| wird der Traffic wie vorgesehen aufgeteilt? | `SampleRatioMismatch` | exact |
| mehrere Metriken oder Gruppen zugleich | `MultipleTests` (e-BH) | False Discovery Rate, exact |

Füttern Sie jede Prozedur Nutzer für Nutzer: `state, out = test.step(state, {...})`.
Handeln Sie nach `out.decision`, wann immer Sie wollen.

## Konversion: stoppen, wenn die Daten eindeutig sind

Die Kontrollgruppe konvertiert 10 % der Nutzer, die Testgruppe 12 %. Der
Test wird nach jedem Nutzer angeschaut und stoppt bei seiner ersten
Entscheidung:

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

Zum Vergleich: Ein Test mit festem Stichprobenumfang und 80 % Power für
diesen Anstieg braucht etwa 3.850 Nutzer pro Gruppe, insgesamt 7.700, und
darf nur einmal ausgewertet werden, am Ende. Der jederzeit gültige Test
bezahlt für seine Freiheit: Um dieselbe Power zu erreichen, braucht er das
1,3- bis 1,6-Fache der Nutzer einer einzelnen Analyse, und dieser Lauf
brauchte noch mehr. Dafür muss kein Stichprobenumfang vorab festgelegt
werden, und Sie dürfen das Ergebnis täglich ansehen und aufhören, sobald es
klar ist. Ist der Effekt größer als geplant, geschieht das viel früher.

## Umsatz: ein exaktes Intervall für eine beschränkte Metrik

`BoundedABTest` braucht nur Schranken für die Metrik. Deckeln Sie den Umsatz
bei einem Wert, den Sie vor dem Test wählen (hier 30), dann ist die
Konfidenzfolge (confidence sequence) für die Differenz der Mittelwerte für
jede Verteilung exakt:

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

Das Intervall gilt bei allen 20.000 Blicken gleichzeitig, nicht nur beim
letzten. Hier enthält es noch die 0: 20.000 Nutzer reichen nicht aus, um
bei einer so verrauschten Metrik einen Anstieg von etwa 0,5 nachzuweisen,
also läuft das Experiment weiter.

## Zuerst die Traffic-Aufteilung prüfen

Ein Sample Ratio Mismatch (SRM) bedeutet, dass die Aufteilung von der
konfigurierten abweicht, etwa wegen eines Fehlers bei der Zuweisung oder
beim Logging. Effektschätzungen aus einem solchen Experiment sind nicht
vertrauenswürdig. Eine Abweichung von 50/50 auf 52/48 wird erkannt, während
das Experiment läuft:

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

## Viele Metriken auf einmal

Wer zehn unabhängige Metriken jeweils zum Niveau 5 % testet, hat eine
Wahrscheinlichkeit von etwa 40 % für mindestens eine falsche Entdeckung.
`MultipleTests` kombiniert die E-Werte (e-values) aller Tests mit dem
e-BH-Verfahren, sodass die False Discovery Rate zu jedem Stoppzeitpunkt bei
`alpha` bleibt:

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

## Fallstricke

* **Randomisieren Sie die Einheit, die Sie analysieren.** Werden Nutzer
  randomisiert, liefern Sie einen Datensatz pro Nutzer, nicht pro
  Seitenaufruf. Für Metriken pro Sitzung verwenden Sie `RatioABTest`, das
  mit Nutzersummen arbeitet.
* **Legen Sie die Obergrenze einer beschränkten Metrik vor dem Test fest.**
  Wer sie erst nach Ansicht der Daten wählt, macht die Garantie hinfällig.
* **Asymptotische Prozeduren brauchen große Stichproben.** Bei `ABTest` und
  `RatioABTest` ist das Intervall nur bei langen Läufen näherungsweise
  gültig. Bevorzugen Sie die exakten Prozeduren, wenn sie passen.
* **Adaptive Traffic-Zuteilung** (Bandits) braucht einen Test, der gültig
  bleibt, wenn die Aufteilung von den Ergebnissen abhängt:
  `TwoProportionTest(method="universal")` oder
  `BoundedABTest(propensity_input=...)`. Siehe
  [Tutorial §10](../../tutorials/ab-test.md).

Mehr: das [A/B-Test-Tutorial](../../tutorials/ab-test.md) (CUPED,
Quotientenmetriken, Raten, Planung der Laufzeit) und
[ein Programm von Experimenten](../../tutorials/experiment-programme.md)
(False Discovery Rate über viele Experimente).
