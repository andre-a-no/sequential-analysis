---
description: Glossario dell'analisi sequenziale e dell'inferenza valida in ogni istante (anytime-valid) - e-valore, e-processo, sequenza di confidenza, p-value sempre valido, mSPRT, spesa dell'alfa, frazione di informazione, ARL, SRM, CUPED, e-BH - con i sinonimi e le procedure di sequential-analysis che implementano ciascun concetto.
language: it
---

# Glossario

> Questa è una traduzione della [pagina in inglese](../../guide/glossary.md). Non è ancora stata rivista da un madrelingua; in caso di differenze, fa fede la pagina in inglese.

Termini usati nell'analisi sequenziale e in questa libreria. I sinonimi
di uso comune sono indicati tra parentesi, insieme al termine inglese.

**Analisi sequenziale** (sequential analysis; test sequenziali,
inferenza sequenziale; sequential testing, sequential inference).
Statistica in cui il numero di osservazioni non è fissato in anticipo.
Dopo ogni osservazione o gruppo di osservazioni, la procedura decide se
fermarsi o continuare. Fondata da Wald (1945).

**Peeking** (sbirciare i risultati; arresto opzionale, monitoraggio
continuo; optional stopping, data peeking, continuous monitoring).
Consultare ripetutamente un test a campione fisso e fermarsi quando è
significativo. Gonfia il tasso di falsi positivi; vedete
[peeking](peeking.md).

**SPRT** (test sequenziale del rapporto di verosimiglianza, test di
Wald; sequential probability ratio test, Wald's test). Accumula il
logaritmo del rapporto di verosimiglianza di due ipotesi semplici e si
ferma quando esso esce da un intervallo. `SPRT`; versioni troncate
`TwoSPRT` (il 2-SPRT di Lorden) e `kiefer_weiss_plan`. Vedete
[SPRT](sprt.md).

**Disegno sequenziale a gruppi** (group sequential design; analisi ad
interim, studio sequenziale a gruppi; interim analyses, group sequential
trial). Poche analisi pianificate, ciascuna con un confine. I confini
sono scelti in modo che l'errore di primo tipo complessivo sia alfa.
`group_sequential_design`. Vedete [studi clinici](clinical-trials.md).

**Funzione di spesa dell'alfa** (alpha spending function; spesa
dell'errore, Lan–DeMets; error spending). Indica quanta parte
dell'errore di primo tipo può essere consumata a ciascuna frazione di
informazione. La spesa di tipo O'Brien–Fleming spende poco all'inizio,
quella di tipo Pocock spende in modo uniforme.
`spending="obrien-fleming"`, `"pocock"`, ...

**Frazione di informazione** (information fraction). La quota
dell'informazione statistica pianificata (pazienti, eventi) raggiunta a
un'analisi.

**Confine di futilità** (futility boundary; futilità non vincolante,
non-binding futility). Un confine inferiore: al di sotto, si raccomanda
di fermarsi per mancanza di effetto. Un confine non vincolante può
essere ignorato senza gonfiare l'errore di primo tipo.

**Inferenza valida in ogni istante** (anytime-valid inference; inferenza
sempre valida, always-valid inference, safe anytime-valid inference,
SAVI). Test e intervalli le cui garanzie valgono simultaneamente per
ogni dimensione campionaria, quindi possono essere monitorati di
continuo e interrotti per qualsiasi motivo.

**E-valore** (e-value; e-variabile, punteggio di scommessa; e-variable,
betting score). Una statistica non negativa il cui valore atteso sotto
l'ipotesi nulla è al massimo 1. Un e-valore grande è evidenza contro
l'ipotesi nulla: rifiutare quando supera 1/alfa ha un errore di primo
tipo al massimo pari ad alfa. L'output `log_e_value` di molte
procedure.

**E-processo** (e-process; martingala di test, supermartingala di test,
processo di ricchezza; test martingale, test supermartingale, wealth
process). Una successione di e-valori che resta valida ai tempi
d'arresto. Il suo massimo corrente supera 1/alfa con probabilità al
massimo alfa sotto l'ipotesi nulla (disuguaglianza di Ville).

**P-value sempre valido** (always-valid p-value; p-value valido in ogni
istante, p-value sequenziale; anytime-valid p-value, sequential
p-value). Un p-value valido a qualsiasi tempo d'arresto. È l'inverso del
massimo corrente di un e-processo. L'output `p_value` delle procedure
valide in ogni istante.

**Sequenza di confidenza** (confidence sequence; intervallo di confidenza
valido in ogni istante, intervallo di confidenza sempre valido,
intervallo di confidenza uniforme nel tempo; anytime-valid confidence
interval, always-valid confidence interval, time-uniform confidence
interval). Una successione di intervalli che contiene il valore vero per
tutte le dimensioni campionarie simultaneamente con probabilità almeno
1 − alfa. `BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, e gli output
`lower` e `upper` di molti test. Vedete
[sequenze di confidenza](confidence-sequences.md).

**mSPRT** (SPRT a miscela, miscela di Robbins; mixture SPRT, Robbins'
mixture). Uno SPRT la cui alternativa è mediata rispetto a una
distribuzione a priori, il che lo rende valido in ogni istante contro
qualsiasi alternativa. `NormalMixtureSPRT` (varianza nota),
`TMixtureSPRT` (varianza ignota).

**Test basati su scommesse** (testing by betting). Costruzione di
e-processi come la ricchezza di uno scommettitore che punta contro
l'ipotesi nulla. `BettingMeanTest`, `BettingConfidenceSequence`,
`KernelTwoSampleTest`.

**GROW** (growth-rate optimal, ottimale per il tasso di crescita). Un
e-valore scelto per massimizzare la crescita logaritmica attesa
dell'evidenza sotto l'alternativa. `TwoProportionTest(method="grow")`.

**Inferenza universale** (universal inference). Un e-valore ottenuto da
un rapporto di verosimiglianza con l'alternativa stimata solo dai dati
passati. Resta valido con disegni adattivi.
`TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). Controlla il tasso di false scoperte
(false discovery rate) su molti e-valori, sotto qualsiasi dipendenza.
`MultipleTests`, `e_bh`.

