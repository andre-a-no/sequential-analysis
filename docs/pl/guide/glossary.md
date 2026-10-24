---
description: Słowniczek terminów analizy sekwencyjnej i wnioskowania ważnego w dowolnym momencie (anytime-valid) - e-wartość, e-proces, ciąg ufności, zawsze ważna wartość p, mSPRT, wydatkowanie alfa, ułamek informacji, ARL, SRM, CUPED, e-BH - z synonimami i procedurami sequential-analysis, które je implementują.
language: pl
---

# Słowniczek

> To jest tłumaczenie [strony w języku angielskim](../../guide/glossary.md). Nie zostało jeszcze sprawdzone przez rodzimego użytkownika języka; w razie rozbieżności rozstrzyga wersja angielska.

Terminy używane w analizie sekwencyjnej i w tej bibliotece. Synonimy
w powszechnym użyciu podano w nawiasach, wraz z angielskimi odpowiednikami.

**Analiza sekwencyjna** (sequential analysis; testowanie sekwencyjne,
sequential testing; wnioskowanie sekwencyjne, sequential inference).
Statystyka, w której liczba obserwacji nie jest ustalona z góry. Po każdej
obserwacji lub grupie obserwacji procedura decyduje, czy zakończyć, czy
kontynuować. Zapoczątkowana przez Walda (1945).

**Podglądanie** (peeking; optional stopping, data peeking, ciągłe
monitorowanie, continuous monitoring). Wielokrotne sprawdzanie testu
o stałej liczebności próby i zatrzymywanie go, gdy wynik jest istotny.
Zawyża odsetek wyników fałszywie dodatnich; zob. [podglądanie](peeking.md).

**SPRT** (sequential probability ratio test, sekwencyjny test ilorazu
prawdopodobieństw, test Walda). Kumuluje logarytm ilorazu wiarygodności dwóch
hipotez prostych i zatrzymuje się, gdy opuści on przedział. `SPRT`; wersje
obcięte `TwoSPRT` (2-SPRT Lordena) i `kiefer_weiss_plan`. Zob. [SPRT](sprt.md).

**Plan grupowo-sekwencyjny** (group sequential design; analizy pośrednie,
interim analyses; badanie grupowo-sekwencyjne, group sequential trial). Kilka
zaplanowanych analiz, każda z własną granicą. Granice dobiera się tak, by
łączny błąd pierwszego rodzaju wynosił alfa.
`group_sequential_design`. Zob. [badania kliniczne](clinical-trials.md).

**Funkcja wydatkowania alfa** (alpha spending function; error spending,
Lan–DeMets). Określa, jaką część błędu pierwszego rodzaju można zużyć do
danego ułamka informacji. Wydatkowanie typu O'Brien–Fleming zużywa na
początku niewiele, wydatkowanie typu Pocock zużywa równomiernie.
`spending="obrien-fleming"`, `"pocock"`, ...

**Ułamek informacji** (information fraction). Część zaplanowanej informacji
statystycznej (pacjenci, zdarzenia) osiągnięta w momencie analizy.

**Granica daremności** (futility boundary; niewiążąca granica daremności,
non-binding futility). Dolna granica: poniżej niej zaleca się zakończenie
z powodu braku efektu. Niewiążącą granicę można zignorować bez zawyżania
błędu pierwszego rodzaju.

**Wnioskowanie ważne w dowolnym momencie** (anytime-valid inference;
always-valid inference, safe anytime-valid inference, SAVI). Testy
i przedziały, których gwarancje obowiązują jednocześnie przy każdej
liczebności próby, więc można je monitorować w sposób ciągły i zatrzymać
z dowolnego powodu.

**E-wartość** (e-value; e-variable, betting score). Nieujemna statystyka,
której wartość oczekiwana przy hipotezie zerowej wynosi co najwyżej 1. Duża
e-wartość jest świadectwem przeciwko hipotezie zerowej: odrzucenie, gdy
przekracza ona 1/alpha, ma błąd pierwszego rodzaju co najwyżej alpha. Wyjście
`log_e_value` wielu procedur.

