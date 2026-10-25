---
description: Mifuatano ya uhakika (confidence sequences) ni vipindi vya uhakika vinavyobaki halali katika kila ukubwa wa sampuli kwa wakati mmoja, kwa hiyo vinaweza kufuatiliwa mfululizo. Jinsi ya kuvikokotoa katika Python kwa wastani wenye mipaka, wastani wa kati au kwantili, na wastani wenye mikia mizito, kwa sequential-analysis.
language: sw
---

# Ninapataje kipindi cha uhakika kinachobaki halali ninapoendelea kutazama?

> Hii ni tafsiri ya [ukurasa wa Kiingereza](../../guide/confidence-sequences.md). Bado haijakaguliwa na mzungumzaji mzawa; pale ambapo hizi mbili zinatofautiana, ukurasa wa Kiingereza ndio wenye mamlaka.

**Jibu fupi.** Tumia **mfuatano wa uhakika** (confidence sequence). Ni
mfuatano wa vipindi, kimoja baada ya kila kipimo, unaojumuisha thamani
halisi katika ukubwa wote wa sampuli kwa wakati mmoja kwa uwezekano wa
angalau 95%. Unaweza kuutazama, kusimama unapokuwa mwembamba vya kutosha
au unapoacha sifuri nje, na kuripoti kipindi ulichosimamia. Kipindi cha
uhakika (confidence interval) cha kawaida cha 95% kinaahidi 95% katika
ukubwa mmoja tu wa sampuli uliowekwa mapema.

| Unachokadiria | Dhana | Utaratibu | Hakikisho |
|---|---|---|---|
| wastani wa data zenye mipaka (viwango, alama, mapato yaliyowekewa kikomo) | thamani ndani ya `[lower, upper]` | `BettingConfidenceSequence` | exact |
| wastani wa kati (median), pasentaili ya 90, kwantili yoyote | hakuna | `QuantileConfidenceSequence` | exact |
| wastani wenye mikia mizito au thamani pweke (outliers) | mpaka wa mkengeuko sanifu | `CatoniConfidenceSequence` | exact |
| wastani wa data za mgawanyo wa kawaida, variansi isiyojulikana | mgawanyo wa kawaida | `TMixtureSPRT` (`lower`, `upper`) | exact chini ya mgawanyo wa kawaida |
| wastani wa kitu chochote, uendeshaji mrefu | variansi yenye kikomo | `AsymptoticConfidenceSequence` | asymptotic |
| tofauti kati ya makundi mawili | tazama [majaribio ya A/B](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## Kipindi cha kawaida kinashindwa kinapotazamwa

Chukua vipimo 500 vya kigeu cha 0/1 chenye wastani 0.3, na kuanzia kipimo
cha 30 kokotoa kipindi cha 95% cha vitabuni baada ya kila kimoja: wastani
± makosa sanifu 1.96. Katika uendeshaji mingapi kati ya 100 kipindi
kinakosa wastani halisi wakati fulani?

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

"95%" yake inashikilia tu katika ukubwa wa sampuli uliowekwa mapema.
Mfuatano wa uhakika kwa data zile zile, kwa kuweka dau (betting)
(Waudby-Smith and Ramdas 2024), unakosa katika n fulani katika si zaidi
ya 5% ya uendeshaji, kwa jinsi ulivyojengwa:

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

## Wastani wa kati wa muda wa kuchelewa, bila dhana yoyote

Muda wa kuchelewa (latency) umepinda na una mikia mizito, kwa hiyo kipindi
cha wastani ± kosa sanifu hakiaminiki kwake. `QuantileConfidenceSequence`
inashughulikia kwantili yoyote ya mgawanyo wowote, ikiwemo thamani
zinazolingana:

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

Thamani halisi ni 120 ms na 258.8 ms. Vipindi vyote viwili vinashikilia
katika ukubwa wote 2,000 wa sampuli kwa wakati mmoja.

## Mitego

* **Mipaka na vikomo ni sehemu ya dhana.** Chagua `lower` na `upper`
  kabla ya kuona data. Thamani iliyo nje yake inakataliwa.
* **Hakuna mbinu inayotoa ufunikaji kamili kwa wastani wa data yoyote
  isiyo na mipaka.** Kwa data kama hizo tumia kwantili, weka kikomo kwa
  thamani, chukulia mpaka wa mkengeuko sanifu (Catoni), au kubali
  mfuatano wa asymptotic.
* **Mifuatano ya uhakika ni mipana kuliko kipindi kimoja** katika ukubwa
  ule ule wa sampuli. Upana huo ndio gharama ya kuwa halali katika kila
  ukubwa wa sampuli kwa wakati mmoja.

Zaidi: [Mbinu ipi?](../../choosing.md),
[marejeo: halali wakati wowote na isiyo ya kiparamita](../../reference/anytime.md).
