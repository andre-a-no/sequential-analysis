---
description: Python-இல் sequential-analysis உடன் Wald-இன் தொடர்முறை நிகழ்தகவு விகிதச் சோதனையை (sequential probability ratio test, SPRT) இயக்குவது எப்படி. பிழை விகிதங்கள், நிலையான-மாதிரிச் சோதனையுடன் ஒப்பிட்டுச் சராசரி மாதிரி அளவு, வெட்டப்பட்ட மாற்றுகள் (2-SPRT, Kiefer–Weiss உகந்த திட்டங்கள்).
language: ta
---

# Python-இல் Wald-இன் SPRT-ஐ இயக்குவது எப்படி?

> இது [ஆங்கிலப் பக்கத்தின்](../../guide/sprt.md) மொழிபெயர்ப்பு. தமிழைத் தாய்மொழியாகக் கொண்ட ஒருவர் இதை இன்னும் மதிப்பாய்வு செய்யவில்லை; இரண்டுக்கும் இடையே வேறுபாடு இருந்தால், ஆங்கிலப் பக்கமே அதிகாரப்பூர்வமானது.

**சுருக்கமான பதில்.** `sequential_analysis.procedures`-இல் உள்ள
`SPRT(family, theta0, theta1, alpha, beta)` Wald-இன் தொடர்முறை நிகழ்தகவு விகிதச்
சோதனையை (sequential probability ratio test) செயல்படுத்துகிறது. இது இரண்டு எளிய
கருதுகோள்களுக்கு (simple hypotheses) இடையே சராசரியாக மிகக் குறைந்த கவனிப்புகளுடன்
முடிவு செய்கிறது. ஒரு நேரத்தில் ஒரு கவனிப்பை வழங்கி, முதல் முடிவில் நிறுத்துங்கள்.
கீழே உள்ள எடுத்துக்காட்டில், அதே பிழை விகிதங்கள் கொண்ட நிலையான-மாதிரிச்
சோதனையின் சுமார் பாதிக் கவனிப்புகளே இதற்குத் தேவை: 133-க்குப் பதிலாகச் சராசரியாக
65–76 பொருட்கள். உத்தரவாதமான அதிகபட்ச மாதிரி அளவு தேவைப்பட்டால், அதற்குப் பதிலாக
`TwoSPRT` அல்லது `kiefer_weiss_plan`-இலிருந்து ஒரு திட்டத்தைப் பயன்படுத்துங்கள்.

## எடுத்துக்காட்டு: குறைபாட்டு விகிதம் 10%-ஆ 20%-ஆ?

ஒரு தொகுதியின் (batch) குறைபாட்டு விகிதம் 10% என்றால் அது ஏற்கப்படுகிறது, 20%
என்றால் நிராகரிக்கப்படுகிறது, இரண்டு பிழை விகிதங்களும் 5%:

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

பல தொகுதிகளில் இது எவ்வளவு நன்றாகச் செயல்படுகிறது?

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

அதே பிழை விகிதங்கள் கொண்ட நிலையான-மாதிரிச் சோதனை ஒவ்வொரு தொகுதியிலும் சுமார் 133
பொருட்களை ஆய்வு செய்கிறது (இயல்நிலைத் தோராயம், normal approximation). SPRT
சராசரியாக 43–51% குறைவாக ஆய்வு செய்கிறது. எனினும் அதன் மாதிரி அளவு சமவாய்ப்பானது,
அதற்கு மேல் வரம்பு இல்லை; சில தொகுதிகள் சராசரியைவிட மிக அதிக நேரம் எடுக்கின்றன.

வாயில் மதிப்புகள் Wald-உடையவை: log((1 − β)/α) மற்றும் log(β/(1 − α)). நிறுத்தும்போது
எந்த மாதிரி அளவு இருந்தாலும், உண்மையான பிழை விகிதங்கள் α′ மற்றும் β′,
α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) மற்றும் α′ + β′ ≤ α + β ஆகியவற்றை நிறைவு செய்யும்
என அவை உத்தரவாதம் அளிக்கின்றன. நிறுத்தும்போது இயல்தகவு விகிதம் (likelihood ratio)
வாயில் மதிப்புகளைத் தாண்டிச் செல்கிறது (overshoot), எனவே நடைமுறையில் விகிதங்கள்
பெயரளவு விகிதங்களுக்குக் கீழே இருக்கின்றன, இங்கே போலவே. `SPRT.guarantee == "exact"`
என்பதன் பொருள் இதுவே. வரம்பிடப்படுவதற்குப் பதிலாகத் துல்லியமாகக் கணக்கிடப்பட்ட பிழை
விகிதங்களுக்கு, ஒரு திட்டத்தின் மீது `operating_characteristic`-ஐப் பயன்படுத்துங்கள்
(கீழே).

## அதிகபட்ச மாதிரி அளவு தேவைப்படும்போது

* `TwoSPRT` (Lorden-இன் 2-SPRT) ஒரு நிலையான எல்லைக்குள் (horizon) நிற்கிறது,
  மோசமான நிலையிலான எதிர்பார்க்கப்படும் மாதிரி அளவை ஏறத்தாழக் குறைந்தபட்சமாக்குகிறது.
* `sequential_analysis.design`-இல் உள்ள
  `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  பின்னோக்கு உய்த்தறிதல் (backward induction) மூலம் அதிகபட்ச மாதிரி அளவு கொண்ட
  உகந்த திட்டத்தைக் கணக்கிடுகிறது. `PlanTest` அதைச் செயல்படுத்துகிறது,
  `operating_characteristic` அதன் துல்லியமான பிழை விகிதங்களையும் எதிர்பார்க்கப்படும்
  மாதிரி அளவையும் உருவகப்படுத்தல் இல்லாமல் தருகிறது. காண்க
  `examples/07_design_kiefer_weiss.py`.
* ஒவ்வொரு கவனிப்புக்கும் ஒரு பார்வைக்குப் பதிலாகச் சில திட்டமிட்ட பார்வைகளுக்கு,
  [குழுத் தொடர்முறை வடிவமைப்பைப்](clinical-trials.md) பயன்படுத்துங்கள்.

## SPRT தவறான கருவியாக இருக்கும்போது

* **கருதுகோள்கள் எளியவை அல்ல.** "விகிதம் 10%" என்பதற்கு எதிராக "விகிதம் வேறு
  எதுவாகவும் இருக்கலாம்" என்பது ஒரு கூட்டு (composite) மாற்றுக் கருதுகோள். கலவை
  SPRT (`NormalMixtureSPRT`, `TMixtureSPRT`) அல்லது பந்தயம் மூலமான சோதனையை
  (`BettingMeanTest`) பயன்படுத்துங்கள்; இவை ஒவ்வொரு மாற்றுக்கும் எதிராக
  எப்போதும்-செல்லுபடியானவை (anytime-valid).
* **உண்மை மதிப்பு θ₀ மற்றும் θ₁-க்கு இடையே உள்ளது.** அப்போது SPRT மிக மெதுவானது,
  அதன் எதிர்பார்க்கப்படும் மாதிரி அளவு நிலையான மாதிரி அளவைவிட அதிகமாகலாம்.
  Kiefer–Weiss திட்டம் சரியாக இந்தச் சூழலுக்காகவே கட்டப்பட்டது.

இயல்தகவு-விகிதச் செயல்முறைகளுக்குக் கிடைக்கும் குடும்பங்கள்: `Gaussian` (அறியப்பட்ட
மாறுபாட்டளவு), `Bernoulli`, `Poisson`, `Exponential`.
