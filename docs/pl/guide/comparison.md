---
description: Jak sequential-analysis wypada na tle innych bibliotek Python i R do testowania sekwencyjnego, testów A/B, planów grupowo-sekwencyjnych, wykrywania zmian i filtrowania (statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn) i kiedy której używać.
language: pl
---

# Jak wypada na tle innych bibliotek?

> To jest tłumaczenie [strony w języku angielskim](../../guide/comparison.md). Nie zostało jeszcze sprawdzone przez rodzimego użytkownika języka; w razie rozbieżności rozstrzyga wersja angielska.

**Krótka odpowiedź.** Większość bibliotek dobrze obsługuje jedną rodzinę
metod. sequential-analysis udostępnia główne rodziny wnioskowania
sekwencyjnego za jednym interfejsem:

* testy SPRT i plany optymalne;
* plany grupowo-sekwencyjne (group sequential designs);
* testy ważne w dowolnym momencie (anytime-valid) i ciągi ufności (confidence sequences);
* wykrywanie zmian;
* filtry w przestrzeni stanów.

Co dodaje poza samymi metodami:

* każda procedura deklaruje swoją gwarancję (`exact`, `asymptotic`, `model`,
  ...);
* każdy przebieg można zapisać w punkcie kontrolnym i wznowić bit w bit;
* formaty są wyspecyfikowane i wykonywane przez drugą implementację
  w TypeScript;
* nie ma wymaganych zależności.

Jeśli potrzebujesz tylko jednej z poniższych metod i już korzystasz
z biblioteki, która się w niej specjalizuje, korzystaj z niej dalej. Tabela
pokazuje, gdzie każde narzędzie jest naturalnym wyborem. Opisy dotyczą
głównego przeznaczenia każdej biblioteki według stanu z października 2026 r.
i nie są pełną listą jej funkcji.

| Potrzeba | Naturalne wybory | Co oferuje sequential-analysis |
|---|---|---|
| testy o stałej liczebności próby, regresja, moc | scipy.stats, statsmodels | nie jest to jej przeznaczeniem |
| plany grupowo-sekwencyjne do wniosku rejestracyjnego | rpact, gsDesign (R) | te same plany, sprawdzone względem rpact w jej zestawie testów; prowadzi badanie krok po kroku z punktami kontrolnymi |
| ciągi ufności, e-wartości | confseq (Python), safestats (R) | ciągi ufności dla średnich, kwantyli, współczynników regresji, efektów dwóch prób; e-BH i e-LOND dla wielu testów |
| testy A/B jako platforma z interfejsem użytkownika | GrowthBook, Statsig, Eppo, Optimizely (platformy) | silnik do osadzenia: dokładne testy dla konwersji, metryk ograniczonych i częstości, SRM, FDR dla wielu metryk |
| segmentacja offline gotowego szeregu według punktów zmiany | ruptures (Python), changepoint (R) | wykrywanie online w trakcie napływu danych: CUSUM, Shiryaev–Roberts, e-detektory, bayesowskie punkty zmiany online |
| filtry Kalmana | filterpy, statsmodels state space | filtr Kalmana, odporny filtr Kalmana, filtry cząsteczkowe i HMM, z wygładzaniem i punktami kontrolnymi |
| GARCH | arch | GARCH(1,1) i GJR dopasowane do maksimum z arch (sprawdzone w testach), następnie uruchamiane online |
| ukryte modele Markowa | hmmlearn | filtr online, Baum–Welch zgodny z hmmlearn, EM online |
| prognozowanie | statsmodels, inne | prognozy ETS i AR zgodne ze statsmodels, uczone online, z przedziałami konforemnymi |

## Przypadki, w których lepsze jest inne narzędzie

* **Wniosek do organu regulacyjnego.** rpact jest powszechnie używany w tym
  celu, a jego twórcy oferują dokumentację walidacyjną. sequential-analysis jest
  z nim zgodna w zakresie planów, które obejmuje, ale sponsor i tak musiałby
  ją zwalidować.
* **Duże analizy offline na tablicach.** Biblioteki oparte na numpy są
  szybsze w przeliczeniu na obserwację. sequential-analysis jest zbudowana
  do pracy z jedną obserwacją naraz; koszt każdej procedury podaje strona
  [Szybkość](../../performance.md).
* **Metody, których nie ma.** Nie ma jeszcze testu dwóch prób dla median,
  wielowymiarowych procesów Hawkesa ani modeli ARIMA z członami średniej
  ruchomej. Co jest dodawane, pokazuje [lista zmian](../../changelog.md).
