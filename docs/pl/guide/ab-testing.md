---
description: Jak wcześniej zakończyć test A/B w Pythonie bez zawyżania liczby wyników fałszywie dodatnich. Testy ważne w dowolnym momencie (anytime-valid) dla konwersji i ograniczonego przychodu, kontrola niezgodności proporcji próby (SRM) i kontrola odsetka fałszywych odkryć (FDR) dla wielu metryk, z sequential-analysis.
language: pl
---

# Jak wcześniej zakończyć test A/B bez zawyżania liczby wyników fałszywie dodatnich?

> To jest tłumaczenie [strony w języku angielskim](../../guide/ab-testing.md). Nie zostało jeszcze sprawdzone przez rodzimego użytkownika języka; w razie rozbieżności rozstrzyga wersja angielska.

**Krótka odpowiedź.** Użyj testu ważnego w dowolnym momencie (anytime-valid):
jego wartość p (p-value) i przedział ufności pozostają ważne bez względu na to,
jak często patrzysz na wyniki, więc możesz przerwać test, gdy tylko wynik
stanie się jasny. W sequential-analysis:

| Metryka | Procedura | Gwarancja |
|---|---|---|
| współczynnik konwersji (0/1) | `TwoProportionTest` | exact |
| dowolna ograniczona metryka (przychód z limitem, udział) | `BoundedABTest` | exact |
| zdarzenia na jednostkę ekspozycji | `RateRatioTest` | exact dla zliczeń Poissona |
| metryka ilorazowa (przychód na sesję) | `RatioABTest` | asymptotic |
| średnia z kowariantą sprzed eksperymentu (CUPED) | `ABTest` | asymptotic |
| czy ruch jest podzielony zgodnie z założeniem? | `SampleRatioMismatch` | exact |
| kilka metryk lub wariantów jednocześnie | `MultipleTests` (e-BH) | odsetek fałszywych odkryć, exact |

Podawaj każdej procedurze dane po jednym użytkowniku: `state, out = test.step(state, {...})`.
Na `out.decision` możesz reagować w dowolnym momencie.

## Konwersja: zakończ, gdy dane są rozstrzygające

W grupie kontrolnej konwertuje 10% użytkowników, w grupie testowej 12%. Test
jest sprawdzany po każdym użytkowniku i kończy się przy pierwszej decyzji:

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

Dla porównania: test o stałej liczebności próby (fixed-sample test) z mocą
80% dla takiego wzrostu wymaga około 3850 użytkowników na wariant, łącznie
7700, i wolno go odczytać tylko raz, na końcu. Test ważny w dowolnym
momencie płaci za swoją swobodę: aby osiągnąć tę samą moc, potrzebuje
1,3–1,6 raza więcej użytkowników niż pojedyncza analiza, a w tym przebiegu
potrzebował jeszcze więcej. W zamian nie trzeba z góry ustalać liczebności
próby, a wynik można sprawdzać codziennie i przerwać test, gdy tylko stanie
się jasny. Gdy efekt jest większy niż zakładano, następuje to znacznie
wcześniej.

## Przychód: dokładny przedział dla ograniczonej metryki

`BoundedABTest` potrzebuje jedynie granic metryki. Ogranicz przychód do
wartości wybranej przed testem (tutaj 30), a ciąg ufności (confidence
sequence) dla różnicy średnich będzie dokładny dla dowolnego rozkładu:

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

Przedział obowiązuje jednocześnie przy każdym z 20 000 sprawdzeń, a nie
tylko przy ostatnim. Tutaj nadal zawiera 0: 20 000 użytkowników nie wystarcza,
by wykazać wzrost o około 0,5 przy metryce o tak dużym szumie, więc
eksperyment trwa dalej.

## Najpierw sprawdź podział ruchu

Niezgodność proporcji próby (sample ratio mismatch, SRM) oznacza, że podział
różni się od skonfigurowanego, na przykład z powodu błędu w przydziale lub
w logowaniu. Oszacowaniom efektu z takiego eksperymentu nie można ufać.
Odchylenie od podziału 50/50 do 52/48 zostaje wychwycone w trakcie
eksperymentu:

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

## Wiele metryk naraz

Testowanie dziesięciu niezależnych metryk, każdej na poziomie 5%, daje około
40% szans na co najmniej jedno fałszywe odkrycie. `MultipleTests` łączy
e-wartości (e-values) wszystkich testów procedurą e-BH, dzięki czemu odsetek
fałszywych odkryć (false discovery rate) pozostaje na poziomie `alpha` przy
dowolnym momencie zatrzymania:

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

## Pułapki

* **Randomizuj tę jednostkę, którą analizujesz.** Jeśli randomizowani są
  użytkownicy, podawaj jeden rekord na użytkownika, a nie na odsłonę strony.
  Dla metryk liczonych na sesję użyj `RatioABTest`, który działa na sumach
  dla użytkowników.
* **Ustal limit ograniczonej metryki przed testem.** Wybranie go po
  obejrzeniu danych unieważnia gwarancję.
* **Procedury asymptotyczne wymagają dużych prób.** Dla `ABTest`
  i `RatioABTest` przedział jest ważny jedynie w przybliżeniu w długich
  przebiegach. Gdy to możliwe, wybieraj procedury dokładne.
* **Adaptacyjny przydział ruchu** (bandyci wielorękie, bandits) wymaga testu,
  który pozostaje ważny, gdy podział zależy od wyników:
  `TwoProportionTest(method="universal")` lub
  `BoundedABTest(propensity_input=...)`. Zob.
  [samouczek §10](../../tutorials/ab-test.md).

Więcej: [samouczek o testach A/B](../../tutorials/ab-test.md) (CUPED, metryki
ilorazowe, częstości, planowanie czasu trwania) oraz
[program eksperymentów](../../tutorials/experiment-programme.md)
(odsetek fałszywych odkryć w wielu eksperymentach).
