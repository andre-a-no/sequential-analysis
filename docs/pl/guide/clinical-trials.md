---
description: Jak w Pythonie zaplanować i przeprowadzić analizy pośrednie badania klinicznego za pomocą planów grupowo-sekwencyjnych (O'Brien–Fleming, Pocock, wydatkowanie alfa Lana–DeMetsa, granice daremności), z liczebnością próby dla średnich, proporcji i przeżycia, sprawdzoną względem rpact, z sequential-analysis.
language: pl
---

# Jak zaplanować analizy pośrednie badania klinicznego?

> To jest tłumaczenie [strony w języku angielskim](../../guide/clinical-trials.md). Nie zostało jeszcze sprawdzone przez rodzimego użytkownika języka; w razie rozbieżności rozstrzyga wersja angielska.

**Krótka odpowiedź.** Użyj planu grupowo-sekwencyjnego (group sequential design).
`group_sequential_design(alpha, fractions, spending=...)` z
`sequential_analysis.group_sequential` oblicza:

* granice skuteczności z wydatkowaniem alfa (alpha spending) Lana–DeMetsa
  (typu O'Brien–Fleming, typu Pocock i inne);
* niewiążące granice daremności (futility boundaries);
* moc i oczekiwaną liczebność próby;
* maksymalną liczebność próby dla średnich i proporcji albo liczbę zdarzeń
  dla analizy przeżycia.

Granice i liczebności prób są zgodne z pakietem R rpact. Następnie procedury
testowe (`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) prowadzą badanie,
pacjent po pacjencie lub zdarzenie po zdarzeniu. Każdą analizę pośrednią
(interim analysis) wykonują w chwili osiągnięcia jej ułamka informacji
(information fraction).

## Plan: cztery analizy, wydatkowanie O'Briena–Fleminga

Jednostronne α = 0,025, analizy przy 25%, 50%, 75% i 100% pacjentów, moc
90%, z granicą daremności:

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

## Binarne punkty końcowe i przeżycie

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

Przy wydatkowaniu O'Briena–Fleminga trzy analizy kosztują o 1,3% więcej
pacjentów niż pojedyncza analiza końcowa.

## Prowadzenie badania

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

Badanie zakończono z powodu skuteczności przy drugiej analizie, po dwóch
trzecich zaplanowanych pacjentów.

## Gdy analizy nie odbywają się zgodnie z planem

Komisje monitorujące dane (data monitoring committees) rzadko zbierają się
dokładnie przy 25% informacji:

* `design.at(fractions)` przelicza granice dla rzeczywiście osiągniętej
  informacji. Wydatkowanie alfa utrzymuje łączny poziom istotności.
* `GroupSequentialMonitor` przyjmuje na każdym posiedzeniu dowolną
  statystykę obliczoną samodzielnie (model Coxa, model mieszany) jako
  wartość Z wraz z jej informacją.

## A jeśli chcesz patrzeć na wyniki po każdym pacjencie?

Plan grupowo-sekwencyjny dopuszcza tylko zaplanowaną liczbę sprawdzeń. Aby
monitorować po każdym pacjencie lub zdarzeniu, użyj procedury ważnej
w dowolnym momencie (anytime-valid): `AnytimeLogRankTest` dla przeżycia,
`TwoProportionTest` dla odsetków odpowiedzi, `TMixtureSPRT` dla średniej.
Przy zaplanowanym efekcie wymagają one więcej pacjentów. Zob.
[samouczek: badanie przeżycia](../../tutorials/survival.md).

## Praktyka regulacyjna

Plany grupowo-sekwencyjne z wydatkowaniem alfa to ugruntowane podejście
w badaniach potwierdzających, opisane w wytycznej ICH E9 i w wytycznych FDA
dotyczących planów adaptacyjnych (2019). Ta biblioteka oblicza plany
i prowadzi audytowalny, możliwy do wznowienia zapis każdej analizy (punkt
kontrolny i jego skrót historii). Nie jest oprogramowaniem walidowanym
w sensie regulacyjnym: sponsor używający jej we wniosku rejestracyjnym musi
ją zwalidować jak każde inne narzędzie.

Więcej: [samouczek: badanie grupowo-sekwencyjne](../../tutorials/group-sequential.md),
w którym liczby są porównane z rpact;
[dokumentacja: plan i planowanie](../../reference/design.md).
