---
description: Perché controllare un p-value ogni giorno gonfia i falsi positivi nei test A/B e negli studi (il problema del peeking), e le tre famiglie di metodi sequenziali che lo risolvono, in Python con sequential-analysis.
language: it
---

# Perché non posso guardare un p-value ogni giorno?

> Questa è una traduzione della [pagina in inglese](../../guide/peeking.md). Non è ancora stata rivista da un madrelingua; in caso di differenze, fa fede la pagina in inglese.

**Risposta breve.** Un test a campione fisso promette un tasso di falsi
positivi del 5% solo se guardate il risultato una volta, alla dimensione
campionaria prevista. Se guardate più volte e vi fermate la prima volta
che p < 0,05, avete molte occasioni di essere ingannati. Con 20 sguardi
il tasso di falsi positivi sale a circa il 25%. I metodi sequenziali
sono costruiti per essere consultati ripetutamente. Con essi il tasso
resta al 5% o al di sotto, per quanto spesso guardiate e in qualunque
momento vi fermiate.

## Il problema del peeking, misurato

Due bracci con lo stesso tasso di conversione del 10% (un test A/A),
2.000 utenti, 200 ripetizioni. Il «peeking» (sbirciare i risultati)
esegue il consueto test z per due proporzioni ogni 100 utenti e si ferma
al primo p < 0,05. Il `TwoProportionTest` sequenziale viene controllato
dopo ogni singolo utente:

```python
import math
import random

from sequential_analysis.procedures import TwoProportionTest

def a_a_test(seed, users=2000):
    """Alternating arms, both converting 10% of the time: any 'effect' is a false positive."""
    rnd = random.Random(seed)
    return [(user % 2, int(rnd.random() < 0.10)) for user in range(users)]

def peeking(data, looks):
    """The z-test for two proportions after every len(data) / looks users; True if it ever rejects."""
    successes, trials, every = [0, 0], [0, 0], len(data) // looks
    for i, (arm, y) in enumerate(data, start=1):
        successes[arm] += y
        trials[arm] += 1
        if i % every == 0:
            pooled = sum(successes) / sum(trials)
            se = math.sqrt(pooled * (1 - pooled) * (1 / trials[0] + 1 / trials[1]))
            if se > 0 and abs(successes[1] / trials[1] - successes[0] / trials[0]) / se > 1.96:
                return True
    return False

def sequential(data):
    """The anytime-valid test, looked at after every user; True if it ever rejects."""
    test = TwoProportionTest(alpha=0.05)
    state = test.initial_state()
    for arm, y in data:
        state, out = test.step(state, {"arm": arm, "y": y})
        if out.decision is not None:
            return True
    return False

runs = [a_a_test(seed) for seed in range(200)]
print(f"z-test, one look at the end:   {sum(peeking(r, 1) for r in runs) / len(runs):.1%} false positives")
print(f"z-test, 20 looks:              {sum(peeking(r, 20) for r in runs) / len(runs):.1%}")
print(f"TwoProportionTest, 2000 looks: {sum(sequential(r) for r in runs) / len(runs):.1%}")
```

```text
z-test, one look at the end:   4.5% false positives
z-test, 20 looks:              28.0%
TwoProportionTest, 2000 looks: 5.0%
```

Lo sguardo singolo mantiene la promessa. Venti sguardi moltiplicano il
tasso di errore per circa sei. Il test sequenziale, consultato dopo
ciascuno dei 2.000 utenti, lo mantiene al 5%. Questa è la promessa: la
sua garanzia è **exact** (`TwoProportionTest.guarantee == "exact"`),
cioè un tasso di falsi positivi al massimo del 5% per ogni dimensione
campionaria, per quanto spesso si guardi. Con 200 ripetizioni, 10 falsi
positivi sono ciò che produce un 5% esatto.

## Le tre famiglie di metodi sequenziali

| Famiglia | Potete guardare | Uso tipico | In sequential-analysis |
|---|---|---|---|
| **Test sequenziali del rapporto di verosimiglianza** (sequential probability ratio tests, Wald 1945) | dopo ogni osservazione | un'ipotesi semplice contro un'altra, il minor numero di osservazioni in media: controllo qualità, simulazione, psicofisica | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Disegni sequenziali a gruppi** (group sequential designs; Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | in poche analisi ad interim pianificate | studi clinici con un comitato di monitoraggio dei dati | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Inferenza valida in ogni istante** (anytime-valid inference): e-valori, sequenze di confidenza, SPRT a miscela (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | dopo ogni osservazione, fermandosi per qualsiasi motivo | test A/B online, dashboard di monitoraggio | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**Quanto costa.** Guardare più spesso richiede più dati all'effetto per
cui si è pianificato:

* un disegno sequenziale a gruppi con quattro analisi richiede dall'1 al
  20% di pazienti in più rispetto a un'analisi singola;
* un test valido in ogni istante per due proporzioni richiede da 1,3 a
  1,6 volte gli utenti di un'analisi singola.

In cambio, un effetto grande ferma presto l'esperimento, e nessuno deve
fissare in anticipo la dimensione campionaria.

## Quando il problema non si pone

Il peeking gonfia gli errori solo quando ciò che fate dipende da ciò che
avete visto. Se guardate la dashboard ma portate sempre l'esperimento
fino alla dimensione prevista e testate una sola volta, il test a
campione fisso è valido. In quel caso è anche la scelta più efficiente.

Poi: [interrompere prima un test A/B](ab-testing.md),
[le sequenze di confidenza](confidence-sequences.md),
[il glossario](glossary.md).
