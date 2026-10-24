---
description: Paano patakbuhin ang sequential probability ratio test (SPRT) ni Wald sa Python gamit ang sequential-analysis. Mga error rate, karaniwang sample size kumpara sa fixed-sample test, at ang mga truncated na alternatibo (2-SPRT, mga optimal na Kiefer–Weiss plan).
language: tl
---

# Paano patakbuhin ang SPRT ni Wald sa Python?

> Ito ay salin ng [pahina sa Ingles](../../guide/sprt.md). Hindi pa ito nasusuri ng isang katutubong tagapagsalita ng wika; kung saan magkaiba ang dalawa, ang pahina sa Ingles ang masusunod.

**Maikling sagot.** Ipinapatupad ng `SPRT(family, theta0, theta1, alpha, beta)`
mula sa `sequential_analysis.procedures` ang sequential probability ratio
test ni Wald. Nagpapasya ito sa pagitan ng dalawang simpleng hypothesis sa
pinakakaunting obserbasyon sa karaniwan. Pakainin ito ng isang obserbasyon
sa bawat pagkakataon at huminto sa unang desisyon. Sa halimbawa sa ibaba,
kailangan nito ng mga kalahati ng mga obserbasyon ng isang fixed-sample
test na may parehong mga error rate: 65–76 na item sa karaniwan sa halip
na 133. Kung kailangan mo ng garantisadong maximum sample size, gamitin na
lang ang `TwoSPRT` o isang plan mula sa `kiefer_weiss_plan`.

## Halimbawa: 10% ba o 20% ang defect rate?

Tinatanggap ang isang batch kung 10% ang defect rate nito at tinatanggihan
kung 20%, na parehong 5% ang dalawang error rate:

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

Gaano ito kahusay sa maraming batch?

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

Ang isang fixed-sample test na may parehong mga error rate ay sumusuri ng
mga 133 item sa bawat batch (normal approximation). Ang SPRT ay sumusuri ng
43–51% na mas kaunti sa karaniwan. Gayunman, random ang sample size nito at
walang upper limit, at may ilang batch na mas matagal nang husto kaysa sa
karaniwan.

Ang mga threshold ay kay Wald: log((1 − β)/α) at log(β/(1 − α)).
Ginagarantiya ng mga ito, para sa anumang sample size sa paghinto, na ang
aktuwal na mga error rate na α′ at β′ ay tumutugon sa α′ ≤ α/(1 − β),
β′ ≤ β/(1 − α) at α′ + β′ ≤ α + β. Lumalampas ang likelihood ratio sa mga
threshold kapag humihinto ito, kaya sa praktika mas mababa ang mga rate
kaysa sa mga nominal, gaya rito. Iyan ang kahulugan ng
`SPRT.guarantee == "exact"`. Para sa mga error rate na kinakalkula nang
eksakto sa halip na nililimitahan lamang ng bound, gamitin ang
`operating_characteristic` sa isang plan (sa ibaba).

## Kapag kailangan mo ng maximum sample size

* Ang `TwoSPRT` (2-SPRT ni Lorden) ay humihinto pagsapit ng isang nakatakdang
  horizon at halos minimisa ang worst-case expected sample size.
* Ang `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  sa `sequential_analysis.design` ay kumakalkula ng optimal na plan na may
  maximum sample size sa pamamagitan ng backward induction. Ang `PlanTest`
  ang nagpapatakbo nito, at ibinibigay ng `operating_characteristic` ang
  eksaktong mga error rate at expected sample size nito nang walang
  simulation. Tingnan ang `examples/07_design_kiefer_weiss.py`.
* Para sa ilang planadong pagtingin sa halip na isa bawat obserbasyon,
  gumamit ng [group sequential design](clinical-trials.md).

## Kapag mali ang SPRT para sa gawain

* **Hindi simple ang mga hypothesis.** Ang "10% ang rate" laban sa "kahit
  ano pa ang rate" ay isang composite alternative. Gumamit ng mixture SPRT
  (`NormalMixtureSPRT`, `TMixtureSPRT`) o ng test by betting
  (`BettingMeanTest`), na anytime-valid laban sa bawat alternatibo.
* **Nasa pagitan ng θ₀ at θ₁ ang tunay na halaga.** Dito pinakamabagal ang
  SPRT, at maaaring lumampas ang expected sample size nito sa fixed-sample
  size. Ang Kiefer–Weiss plan ay ginawa mismo para sa kasong ito.

Mga family na magagamit para sa mga likelihood-ratio procedure: `Gaussian`
(alam ang variance), `Bernoulli`, `Poisson`, `Exponential`.
