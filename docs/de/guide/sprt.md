---
description: Wie man Walds sequentiellen Wahrscheinlichkeitsquotiententest (SPRT) in Python mit sequential-analysis durchführt. Fehlerraten, mittlerer Stichprobenumfang im Vergleich zu einem Test mit festem Stichprobenumfang und die gestutzten Alternativen (2-SPRT, optimale Kiefer–Weiss-Pläne).
language: de
---

# Wie führe ich Walds SPRT in Python durch?

> Dies ist eine Übersetzung der [englischen Seite](../../guide/sprt.md). Sie wurde noch nicht von einer Muttersprachlerin oder einem Muttersprachler geprüft; wo die beiden voneinander abweichen, ist die englische Seite maßgeblich.

**Kurze Antwort.** `SPRT(family, theta0, theta1, alpha, beta)` aus
`sequential_analysis.procedures` implementiert Walds sequentiellen
Wahrscheinlichkeitsquotiententest (sequential probability ratio test,
SPRT). Er entscheidet zwischen zwei einfachen Hypothesen mit im Mittel den
wenigsten Beobachtungen. Füttern Sie ihn Beobachtung für Beobachtung und
hören Sie bei der ersten Entscheidung auf. Im Beispiel unten braucht er
etwa halb so viele Beobachtungen wie ein Test mit festem Stichprobenumfang
und denselben Fehlerraten: im Mittel 65–76 Teile statt 133. Wenn Sie einen
garantierten maximalen Stichprobenumfang brauchen, verwenden Sie
stattdessen `TwoSPRT` oder einen Plan aus `kiefer_weiss_plan`.

## Beispiel: Liegt die Ausschussquote bei 10 % oder bei 20 %?

Ein Los wird angenommen, wenn seine Ausschussquote 10 % beträgt, und
abgelehnt, wenn sie 20 % beträgt, mit beiden Fehlerraten bei 5 %:

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

Wie schlägt er sich über viele Lose?

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

Ein Test mit festem Stichprobenumfang und denselben Fehlerraten prüft in
jedem Los etwa 133 Teile (Normalapproximation). Der SPRT prüft im Mittel
43–51 % weniger. Sein Stichprobenumfang ist allerdings zufällig und nach
oben unbeschränkt, und einige Lose dauern viel länger als der Durchschnitt.

Die Schwellen sind die von Wald: log((1 − β)/α) und log(β/(1 − α)). Sie
garantieren für jeden Stichprobenumfang beim Stoppen, dass die tatsächlichen
Fehlerraten α′ und β′ die Ungleichungen α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) und
α′ + β′ ≤ α + β erfüllen. Der Likelihood-Quotient schießt beim Stoppen über
die Schwellen hinaus, deshalb liegen die Raten in der Praxis unter den
nominalen, wie hier. In diesem Sinne gilt `SPRT.guarantee == "exact"`. Für
exakt berechnete statt nur beschränkte Fehlerraten verwenden Sie
`operating_characteristic` auf einem Plan (siehe unten).

## Wenn Sie einen maximalen Stichprobenumfang brauchen

* `TwoSPRT` (Lordens 2-SPRT) stoppt spätestens bei einem festen Horizont
  und minimiert nahezu den erwarteten Stichprobenumfang im ungünstigsten
  Fall.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  in `sequential_analysis.design` berechnet den optimalen Plan mit einem
  maximalen Stichprobenumfang durch Rückwärtsinduktion. `PlanTest` führt
  ihn aus, und `operating_characteristic` liefert seine exakten Fehlerraten
  und den erwarteten Stichprobenumfang ohne Simulation. Siehe
  `examples/07_design_kiefer_weiss.py`.
* Für wenige geplante Blicke statt eines Blicks pro Beobachtung verwenden
  Sie ein [gruppensequentielles Design](clinical-trials.md).

## Wann der SPRT das falsche Werkzeug ist

* **Die Hypothesen sind nicht einfach.** „Die Rate ist 10 %“ gegen „die
  Rate ist irgendetwas anderes“ ist eine zusammengesetzte Alternative.
  Verwenden Sie einen Mixture-SPRT (`NormalMixtureSPRT`, `TMixtureSPRT`)
  oder einen Test über Wetten (`BettingMeanTest`); beide sind gegen jede
  Alternative jederzeit gültig (anytime-valid).
* **Der wahre Wert liegt zwischen θ₀ und θ₁.** Dann ist der SPRT am
  langsamsten, und sein erwarteter Stichprobenumfang kann den festen
  Stichprobenumfang übersteigen. Der Kiefer–Weiss-Plan ist genau für diesen
  Fall gebaut.

Für Likelihood-Quotienten-Prozeduren verfügbare Verteilungsfamilien:
`Gaussian` (bekannte Varianz), `Bernoulli`, `Poisson`, `Exponential`.
