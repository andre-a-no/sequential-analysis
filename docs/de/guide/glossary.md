---
description: Glossar der Begriffe aus Sequentialanalyse und jederzeit gültiger Inferenz (anytime-valid) - E-Wert, E-Prozess, Konfidenzfolge, stets gültiger p-Wert, mSPRT, Alpha-Spending, Informationsanteil, ARL, SRM, CUPED, e-BH - mit Synonymen und den Prozeduren von sequential-analysis, die sie umsetzen.
language: de
---

# Glossar

> Dies ist eine Übersetzung der [englischen Seite](../../guide/glossary.md). Sie wurde noch nicht von einer Muttersprachlerin oder einem Muttersprachler geprüft; wo die beiden voneinander abweichen, ist die englische Seite maßgeblich.

Begriffe aus der Sequentialanalyse und aus dieser Bibliothek. Gebräuchliche
Synonyme stehen in Klammern.

**Sequentialanalyse** (sequential analysis; sequential testing, sequential
inference – sequentielles Testen, sequentielle Inferenz). Statistik, bei
der die Zahl der Beobachtungen nicht vorab festgelegt ist. Nach jeder
Beobachtung oder Gruppe von Beobachtungen entscheidet die Prozedur, ob
gestoppt oder fortgefahren wird. Begründet von Wald (1945).

**Peeking** (optional stopping, data peeking, continuous monitoring –
optionales Stoppen, laufende Überwachung). Wiederholtes Anschauen eines
Tests mit festem Stichprobenumfang und Abbruch, sobald er signifikant ist.
Es erhöht die Falsch-positiv-Rate; siehe [Peeking](peeking.md).

**SPRT** (sequential probability ratio test – sequentieller
Wahrscheinlichkeitsquotiententest, Wald-Test). Er summiert den
logarithmierten Likelihood-Quotienten zweier einfacher Hypothesen auf und
stoppt, wenn dieser ein Intervall verlässt. `SPRT`; gestutzte Varianten
`TwoSPRT` (Lordens 2-SPRT) und `kiefer_weiss_plan`. Siehe [SPRT](sprt.md).

**Gruppensequentielles Design** (group sequential design; interim
analyses, group sequential trial – Zwischenanalysen, gruppensequentielle
Studie). Wenige geplante Analysen, jede mit einer Grenze. Die Grenzen werden
so gewählt, dass der Fehler 1. Art insgesamt alpha beträgt.
`group_sequential_design`. Siehe [klinische Studien](clinical-trials.md).

**Alpha-Spending-Funktion** (alpha spending function; error spending,
Lan–DeMets – Alpha-Verbrauchsfunktion). Sie legt fest, wie viel des Fehlers
1. Art bis zu jedem Informationsanteil verbraucht werden darf. Spending vom
Typ O'Brien–Fleming verbraucht anfangs wenig, Spending vom Typ Pocock
gleichmäßig. `spending="obrien-fleming"`, `"pocock"`, ...

**Informationsanteil** (information fraction). Der Anteil der geplanten
statistischen Information (Patienten, Ereignisse), der bei einer Analyse
erreicht ist.

**Futility-Grenze** (futility boundary; non-binding futility – nicht
bindende Futility-Grenze). Eine untere Grenze: Unterhalb davon wird ein
Abbruch wegen fehlenden Effekts empfohlen. Eine nicht bindende Grenze darf
ignoriert werden, ohne den Fehler 1. Art zu erhöhen.

**Jederzeit gültige Inferenz** (anytime-valid inference; always-valid
inference, safe anytime-valid inference, SAVI). Tests und Intervalle,
deren Garantien bei allen Stichprobenumfängen zugleich gelten, sodass sie
laufend überwacht und aus beliebigem Grund gestoppt werden dürfen.

**E-Wert** (e-value; e-variable, betting score – E-Variable,
Wett-Score). Eine nichtnegative Statistik, deren Erwartungswert unter der
Nullhypothese höchstens 1 ist. Ein großer E-Wert ist Evidenz gegen die
Nullhypothese: Wer ablehnt, sobald er 1/alpha übersteigt, hat einen Fehler
1. Art von höchstens alpha. Die Ausgabe `log_e_value` vieler Prozeduren.

