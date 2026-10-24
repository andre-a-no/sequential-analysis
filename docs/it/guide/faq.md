---
description: Domande frequenti su sequential-analysis, la libreria Python per test sequenziali e inferenza valida in ogni istante (anytime-valid) - installazione, licenza e uso commerciale, test A/B in produzione, studi clinici, potenza, velocità, TypeScript, citazione.
language: it
---

# Domande frequenti

> Questa è una traduzione della [pagina in inglese](../../guide/faq.md). Non è ancora stata rivista da un madrelingua; in caso di differenze, fa fede la pagina in inglese.

## La libreria

### Che cos'è sequential-analysis?

Una libreria Python per l'inferenza statistica sequenziale. I suoi test,
le sue sequenze di confidenza (confidence sequences) e i suoi rilevatori
possono essere controllati dopo ogni osservazione e interrotti in
qualsiasi momento, senza perdere le loro garanzie sugli errori. Offre:

* SPRT;
* disegni sequenziali a gruppi (group sequential designs);
* test A/B validi in ogni istante (anytime-valid);
* rilevatori di punti di cambiamento (change-point detectors);
* filtri di Kalman, particellari e di Markov nascosti;
* previsione e GARCH.

Tutti funzionano dietro un'unica interfaccia, con checkpoint JSON. È
sviluppata da Novikov Laboratories LLC.

### Come si installa? Da che cosa dipende?

`pip install sequential-analysis`. Richiede Python 3.8 o successivo
(testata fino alla 3.14) e nient'altro.
`pip install "sequential-analysis[fast]"` aggiunge numpy per le
procedure che lavorano su array. pandas, polars, i client Kafka e
matplotlib vengono usati solo se chiamate gli adattatori o le funzioni
di grafico.

### È gratuita per uso commerciale?

È distribuita con doppia licenza, AGPL-3.0 e licenza commerciale. Questi
usi sono gratuiti sotto l'AGPL:

* ricerca e didattica;
* progetti open source sotto AGPL o GPL v3;
* uso interno in un'organizzazione, senza copie cedute ad altri e senza
  accesso via rete per persone esterne.

Un prodotto a codice chiuso, o un servizio di rete di cui non pubblicate
il codice sorgente, richiede una licenza commerciale. La tabella in
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)
decide i singoli casi. Richieste di licenza: andrei@hobukob.ru.

### Come si cita?

[CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff)
nel repository fornisce la citazione, e il pulsante *Cite this
repository* di GitHub la converte in BibTeX o APA. Le release sono
archiviate su Zenodo con un DOI. I metodi e le loro verifiche sono
descritti nell'[articolo](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf).

## Uso

### Posso usarla per test A/B in produzione?

Sì, come motore statistico. Fornisce test esatti per:

* la conversione (`TwoProportionTest`);
* le metriche limitate (`BoundedABTest`);
* i tassi (`RateRatioTest`);
* la ripartizione del traffico (`SampleRatioMismatch`);
* molte metriche con controllo del tasso di false scoperte (false
  discovery rate) (`MultipleTests`).

In Python puro il test di conversione richiede circa 10 microsecondi per
utente, il controllo della ripartizione 4 e il test sui tassi 40. Un
checkpoint di ciascuno occupa 2–4 kilobyte.
`BoundedABTest` mantiene una griglia e richiede 0,1–0,5 ms.

La libreria non è una piattaforma di sperimentazione: l'assegnazione,
la raccolta degli eventi e le dashboard tocca a voi costruirle o
prenderle da una piattaforma. Vedete [test A/B](ab-testing.md).

### Posso sbirciare i risultati ogni giorno?

Sì, con le procedure valide in ogni istante: servono proprio a questo.
Con un disegno sequenziale a gruppi, guardate solo alle analisi
pianificate. Con un classico test a campione fisso, guardate una volta.
Vedete [peeking](peeking.md).

### Un test valido in ogni istante è meno potente di un test a campione fisso?

