---
description: Warum das tägliche Prüfen eines p-Werts die falsch-positiven Ergebnisse in A/B-Tests und Studien erhöht (das Peeking-Problem), und die drei Familien sequentieller Methoden, die es beheben, in Python mit sequential-analysis.
language: de
---

# Warum darf ich nicht jeden Tag auf einen p-Wert schauen?

> Dies ist eine Übersetzung der [englischen Seite](../../guide/peeking.md). Sie wurde noch nicht von einer Muttersprachlerin oder einem Muttersprachler geprüft; wo die beiden voneinander abweichen, ist die englische Seite maßgeblich.

**Kurze Antwort.** Ein Test mit festem Stichprobenumfang verspricht eine
Falsch-positiv-Rate (false positive rate) von 5 % nur, wenn man das Ergebnis einmal ansieht, beim
geplanten Stichprobenumfang. Wer wiederholt hinschaut und beim ersten
p < 0,05 aufhört, gibt dem Zufall viele Gelegenheiten, ihn zu täuschen. Bei
20 Blicken steigt die Falsch-positiv-Rate auf etwa 25 %. Sequentielle
Methoden sind dafür gebaut, wiederholt angeschaut zu werden. Mit ihnen
bleibt die Rate bei höchstens 5 %, wie oft man auch hinschaut und wann man
auch aufhört.

## Das Peeking-Problem, gemessen

Zwei Gruppen mit derselben Konversionsrate von 10 % (ein A/A-Test),
2.000 Nutzer, 200 Wiederholungen. Beim „Peeking“ (wiederholtes
Zwischenauswerten) wird nach jeweils 100 Nutzern der übliche z-Test für zwei
Anteile gerechnet und beim ersten p < 0,05 gestoppt. Der sequentielle
`TwoProportionTest` wird nach jedem einzelnen Nutzer geprüft:

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

Der einzelne Blick hält sein Versprechen. Zwanzig Blicke erhöhen die Fehlerrate
etwa auf das Sechsfache. Der sequentielle Test, nach jedem der
2.000 Nutzer angeschaut, hält sie bei 5 %. Das ist das Versprechen: Seine
Garantie ist **exact** (`TwoProportionTest.guarantee == "exact"`), eine
Falsch-positiv-Rate von höchstens 5 % bei jedem Stichprobenumfang, wie oft
man auch hinschaut. Bei 200 Wiederholungen sind 10 falsch-positive
Ergebnisse genau das, was exakte 5 % ergeben.

## Die drei Familien sequentieller Methoden

| Familie | Hinschauen erlaubt | Typische Anwendung | In sequential-analysis |
|---|---|---|---|
| **Sequentielle Wahrscheinlichkeitsquotiententests** (sequential probability ratio tests; Wald 1945) | nach jeder Beobachtung | eine einfache Hypothese gegen eine andere, im Mittel die wenigsten Beobachtungen: Qualitätskontrolle, Simulation, Psychophysik | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Gruppensequentielle Designs** (group sequential designs; Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | bei wenigen geplanten Zwischenanalysen | klinische Studien mit einem Data Monitoring Committee | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Jederzeit gültige Inferenz** (anytime-valid inference): E-Werte, Konfidenzfolgen, Mixture-SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | nach jeder Beobachtung, Abbruch aus beliebigem Grund | Online-A/B-Tests, Monitoring-Dashboards | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**Was es kostet.** Häufigeres Hinschauen braucht beim geplanten Effekt mehr
Daten:

* ein gruppensequentielles Design mit vier Analysen braucht 1–20 % mehr
  Patienten als eine einzelne Analyse;
* ein jederzeit gültiger Test für zwei Anteile braucht das 1,3- bis
  1,6-Fache der Nutzer einer einzelnen Analyse.

Im Gegenzug stoppt ein großer Effekt das Experiment früh, und niemand muss
den Stichprobenumfang vorab festlegen.

## Wann das nicht das Problem ist

Peeking erhöht die Fehler nur, wenn das, was man tut, davon abhängt, was
man gesehen hat. Wer auf das Dashboard schaut, das Experiment aber immer bis
zum geplanten Umfang laufen lässt und einmal testet, für den ist der Test
mit festem Stichprobenumfang gültig. In diesem Fall ist er zudem die
effizienteste Wahl.

Weiter: [einen A/B-Test vorzeitig beenden](ab-testing.md),
[Konfidenzfolgen](confidence-sequences.md),
[das Glossar](glossary.md).
