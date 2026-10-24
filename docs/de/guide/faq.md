---
description: Häufig gestellte Fragen zu sequential-analysis, der Python-Bibliothek für sequentielles Testen und jederzeit gültige Inferenz (anytime-valid) - Installation, Lizenz und kommerzielle Nutzung, A/B-Tests in Produktion, klinische Studien, Power, Geschwindigkeit, TypeScript, Zitieren.
language: de
---

# Häufig gestellte Fragen

> Dies ist eine Übersetzung der [englischen Seite](../../guide/faq.md). Sie wurde noch nicht von einer Muttersprachlerin oder einem Muttersprachler geprüft; wo die beiden voneinander abweichen, ist die englische Seite maßgeblich.

## Über die Bibliothek

### Was ist sequential-analysis?

Eine Python-Bibliothek für sequentielle statistische Inferenz. Ihre Tests,
Konfidenzfolgen (confidence sequences) und Detektoren dürfen nach jeder
Beobachtung geprüft und jederzeit gestoppt werden, ohne ihre
Fehlergarantien zu verlieren. Sie bietet:

* SPRTs;
* gruppensequentielle Designs;
* jederzeit gültige (anytime-valid) A/B-Tests;
* Change-Point-Detektoren;
* Kalman-, Partikel- und Hidden-Markov-Filter;
* Prognosen und GARCH.

Alle laufen hinter einer Schnittstelle mit JSON-Checkpoints. Entwickelt
wird sie von Novikov Laboratories LLC.

### Wie installiere ich sie? Wovon hängt sie ab?

`pip install sequential-analysis`. Sie braucht Python 3.8 oder neuer
(getestet bis 3.14) und sonst nichts. `pip install "sequential-analysis[fast]"`
fügt numpy für die Prozeduren hinzu, die auf Arrays arbeiten. pandas,
polars, Kafka-Clients und matplotlib werden nur verwendet, wenn Sie die
Adapter oder die Plot-Funktionen aufrufen.

### Ist sie für die kommerzielle Nutzung kostenlos?

Sie steht unter einer Doppellizenz aus AGPL-3.0 und einer kommerziellen
Lizenz. Diese Nutzungen sind unter der AGPL kostenlos:

* Forschung und Lehre;
* Open-Source-Projekte unter der AGPL oder der GPL v3;
* interne Nutzung in einer Organisation, ohne Weitergabe von Kopien an
  andere und ohne Netzwerkzugriff für Personen außerhalb der Organisation.

Ein Closed-Source-Produkt oder ein Netzwerkdienst, dessen Quellcode Sie
nicht veröffentlichen, braucht eine kommerzielle Lizenz. Die Tabelle in
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)
entscheidet die einzelnen Fälle. Lizenzanfragen: andrei@hobukob.ru.

### Wie zitiere ich sie?

[CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff)
im Repository enthält die Zitierangabe, und die GitHub-Schaltfläche *Cite
this repository* wandelt sie in BibTeX oder APA um. Releases werden auf
Zenodo mit einer DOI archiviert. Die Methoden und ihre Prüfungen sind im
[Paper](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf)
beschrieben.

## Anwendung

### Kann ich sie für A/B-Tests in Produktion einsetzen?

Ja, als statistische Engine. Sie liefert exakte Tests für:

* Konversion (`TwoProportionTest`);
* beschränkte Metriken (`BoundedABTest`);
* Raten (`RateRatioTest`);
* die Traffic-Aufteilung (`SampleRatioMismatch`);
* viele Metriken mit Kontrolle der False Discovery Rate (`MultipleTests`).

In reinem Python braucht der Konversionstest etwa 10 Mikrosekunden pro
Nutzer, die Aufteilungsprüfung 4 und der Ratentest 40. Ein Checkpoint
jedes dieser Tests belegt 2–4 Kilobyte.
`BoundedABTest` hält ein Gitter vor und braucht 0,1–0,5 ms.

Die Bibliothek ist keine Experimentierplattform: Zuweisung,
Ereigniserfassung und Dashboards bauen Sie selbst oder übernehmen sie von
einer Plattform. Siehe [A/B-Tests](ab-testing.md).

### Darf ich jeden Tag auf die Ergebnisse schauen?

Ja, mit den jederzeit gültigen Prozeduren: Genau dafür sind sie da. Bei
einem gruppensequentiellen Design schauen Sie nur bei den geplanten
Analysen hin. Bei einem klassischen Test mit festem Stichprobenumfang
schauen Sie einmal hin. Siehe [Peeking](peeking.md).

### Hat ein jederzeit gültiger Test weniger Power als ein Test mit festem Stichprobenumfang?

