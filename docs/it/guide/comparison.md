---
description: Come si confronta sequential-analysis con altre librerie Python e R per test sequenziali, test A/B, disegni sequenziali a gruppi, rilevamento di cambiamenti e filtraggio (statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn), e quando usare quale.
language: it
---

# Come si confronta con altre librerie?

> Questa è una traduzione della [pagina in inglese](../../guide/comparison.md). Non è ancora stata rivista da un madrelingua; in caso di differenze, fa fede la pagina in inglese.

**Risposta breve.** La maggior parte delle librerie copre bene una sola
famiglia di metodi. sequential-analysis riunisce le principali famiglie
dell'inferenza sequenziale dietro un'unica interfaccia:

* gli SPRT e i piani ottimali;
* i disegni sequenziali a gruppi (group sequential designs);
* i test validi in ogni istante (anytime-valid) e le sequenze di
  confidenza (confidence sequences);
* il rilevamento di cambiamenti (change detection);
* i filtri a spazio degli stati.

Che cosa aggiunge oltre ai metodi stessi:

* ogni procedura dichiara la propria garanzia (`exact`, `asymptotic`,
  `model`, ...);
* ogni esecuzione può essere salvata in un checkpoint e ripresa bit per
  bit;
* i formati sono specificati ed eseguiti da una seconda implementazione
  in TypeScript;
* non ci sono dipendenze obbligatorie.

Se vi serve solo uno dei metodi qui sotto e usate già la libreria
specializzata in esso, continuate a usare quella libreria. La tabella
indica dove ciascuno strumento è la scelta naturale. Le descrizioni
riguardano lo scopo principale di ciascuna libreria, a ottobre 2026, e
non sono un elenco completo delle sue funzionalità.

| Esigenza | Scelte naturali | Che cosa offre sequential-analysis |
|---|---|---|
| test a campione fisso, regressione, potenza | scipy.stats, statsmodels | non è il suo scopo |
| disegni sequenziali a gruppi per una sottomissione regolatoria | rpact, gsDesign (R) | gli stessi disegni, verificati rispetto a rpact nella sua suite di test; conduce lo studio passo per passo con checkpoint |
| sequenze di confidenza, e-valori | confseq (Python), safestats (R) | sequenze di confidenza per medie, quantili, coefficienti di regressione, effetti a due campioni; e-BH ed e-LOND per molti test |
| test A/B come piattaforma con interfaccia utente | GrowthBook, Statsig, Eppo, Optimizely (piattaforme) | un motore da integrare: test esatti per conversione, metriche limitate e di tasso, SRM, FDR su più metriche |
| segmentazione offline in punti di cambiamento di una serie conclusa | ruptures (Python), changepoint (R) | rilevamento online mentre i dati arrivano: CUSUM, Shiryaev–Roberts, e-detector, punti di cambiamento bayesiani online |
| filtri di Kalman | filterpy, statsmodels state space | filtri di Kalman, di Kalman robusto, particellari e HMM, con smoothing e checkpoint |
| GARCH | arch | GARCH(1,1) e GJR stimati con lo stesso massimo raggiunto da arch (verificato nei test), poi eseguiti online |
| modelli di Markov nascosti | hmmlearn | il filtro online, Baum–Welch in accordo con hmmlearn, EM online |
| previsione | statsmodels, altri | previsioni ETS e AR in accordo con statsmodels, apprese online, con intervalli conformali |

## Casi in cui un altro strumento è migliore

* **Una sottomissione a un'autorità regolatoria.** rpact è ampiamente
  usato a questo scopo, e i suoi sviluppatori offrono documentazione di
  validazione. sequential-analysis concorda con esso sui disegni che
  copre, ma uno sponsor dovrebbe comunque validarla.
* **Grandi analisi offline su array.** Le librerie basate su numpy sono
  più veloci per osservazione. sequential-analysis è costruita per
  un'osservazione alla volta; vedete [Velocità](../../performance.md) per
  il costo di ciascuna procedura.
* **Metodi che non ha.** Non ha ancora un test a due campioni per le
  mediane, né processi di Hawkes multivariati, né modelli ARIMA con
  termini a media mobile. Vedete il [registro delle modifiche](../../changelog.md) per
  ciò che viene aggiunto.
