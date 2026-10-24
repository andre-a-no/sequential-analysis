---
description: Guida utente di sequential-analysis, una libreria Python per test sequenziali e inferenza valida in ogni istante (anytime-valid). Ogni pagina risponde direttamente a una domanda, con codice funzionante e il relativo output.
language: it
---

# Guida utente

> Questa è una traduzione della [pagina in inglese](../../guide/index.md). Non è ancora stata rivista da un madrelingua; in caso di differenze, fa fede la pagina in inglese.

Questa guida è organizzata secondo le domande che ci si pone. Ogni
pagina si apre con una risposta diretta, poi presenta un breve programma
che funziona così com'è scritto, il suo output, la garanzia su cui si
basa la risposta e i casi in cui il metodo non si applica. I
[tutorial](../../tutorials/ab-test.md) approfondiscono ciascun argomento.

## La libreria in un paragrafo

**sequential-analysis** è una libreria Python per l'inferenza
statistica su dati che arrivano un'osservazione alla volta. I suoi test,
intervalli di confidenza e rilevatori possono essere consultati dopo
ogni osservazione e interrotti in qualsiasi momento, e i loro tassi di
errore restano comunque garantiti. Copre:

* lo SPRT di Wald e i piani sequenziali ottimali;
* i disegni sequenziali a gruppi (group sequential designs) per gli
  studi clinici (spesa dell'alfa di O'Brien–Fleming e di Pocock, confini
  di futilità);
* i test A/B validi in ogni istante (anytime-valid), con e-valori
  (e-values) e sequenze di confidenza (confidence sequences);
* il rilevamento di punti di cambiamento (change-point detection);
* i filtri di Kalman, particellari e di Markov nascosti;
* la previsione e la volatilità GARCH.

Ogni esecuzione può essere salvata come checkpoint JSON e ripresa bit
per bit in Python, oppure proseguita nel suo esecutore TypeScript con le
stesse decisioni.

| | |
|---|---|
| Installazione | `pip install sequential-analysis` |
| Import | `import sequential_analysis` |
| Python | da 3.8 a 3.14, nessuna dipendenza obbligatoria (numpy facoltativo) |
| Licenza | AGPL-3.0, oppure licenza commerciale di Novikov Laboratories LLC |
| Sorgenti | <https://github.com/andre-a-no/sequential-analysis> |
| Documentazione | <https://andre-a-no.github.io/sequential-analysis/> |

## Domande

**Concetti**

* [Perché non posso guardare un p-value ogni giorno?](peeking.md)
  Il peeking e le tre famiglie di metodi sequenziali.
* [Glossario](glossary.md): e-valore, sequenza di confidenza, spesa
  dell'alfa, ARL e gli altri termini, con i loro sinonimi.

**Attività**

* [Come interrompere prima un test A/B senza gonfiare i falsi positivi?](ab-testing.md)
* [Come ottenere un intervallo di confidenza che resti valido se continuo a guardare?](confidence-sequences.md)
* [Come eseguire lo SPRT di Wald in Python?](sprt.md)
* [Come pianificare le analisi ad interim di uno studio clinico?](clinical-trials.md)
* [Come rilevare un cambiamento in un flusso di misure?](change-detection.md)
* [Come fare statistica su un flusso e riprendere dopo un crash?](streaming.md)

**Scegliere**

* [Quale metodo per la mia domanda?](../../choosing.md): la tabella completa.
* [Come si confronta con altre librerie?](comparison.md)
* [Domande frequenti](faq.md)

## Come leggere le garanzie

Ogni procedura ha un attributo `guarantee`. La guida lo cita con ogni
risposta:

* **exact:** il tasso di errore vale per ogni dimensione campionaria
  sotto le ipotesi dichiarate.
* **asymptotic:** vale approssimativamente, e tanto meglio quanto più
  grande è il campione.
* **model:** le probabilità sono esatte sotto il modello dichiarato, ma
  non si afferma nulla al di là di esso.
* **approximate:** un'approssimazione anche sotto il modello.
* **none:** la procedura trasforma i dati e non afferma nulla.