Bei dem Effekt, für den ein Test mit festem Stichprobenumfang geplant ist,
ja. Um dieselbe Power zu erreichen, braucht ein jederzeit gültiger Test
für zwei Anteile das 1,3- bis 1,6-Fache an Nutzern. Im Gegenzug können Sie
früh aufhören, wenn der Effekt größer ist, und brauchen keinen vorab
festgelegten Stichprobenumfang. Ein gruppensequentielles Design mit wenigen
geplanten Blicken kostet nur 1–20 % mehr als eine einzelne Analyse.

### Gruppensequentiell oder jederzeit gültig: Was soll ich verwenden?

* **Gruppensequentiell**, wenn die Analysen wenige und geplant sind, etwa
  bei einem Data Monitoring Committee oder einem Release-Zyklus, und
  besonders bei einer konfirmatorischen klinischen Studie.
* **Jederzeit gültig**, wenn Sie laufend hinschauen wollen oder nicht im
  Voraus sagen können, wann Sie hinschauen oder aufhören werden.

### Bietet sie bayessche A/B-Tests?

Ihre A/B-Tests sind frequentistisch, mit Garantien für Fehlerraten.
Bayessche Komponenten gibt es dort, wo sie passen:

* `ThompsonAllocation` verteilt den Traffic nach der
  A-posteriori-Wahrscheinlichkeit, dass jede Gruppe die beste ist, mit
  einer Expected-Loss-Regel für das Ausrollen;
* `BayesianChangePoint` erkennt Change Points;
* die Prognosemodelle lernen ihre Parameter durch bayessches Updating.

### Ist sie für klinische Studien validiert?

Ihre gruppensequentiellen Designs (Grenzen, Power, Fallzahlen,
Ereigniszahlen) werden in der Testsuite mit rpact und dem R-Paket survival
abgeglichen. Sie ist keine validierte Software im regulatorischen Sinn. Ein
Sponsor, der sie für eine Einreichung verwendet, validiert sie wie jedes
andere Werkzeug. Siehe [klinische Studien](clinical-trials.md).

### Meine Metrik hat schwere Ränder (Umsatz, Latenz). Was soll ich verwenden?

* Für ein Quantil (Median, 90. Perzentil) verwenden Sie `QuantileTest`
  oder `QuantileConfidenceSequence`, die ohne Annahmen auskommen.
* Für einen Mittelwert deckeln Sie die Werte bei einem vorab festgelegten
  Niveau und verwenden `BoundedABTest` oder `BettingConfidenceSequence`
  (exakt).
* Alternativ nehmen Sie eine Schranke für die Standardabweichung an und
  verwenden `CatoniConfidenceSequence`.

Ein Zweistichprobentest für Mediane ist noch nicht in der Bibliothek.

### Wie schnell ist sie?

Die einfachsten Prozeduren brauchen in reinem Python 1–10 Mikrosekunden
pro Beobachtung: SPRTs, CUSUM, die gruppensequentiellen und
Mixture-Tests, GARCH. Prozeduren, die ein Gitter oder die ganze Stichprobe
vorhalten, brauchen 0,1–10 ms. Beispiele sind die Konfidenzfolgen über
Wetten und nach Catoni, der Kernel-Test und die gelernten Prognosemodelle.
[Geschwindigkeit](../../performance.md) listet die Kosten und die
Checkpoint-Größe jeder Prozedur auf.

### Kann ich sie in JavaScript oder im Browser ausführen?

Ja. Der TypeScript-Executor in `ts/` führt die Prozeduren aus und setzt
Python-Checkpoints fort. History-Digests und Entscheidungen sind
identisch, und die Zahlen stimmen bis auf die letzten Bits überein. Siehe
[TypeScript-Executor](../../typescript.md).

### Übersteht ein Lauf einen Absturz?

Ja. `run.checkpoint()` ist einfaches JSON, und `Run.restore` setzt bitgenau
fort. Erneut zugestellte Beobachtungen werden verworfen. Siehe
[Streaming](streaming.md).

### Was bedeuten „exact“ und „asymptotic“ in der Dokumentation?

Das Attribut `guarantee` jeder Prozedur nennt ihr Versprechen:

* `exact`: Die Fehlerrate gilt bei jedem Stichprobenumfang unter den
  genannten Annahmen;
* `asymptotic`: näherungsweise, bei langen Läufen;
* `model`: exakt unter dem genannten Modell;
* `approximate`;
* `none`.

Die Dokumentation empfiehlt die exakte Prozedur, wo eine passt. Siehe
[Welche Methode?](../../choosing.md).
