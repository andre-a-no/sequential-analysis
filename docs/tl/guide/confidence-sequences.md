---
description: Ang mga confidence sequence ay mga confidence interval na nananatiling valid sa lahat ng sample size nang sabay-sabay, kaya maaari silang bantayan nang tuloy-tuloy. Paano kalkulahin ang mga ito sa Python para sa bounded na mean, median o quantile, at mean na may heavy tails, gamit ang sequential-analysis.
language: tl
---

# Paano makakuha ng confidence interval na nananatiling valid kahit paulit-ulit akong tumitingin?

> Ito ay salin ng [pahina sa Ingles](../../guide/confidence-sequences.md). Hindi pa ito nasusuri ng isang katutubong tagapagsalita ng wika; kung saan magkaiba ang dalawa, ang pahina sa Ingles ang masusunod.

**Maikling sagot.** Gumamit ng **confidence sequence**. Isa itong
pagkakasunod-sunod ng mga interval, isa pagkatapos ng bawat obserbasyon,
na naglalaman ng tunay na halaga sa lahat ng sample size nang sabay-sabay
na may probabilidad na hindi bababa sa 95%. Puwede mo itong bantayan,
huminto kapag sapat na itong makitid o kapag hindi na nito sinasaklaw ang
zero, at iulat ang interval kung saan ka huminto. Ang karaniwang 95% na
confidence interval ay nangangako ng 95% sa iisang sample size lamang na
itinakda nang maaga.

| Ang tinatantiya mo | Assumption | Procedure | Garantiya |
|---|---|---|---|
| mean ng bounded na datos (mga rate, score, revenue na may cap) | mga halaga sa `[lower, upper]` | `BettingConfidenceSequence` | exact |
| median, 90th percentile, anumang quantile | wala | `QuantileConfidenceSequence` | exact |
| mean na may heavy tails o mga outlier | isang bound sa standard deviation | `CatoniConfidenceSequence` | exact |
| mean ng normal na datos, hindi alam ang variance | normality | `TMixtureSPRT` (`lower`, `upper`) | exact sa ilalim ng normality |
| mean ng kahit ano, mahahabang run | may hangganan ang variance | `AsymptoticConfidenceSequence` | asymptotic |
| pagkakaiba ng dalawang arm | tingnan ang [mga A/B test](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## Pumapalya ang karaniwang interval kapag binabantayan

Kumuha ng 500 obserbasyon ng isang 0/1 variable na may mean na 0.3, at mula
sa ika-30 pataas, kalkulahin pagkatapos ng bawat isa ang textbook na 95% na
interval: ang mean ± 1.96 standard error. Sa ilan sa 100 run hindi
nasasaklaw ng interval ang tunay na mean sa isang punto?

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

Ang "95%" nito ay nananatili lamang sa isang sample size na itinakda nang
maaga. Ang confidence sequence para sa parehong datos, gamit ang betting
(Waudby-Smith and Ramdas 2024), ay pumapalya sa isang n sa hindi hihigit sa
5% ng mga run, dahil sa mismong pagkakabuo nito:

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

## Median ng latency, nang walang anumang assumption

Ang mga latency ay skewed at heavy-tailed, kaya hindi mapagkakatiwalaan
para sa kanila ang interval na mean ± standard error. Saklaw ng
`QuantileConfidenceSequence` ang anumang quantile ng anumang distribution,
kasama ang mga tie:

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

Ang mga tunay na halaga ay 120 ms at 258.8 ms. Nananatili ang dalawang
interval sa lahat ng 2,000 sample size nang sabay-sabay.

## Mga dapat iwasan

* **Bahagi ng assumption ang mga bound at cap.** Piliin ang `lower` at
  `upper` bago makita ang datos. Tinatanggihan ang halagang nasa labas ng
  mga ito.
* **Walang pamamaraang nagbibigay ng eksaktong coverage para sa mean ng
  arbitraryong unbounded na datos.** Para sa ganitong datos, gumamit ng
  quantile, lagyan ng cap ang mga halaga, mag-assume ng bound sa standard
  deviation (Catoni), o tanggapin ang isang asymptotic na sequence.
* **Mas malapad ang mga confidence sequence kaysa sa iisang interval** sa
  parehong sample size. Ang lapad ang kapalit ng pagiging valid sa bawat
  sample size nang sabay-sabay.

Higit pa: [Aling pamamaraan?](../../choosing.md),
[reference: anytime-valid at nonparametric](../../reference/anytime.md).