All'effetto per cui è pianificato il test a campione fisso, sì. Per
raggiungere la stessa potenza, un test valido in ogni istante per due
proporzioni richiede da 1,3 a 1,6 volte gli utenti. In cambio potete
fermarvi presto quando l'effetto è più grande, e non serve alcuna
dimensione campionaria fissata in anticipo. Un disegno sequenziale a
gruppi con pochi sguardi pianificati costa solo dall'1 al 20% in più di
un'analisi singola.

### Sequenziale a gruppi o valido in ogni istante: quale usare?

* **Sequenziale a gruppi** se le analisi sono poche e pianificate, come
  con un comitato di monitoraggio dei dati o un ciclo di rilascio, e in
  particolare per uno studio clinico confermativo.
* **Valido in ogni istante** se volete guardare di continuo, o non
  potete dire in anticipo quando guarderete o vi fermerete.

### Fa test A/B bayesiani?

I suoi test A/B sono frequentisti, con garanzie sui tassi di errore.
Componenti bayesiane sono disponibili dove sono adatte:

* `ThompsonAllocation` assegna il traffico in base alla probabilità a
  posteriori che ciascun braccio sia il migliore, con una regola di
  perdita attesa per il rilascio;
* `BayesianChangePoint` rileva i punti di cambiamento;
* i modelli di previsione apprendono i loro parametri per aggiornamento
  bayesiano.

### È validata per gli studi clinici?

I suoi disegni sequenziali a gruppi (confini, potenza, dimensioni
campionarie, numeri di eventi) sono verificati rispetto a rpact e al
pacchetto R survival nella suite di test. Non è un software validato in
senso regolatorio. Uno sponsor che la usa per una sottomissione la
valida come qualsiasi altro strumento. Vedete
[studi clinici](clinical-trials.md).

### La mia metrica ha code pesanti (ricavi, latenza). Che cosa uso?

* Per un quantile (mediana, 90° percentile), usate `QuantileTest` o
  `QuantileConfidenceSequence`, che non richiedono ipotesi.
* Per una media, ponete un tetto ai valori a un livello fissato in
  anticipo e usate `BoundedABTest` o `BettingConfidenceSequence`
  (esatti).
* In alternativa, assumete un limite sulla deviazione standard e usate
  `CatoniConfidenceSequence`.

Un test a due campioni per le mediane non è ancora presente nella
libreria.

### Quanto è veloce?

Le procedure più semplici richiedono 1–10 microsecondi per osservazione
in Python puro: SPRT, CUSUM, i test sequenziali a gruppi e a miscela,
GARCH. Quelle che mantengono una griglia o l'intero campione richiedono
0,1–10 ms. Ne sono esempi le sequenze di confidenza basate su scommesse
e di Catoni, il test a kernel e i modelli di previsione appresi.
[Velocità](../../performance.md) elenca il costo e la dimensione del
checkpoint di ciascuna procedura.

### Posso eseguirla in JavaScript o nel browser?

Sì. L'esecutore TypeScript in `ts/` esegue le procedure e prosegue i
checkpoint Python. I digest della storia e le decisioni sono identici, e
i numeri concordano fino agli ultimi bit. Vedete
[esecutore TypeScript](../../typescript.md).

### Un'esecuzione può sopravvivere a un crash?

Sì. `run.checkpoint()` è semplice JSON, e `Run.restore` riprende bit per
bit. Le osservazioni consegnate di nuovo vengono scartate. Vedete
[streaming](streaming.md).

### Che cosa significano «exact» e «asymptotic» nella documentazione?

L'attributo `guarantee` di ogni procedura dichiara la sua promessa:

* `exact`: il tasso di errore vale per ogni dimensione campionaria
  sotto le ipotesi dichiarate;
* `asymptotic`: approssimativamente, su esecuzioni lunghe;
* `model`: esatto sotto il modello dichiarato;
* `approximate`;
* `none`.

La documentazione raccomanda la procedura esatta quando ce n'è una
adatta. Vedete [Quale metodo?](../../choosing.md).
