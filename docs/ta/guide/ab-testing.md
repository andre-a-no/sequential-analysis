---
description: Python-இல் தவறான நேர்மறைகளை (false positives) அதிகரிக்காமல் A/B சோதனையை முன்கூட்டியே நிறுத்துவது எப்படி. மாற்ற விகிதம் மற்றும் வரம்புக்குட்பட்ட வருவாய்க்கான எப்போதும்-செல்லுபடியான (anytime-valid) சோதனைகள், மாதிரி விகிதப் பொருத்தமின்மை (SRM) சரிபார்ப்பு, பல அளவீடுகளின் மீது தவறான கண்டுபிடிப்பு விகிதக் (FDR) கட்டுப்பாடு, sequential-analysis உடன்.
language: ta
---

# தவறான நேர்மறைகளை அதிகரிக்காமல் A/B சோதனையை முன்கூட்டியே நிறுத்துவது எப்படி?

> இது [ஆங்கிலப் பக்கத்தின்](../../guide/ab-testing.md) மொழிபெயர்ப்பு. தமிழைத் தாய்மொழியாகக் கொண்ட ஒருவர் இதை இன்னும் மதிப்பாய்வு செய்யவில்லை; இரண்டுக்கும் இடையே வேறுபாடு இருந்தால், ஆங்கிலப் பக்கமே அதிகாரப்பூர்வமானது.

**சுருக்கமான பதில்.** எப்போதும்-செல்லுபடியான (anytime-valid) சோதனையைப்
பயன்படுத்துங்கள்: நீங்கள் எத்தனை முறை பார்த்தாலும் அதன் p-மதிப்பும் (p-value)
நம்பக இடைவெளியும் (confidence interval) செல்லுபடியாகவே இருக்கும், எனவே முடிவு
தெளிவானவுடன் நிறுத்தலாம். sequential-analysis-இல்:

| அளவீடு | செயல்முறை | உத்தரவாதம் |
|---|---|---|
| மாற்ற விகிதம் (conversion rate) (0/1) | `TwoProportionTest` | exact |
| வரம்புக்குட்பட்ட எந்த அளவீடும் (உச்சவரம்பிட்ட வருவாய், பங்கு) | `BoundedABTest` | exact |
| வெளிப்பாட்டின் (exposure) ஓர் அலகுக்கான நிகழ்வுகள் | `RateRatioTest` | Poisson எண்ணிக்கைகளுக்கு exact |
| விகித அளவீடு (ratio metric) (ஓர் அமர்வுக்கான வருவாய்) | `RatioABTest` | asymptotic |
| சோதனைக்கு முந்தைய இணைமாறியுடன் (covariate) சராசரி (CUPED) | `ABTest` | asymptotic |
| போக்குவரத்துப் பிரிப்பு திட்டமிட்டபடி உள்ளதா? | `SampleRatioMismatch` | exact |
| பல அளவீடுகள் அல்லது கிளைகள் (arms) ஒன்றாக | `MultipleTests` (e-BH) | தவறான கண்டுபிடிப்பு விகிதம் (false discovery rate), exact |

ஒவ்வொரு செயல்முறைக்கும் ஒரு நேரத்தில் ஒரு பயனரை வழங்குங்கள்: `state, out = test.step(state, {...})`.
`out.decision`-ஐ வைத்து நீங்கள் விரும்பும் நேரத்தில் செயல்படுங்கள்.

## மாற்றம்: தரவு உறுதியானவுடன் நிறுத்துங்கள்

கட்டுப்பாட்டுக் குழுவில் (control) 10% பயனர்கள் மாற்றம் அடைகின்றனர், சிகிச்சைக்
குழுவில் (treatment) 12%. சோதனை ஒவ்வொரு பயனருக்குப் பிறகும் பார்க்கப்பட்டு, அதன்
முதல் முடிவில் நிற்கிறது:

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

ஒப்பிட்டுப் பார்க்க, இந்த உயர்வுக்கு 80% திறன் (power) கொண்ட நிலையான-மாதிரிச்
சோதனைக்கு (fixed-sample test) ஒரு கிளைக்குச் சுமார் 3,850, மொத்தம் 7,700
பயனர்கள் தேவை, அதை இறுதியில் ஒரே ஒருமுறை மட்டுமே படிக்கலாம். எப்போதும்-செல்லுபடியான
சோதனை தன் சுதந்திரத்துக்கு விலை கொடுக்கிறது: அதே திறனை அடைய அதற்கு ஒற்றைப்
பகுப்பாய்வின் 1.3–1.6 மடங்கு பயனர்கள் தேவை, இந்த ஓட்டத்துக்கு அதைவிடவும் அதிகம்
தேவைப்பட்டது. அதற்கு ஈடாக, முன்கூட்டியே நிர்ணயிக்க வேண்டிய மாதிரி அளவு எதுவும்
இல்லை; முடிவைத் தினமும் பார்த்து, அது தெளிவானவுடன் நிறுத்தலாம். விளைவு
திட்டமிட்டதைவிடப் பெரிதாக இருந்தால், அது மிக முன்னதாகவே நிகழ்கிறது.

