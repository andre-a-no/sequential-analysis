---
description: Wie sich sequential-analysis von anderen Python- und R-Bibliotheken für sequentielles Testen, A/B-Tests, gruppensequentielle Designs, Change-Point-Erkennung und Filterung unterscheidet (statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn), und wann man welche verwendet.
language: de
---

# Wie schneidet sie im Vergleich zu anderen Bibliotheken ab?

> Dies ist eine Übersetzung der [englischen Seite](../../guide/comparison.md). Sie wurde noch nicht von einer Muttersprachlerin oder einem Muttersprachler geprüft; wo die beiden voneinander abweichen, ist die englische Seite maßgeblich.

**Kurze Antwort.** Die meisten Bibliotheken decken eine Methodenfamilie gut
ab. sequential-analysis vereint die wichtigsten Familien der sequentiellen
Inferenz (sequential inference) hinter einer Schnittstelle:

* SPRTs und optimale Pläne;
* gruppensequentielle Designs;
* jederzeit gültige (anytime-valid) Tests und Konfidenzfolgen;
* Change-Point-Erkennung;
* Zustandsraumfilter (state-space filters).

Was sie über die Methoden selbst hinaus bietet:

* Jede Prozedur nennt ihre Garantie (`exact`, `asymptotic`, `model`,
  ...);
* jeder Lauf lässt sich als Checkpoint sichern und bitgenau fortsetzen;
* die Formate sind spezifiziert und werden von einer zweiten
  Implementierung in TypeScript ausgeführt;
* es gibt keine Pflichtabhängigkeiten.

Wenn Sie nur eine der unten genannten Methoden brauchen und bereits die
darauf spezialisierte Bibliothek nutzen, bleiben Sie bei dieser
Bibliothek. Die Tabelle zeigt, wo welches Werkzeug die naheliegende Wahl
ist. Die Beschreibungen geben den Hauptzweck jeder Bibliothek wieder, Stand
Oktober 2026, und sind keine vollständige Liste ihrer Funktionen.

| Bedarf | Naheliegende Wahl | Was sequential-analysis bietet |
|---|---|---|
| Tests mit festem Stichprobenumfang, Regression, Power | scipy.stats, statsmodels | nicht ihr Zweck |
| gruppensequentielle Designs für eine Zulassungseinreichung | rpact, gsDesign (R) | dieselben Designs, in ihrer Testsuite mit rpact abgeglichen; führt die Studie Schritt für Schritt mit Checkpoints durch |
| Konfidenzfolgen, E-Werte | confseq (Python), safestats (R) | Konfidenzfolgen für Mittelwerte, Quantile, Regressionskoeffizienten, Zweistichprobeneffekte; e-BH und e-LOND für viele Tests |
| A/B-Tests als Plattform mit Benutzeroberfläche | GrowthBook, Statsig, Eppo, Optimizely (Plattformen) | eine einbettbare Engine: exakte Tests für Konversion, beschränkte Metriken und Raten, SRM, FDR über Metriken |
| Offline-Segmentierung einer abgeschlossenen Reihe nach Change Points | ruptures (Python), changepoint (R) | Online-Erkennung, während die Daten eintreffen: CUSUM, Shiryaev–Roberts, E-Detektoren, bayessche Online-Change-Points |
| Kalman-Filter | filterpy, statsmodels state space | Kalman-, robuste Kalman-, Partikel- und HMM-Filter, mit Glättung und Checkpoints |
| GARCH | arch | GARCH(1,1) und GJR, angepasst an das Maximum von arch (in den Tests geprüft), dann online ausgeführt |
| Hidden-Markov-Modelle | hmmlearn | der Filter online, Baum–Welch in Übereinstimmung mit hmmlearn, Online-EM |
| Prognosen | statsmodels, andere | ETS- und AR-Prognosen in Übereinstimmung mit statsmodels, online gelernt, mit konformen Intervallen |

## Fälle, in denen ein anderes Werkzeug besser ist

* **Eine Einreichung bei einer Zulassungsbehörde.** rpact ist für diesen
  Zweck weit verbreitet, und seine Entwickler bieten
  Validierungsdokumentation an. sequential-analysis stimmt bei den Designs,
  die sie abdeckt, mit rpact überein, aber ein Sponsor müsste sie dennoch
  validieren.
* **Große Offline-Analysen auf Arrays.** Auf numpy basierende Bibliotheken
  sind pro Beobachtung schneller. sequential-analysis ist für die
  Verarbeitung Beobachtung für Beobachtung gebaut; die Kosten jeder
  Prozedur finden Sie unter [Geschwindigkeit](../../performance.md).
* **Methoden, die sie nicht hat.** Sie hat noch keinen Zweistichprobentest
  für Mediane, keine multivariaten Hawkes-Prozesse und keine ARIMA-Modelle
  mit Moving-Average-Termen. Was hinzukommt, steht im
  [Changelog](../../changelog.md).
