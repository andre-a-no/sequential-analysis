---
description: Jak uruchomić w Pythonie sekwencyjny test ilorazu prawdopodobieństw Walda (SPRT) z sequential-analysis. Poziomy błędów, średnia liczebność próby w porównaniu z testem o stałej liczebności próby oraz obcięte alternatywy (2-SPRT, optymalne plany Kiefera–Weissa).
language: pl
---

# Jak uruchomić test SPRT Walda w Pythonie?

> To jest tłumaczenie [strony w języku angielskim](../../guide/sprt.md). Nie zostało jeszcze sprawdzone przez rodzimego użytkownika języka; w razie rozbieżności rozstrzyga wersja angielska.

**Krótka odpowiedź.** `SPRT(family, theta0, theta1, alpha, beta)` z
`sequential_analysis.procedures` implementuje sekwencyjny test ilorazu
prawdopodobieństw Walda (sequential probability ratio test, SPRT).
Rozstrzyga między dwiema hipotezami prostymi przy średnio najmniejszej
liczbie obserwacji. Podawaj mu po jednej obserwacji i zatrzymaj się przy
pierwszej decyzji. W poniższym przykładzie potrzebuje mniej więcej połowy
obserwacji testu o stałej liczebności próby przy tych samych poziomach
błędów: średnio 65–76 sztuk zamiast 133. Jeśli potrzebujesz gwarantowanej
maksymalnej liczebności próby, użyj zamiast niego `TwoSPRT` lub planu
z `kiefer_weiss_plan`.

## Przykład: czy odsetek wad wynosi 10%, czy 20%?

Partia jest przyjmowana, jeśli jej odsetek wad wynosi 10%, i odrzucana, jeśli
wynosi 20%, przy obu poziomach błędów równych 5%:

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

Jak radzi sobie na wielu partiach?

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

Test o stałej liczebności próby przy tych samych poziomach błędów sprawdza
w każdej partii około 133 sztuk (przybliżenie normalne). SPRT sprawdza
średnio o 43–51% mniej. Jego liczebność próby jest jednak losowa i nie ma
górnej granicy, a niektóre partie wymagają znacznie więcej niż średnio.

Progi są progami Walda: log((1 − β)/α) i log(β/(1 − α)). Gwarantują one, przy
dowolnej liczebności próby w momencie zatrzymania, że rzeczywiste poziomy
błędów α′ i β′ spełniają α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) oraz α′ + β′ ≤ α + β.
Iloraz wiarygodności w chwili zatrzymania przekracza próg z nadmiarem
(overshoot), więc w praktyce poziomy błędów są niższe od nominalnych, jak
tutaj. W tym sensie `SPRT.guarantee == "exact"`. Aby uzyskać poziomy błędów
obliczone dokładnie, a nie tylko ograniczone, użyj `operating_characteristic`
na planie (poniżej).

## Gdy potrzebujesz maksymalnej liczebności próby

* `TwoSPRT` (2-SPRT Lordena) zatrzymuje się najpóźniej przy ustalonym
  horyzoncie i prawie minimalizuje oczekiwaną liczebność próby w najgorszym
  przypadku.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  w `sequential_analysis.design` oblicza metodą indukcji wstecznej plan
  optymalny z maksymalną liczebnością próby. `PlanTest` go wykonuje,
  a `operating_characteristic` podaje jego dokładne poziomy błędów
  i oczekiwaną liczebność próby bez symulacji. Zob.
  `examples/07_design_kiefer_weiss.py`.
* Jeśli zamiast sprawdzania po każdej obserwacji chcesz kilku zaplanowanych
  sprawdzeń, użyj [planu grupowo-sekwencyjnego](clinical-trials.md).

## Kiedy SPRT jest niewłaściwym narzędziem

* **Hipotezy nie są proste.** „Odsetek wynosi 10%” przeciwko „odsetek ma
  dowolną inną wartość” to alternatywa złożona. Użyj mieszankowego SPRT
  (mixture SPRT: `NormalMixtureSPRT`, `TMixtureSPRT`) lub testu opartego na
  zakładach (`BettingMeanTest`), które są ważne w dowolnym momencie
  (anytime-valid) wobec każdej alternatywy.
* **Prawdziwa wartość leży między θ₀ a θ₁.** SPRT jest wtedy najwolniejszy,
  a jego oczekiwana liczebność próby może przekroczyć liczebność testu
  o stałej liczebności próby. Plan Kiefera–Weissa jest zbudowany właśnie na
  ten przypadek.

Rodziny dostępne dla procedur opartych na ilorazie wiarygodności: `Gaussian`
(znana wariancja), `Bernoulli`, `Poisson`, `Exponential`.