**E-proces** (e-process; martyngał testowy, test martingale; nadmartyngał
testowy, test supermartingale; proces majątku, wealth process). Ciąg
e-wartości, który pozostaje ważny w momentach zatrzymania. Jego bieżące
maksimum przekracza 1/alpha z prawdopodobieństwem co najwyżej alpha przy
hipotezie zerowej (nierówność Ville'a).

**Zawsze ważna wartość p** (always-valid p-value; anytime-valid p-value,
sekwencyjna wartość p, sequential p-value). Wartość p ważna w dowolnym
momencie zatrzymania. Jest odwrotnością bieżącego maksimum e-procesu.
Wyjście `p_value` procedur ważnych w dowolnym momencie.

**Ciąg ufności** (confidence sequence; anytime-valid confidence interval,
always-valid confidence interval, przedział ufności jednostajny w czasie,
time-uniform confidence interval). Ciąg przedziałów, który
z prawdopodobieństwem co najmniej 1 − alpha zawiera prawdziwą wartość
jednocześnie przy wszystkich liczebnościach próby.
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence` oraz wyjścia
`lower` i `upper` wielu testów. Zob.
[ciągi ufności](confidence-sequences.md).

**mSPRT** (mixture SPRT, mieszanka Robbinsa, Robbins' mixture). SPRT, którego
hipoteza alternatywna jest uśredniona względem rozkładu a priori, co czyni go
ważnym w dowolnym momencie wobec każdej alternatywy. `NormalMixtureSPRT`
(znana wariancja), `TMixtureSPRT` (nieznana wariancja).

**Testowanie przez zakłady** (testing by betting). Konstruowanie e-procesów
jako majątku gracza, który zakłada się przeciwko hipotezie zerowej.
`BettingMeanTest`, `BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal, optymalna stopa wzrostu). E-wartość wybrana
tak, by maksymalizować oczekiwany logarytmiczny wzrost świadectwa przy
hipotezie alternatywnej. `TwoProportionTest(method="grow")`.

**Wnioskowanie uniwersalne** (universal inference). E-wartość z ilorazu
wiarygodności, w którym alternatywa jest szacowana wyłącznie na podstawie
wcześniejszych danych. Pozostaje ważna przy planach adaptacyjnych.
`TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). Kontroluje odsetek fałszywych odkryć (false
discovery rate) dla wielu e-wartości przy dowolnej zależności.
`MultipleTests`, `e_bh`.

**e-LOND, FDR online** (online FDR). Kontrola odsetka fałszywych odkryć dla
serii hipotez rozstrzyganych po kolei. `OnlineFDR`.

**SRM** (sample ratio mismatch, niezgodność proporcji próby). Obserwowany
podział ruchu między warianty różni się od skonfigurowanego, co świadczy
o błędzie w eksperymencie. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data; korekta
o kowariantę, covariate adjustment; korekta regresyjna, regression
adjustment). Zmniejsza wariancję efektu w teście A/B za pomocą kowarianty
zmierzonej przed eksperymentem. `ABTest(covariate=True)`, `AnytimeLinearModel`.

**Metryka ilorazowa** (ratio metric; metoda delta, delta method). Metryka
będąca ilorazem dwóch sum na użytkownika, np. przychód na sesję.
`RatioABTest`.

**Wykrywanie punktów zmiany** (change-point detection; wykrywanie zmian,
change detection; najszybsze wykrywanie, quickest detection; wykrywanie
anomalii online, online anomaly detection). Podnoszenie alarmu wkrótce po
zmianie rozkładu strumienia. `CUSUM`, `ShiryaevRoberts`,
`MeanEDetector`, `QuantileEDetector`, `BayesianChangePoint`. Zob.
[wykrywanie zmian](change-detection.md).

**ARL** (average run length, średnia długość przebiegu, ARL₀; średni czas do
fałszywego alarmu, mean time to false alarm). Oczekiwana liczba obserwacji do
fałszywego alarmu, gdy nic się nie zmieniło. Miara kontroli fałszywych
alarmów detektorów zmian.

**E-detektor** (e-detector). Detektor zmian zbudowany z e-procesów, z których
każdy startuje w innym możliwym momencie zmiany. Jego ARL jest gwarantowane
przy nieparametrycznej hipotezie zerowej. `MeanEDetector`, `QuantileEDetector`.

**Problem Kiefera–Weissa** (Kiefer–Weiss problem). Znalezienie testu
sekwencyjnego z maksymalną liczebnością próby, który minimalizuje największą
oczekiwaną liczebność próby. `kiefer_weiss_plan`.

**Charakterystyka operacyjna** (operating characteristic). Prawdopodobieństwa
błędów i rozkład liczebności próby planu jako funkcje prawdziwego parametru.
`operating_characteristic`.

**Punkt kontrolny** (checkpoint). Wartość JSON, od której przebieg jest
kontynuowany dokładnie. `Run.checkpoint`, `Run.restore`. Zob.
[przetwarzanie strumieniowe](streaming.md).

**Skrót historii** (history digest). Łańcuch skrótów SHA-256 obejmujący
obserwacje wykorzystane przez przebieg, przechowywany w każdym punkcie
kontrolnym na potrzeby audytu.

**Gwarancja** (guarantee; `exact`, `asymptotic`, `model`, `approximate`, `none`).
Atrybut, w którym każda procedura tej biblioteki określa, co obiecuje. Zob.
[Która metoda?](../../choosing.md).
