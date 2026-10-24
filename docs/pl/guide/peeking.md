---
description: Dlaczego codzienne sprawdzanie wartości p zawyża liczbę wyników fałszywie dodatnich w testach A/B i badaniach (problem podglądania, peeking) oraz trzy rodziny metod sekwencyjnych, które go rozwiązują, w Pythonie z sequential-analysis.
language: pl
---

# Dlaczego nie mogę codziennie sprawdzać wartości p?

> To jest tłumaczenie [strony w języku angielskim](../../guide/peeking.md). Nie zostało jeszcze sprawdzone przez rodzimego użytkownika języka; w razie rozbieżności rozstrzyga wersja angielska.

**Krótka odpowiedź.** Test o stałej liczebności próby (fixed-sample test)
obiecuje 5% wyników fałszywie dodatnich tylko wtedy, gdy spojrzysz na wynik
raz, przy zaplanowanej liczebności próby. Jeśli patrzysz wielokrotnie
i zatrzymujesz się przy pierwszym p < 0,05, masz wiele okazji, by dać się
zwieść. Przy 20 sprawdzeniach odsetek wyników fałszywie dodatnich rośnie do
około 25%. Metody sekwencyjne są zbudowane tak, by można było na nie patrzeć
wielokrotnie. Przy nich odsetek ten pozostaje na poziomie 5% lub niższym bez
względu na to, jak często patrzysz i kiedy się zatrzymasz.

## Problem podglądania (peeking) w liczbach

Dwa warianty z tym samym współczynnikiem konwersji 10% (test A/A), 2000
użytkowników, 200 powtórzeń. „Podglądanie” wykonuje zwykły test z dla dwóch
proporcji po każdych 100 użytkownikach i zatrzymuje się przy pierwszym
p < 0,05. Sekwencyjny `TwoProportionTest` jest sprawdzany po każdym
pojedynczym użytkowniku:

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

Pojedyncze sprawdzenie dotrzymuje obietnicy. Dwadzieścia sprawdzeń zwiększa
poziom błędu mniej więcej sześciokrotnie. Test sekwencyjny, sprawdzany po
każdym z 2000 użytkowników, utrzymuje go na poziomie 5%. Na tym polega
obietnica: jego gwarancja to **exact** (`TwoProportionTest.guarantee == "exact"`),
czyli odsetek wyników fałszywie dodatnich co najwyżej 5% przy każdej
liczebności próby, bez względu na to, jak często patrzysz. Przy 200
powtórzeniach 10 wyników fałszywie dodatnich to dokładnie to, czego należy
się spodziewać przy dokładnych 5%.

## Trzy rodziny metod sekwencyjnych

| Rodzina | Możesz patrzeć | Typowe zastosowanie | W sequential-analysis |
|---|---|---|---|
| **Sekwencyjne testy ilorazu prawdopodobieństw** (SPRT; Wald 1945) | po każdej obserwacji | jedna hipoteza prosta przeciwko drugiej, najmniej obserwacji średnio: kontrola jakości, symulacja, psychofizyka | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Plany grupowo-sekwencyjne** (group sequential designs; Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | przy kilku zaplanowanych analizach pośrednich | badania kliniczne z komisją monitorującą dane | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Wnioskowanie ważne w dowolnym momencie** (anytime-valid inference): e-wartości, ciągi ufności, mieszankowy SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | po każdej obserwacji, z zatrzymaniem z dowolnego powodu | testy A/B online, pulpity monitorujące | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**Ile to kosztuje.** Częstsze patrzenie wymaga więcej danych przy efekcie,
dla którego planowano:

* plan grupowo-sekwencyjny z czterema analizami wymaga o 1–20% więcej
  pacjentów niż pojedyncza analiza;
* test ważny w dowolnym momencie dla dwóch proporcji wymaga 1,3–1,6 raza
  więcej użytkowników niż pojedyncza analiza.

W zamian duży efekt pozwala wcześniej zakończyć eksperyment i nikt nie musi
z góry ustalać liczebności próby.

## Kiedy to nie jest problem

Podglądanie zawyża błędy tylko wtedy, gdy to, co robisz, zależy od tego, co
zobaczyłeś. Jeśli patrzysz na pulpit, ale zawsze prowadzisz eksperyment do
zaplanowanej liczebności i testujesz raz, test o stałej liczebności próby
jest ważny. W takim przypadku jest też najbardziej efektywnym wyborem.

Dalej: [wcześniejsze zakończenie testu A/B](ab-testing.md),
[ciągi ufności](confidence-sequences.md),
[słowniczek](glossary.md).