**e-LOND, FDR online** (online FDR). Controllo del tasso di false
scoperte su una serie di ipotesi decise una alla volta. `OnlineFDR`.

**SRM** (sample ratio mismatch; squilibrio nella ripartizione dei
campioni). La ripartizione osservata del traffico tra i bracci
differisce da quella configurata, segno di un bug nell'esperimento.
`SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data;
aggiustamento per covariate, aggiustamento per regressione; covariate
adjustment, regression adjustment). Riduce la varianza di un effetto A/B
con una covariata misurata prima dell'esperimento.
`ABTest(covariate=True)`, `AnytimeLinearModel`.

**Metrica rapporto** (ratio metric; metodo delta, delta method). Una
metrica che è il rapporto di due somme per utente, come il ricavo per
sessione. `RatioABTest`.

**Rilevamento di punti di cambiamento** (change-point detection;
rilevamento di cambiamenti, rilevamento più rapido, rilevamento online
di anomalie; change detection, quickest detection, online anomaly
detection). Lanciare un allarme poco dopo che la distribuzione di un
flusso è cambiata. `CUSUM`, `ShiryaevRoberts`, `MeanEDetector`,
`QuantileEDetector`, `BayesianChangePoint`. Vedete
[rilevamento di cambiamenti](change-detection.md).

**ARL** (average run length; lunghezza media della sequenza, ARL₀,
tempo medio al falso allarme; mean time to false alarm). Il numero
atteso di osservazioni fino a un falso allarme quando nulla è cambiato.
Il controllo dei falsi allarmi dei rilevatori di cambiamenti.

**E-detector** (e-rilevatore). Un rilevatore di cambiamenti costruito da
e-processi, uno avviato a ogni possibile istante di cambiamento. La sua
ARL è garantita sotto un'ipotesi nulla non parametrica.
`MeanEDetector`, `QuantileEDetector`.

**Problema di Kiefer–Weiss** (Kiefer–Weiss problem). Trovare il test
sequenziale con dimensione campionaria massima che minimizza la più
grande dimensione campionaria attesa. `kiefer_weiss_plan`.

**Caratteristica operativa** (operating characteristic). Le probabilità
di errore e la distribuzione della dimensione campionaria di un piano,
in funzione del vero valore del parametro. `operating_characteristic`.

**Checkpoint** (punto di ripristino). Un valore JSON da cui
un'esecuzione riprende esattamente. `Run.checkpoint`, `Run.restore`.
Vedete [streaming](streaming.md).

**Digest della storia** (history digest). Una catena di hash SHA-256
sulle osservazioni usate da un'esecuzione, conservata in ogni
checkpoint, a fini di audit.

**Garanzia** (guarantee; `exact`, `asymptotic`, `model`, `approximate`,
`none`). L'attributo in cui ogni procedura di questa libreria dichiara
ciò che promette. Vedete [Quale metodo?](../../choosing.md).
