---
description: Come interrompere prima un test A/B senza gonfiare i falsi positivi, in Python. Test validi in ogni istante (anytime-valid) per la conversione e per ricavi limitati, controllo del sample ratio mismatch (SRM) e del tasso di false scoperte su molte metriche, con sequential-analysis.
language: it
---

# Come interrompere prima un test A/B senza gonfiare i falsi positivi?

> Questa è una traduzione della [pagina in inglese](../../guide/ab-testing.md). Non è ancora stata rivista da un madrelingua; in caso di differenze, fa fede la pagina in inglese.

**Risposta breve.** Usate un test valido in ogni istante
(anytime-valid): il suo p-value e il suo intervallo di confidenza
restano validi per quanto spesso guardiate, quindi potete fermarvi non
appena il risultato è chiaro. In sequential-analysis:

| Metrica | Procedura | Garanzia |
|---|---|---|
| tasso di conversione (0/1) | `TwoProportionTest` | exact |
| qualsiasi metrica limitata (ricavo con tetto, quota) | `BoundedABTest` | exact |
| eventi per unità di esposizione | `RateRatioTest` | exact per conteggi di Poisson |
| metrica rapporto (ricavo per sessione) | `RatioABTest` | asymptotic |
| media con una covariata pre-esperimento (CUPED) | `ABTest` | asymptotic |
| il traffico è ripartito come previsto? | `SampleRatioMismatch` | exact |
| più metriche o bracci insieme | `MultipleTests` (e-BH) | tasso di false scoperte (false discovery rate), exact |

Alimentate ogni procedura un utente alla volta: `state, out = test.step(state, {...})`.
Agite su `out.decision` quando volete.

## Conversione: fermarsi quando i dati sono conclusivi

Il gruppo di controllo converte il 10% degli utenti, il trattamento il
12%. Il test viene consultato dopo ogni utente e si ferma alla sua prima
decisione:

```python
import random

from sequential_analysis.procedures import TwoProportionTest

def users(n, rates=(0.10, 0.12), seed=1):
    """(arm, converted) per user; arm 1 is the treatment."""
    rnd = random.Random(seed)
    for _ in range(n):
        arm = int(rnd.random() < 0.5)
        yield arm, int(rnd.random() < rates[arm])

test = TwoProportionTest(alpha=0.05)
state = test.initial_state()
for arm, converted in users(60_000):
    state, out = test.step(state, {"arm": arm, "y": converted})
    if out.decision is not None:
        break
print(f"stopped after {out.n} users: conversion {out.rates[0]:.4f} (treatment) vs {out.rates[1]:.4f}, "
      f"anytime-valid p = {out.p_value:.4f}, decision: {out.decision}")
```

```text
stopped after 16469 users: conversion 0.1259 (treatment) vs 0.1068, anytime-valid p = 0.0496, decision: reject_h0
```

Per confronto, un test a campione fisso con potenza dell'80% per questo
incremento richiede circa 3.850 utenti per braccio, 7.700 in totale, e
può essere letto una sola volta, alla fine. Il test valido in ogni
istante paga la sua libertà: per raggiungere la stessa potenza gli
servono da 1,3 a 1,6 volte gli utenti di un'analisi singola, e questa
esecuzione ne ha richiesti di più. In cambio non c'è alcuna dimensione
campionaria da fissare in anticipo, e potete guardare il risultato ogni
giorno e fermarvi non appena è chiaro. Quando l'effetto è più grande del
previsto, questo accade molto prima.

## Ricavi: un intervallo esatto per una metrica limitata

`BoundedABTest` ha bisogno solo di limiti sulla metrica. Ponete un tetto
al ricavo a un valore scelto prima del test (qui 30), e la sequenza di
confidenza (confidence sequence) per la differenza tra le medie è esatta
per qualsiasi distribuzione:

```python
from sequential_analysis.procedures import BoundedABTest

rnd = random.Random(2)
revenue = BoundedABTest(lower=0.0, upper=30.0, allocation=0.5, input="revenue", grid=300)
state = revenue.initial_state()
for _ in range(20_000):
    arm = int(rnd.random() < 0.5)
    spend = min(rnd.expovariate(1 / (5.0 if arm == 0 else 5.6)), 30.0)   # capped at 30
    state, out = revenue.step(state, {"arm": arm, "revenue": spend})
print(f"after {out.n} users: mean revenue {out.means[0]:.2f} (treatment) vs {out.means[1]:.2f}, "
      f"95% confidence sequence for the difference [{out.lower:.2f}, {out.upper:.2f}]")
```