## வருவாய்: வரம்புக்குட்பட்ட அளவீட்டுக்கான துல்லியமான இடைவெளி

`BoundedABTest`-க்கு அளவீட்டின் வரம்புகள் மட்டுமே தேவை. சோதனைக்கு முன்பே நீங்கள்
தேர்ந்தெடுக்கும் ஒரு மதிப்பில் (இங்கே 30) வருவாய்க்கு உச்சவரம்பு இடுங்கள்;
சராசரிகளுக்கு இடையிலான வேறுபாட்டுக்கான நம்பகத் தொடர் (confidence sequence) எந்தப்
பரவலுக்கும் துல்லியமானது:

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

இந்த இடைவெளி கடைசிப் பார்வையில் மட்டுமல்ல, 20,000 பார்வைகள் ஒவ்வொன்றிலும் ஒரே
நேரத்தில் நிலைக்கிறது. இங்கே அது இன்னும் 0-ஐக் கொண்டுள்ளது: இவ்வளவு இரைச்சல்
(noise) மிக்க அளவீட்டில் சுமார் 0.5 உயர்வை நிறுவ 20,000 பயனர்கள் போதாது, எனவே
சோதனை தொடர்கிறது.

## முதலில் போக்குவரத்துப் பிரிப்பைச் சரிபாருங்கள்

மாதிரி விகிதப் பொருத்தமின்மை (sample ratio mismatch) என்றால், பிரிப்பு
அமைக்கப்பட்டதிலிருந்து வேறுபடுகிறது, எடுத்துக்காட்டாக ஒதுக்கீட்டில் (assignment)
அல்லது பதிவிடலில் உள்ள பிழை காரணமாக. அத்தகைய சோதனையிலிருந்து பெறப்படும் விளைவு
மதிப்பீடுகள் நம்பத்தகுந்தவை அல்ல. 50/50-இலிருந்து 52/48 ஆகும் பொருத்தமின்மை,
சோதனை இயங்கும்போதே பிடிபடுகிறது:

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

## ஒரே நேரத்தில் பல அளவீடுகள்

பத்து சாரா (independent) அளவீடுகளை ஒவ்வொன்றையும் 5%-இல் சோதித்தால், குறைந்தது ஒரு
தவறான கண்டுபிடிப்புக்கு (false discovery) சுமார் 40% வாய்ப்பு உண்டு.
`MultipleTests` எல்லாச் சோதனைகளின் e-மதிப்புகளையும் (e-values) e-BH
செயல்முறையால் இணைக்கிறது; எனவே எந்த நிறுத்த நேரத்திலும் (stopping time) தவறான
கண்டுபிடிப்பு விகிதம் `alpha`-இல் இருக்கிறது:

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

## தவறுகள் நிகழும் இடங்கள்

* **நீங்கள் பகுப்பாய்வு செய்யும் அலகையே சமவாய்ப்பாக்குங்கள் (randomise).**
  பயனர்கள் சமவாய்ப்பாக்கப்பட்டால், ஒரு பக்கப் பார்வைக்கு (page view) அல்ல, ஒரு
  பயனருக்கு ஒரு பதிவை வழங்குங்கள். ஓர் அமர்வுக்கான அளவீடுகளுக்கு `RatioABTest`-ஐப்
  பயன்படுத்துங்கள், அது பயனர் மொத்தங்களின் மீது செயல்படுகிறது.
* **வரம்புக்குட்பட்ட அளவீட்டின் உச்சவரம்பைச் சோதனைக்கு முன்பே நிர்ணயியுங்கள்.**
  தரவைப் பார்த்த பிறகு அதைத் தேர்ந்தெடுத்தால் உத்தரவாதம் செல்லாததாகிவிடும்.
* **asymptotic செயல்முறைகளுக்குப் பெரிய மாதிரிகள் தேவை.** `ABTest` மற்றும்
  `RatioABTest`-க்கு இடைவெளி நீண்ட ஓட்டங்களில் மட்டுமே தோராயமாகச் செல்லுபடியாகும்.
  துல்லியமான செயல்முறைகள் பொருந்தும்போது அவற்றையே விரும்புங்கள்.
* **தகவமைவுப் போக்குவரத்து ஒதுக்கீட்டுக்கு (adaptive traffic allocation)**
  (bandits), பிரிப்பு விளைவுகளைச் சார்ந்திருக்கும்போதும் செல்லுபடியாகும் சோதனை
  தேவை: `TwoProportionTest(method="universal")` அல்லது
  `BoundedABTest(propensity_input=...)`. காண்க
  [பயிற்சி §10](../../tutorials/ab-test.md).

மேலும்: [A/B சோதனைப் பயிற்சி](../../tutorials/ab-test.md) (CUPED, விகித அளவீடுகள்,
விகிதங்கள், கால அளவைத் திட்டமிடுதல்) மற்றும்
[சோதனைகளின் ஒரு திட்டம்](../../tutorials/experiment-programme.md)
(பல சோதனைகளின் மீது தவறான கண்டுபிடிப்பு விகிதம்).
