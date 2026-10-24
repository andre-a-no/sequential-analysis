---
description: Come eseguire il test sequenziale del rapporto di verosimiglianza di Wald (SPRT) in Python con sequential-analysis. Tassi di errore, dimensione campionaria media rispetto a un test a campione fisso e le alternative troncate (2-SPRT, piani ottimali di Kiefer–Weiss).
language: it
---

# Come eseguire lo SPRT di Wald in Python?

> Questa è una traduzione della [pagina in inglese](../../guide/sprt.md). Non è ancora stata rivista da un madrelingua; in caso di differenze, fa fede la pagina in inglese.

**Risposta breve.** `SPRT(family, theta0, theta1, alpha, beta)` di
`sequential_analysis.procedures` implementa il test sequenziale del
rapporto di verosimiglianza (sequential probability ratio test, SPRT)
di Wald. Decide tra due ipotesi semplici con il minor numero di
osservazioni in media. Fornitegli un'osservazione alla volta e
fermatevi alla prima decisione. Nell'esempio qui sotto gli serve circa
la metà delle osservazioni di un test a campione fisso con gli stessi
tassi di errore: da 65 a 76 pezzi in media invece di 133. Se vi serve
una dimensione campionaria massima garantita, usate invece `TwoSPRT` o
un piano ottenuto da `kiefer_weiss_plan`.

## Esempio: il tasso di difetti è del 10% o del 20%?

Un lotto viene accettato se il suo tasso di difetti è del 10% e
rifiutato se è del 20%, con entrambi i tassi di errore al 5%:

```python
import random

from sequential_analysis.procedures import SPRT, Bernoulli

test = SPRT(Bernoulli(), theta0=0.10, theta1=0.20, alpha=0.05, beta=0.05)

def inspect_items(rate, seed):
    """Inspect items until the test decides; returns (decision, items inspected)."""
    rnd = random.Random(seed)
    state = test.initial_state()
    while state.decision is None:
        state, out = test.step(state, {"x": int(rnd.random() < rate)})
    return state.decision, state.n

decision, n = inspect_items(0.10, seed=1)
print(f"a good batch: {decision} after {n} items")
```

```text
a good batch: accept_h0 after 108 items
```

Come si comporta su molti lotti?

```python
for rate in (0.10, 0.20):
    results = [inspect_items(rate, seed) for seed in range(2000)]
    wrong = sum(d == ("reject_h0" if rate == 0.10 else "accept_h0") for d, _ in results) / len(results)
    average = sum(n for _, n in results) / len(results)
    longest = max(n for _, n in results)
    print(f"defect rate {rate:.0%}: wrong decision {wrong:.1%}, average {average:.0f} items, longest {longest}")
```

```text
defect rate 10%: wrong decision 3.5%, average 76 items, longest 370
defect rate 20%: wrong decision 4.3%, average 65 items, longest 315
```

Un test a campione fisso con gli stessi tassi di errore ispeziona circa
133 pezzi in ogni lotto (approssimazione normale). Lo SPRT ne ispeziona
in media dal 43 al 51% in meno. La sua dimensione campionaria è però
casuale e non ha limite superiore, e alcuni lotti richiedono molto più
della media.

Le soglie sono quelle di Wald: log((1 − β)/α) e log(β/(1 − α)).
Garantiscono, per qualsiasi dimensione campionaria all'arresto, che i
tassi di errore effettivi α′ e β′ soddisfino α′ ≤ α/(1 − β),
β′ ≤ β/(1 − α) e α′ + β′ ≤ α + β. Al momento dell'arresto il rapporto
di verosimiglianza oltrepassa le soglie, quindi in pratica i tassi sono
inferiori a quelli nominali, come qui. È questo il senso di
`SPRT.guarantee == "exact"`. Per tassi di errore calcolati esattamente
anziché limitati, usate `operating_characteristic` su un piano (più
sotto).

## Quando vi serve una dimensione campionaria massima

* `TwoSPRT` (il 2-SPRT di Lorden) si ferma entro un orizzonte fisso e
  minimizza quasi la dimensione campionaria attesa nel caso peggiore.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  in `sequential_analysis.design` calcola per induzione all'indietro il
  piano ottimale con una dimensione campionaria massima. `PlanTest` lo
  esegue, e `operating_characteristic` ne fornisce i tassi di errore
  esatti e la dimensione campionaria attesa senza simulazione. Vedete
  `examples/07_design_kiefer_weiss.py`.
* Per pochi sguardi pianificati invece di uno per osservazione, usate un
  [disegno sequenziale a gruppi](clinical-trials.md).

## Quando lo SPRT è lo strumento sbagliato

* **Le ipotesi non sono semplici.** «Il tasso è del 10%» contro «il
  tasso è qualsiasi altro valore» è un'alternativa composta. Usate uno
  SPRT a miscela (`NormalMixtureSPRT`, `TMixtureSPRT`) o un test basato
  su scommesse (`BettingMeanTest`), che sono validi in ogni istante
  (anytime-valid) contro qualsiasi alternativa.
* **Il valore vero sta tra θ₀ e θ₁.** È il caso in cui lo SPRT è più
  lento, e la sua dimensione campionaria attesa può superare quella del test a
  campione fisso. Il piano di Kiefer–Weiss è costruito proprio per
  questo caso.

Famiglie disponibili per le procedure basate sul rapporto di
verosimiglianza: `Gaussian` (varianza nota), `Bernoulli`, `Poisson`,
`Exponential`.