**E-Prozess** (e-process; test martingale, test supermartingale, wealth
process – Testmartingal, Testsupermartingal, Vermögensprozess). Eine
Folge von E-Werten, die zu Stoppzeiten gültig bleibt. Ihr laufendes
Maximum überschreitet 1/alpha unter der Nullhypothese mit
Wahrscheinlichkeit höchstens alpha (Ville-Ungleichung, Ville's inequality).

**Stets gültiger p-Wert** (always-valid p-value; anytime-valid p-value,
sequential p-value – jederzeit gültiger p-Wert, sequentieller p-Wert). Ein
p-Wert, der zu jeder Stoppzeit gültig ist. Er ist der Kehrwert des
laufenden Maximums eines E-Prozesses. Die Ausgabe `p_value` der jederzeit
gültigen Prozeduren.

**Konfidenzfolge** (confidence sequence; anytime-valid confidence
interval, always-valid confidence interval, time-uniform confidence
interval – jederzeit gültiges Konfidenzintervall, zeitlich gleichmäßiges
Konfidenzintervall). Eine Folge von Intervallen, die den wahren Wert mit
Wahrscheinlichkeit mindestens 1 − alpha bei allen Stichprobenumfängen
gleichzeitig enthält. `BettingConfidenceSequence`,
`QuantileConfidenceSequence`, `CatoniConfidenceSequence`,
`AsymptoticConfidenceSequence` sowie die Ausgaben `lower` und `upper`
vieler Tests. Siehe [Konfidenzfolgen](confidence-sequences.md).

**mSPRT** (mixture SPRT, Robbins' mixture – Mixture-SPRT, Robbins-Mischung).
Ein SPRT, dessen Alternative über eine Prior-Verteilung gemittelt wird,
wodurch er gegen jede Alternative jederzeit gültig ist.
`NormalMixtureSPRT` (bekannte Varianz), `TMixtureSPRT` (unbekannte
Varianz).

**Testen durch Wetten** (testing by betting). Konstruktion von E-Prozessen
als Vermögen eines Spielers, der gegen die Nullhypothese wettet.
`BettingMeanTest`, `BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal – wachstumsratenoptimal). Ein E-Wert, der so
gewählt ist, dass er das erwartete logarithmische Wachstum der Evidenz
unter der Alternative maximiert. `TwoProportionTest(method="grow")`.

**Universelle Inferenz** (universal inference). Ein E-Wert aus einem
Likelihood-Quotienten, bei dem die Alternative nur aus vergangenen Daten
geschätzt wird. Er bleibt unter adaptiven Designs gültig.
`TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). Kontrolliert die False Discovery Rate
(Falscherkennungsrate) über viele E-Werte, unter beliebiger Abhängigkeit.
`MultipleTests`, `e_bh`.

**e-LOND, Online-FDR** (online FDR). Kontrolle der False Discovery Rate
über eine Reihe von Hypothesen, die nacheinander entschieden werden.
`OnlineFDR`.

**SRM** (sample ratio mismatch – Abweichung des Stichprobenverhältnisses).
Die beobachtete Aufteilung des Traffics auf die Gruppen weicht von der
konfigurierten ab, ein Anzeichen für einen Fehler im Experiment.
`SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data, covariate
adjustment, regression adjustment – Kovariatenadjustierung,
Regressionsadjustierung). Verringert die Varianz eines A/B-Effekts mit
einer Kovariate, die vor dem Experiment gemessen wurde.
`ABTest(covariate=True)`, `AnytimeLinearModel`.

**Quotientenmetrik** (ratio metric; delta method – Delta-Methode). Eine
Metrik, die ein Quotient zweier Summen pro Nutzer ist, etwa Umsatz pro
Sitzung. `RatioABTest`.

**Change-Point-Erkennung** (change-point detection; change detection,
quickest detection, online anomaly detection – Strukturbrucherkennung,
schnellste Erkennung, Online-Anomalieerkennung). Ein Alarm kurz nachdem
sich die Verteilung eines Datenstroms geändert hat. `CUSUM`,
`ShiryaevRoberts`, `MeanEDetector`, `QuantileEDetector`,
`BayesianChangePoint`. Siehe [Änderungserkennung](change-detection.md).

**ARL** (average run length, ARL₀, mean time to false alarm – mittlere
Lauflänge, mittlere Zeit bis zum Fehlalarm). Die erwartete Zahl von
Beobachtungen bis zu einem Fehlalarm, wenn sich nichts geändert hat. Die
Fehlalarmkontrolle von Change-Point-Detektoren.

**E-Detektor** (e-detector). Ein Change-Point-Detektor aus E-Prozessen,
von denen zu jedem möglichen Änderungszeitpunkt einer gestartet wird. Seine
ARL ist unter einer nichtparametrischen Nullhypothese garantiert.
`MeanEDetector`, `QuantileEDetector`.

**Kiefer–Weiss-Problem** (Kiefer–Weiss problem). Die Suche nach dem
sequentiellen Test mit maximalem Stichprobenumfang, der den größten
erwarteten Stichprobenumfang minimiert. `kiefer_weiss_plan`.

**Operationscharakteristik** (operating characteristic). Die
Fehlerwahrscheinlichkeiten und die Verteilung des Stichprobenumfangs eines
Plans als Funktionen des wahren Parameters. `operating_characteristic`.

**Checkpoint.** Ein JSON-Wert, von dem aus ein Lauf exakt fortgesetzt
wird. `Run.checkpoint`, `Run.restore`. Siehe [Streaming](streaming.md).

**History-Digest** (history digest). Eine SHA-256-Hash-Kette über die
Beobachtungen, die ein Lauf verwendet hat, in jedem Checkpoint gespeichert,
für Audits.

**Garantie** (guarantee; `exact`, `asymptotic`, `model`, `approximate`,
`none`). Das Attribut, in dem jede Prozedur dieser Bibliothek angibt, was
sie verspricht. Siehe [Welche Methode?](../../choosing.md).
