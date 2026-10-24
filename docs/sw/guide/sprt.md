---
description: Jinsi ya kuendesha jaribio la mfuatano la uwiano wa uwezekano (SPRT) la Wald katika Python kwa sequential-analysis. Viwango vya makosa, wastani wa ukubwa wa sampuli ukilinganishwa na jaribio la sampuli isiyobadilika, na mbadala zilizokatwa (2-SPRT, mipango bora ya Kiefer–Weiss).
language: sw
---

# Ninaendeshaje SPRT ya Wald katika Python?

> Hii ni tafsiri ya [ukurasa wa Kiingereza](../../guide/sprt.md). Bado haijakaguliwa na mzungumzaji mzawa; pale ambapo hizi mbili zinatofautiana, ukurasa wa Kiingereza ndio wenye mamlaka.

**Jibu fupi.** `SPRT(family, theta0, theta1, alpha, beta)` kutoka
`sequential_analysis.procedures` inatekeleza jaribio la mfuatano la
uwiano wa uwezekano (sequential probability ratio test) la Wald.
Linaamua kati ya nadharia tete (hypotheses) mbili sahili kwa wastani wa
vipimo vichache zaidi. Lilishe kipimo kimoja kwa wakati na usimame kwenye
uamuzi wa kwanza. Katika mfano ulio hapa chini linahitaji takriban nusu
ya vipimo vya jaribio la sampuli isiyobadilika (fixed-sample test) lenye
viwango sawa vya makosa: wastani wa vitu 65–76 badala ya 133. Ikiwa
unahitaji ukubwa wa juu wa sampuli uliohakikishwa, tumia `TwoSPRT` au
mpango kutoka `kiefer_weiss_plan` badala yake.

## Mfano: je, kiwango cha kasoro ni 10% au 20%?

Shehena inakubaliwa ikiwa kiwango chake cha kasoro ni 10% na kukataliwa
ikiwa ni 20%, huku viwango vyote viwili vya makosa vikiwa 5%:

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

Linafanya vizuri kiasi gani kwa shehena nyingi?

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

Jaribio la sampuli isiyobadilika lenye viwango sawa vya makosa hukagua
takriban vitu 133 katika kila shehena (ukadiriaji wa mgawanyo wa
kawaida). SPRT hukagua vitu 43–51% vichache zaidi kwa wastani. Hata
hivyo, ukubwa wake wa sampuli ni wa nasibu na hauna kikomo cha juu, na
shehena chache huchukua muda mrefu zaidi sana kuliko wastani.

Vizingiti ni vya Wald: log((1 − β)/α) na log(β/(1 − α)). Vinahakikisha,
kwa ukubwa wowote wa sampuli wakati wa kusimama, kwamba viwango halisi
vya makosa α′ na β′ vinatimiza α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) na
α′ + β′ ≤ α + β. Uwiano wa uwezekano (likelihood ratio) unavuka vizingiti
unaposimama, kwa hiyo kiutendaji viwango viko chini ya vile vya kawaida
vilivyotajwa (nominal), kama hapa. Hiyo ndiyo maana ya
`SPRT.guarantee == "exact"`. Kwa viwango vya makosa vilivyokokotolewa
kwa usahihi badala ya kuwekewa mipaka, tumia `operating_characteristic`
kwenye mpango (tazama hapa chini).

## Unapohitaji ukubwa wa juu wa sampuli

* `TwoSPRT` (2-SPRT ya Lorden) inasimama kabla ya upeo uliowekwa na
  karibu inapunguza hadi kiwango cha chini ukubwa wa sampuli unaotarajiwa
  katika hali mbaya zaidi.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  katika `sequential_analysis.design` inakokotoa mpango bora wenye ukubwa
  wa juu wa sampuli kwa uingizaji wa kurudi nyuma (backward induction).
  `PlanTest` inautekeleza, na `operating_characteristic` inatoa viwango
  vyake kamili vya makosa na ukubwa wa sampuli unaotarajiwa bila uigaji.
  Tazama `examples/07_design_kiefer_weiss.py`.
* Kwa matazamo machache yaliyopangwa badala ya moja kwa kila kipimo,
  tumia [muundo wa mfuatano wa vikundi](clinical-trials.md).

## Wakati SPRT si zana sahihi

* **Nadharia tete si sahili.** "Kiwango ni 10%" dhidi ya "kiwango ni
  chochote kingine" ni mbadala mchanganyiko (composite). Tumia SPRT ya
  mchanganyiko (mixture SPRT) (`NormalMixtureSPRT`, `TMixtureSPRT`) au
  jaribio kwa kuweka dau (`BettingMeanTest`), ambazo ni halali wakati
  wowote dhidi ya kila mbadala.
* **Thamani halisi iko kati ya θ₀ na θ₁.** SPRT basi ndiyo inakuwa
  polepole zaidi, na ukubwa wake wa sampuli unaotarajiwa unaweza kuzidi
  ukubwa wa sampuli isiyobadilika. Mpango wa Kiefer–Weiss umejengwa hasa
  kwa hali hii.

Familia zinazopatikana kwa taratibu za uwiano wa uwezekano: `Gaussian`
(variansi inayojulikana), `Bernoulli`, `Poisson`, `Exponential`.
