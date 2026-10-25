---
description: Le sequenze di confidenza (confidence sequences) sono intervalli di confidenza validi simultaneamente per ogni dimensione campionaria, che si possono quindi monitorare di continuo. Come calcolarle in Python per una media limitata, una mediana o un quantile e una media con code pesanti, con sequential-analysis.
language: it
---

# Come ottenere un intervallo di confidenza che resti valido se continuo a guardare?

> Questa è una traduzione della [pagina in inglese](../../guide/confidence-sequences.md). Non è ancora stata rivista da un madrelingua; in caso di differenze, fa fede la pagina in inglese.

**Risposta breve.** Usate una **sequenza di confidenza** (confidence
sequence). È una successione di intervalli, uno dopo ogni osservazione,
che contiene il valore vero per tutte le dimensioni campionarie
simultaneamente con probabilità almeno del 95%. Potete seguirla,
fermarvi quando è abbastanza stretta o esclude lo zero, e riportare
l'intervallo a cui vi siete fermati. Un normale intervallo di confidenza
al 95% promette il 95% solo per una dimensione campionaria fissata in
anticipo.

| Che cosa stimate | Ipotesi | Procedura | Garanzia |
|---|---|---|---|
| media di dati limitati (tassi, punteggi, ricavo con tetto) | valori in `[lower, upper]` | `BettingConfidenceSequence` | exact |
| mediana, 90° percentile, qualsiasi quantile | nessuna | `QuantileConfidenceSequence` | exact |
| media con code pesanti o valori anomali | un limite sulla deviazione standard | `CatoniConfidenceSequence` | exact |
| media di dati normali, varianza ignota | normalità | `TMixtureSPRT` (`lower`, `upper`) | exact sotto normalità |
| media di qualsiasi cosa, esecuzioni lunghe | varianza finita | `AsymptoticConfidenceSequence` | asymptotic |
| differenza tra due bracci | vedete [test A/B](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## L'intervallo usuale fallisce se lo si osserva

Estraete 500 osservazioni di una variabile 0/1 con media 0,3 e, dalla
30ª in poi, calcolate dopo ciascuna l'intervallo al 95% da manuale: la
media ± 1,96 errori standard. In quante delle 100 esecuzioni
l'intervallo manca la media vera a un certo punto?

```python
import math
import random

def stream(seed, n=500, p=0.3):
    rnd = random.Random(seed)
    return [float(rnd.random() < p) for _ in range(n)]

def textbook_ever_misses(xs, truth=0.3):
    total = total2 = 0.0
    for n, x in enumerate(xs, start=1):
        total, total2 = total + x, total2 + x * x
        if n >= 30:
            mean = total / n
            se = math.sqrt(max(total2 / n - mean * mean, 1e-12) / n)
            if abs(mean - truth) > 1.96 * se:
                return True
    return False

runs = [stream(seed) for seed in range(100)]
print(f"textbook interval misses the truth at some n in {sum(map(textbook_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
textbook interval misses the truth at some n in 28% of runs
```

Il suo «95%» vale solo per una dimensione campionaria fissata in
anticipo. La sequenza di confidenza per gli stessi dati, costruita
tramite scommesse (Waudby-Smith and Ramdas 2024), manca il valore vero
per qualche n al massimo nel 5% delle esecuzioni, per costruzione:

```python
from sequential_analysis.procedures import BettingConfidenceSequence

def sequence_ever_misses(xs, truth=0.3):
    cs = BettingConfidenceSequence(lower=0.0, upper=1.0, alpha=0.05, grid=100)
    state = cs.initial_state()
    for x in xs:
        state, out = cs.step(state, {"x": x})
        if not out.lower <= truth <= out.upper:
            return True
    return False

print(f"confidence sequence misses the truth at some n in {sum(map(sequence_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
confidence sequence misses the truth at some n in 1% of runs
```

## Una latenza mediana, senza alcuna ipotesi

Le latenze sono asimmetriche e con code pesanti, quindi per esse un
intervallo media ± errore standard non è affidabile.
`QuantileConfidenceSequence` copre qualsiasi quantile di qualsiasi
distribuzione, valori ripetuti (ties) compresi:

```python
from sequential_analysis.procedures import QuantileConfidenceSequence

rnd = random.Random(7)
median = QuantileConfidenceSequence(p=0.5, alpha=0.05)
p90 = QuantileConfidenceSequence(p=0.9, alpha=0.05)
m_state, q_state = median.initial_state(), p90.initial_state()
for _ in range(2000):
    latency = rnd.lognormvariate(math.log(120.0), 0.6)   # milliseconds; true median 120
    m_state, m = median.step(m_state, {"x": latency})
    q_state, q = p90.step(q_state, {"x": latency})
print(f"median: {m.estimate:.1f} ms, 95% confidence sequence [{m.lower:.1f}, {m.upper:.1f}]")
print(f"90th percentile: {q.estimate:.1f} ms, [{q.lower:.1f}, {q.upper:.1f}]")
```

```text
median: 117.3 ms, 95% confidence sequence [111.3, 122.6]
90th percentile: 252.7 ms, [237.9, 272.5]
```

I valori veri sono 120 ms e 258,8 ms. Entrambi gli intervalli valgono
simultaneamente per tutte le 2.000 dimensioni campionarie.

## Insidie

* **Limiti e tetti fanno parte dell'ipotesi.** Scegliete `lower` e
  `upper` prima di vedere i dati. Un valore al di fuori viene rifiutato.
* **Nessun metodo dà una copertura esatta per la media di dati
  illimitati arbitrari.** Per dati del genere usate un quantile, ponete
  un tetto ai valori, assumete un limite sulla deviazione standard
  (Catoni) o accettate una sequenza asintotica.
* **Le sequenze di confidenza sono più larghe di un intervallo singolo**
  a parità di dimensione campionaria. L'ampiezza è il prezzo dell'essere
  validi per ogni dimensione campionaria simultaneamente.

Per approfondire: [Quale metodo?](../../choosing.md),
[riferimento: inferenza valida in ogni istante e non parametrica](../../reference/anytime.md).
