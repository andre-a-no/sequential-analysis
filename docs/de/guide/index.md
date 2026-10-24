---
description: Benutzerhandbuch zu sequential-analysis, einer Python-Bibliothek für sequentielles Testen und jederzeit gültige Inferenz (anytime-valid inference). Jede Seite beantwortet eine Frage direkt, mit lauffähigem Code und seiner Ausgabe.
language: de
---

# Benutzerhandbuch

> Dies ist eine Übersetzung der [englischen Seite](../../guide/index.md). Sie wurde noch nicht von einer Muttersprachlerin oder einem Muttersprachler geprüft; wo die beiden voneinander abweichen, ist die englische Seite maßgeblich.

Dieses Handbuch ist nach den Fragen gegliedert, die Anwender stellen. Jede
Seite beginnt mit einer direkten Antwort und zeigt dann ein kurzes Programm,
das so, wie es dasteht, läuft, seine Ausgabe, die Garantie hinter der
Antwort und die Fälle, in denen die Methode nicht anwendbar ist. Die
[Tutorials](../../tutorials/ab-test.md) gehen bei jedem Thema weiter in die
Tiefe.

## Die Bibliothek in einem Absatz

**sequential-analysis** ist eine Python-Bibliothek für statistische
Inferenz auf Daten, die Beobachtung für Beobachtung eintreffen. Ihre Tests,
Konfidenzintervalle und Detektoren dürfen nach jeder Beobachtung
angeschaut und jederzeit gestoppt werden, und ihre Fehlerraten gelten
trotzdem. Sie umfasst:

* Walds sequentiellen Wahrscheinlichkeitsquotiententest (SPRT) und
  optimale sequentielle Pläne;
* gruppensequentielle Designs (group sequential designs) für klinische
  Studien (Alpha-Spending nach O'Brien–Fleming und Pocock,
  Futility-Grenzen);
* jederzeit gültige (anytime-valid) A/B-Tests mit E-Werten und
  Konfidenzfolgen;
* Change-Point-Erkennung;
* Kalman-, Partikel- und Hidden-Markov-Filter;
* Prognosen und GARCH-Volatilität.

Jeder Lauf lässt sich als JSON-Checkpoint sichern und in Python bitgenau
fortsetzen oder im TypeScript-Executor mit denselben Entscheidungen
weiterführen.

| | |
|---|---|
| Installation | `pip install sequential-analysis` |
| Import | `import sequential_analysis` |
| Python | 3.8 bis 3.14, keine Pflichtabhängigkeiten (numpy optional) |
| Lizenz | AGPL-3.0 oder eine kommerzielle Lizenz von Novikov Laboratories LLC |
| Quellcode | <https://github.com/andre-a-no/sequential-analysis> |
| Dokumentation | <https://andre-a-no.github.io/sequential-analysis/> |

## Fragen

**Grundbegriffe**

* [Warum darf ich nicht jeden Tag auf einen p-Wert schauen?](peeking.md)
  Peeking und die drei Familien sequentieller Methoden.
* [Glossar](glossary.md): E-Wert, Konfidenzfolge, Alpha-Spending, ARL und
  die anderen Begriffe, mit ihren Synonymen.

**Aufgaben**

* [Wie beende ich einen A/B-Test vorzeitig, ohne die falsch-positiven Ergebnisse zu erhöhen?](ab-testing.md)
* [Wie bekomme ich ein Konfidenzintervall, das gültig bleibt, wenn ich immer wieder hinschaue?](confidence-sequences.md)
* [Wie führe ich Walds SPRT in Python durch?](sprt.md)
* [Wie plane ich Zwischenanalysen einer klinischen Studie?](clinical-trials.md)
* [Wie erkenne ich eine Änderung in einem Strom von Messwerten?](change-detection.md)
* [Wie rechne ich Statistik auf einem Datenstrom und setze nach einem Absturz fort?](streaming.md)

**Auswahl**

* [Welche Methode für meine Frage?](../../choosing.md): die vollständige Tabelle.
* [Wie schneidet sie im Vergleich zu anderen Bibliotheken ab?](comparison.md)
* [Häufig gestellte Fragen](faq.md)

## Wie die Garantien zu lesen sind

Jede Prozedur hat ein Attribut `guarantee`. Das Handbuch nennt es bei jeder
Antwort:

* **exact:** Die Fehlerrate gilt bei jedem Stichprobenumfang unter den
  genannten Annahmen.
* **asymptotic:** Sie gilt näherungsweise, und zwar umso besser, je größer
  die Stichprobe ist.
* **model:** Die Wahrscheinlichkeiten sind unter dem genannten Modell
  exakt, darüber hinaus wird nichts behauptet.
* **approximate:** eine Näherung selbst unter dem Modell.
* **none:** Die Prozedur transformiert die Daten und erhebt keinen
  Anspruch.