```text
after 20000 users: mean revenue 5.47 (treatment) vs 4.99, 95% confidence sequence for the difference [-0.30, 1.30]
```

L'intervallo vale simultaneamente in ciascuno dei 20.000 sguardi, non
solo nell'ultimo. Qui contiene ancora lo 0: 20.000 utenti non bastano a
stabilire un incremento di circa 0,5 su una metrica così rumorosa,
quindi l'esperimento prosegue.

## Controllare prima la ripartizione del traffico

Un sample ratio mismatch (SRM, squilibrio nella ripartizione dei
campioni) significa che la ripartizione differisce da quella
configurata, per esempio a causa di un bug nell'assegnazione o nel
logging. Le stime dell'effetto ottenute da un esperimento del genere non
sono affidabili. Uno scostamento da 50/50 a 52/48 viene individuato
mentre l'esperimento è in corso:

```python
from sequential_analysis.procedures import SampleRatioMismatch

srm = SampleRatioMismatch(weights=(0.5, 0.5), alpha=0.001)
state = srm.initial_state()
rnd = random.Random(3)
for _ in range(50_000):
    state, out = srm.step(state, {"arm": int(rnd.random() < 0.52)})
    if out.decision is not None:
        break
print(f"mismatch detected after {out.n} users: split {out.proportions[0]:.3f} / {out.proportions[1]:.3f}")
```

```text
mismatch detected after 4927 users: split 0.470 / 0.530
```

## Molte metriche insieme

Testare dieci metriche indipendenti al 5% ciascuna dà circa il 40% di
probabilità di almeno una falsa scoperta. `MultipleTests` combina gli
e-valori (e-values) di tutti i test con la procedura e-BH, così il tasso
di false scoperte resta ad `alpha` in qualsiasi tempo d'arresto:

```python
from sequential_analysis.procedures import MultipleTests

metrics = MultipleTests({
    "conversion": TwoProportionTest(input="converted"),
    "revenue": BoundedABTest(lower=0.0, upper=30.0, input="revenue", grid=100),
    "traffic split": SampleRatioMismatch((0.5, 0.5)),
}, alpha=0.05)
state = metrics.initial_state()
rnd = random.Random(4)
for _ in range(15_000):
    arm = int(rnd.random() < 0.5)
    converted = int(rnd.random() < (0.10, 0.13)[arm])
    spend = min(rnd.expovariate(1 / 5.0), 30.0)                          # no effect on revenue
    state, out = metrics.step(state, {"arm": arm, "converted": converted, "revenue": spend})
print("discoveries:", out.rejected)
```

```text
discoveries: ('conversion',)
```

## Insidie

* **Randomizzate l'unità che analizzate.** Se sono gli utenti a essere
  randomizzati, fornite un record per utente, non per visualizzazione di
  pagina. Per le metriche per sessione usate `RatioABTest`, che lavora
  sui totali per utente.
* **Fissate il tetto di una metrica limitata prima del test.**
  Sceglierlo dopo aver visto i dati annulla la garanzia.
* **Le procedure asintotiche richiedono campioni grandi.** Per `ABTest`
  e `RatioABTest` l'intervallo è valido solo approssimativamente su
  esecuzioni lunghe. Preferite le procedure esatte quando sono adatte.
* **L'allocazione adattiva del traffico** (bandit) richiede un test che
  resti valido quando la ripartizione dipende dagli esiti:
  `TwoProportionTest(method="universal")` oppure
  `BoundedABTest(propensity_input=...)`. Vedete il
  [tutorial, §10](../../tutorials/ab-test.md).

Per approfondire: il [tutorial sui test A/B](../../tutorials/ab-test.md)
(CUPED, metriche rapporto, tassi, pianificazione della durata) e
[un programma di esperimenti](../../tutorials/experiment-programme.md)
(tasso di false scoperte su molti esperimenti).
