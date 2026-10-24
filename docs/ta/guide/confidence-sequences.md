---
description: நம்பகத் தொடர்கள் (confidence sequences) என்பவை எல்லா மாதிரி அளவுகளிலும் ஒரே நேரத்தில் செல்லுபடியாக இருக்கும் நம்பக இடைவெளிகள், எனவே அவற்றைத் தொடர்ச்சியாகக் கண்காணிக்கலாம். Python-இல் வரம்புக்குட்பட்ட சராசரி, இடைநிலை அல்லது கணுமம் (quantile), கனத்த வால்கள் கொண்ட சராசரி ஆகியவற்றுக்கு அவற்றைக் கணக்கிடுவது எப்படி, sequential-analysis உடன்.
language: ta
---

# தொடர்ந்து பார்த்துக்கொண்டிருந்தாலும் செல்லுபடியாக இருக்கும் நம்பக இடைவெளியைப் பெறுவது எப்படி?

> இது [ஆங்கிலப் பக்கத்தின்](../../guide/confidence-sequences.md) மொழிபெயர்ப்பு. தமிழைத் தாய்மொழியாகக் கொண்ட ஒருவர் இதை இன்னும் மதிப்பாய்வு செய்யவில்லை; இரண்டுக்கும் இடையே வேறுபாடு இருந்தால், ஆங்கிலப் பக்கமே அதிகாரப்பூர்வமானது.

**சுருக்கமான பதில்.** **நம்பகத் தொடரைப்** (confidence sequence) பயன்படுத்துங்கள்.
இது இடைவெளிகளின் ஒரு தொடர், ஒவ்வொரு கவனிப்புக்குப் பிறகும் ஒன்று; குறைந்தது 95%
நிகழ்தகவுடன் அனைத்து மாதிரி அளவுகளிலும் ஒரே நேரத்தில் உண்மை மதிப்பை அது
கொண்டிருக்கும். நீங்கள் அதைக் கவனித்துக்கொண்டிருக்கலாம், போதுமான அளவு குறுகியதும்
அல்லது பூஜ்ஜியத்தை விலக்கியதும் நிறுத்தலாம், நிறுத்திய இடத்திலுள்ள இடைவெளியை
அறிக்கையிடலாம். வழக்கமான 95% நம்பக இடைவெளி (confidence interval) 95%-ஐ முன்கூட்டியே
நிர்ணயித்த ஒரே ஒரு மாதிரி அளவில் மட்டுமே உறுதியளிக்கிறது.

| நீங்கள் மதிப்பிடுவது | அனுமானம் | செயல்முறை | உத்தரவாதம் |
|---|---|---|---|
| வரம்புக்குட்பட்ட தரவின் சராசரி (விகிதங்கள், மதிப்பெண்கள், உச்சவரம்பிட்ட வருவாய்) | மதிப்புகள் `[lower, upper]`-இல் | `BettingConfidenceSequence` | exact |
| இடைநிலை (median), 90-ஆவது சதமானம் (percentile), எந்தக் கணுமமும் (quantile) | எதுவும் இல்லை | `QuantileConfidenceSequence` | exact |
| கனத்த வால்கள் (heavy tails) அல்லது விலகிய மதிப்புகள் (outliers) கொண்ட சராசரி | திட்ட விலக்கத்தின் மீது ஒரு வரம்பு | `CatoniConfidenceSequence` | exact |
| இயல்நிலை (normal) தரவின் சராசரி, மாறுபாட்டளவு (variance) தெரியாது | இயல்நிலைத்தன்மை | `TMixtureSPRT` (`lower`, `upper`) | இயல்நிலைத்தன்மையின் கீழ் exact |
| எதனுடைய சராசரியும், நீண்ட ஓட்டங்கள் | முடிவுறு மாறுபாட்டளவு | `AsymptoticConfidenceSequence` | asymptotic |
| இரண்டு கிளைகளுக்கு இடையிலான வேறுபாடு | காண்க [A/B சோதனைகள்](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## கண்காணிக்கும்போது வழக்கமான இடைவெளி தோல்வியடைகிறது

சராசரி 0.3 கொண்ட ஒரு 0/1 மாறியின் 500 கவனிப்புகளை எடுங்கள்; 30-ஆவதிலிருந்து
ஒவ்வொன்றுக்குப் பிறகும் பாடநூல் 95% இடைவெளியைக் கணக்கிடுங்கள்: சராசரி ± 1.96
திட்டப் பிழைகள் (standard errors). 100 ஓட்டங்களில் எத்தனையில் இடைவெளி ஏதாவது ஒரு
கட்டத்தில் உண்மைச் சராசரியைத் தவறவிடுகிறது?

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

அதன் "95%" முன்கூட்டியே நிர்ணயித்த மாதிரி அளவில் மட்டுமே நிலைக்கிறது. அதே தரவுக்கு,
பந்தயம் கட்டுதல் (betting) மூலம் பெறப்படும் நம்பகத் தொடர் (Waudby-Smith and Ramdas
2024) அதன் கட்டமைப்பின்படியே அதிகபட்சம் 5% ஓட்டங்களில் மட்டுமே ஏதாவது ஒரு n-இல்
தவறவிடுகிறது:

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

## எந்த அனுமானமும் இல்லாமல் இடைநிலைத் தாமதம்

தாமதங்கள் (latencies) சாய்வானவை, கனத்த வால்கள் கொண்டவை; எனவே அவற்றுக்குச் சராசரி ±
திட்டப் பிழை இடைவெளி நம்பத்தகுந்ததல்ல. `QuantileConfidenceSequence` எந்தப்
பரவலின் எந்தக் கணுமத்தையும் உள்ளடக்குகிறது, சமமான மதிப்புகள் (ties) உட்பட:

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

உண்மை மதிப்புகள் 120 ms மற்றும் 258.8 ms. இரண்டு இடைவெளிகளும் அனைத்து 2,000 மாதிரி
அளவுகளிலும் ஒரே நேரத்தில் நிலைக்கின்றன.

## தவறுகள் நிகழும் இடங்கள்

* **வரம்புகளும் உச்சவரம்புகளும் அனுமானத்தின் ஒரு பகுதி.** தரவைப் பார்ப்பதற்கு
  முன்பே `lower` மற்றும் `upper`-ஐத் தேர்ந்தெடுங்கள். அவற்றுக்கு வெளியே உள்ள
  மதிப்பு நிராகரிக்கப்படுகிறது.
* **தன்னிச்சையான வரம்பற்ற தரவின் சராசரிக்கு எந்த முறையும் துல்லியமான உள்ளடக்கத்தைத்
  (coverage) தருவதில்லை.** அத்தகைய தரவுக்கு ஒரு கணுமத்தைப் பயன்படுத்துங்கள்,
  மதிப்புகளுக்கு உச்சவரம்பு இடுங்கள், திட்ட விலக்கத்தின் மீது ஒரு வரம்பை
  அனுமானியுங்கள் (Catoni), அல்லது asymptotic தொடரை ஏற்றுக்கொள்ளுங்கள்.
* **அதே மாதிரி அளவில், நம்பகத் தொடர்கள் ஒற்றை இடைவெளியைவிட அகலமானவை.** ஒவ்வொரு
  மாதிரி அளவிலும் ஒரே நேரத்தில் செல்லுபடியாக இருப்பதற்கான விலையே அந்த அகலம்.

மேலும்: [எந்த முறை?](../../choosing.md),
[குறிப்புதவி: எப்போதும்-செல்லுபடியான மற்றும் அளவுருசாரா (nonparametric)](../../reference/anytime.md).
