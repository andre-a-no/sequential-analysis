---
description: Ciągi ufności (confidence sequences) to przedziały ufności ważne jednocześnie przy każdej liczebności próby, dzięki czemu można je monitorować w sposób ciągły. Jak obliczyć je w Pythonie dla ograniczonej średniej, mediany lub kwantyla oraz średniej o ciężkich ogonach, z sequential-analysis.
language: pl
---

# Jak uzyskać przedział ufności, który pozostaje ważny, gdy wciąż patrzę na wyniki?

> To jest tłumaczenie [strony w języku angielskim](../../guide/confidence-sequences.md). Nie zostało jeszcze sprawdzone przez rodzimego użytkownika języka; w razie rozbieżności rozstrzyga wersja angielska.

**Krótka odpowiedź.** Użyj **ciągu ufności** (confidence sequence). Jest to
ciąg przedziałów, po jednym po każdej obserwacji, który z prawdopodobieństwem
co najmniej 95% zawiera prawdziwą wartość jednocześnie przy wszystkich
liczebnościach próby. Możesz go obserwować, zatrzymać się, gdy jest
wystarczająco wąski lub wyklucza zero, i podać przedział, przy którym się
zatrzymałeś. Zwykły 95-procentowy przedział ufności obiecuje 95% tylko przy
jednej, z góry ustalonej liczebności próby.

| Co szacujesz | Założenie | Procedura | Gwarancja |
|---|---|---|---|
| średnia danych ograniczonych (odsetki, oceny, przychód z limitem) | wartości w `[lower, upper]` | `BettingConfidenceSequence` | exact |
| mediana, 90. percentyl, dowolny kwantyl | brak | `QuantileConfidenceSequence` | exact |
| średnia przy ciężkich ogonach lub obserwacjach odstających | ograniczenie odchylenia standardowego | `CatoniConfidenceSequence` | exact |
| średnia danych normalnych, nieznana wariancja | normalność | `TMixtureSPRT` (`lower`, `upper`) | exact przy normalności |
| średnia dowolnych danych, długie przebiegi | skończona wariancja | `AsymptoticConfidenceSequence` | asymptotic |
| różnica między dwoma wariantami | zob. [testy A/B](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## Zwykły przedział zawodzi, gdy się go obserwuje

Wylosuj 500 obserwacji zmiennej 0/1 o średniej 0,3 i od 30. obserwacji
obliczaj po każdej podręcznikowy przedział 95%: średnia ± 1,96 błędu
standardowego. W ilu na 100 przebiegów przedział w którymś momencie nie
obejmuje prawdziwej średniej?

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

Jego „95%” obowiązuje tylko przy liczebności próby ustalonej z góry. Ciąg
ufności dla tych samych danych, oparty na zakładach (betting; Waudby-Smith
i Ramdas 2024), z konstrukcji chybia przy jakimś n w co najwyżej 5%
przebiegów:

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

## Mediana opóźnienia bez żadnych założeń

Opóźnienia mają rozkład skośny o ciężkich ogonach, więc przedział postaci
średnia ± błąd standardowy nie jest dla nich wiarygodny.
`QuantileConfidenceSequence` obejmuje dowolny kwantyl dowolnego rozkładu,
także przy wartościach powtarzających się (ties):

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

Prawdziwe wartości to 120 ms i 258,8 ms. Oba przedziały obowiązują
jednocześnie przy wszystkich 2000 liczebnościach próby.

## Pułapki

* **Granice i limity są częścią założenia.** Wybierz `lower` i `upper`
  przed obejrzeniem danych. Wartość spoza nich zostanie odrzucona.
* **Żadna metoda nie daje dokładnego pokrycia dla średniej dowolnych
  nieograniczonych danych.** Dla takich danych użyj kwantyla, ogranicz
  wartości, załóż ograniczenie odchylenia standardowego (Catoni) albo
  zaakceptuj ciąg asymptotyczny.
* **Ciągi ufności są szersze niż pojedynczy przedział** przy tej samej
  liczebności próby. Szerokość to cena za ważność jednocześnie przy każdej
  liczebności próby.

Więcej: [Która metoda?](../../choosing.md),
[dokumentacja: metody anytime-valid i nieparametryczne](../../reference/anytime.md).
