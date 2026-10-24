---
description: Jak w Pythonie wykryć zmianę w strumieniu odczytów czujników, opóźnień lub metryk za pomocą CUSUM, Shiryaeva–Robertsa, nieparametrycznych e-detektorów i bayesowskiego wykrywania punktów zmiany online. Fałszywe alarmy kontrolowane przez średnią długość przebiegu (ARL), z sequential-analysis.
language: pl
---

# Jak wykryć zmianę w strumieniu pomiarów?

> To jest tłumaczenie [strony w języku angielskim](../../guide/change-detection.md). Nie zostało jeszcze sprawdzone przez rodzimego użytkownika języka; w razie rozbieżności rozstrzyga wersja angielska.

**Krótka odpowiedź.** Użyj detektora punktów zmiany online (online
change-point detection). Obserwuje on strumień i podnosi alarm, gdy tylko
rozkład wydaje się zmieniony. Jego fałszywe alarmy są kontrolowane przez
**średnią długość przebiegu** (average run length, ARL): oczekiwaną liczbę
obserwacji do fałszywego alarmu, gdy nic się nie zmieniło. W sequential-analysis:

| Co wiesz przed zmianą | Procedura | Gwarancja |
|---|---|---|
| oba rozkłady (np. normalny, średnia 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| tylko średnią i granice wartości | `MeanEDetector` | exact dla każdego takiego rozkładu |
| tylko kwantyl (np. 95. percentyl opóźnienia) | `QuantileEDetector` | exact dla każdego rozkładu |
| model z nieznanymi parametrami przed zmianą i po niej | `BayesianChangePoint` | w ramach modelu i rozkładu a priori |

## Czujnik, którego średnia się przesuwa

Czujnik temperatury wskazuje 70,0 °C z szumem o odchyleniu standardowym
0,5. Od odczytu 600 średnia wynosi 70,4. CUSUM z progiem
log(1000) ≈ 6,9 ma ARL wynoszące co najmniej 1000 odczytów:

```python
import math
import random

from sequential_analysis.procedures import CUSUM, Gaussian

rnd = random.Random(1)
readings = [rnd.gauss(70.0, 0.5) for _ in range(600)] + [rnd.gauss(70.4, 0.5) for _ in range(400)]

detector = CUSUM(Gaussian(sigma=0.5), theta0=70.0, theta1=70.4, threshold=math.log(1000))
state = detector.initial_state()
for t, x in enumerate(readings, start=1):
    state, out = detector.step(state, {"x": x})
    if out.alarm:
        print(f"alarm at reading {t}, {t - 600} readings after the shift")
        break
```

```text
alarm at reading 615, 15 readings after the shift
```

Przesunięcia mniejszego niż jedno odchylenie standardowe nie widać gołym
okiem w żadnym pojedynczym odczycie. CUSUM kumuluje świadectwa i je wykrywa.

## Gdy odczyty nie mają rozkładu normalnego

ARL detektora CUSUM obowiązuje tylko wtedy, gdy odczyty mają rozkłady, które
mu podano. Dla danych skośnych (amplitudy drgań, opóźnienia, długości kolejek)
podnosi on fałszywe alarmy znacznie częściej, niż zaplanowano. E-detektory
wymagają znacznie mniej:

* `MeanEDetector` potrzebuje średniej przed zmianą i granic wartości.
* `QuantileEDetector` potrzebuje jedynie kwantyla przed zmianą.

Ich ARL wynosi co najmniej wartość docelową dla **każdego** rozkładu o tej
średniej lub tym kwantylu:

```python
from sequential_analysis.procedures import QuantileEDetector

rnd = random.Random(2)
vibration = [rnd.lognormvariate(0.0, 0.8) for _ in range(800)] + [rnd.lognormvariate(0.5, 0.8) for _ in range(400)]
q95 = math.exp(0.8 * 1.6449)          # the 95th percentile before the change
p95 = QuantileEDetector(q0=q95, p=0.95, arl=1000, direction="increase", statistic="cusum")
state = p95.initial_state()
for t, x in enumerate(vibration, start=1):
    state, out = p95.step(state, {"x": x})
    if out.alarm:
        print(f"the 95th percentile rose: alarm at reading {t}, {t - 800} readings after the change")
        break
```

```text
the 95th percentile rose: alarm at reading 887, 87 readings after the change
```

W praktyce kwantyl przed zmianą szacuje się na podstawie spokojnego okresu.
Gwarancja obowiązuje wówczas w przybliżeniu, tym lepszym, im dłuższy był ten
okres.

## Wybór ARL

ARL równoważy fałszywe alarmy i opóźnienie wykrycia. Przy jednym odczycie na
minutę ARL równe 1000 odczytów oznacza mniej więcej jeden fałszywy alarm na
17 godzin normalnej pracy, na każdy czujnik. Przy 50 czujnikach to około 70
dziennie. Wybieraj ARL na podstawie liczby fałszywych alarmów dziennie, na
jaką możesz sobie pozwolić łącznie dla wszystkich czujników: tutaj ARL równe
1 000 000 odczytów ogranicza 50 czujników do około jednego fałszywego alarmu
na dwa tygodnie. Kosztuje to mniej, niż się wydaje, ponieważ opóźnienie
wykrycia rośnie tylko jak logarytm ARL. Dla CUSUM próg rośnie z 6,9 do 13,8,
a opóźnienie mniej więcej się podwaja.

Te detektory są narzędziami monitorowania, a nie systemami bezpieczeństwa.
Nie używaj ich w miejsce certyfikowanego przyrządowego systemu
bezpieczeństwa (safety instrumented system).

Więcej: [samouczek: monitorowanie procesów i wykrywanie zmian](../../tutorials/monitoring.md),
[reżimy w ukrytych modelach Markowa](../../tutorials/regimes.md),
[dokumentacja: wykrywanie zmian](../../reference/detection.md).
