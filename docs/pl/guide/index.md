---
description: Przewodnik użytkownika sequential-analysis, biblioteki Python do testowania sekwencyjnego i wnioskowania ważnego w dowolnym momencie (anytime-valid). Każda strona odpowiada wprost na jedno pytanie i zawiera działający kod wraz z jego wynikiem.
language: pl
---

# Przewodnik użytkownika

> To jest tłumaczenie [strony w języku angielskim](../../guide/index.md). Nie zostało jeszcze sprawdzone przez rodzimego użytkownika języka; w razie rozbieżności rozstrzyga wersja angielska.

Przewodnik jest uporządkowany według pytań, które zadają użytkownicy. Każda
strona zaczyna się od bezpośredniej odpowiedzi, po której następuje krótki
program działający bez zmian, jego wynik, gwarancja stojąca za odpowiedzią
oraz przypadki, w których metoda nie ma zastosowania. [Samouczki](../../tutorials/ab-test.md)
omawiają każdy temat dokładniej.

## Biblioteka w jednym akapicie

**sequential-analysis** to biblioteka Python do wnioskowania statystycznego
na danych napływających po jednej obserwacji. Jej testy, przedziały
ufności i detektory można sprawdzać po każdej obserwacji i zatrzymać
w dowolnym momencie, a ich poziomy błędów nadal obowiązują. Obejmuje:

* test SPRT Walda i optymalne plany sekwencyjne;
* plany grupowo-sekwencyjne (group sequential designs) dla badań klinicznych
  (wydatkowanie alfa typu O'Brien–Fleming i Pocock, granice daremności);
* testy A/B ważne w dowolnym momencie (anytime-valid), oparte na e-wartościach
  i ciągach ufności (confidence sequences);
* wykrywanie punktów zmiany (change-point detection);
* filtry Kalmana, filtry cząsteczkowe i filtry ukrytych modeli Markowa;
* prognozowanie i zmienność GARCH.

Każdy przebieg można zapisać jako punkt kontrolny w formacie JSON i wznowić
w Pythonie bit w bit albo kontynuować w wykonawcy TypeScript z tymi samymi
decyzjami.

| | |
|---|---|
| Instalacja | `pip install sequential-analysis` |
| Import | `import sequential_analysis` |
| Python | od 3.8 do 3.14, bez wymaganych zależności (numpy opcjonalnie) |
| Licencja | AGPL-3.0 lub licencja komercyjna od Novikov Laboratories LLC |
| Kod źródłowy | <https://github.com/andre-a-no/sequential-analysis> |
| Dokumentacja | <https://andre-a-no.github.io/sequential-analysis/> |

## Pytania

**Pojęcia**

* [Dlaczego nie mogę codziennie sprawdzać wartości p?](peeking.md) Podglądanie
  (peeking) i trzy rodziny metod sekwencyjnych.
* [Słowniczek](glossary.md): e-wartość, ciąg ufności, wydatkowanie alfa,
  ARL i inne terminy wraz z synonimami.

**Zadania**

* [Jak wcześniej zakończyć test A/B bez zawyżania liczby wyników fałszywie dodatnich?](ab-testing.md)
* [Jak uzyskać przedział ufności, który pozostaje ważny, gdy wciąż patrzę na wyniki?](confidence-sequences.md)
* [Jak uruchomić test SPRT Walda w Pythonie?](sprt.md)
* [Jak zaplanować analizy pośrednie badania klinicznego?](clinical-trials.md)
* [Jak wykryć zmianę w strumieniu pomiarów?](change-detection.md)
* [Jak prowadzić obliczenia statystyczne na strumieniu i wznowić je po awarii?](streaming.md)

**Wybór**

* [Która metoda pasuje do mojego pytania?](../../choosing.md): pełna tabela.
* [Jak wypada na tle innych bibliotek?](comparison.md)
* [Najczęściej zadawane pytania](faq.md)

## Jak czytać gwarancje

Każda procedura ma atrybut `guarantee`. Przewodnik przytacza go przy
każdej odpowiedzi:

* **exact:** poziom błędu obowiązuje przy każdej liczebności próby przy
  podanych założeniach.
* **asymptotic:** obowiązuje w przybliżeniu, tym lepiej, im większa próba.
* **model:** prawdopodobieństwa są dokładne w ramach podanego modelu, ale
  poza nim niczego się nie twierdzi.
* **approximate:** przybliżenie nawet w ramach modelu.
* **none:** procedura przekształca dane i niczego nie gwarantuje.
