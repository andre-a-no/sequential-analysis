---
description: Najczęściej zadawane pytania o sequential-analysis, bibliotekę Python do testowania sekwencyjnego i wnioskowania ważnego w dowolnym momencie (anytime-valid) - instalacja, licencja i użycie komercyjne, testy A/B w produkcji, badania kliniczne, moc, szybkość, TypeScript, cytowanie.
language: pl
---

# Najczęściej zadawane pytania

> To jest tłumaczenie [strony w języku angielskim](../../guide/faq.md). Nie zostało jeszcze sprawdzone przez rodzimego użytkownika języka; w razie rozbieżności rozstrzyga wersja angielska.

## O bibliotece

### Czym jest sequential-analysis?

To biblioteka Python do sekwencyjnego wnioskowania statystycznego. Jej testy,
ciągi ufności (confidence sequences) i detektory można sprawdzać po każdej
obserwacji i zatrzymać w dowolnym momencie bez utraty gwarancji dotyczących
błędów. Zawiera:

* testy SPRT;
* plany grupowo-sekwencyjne (group sequential designs);
* testy A/B ważne w dowolnym momencie (anytime-valid);
* detektory punktów zmiany;
* filtry Kalmana, filtry cząsteczkowe i filtry ukrytych modeli Markowa;
* prognozowanie i GARCH.

Wszystkie działają za jednym interfejsem z punktami kontrolnymi w formacie
JSON. Bibliotekę rozwija Novikov Laboratories LLC.

### Jak ją zainstalować? Od czego zależy?

`pip install sequential-analysis`. Wymaga Pythona 3.8 lub nowszego
(testowana do wersji 3.14) i niczego więcej. `pip install "sequential-analysis[fast]"`
dodaje numpy dla procedur działających na tablicach. pandas, polars, klienty
Kafki i matplotlib są używane tylko wtedy, gdy wywołujesz adaptery lub
funkcje wykresów.

### Czy można jej używać komercyjnie za darmo?

Biblioteka ma podwójną licencję: AGPL-3.0 i licencję komercyjną. Na
warunkach AGPL bezpłatne są następujące zastosowania:

* badania naukowe i dydaktyka;
* projekty open source na licencji AGPL lub GPL v3;
* użytek wewnętrzny w organizacji, bez przekazywania kopii innym i bez
  dostępu przez sieć dla osób spoza niej.

Produkt o zamkniętym kodzie albo usługa sieciowa, której kodu źródłowego nie
publikujesz, wymaga licencji komercyjnej. O poszczególnych przypadkach
rozstrzyga tabela w
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md).
Zapytania licencyjne: andrei@hobukob.ru.

### Jak ją cytować?

Plik [CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff)
w repozytorium podaje sposób cytowania, a przycisk GitHuba *Cite this
repository* zamienia go na BibTeX lub APA. Wydania są archiwizowane
w Zenodo z numerem DOI. Metody i ich weryfikacja są opisane
w [artykule](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf).

## Korzystanie

### Czy mogę jej używać do testów A/B w produkcji?

Tak, jako silnika statystycznego. Daje dokładne testy dla:

* konwersji (`TwoProportionTest`);
* metryk ograniczonych (`BoundedABTest`);
* częstości (`RateRatioTest`);
* podziału ruchu (`SampleRatioMismatch`);
* wielu metryk z kontrolą odsetka fałszywych odkryć (`MultipleTests`).

W czystym Pythonie test konwersji zajmuje około 10 mikrosekund na
użytkownika, kontrola podziału 4, a test częstości 40. Punkt kontrolny
każdego z nich zajmuje 2–4 kilobajty.
`BoundedABTest` przechowuje siatkę i zajmuje 0,1–0,5 ms.

Biblioteka nie jest platformą eksperymentów: przydział, zbieranie zdarzeń
i pulpity musisz zbudować sam lub wziąć z platformy. Zob. [testy A/B](ab-testing.md).

### Czy mogę codziennie podglądać wyniki?

Tak, w przypadku procedur ważnych w dowolnym momencie: właśnie do tego służą.
Przy planie grupowo-sekwencyjnym patrz tylko na zaplanowane analizy. Przy
klasycznym teście o stałej liczebności próby patrz raz. Zob.
[podglądanie](peeking.md).

### Czy test ważny w dowolnym momencie ma mniejszą moc niż test o stałej liczebności próby?

