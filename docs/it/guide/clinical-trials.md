---
description: Come pianificare e condurre le analisi ad interim di uno studio clinico in Python, con disegni sequenziali a gruppi (O'Brien–Fleming, Pocock, spesa dell'alfa di Lan–DeMets, confini di futilità), dimensioni campionarie per medie, proporzioni e sopravvivenza, verificate rispetto a rpact, con sequential-analysis.
language: it
---

# Come pianificare le analisi ad interim di uno studio clinico?

> Questa è una traduzione della [pagina in inglese](../../guide/clinical-trials.md). Non è ancora stata rivista da un madrelingua; in caso di differenze, fa fede la pagina in inglese.

**Risposta breve.** Usate un disegno sequenziale a gruppi (group
sequential design). `group_sequential_design(alpha, fractions, spending=...)`
di `sequential_analysis.group_sequential` calcola:

* i confini di efficacia, con la spesa dell'alfa (alpha spending) di
  Lan–DeMets (di tipo O'Brien–Fleming, di tipo Pocock e altri);
* confini di futilità (futility boundaries) non vincolanti;
* la potenza e la dimensione campionaria attesa;
* la dimensione campionaria massima per medie e proporzioni, o il numero
  di eventi per la sopravvivenza.

I confini e le dimensioni campionarie concordano con il pacchetto R
rpact. Le procedure di test (`GroupSequentialTest`,
`GroupSequentialTwoMeans`, `GroupSequentialProportions`,
`GroupSequentialLogRank`) conducono poi lo studio, paziente per paziente
o evento per evento. Eseguono ciascuna analisi ad interim (interim
analysis) quando viene raggiunta la sua frazione di informazione.

## Disegno: quattro analisi, spesa di O'Brien–Fleming

α unilaterale = 0,025, analisi al 25%, 50%, 75% e 100% dei pazienti,
potenza del 90%, con un confine di futilità:

```python
from sequential_analysis.group_sequential import group_sequential_design

design = group_sequential_design(0.025, [0.25, 0.5, 0.75, 1.0], spending="obrien-fleming",
                                 futility="obrien-fleming", power=0.9)
for k, (t, b, f) in enumerate(zip(design.fractions, design.bounds, design.futility), start=1):
    print(f"analysis {k} at {t:.0%}: efficacy if Z >= {b:.3f}, futility if Z <= {f:.3f}")
print("patients for an effect of 0.3 standard deviations:", design.max_sample_size(effect=0.3, sigma=1.0))
print(f"expected share of the patients used: {design.expected_fraction(0.0):.2f} with no effect, "
      f"{design.expected_fraction(design.drift):.2f} with the planned effect")
```

```text
analysis 1 at 25%: efficacy if Z >= 4.333, futility if Z <= -1.403
analysis 2 at 50%: efficacy if Z >= 2.963, futility if Z <= 0.325
analysis 3 at 75%: efficacy if Z >= 2.359, futility if Z <= 1.291
analysis 4 at 100%: efficacy if Z >= 2.014, futility if Z <= 2.014
patients for an effect of 0.3 standard deviations: 127
expected share of the patients used: 0.59 with no effect, 0.73 with the planned effect
```

## Endpoint binari e di sopravvivenza

```python
binary = group_sequential_design(0.025, [1 / 3, 2 / 3, 1.0], spending="obrien-fleming")
print("patients, response 10% vs 12%, 80% power:",
      binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8))
print("events for a hazard ratio of 0.7, 80% power:", binary.max_events(hazard_ratio=0.7, power=0.8))
print(f"inflation factor over a single analysis: {binary.inflation_factor(0.8):.3f}")
```

```text
patients, response 10% vs 12%, 80% power: 7780
events for a hazard ratio of 0.7, 80% power: 250
inflation factor over a single analysis: 1.013
```

Con la spesa di O'Brien–Fleming, tre analisi costano l'1,3% di pazienti
in più rispetto a un'unica analisi finale.

## Condurre lo studio

```python
import random

from sequential_analysis.procedures import GroupSequentialProportions

n_max = binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8)
test = GroupSequentialProportions.from_design(binary, n_max)
state, rnd = test.initial_state(), random.Random(3)
for patient in range(n_max):
    arm = patient % 2                                         # 1 treatment, 0 control
    state, out = test.step(state, {"arm": arm, "y": int(rnd.random() < (0.12 if arm else 0.10))})
    if out.analysis:
        print(f"analysis {out.analysis} after {out.n} patients: Z = {out.z:.2f}, bound {out.bound:.2f}")
    if out.decision:
        print("decision:", out.decision)
        break
```

```text
analysis 1 after 2594 patients: Z = 2.14, bound 3.71
analysis 2 after 5187 patients: Z = 2.64, bound 2.51
decision: reject_h0
```

Lo studio si è fermato per efficacia alla seconda analisi, dopo due
terzi dei pazienti previsti.

## Quando le analisi non avvengono come previsto

I comitati di monitoraggio dei dati raramente si riuniscono esattamente
al 25% dell'informazione:

* `design.at(fractions)` ricalcola i confini per l'informazione
  effettivamente raggiunta. La spesa dell'alfa preserva il livello
  complessivo.
* `GroupSequentialMonitor` accetta qualsiasi statistica che calcoliate
  voi stessi (un modello di Cox, un modello misto) come valore Z, insieme
  alla sua informazione, a ogni riunione.

## E se volete guardare dopo ogni paziente?

Un disegno sequenziale a gruppi consente solo il numero di sguardi
pianificato. Per monitorare dopo ogni paziente o evento, usate una
procedura valida in ogni istante (anytime-valid): `AnytimeLogRankTest`
per la sopravvivenza, `TwoProportionTest` per i tassi di risposta,
`TMixtureSPRT` per una media. Richiedono più pazienti all'effetto
pianificato. Vedete il [tutorial: studio di sopravvivenza](../../tutorials/survival.md).

## Prassi regolatoria

I disegni sequenziali a gruppi con spesa dell'alfa sono l'approccio
consolidato negli studi confermativi, descritto nella linea guida ICH E9
e nella guida della FDA sui disegni adattivi (2019). Questa libreria
calcola i disegni e conserva una registrazione verificabile e
riprendibile di ogni analisi (il checkpoint e il digest della sua
storia). Non è un software validato in senso regolatorio: uno sponsor
che la usa in una sottomissione deve validarla come qualsiasi altro
strumento.

Per approfondire: [tutorial: studio sequenziale a gruppi](../../tutorials/group-sequential.md),
che confronta i numeri con rpact;
[riferimento: disegno e pianificazione](../../reference/design.md).