Przy efekcie, dla którego zaplanowano test o stałej liczebności próby, tak.
Aby osiągnąć tę samą moc, test ważny w dowolnym momencie dla dwóch proporcji
potrzebuje 1,3–1,6 raza więcej użytkowników. W zamian możesz zakończyć
wcześniej, gdy efekt jest większy, i nie musisz z góry ustalać liczebności
próby. Plan grupowo-sekwencyjny z kilkoma zaplanowanymi sprawdzeniami
kosztuje tylko o 1–20% więcej niż pojedyncza analiza.

### Plan grupowo-sekwencyjny czy anytime-valid: co wybrać?

* **Grupowo-sekwencyjny**, jeśli analiz jest niewiele i są zaplanowane, jak
  w przypadku komisji monitorującej dane lub cyklu wydań, a zwłaszcza
  w potwierdzającym badaniu klinicznym.
* **Anytime-valid**, jeśli chcesz patrzeć w sposób ciągły albo nie potrafisz
  z góry powiedzieć, kiedy spojrzysz lub zakończysz.

### Czy obsługuje bayesowskie testy A/B?

Jej testy A/B są częstościowe, z gwarancjami dotyczącymi poziomów błędów.
Komponenty bayesowskie są dostępne tam, gdzie pasują:

* `ThompsonAllocation` kieruje ruch według prawdopodobieństwa a posteriori,
  że dany wariant jest najlepszy, z regułą oczekiwanej straty przy wdrożeniu;
* `BayesianChangePoint` wykrywa punkty zmiany;
* prognozery uczą się swoich parametrów przez aktualizację bayesowską.

### Czy jest walidowana do badań klinicznych?

Jej plany grupowo-sekwencyjne (granice, moc, liczebności prób, liczby zdarzeń)
są w zestawie testów sprawdzane względem rpact i pakietu R survival. Nie jest
oprogramowaniem walidowanym w sensie regulacyjnym. Sponsor używający jej we
wniosku rejestracyjnym waliduje ją jak każde inne narzędzie. Zob.
[badania kliniczne](clinical-trials.md).

### Moja metryka ma ciężkie ogony (przychód, opóźnienie). Czego użyć?

* Dla kwantyla (mediana, 90. percentyl) użyj `QuantileTest` lub
  `QuantileConfidenceSequence`, które nie wymagają żadnych założeń.
* Dla średniej ogranicz wartości do poziomu ustalonego z góry i użyj
  `BoundedABTest` lub `BettingConfidenceSequence` (exact).
* Alternatywnie załóż ograniczenie odchylenia standardowego i użyj
  `CatoniConfidenceSequence`.

Testu dwóch prób dla median jeszcze w bibliotece nie ma.

### Jak szybko działa?

Najprostsze procedury zajmują w czystym Pythonie 1–10 mikrosekund na
obserwację: testy SPRT, CUSUM, testy grupowo-sekwencyjne i mieszankowe,
GARCH. Te, które przechowują siatkę lub całą próbę, zajmują 0,1–10 ms.
Przykładami są ciągi ufności oparte na zakładach i Catoniego, test jądrowy
oraz uczone prognozery.
Strona [Szybkość](../../performance.md) podaje koszt i rozmiar punktu
kontrolnego każdej procedury.

### Czy mogę ją uruchomić w JavaScripcie lub w przeglądarce?

Tak. Wykonawca TypeScript w `ts/` uruchamia procedury i kontynuuje punkty
kontrolne z Pythona. Skróty historii i decyzje są identyczne, a liczby
zgadzają się co do ostatnich bitów. Zob. [wykonawca TypeScript](../../typescript.md).

### Czy przebieg przetrwa awarię?

Tak. `run.checkpoint()` to zwykły JSON, a `Run.restore` kontynuuje bit
w bit. Obserwacje dostarczone ponownie są odrzucane. Zob.
[przetwarzanie strumieniowe](streaming.md).

### Co oznaczają „exact” i „asymptotic” w dokumentacji?

Atrybut `guarantee` każdej procedury określa jej obietnicę:

* `exact`: poziom błędu obowiązuje przy każdej liczebności próby przy
  podanych założeniach;
* `asymptotic`: w przybliżeniu, w długich przebiegach;
* `model`: dokładnie w ramach podanego modelu;
* `approximate`;
* `none`.

Dokumentacja zaleca procedurę dokładną wszędzie tam, gdzie taka pasuje. Zob.
[Która metoda?](../../choosing.md).
