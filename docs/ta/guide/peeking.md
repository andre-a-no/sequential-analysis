---
description: A/B சோதனைகளிலும் மருத்துவ ஆய்வுகளிலும் தினமும் p-மதிப்பைச் சரிபார்ப்பது ஏன் தவறான நேர்மறைகளை உயர்த்துகிறது (எட்டிப்பார்த்தல் சிக்கல், peeking problem), அதைச் சரிசெய்யும் தொடர்முறை முறைகளின் மூன்று குடும்பங்கள், Python-இல் sequential-analysis உடன்.
language: ta
---

# நான் ஏன் தினமும் p-மதிப்பைப் பார்க்கக் கூடாது?

> இது [ஆங்கிலப் பக்கத்தின்](../../guide/peeking.md) மொழிபெயர்ப்பு. தமிழைத் தாய்மொழியாகக் கொண்ட ஒருவர் இதை இன்னும் மதிப்பாய்வு செய்யவில்லை; இரண்டுக்கும் இடையே வேறுபாடு இருந்தால், ஆங்கிலப் பக்கமே அதிகாரப்பூர்வமானது.

**சுருக்கமான பதில்.** நிலையான-மாதிரிச் சோதனை (fixed-sample test) 5% தவறான நேர்மறை
விகிதத்தை (false-positive rate) உறுதியளிப்பது, திட்டமிட்ட மாதிரி அளவில் நீங்கள்
முடிவை ஒருமுறை மட்டுமே பார்த்தால்தான். நீங்கள் மீண்டும் மீண்டும் பார்த்து, முதல்முறை
p < 0.05 ஆனதும் நிறுத்தினால், ஏமாறுவதற்குப் பல வாய்ப்புகள் கிடைக்கின்றன. 20
பார்வைகளுடன் தவறான நேர்மறை விகிதம் சுமார் 25% வரை உயர்கிறது. தொடர்முறை முறைகள்
(sequential methods) மீண்டும் மீண்டும் பார்க்கப்படுவதற்காகவே கட்டப்பட்டவை. அவற்றுடன்,
நீங்கள் எத்தனை முறை பார்த்தாலும் எப்போது நிறுத்தினாலும் விகிதம் 5%-இலோ அதற்குக்
கீழோ இருக்கும்.

## எட்டிப்பார்த்தல் சிக்கல், அளவிடப்பட்டது

ஒரே 10% மாற்ற விகிதம் (conversion rate) கொண்ட இரண்டு கிளைகள் (ஒரு A/A சோதனை),
2,000 பயனர்கள், 200 மறுநிகழ்வுகள். "எட்டிப்பார்த்தல்" (peeking) ஒவ்வொரு 100
பயனர்களுக்குப் பிறகும் வழக்கமான இரு-விகித z-சோதனையை இயக்கி, முதல் p < 0.05-இல்
நிற்கிறது. தொடர்முறை `TwoProportionTest` ஒவ்வொரு தனிப் பயனருக்குப் பிறகும்
சரிபார்க்கப்படுகிறது:

```python
import math
import random

from sequential_analysis.procedures import TwoProportionTest

def a_a_test(seed, users=2000):
    """Alternating arms, both converting 10% of the time: any 'effect' is a false positive."""
    rnd = random.Random(seed)
    return [(user % 2, int(rnd.random() < 0.10)) for user in range(users)]

def peeking(data, looks):
    """The z-test for two proportions after every len(data) / looks users; True if it ever rejects."""
    successes, trials, every = [0, 0], [0, 0], len(data) // looks
    for i, (arm, y) in enumerate(data, start=1):
        successes[arm] += y
        trials[arm] += 1
        if i % every == 0:
            pooled = sum(successes) / sum(trials)
            se = math.sqrt(pooled * (1 - pooled) * (1 / trials[0] + 1 / trials[1]))
            if se > 0 and abs(successes[1] / trials[1] - successes[0] / trials[0]) / se > 1.96:
                return True
    return False

def sequential(data):
    """The anytime-valid test, looked at after every user; True if it ever rejects."""
    test = TwoProportionTest(alpha=0.05)
    state = test.initial_state()
    for arm, y in data:
        state, out = test.step(state, {"arm": arm, "y": y})
        if out.decision is not None:
            return True
    return False

runs = [a_a_test(seed) for seed in range(200)]
print(f"z-test, one look at the end:   {sum(peeking(r, 1) for r in runs) / len(runs):.1%} false positives")
print(f"z-test, 20 looks:              {sum(peeking(r, 20) for r in runs) / len(runs):.1%}")
print(f"TwoProportionTest, 2000 looks: {sum(sequential(r) for r in runs) / len(runs):.1%}")
```

```text
z-test, one look at the end:   4.5% false positives
z-test, 20 looks:              28.0%
TwoProportionTest, 2000 looks: 5.0%
```

ஒற்றைப் பார்வை தன் உறுதிமொழியைக் காப்பாற்றுகிறது. இருபது பார்வைகள் பிழை விகிதத்தைச்
சுமார் ஆறு மடங்கு பெருக்குகின்றன. 2,000 பயனர்கள் ஒவ்வொருவருக்குப் பிறகும்
பார்க்கப்பட்ட தொடர்முறைச் சோதனை அதை 5%-இல் வைத்திருக்கிறது. அதுதான் உறுதிமொழி:
அதன் உத்தரவாதம் **exact** (`TwoProportionTest.guarantee == "exact"`), அதாவது
நீங்கள் எத்தனை முறை பார்த்தாலும் ஒவ்வொரு மாதிரி அளவிலும் அதிகபட்சம் 5% தவறான
நேர்மறை விகிதம். 200 மறுநிகழ்வுகளில், துல்லியமான 5% தருவது 10 தவறான நேர்மறைகளையே.

## தொடர்முறை முறைகளின் மூன்று குடும்பங்கள்

| குடும்பம் | நீங்கள் பார்க்கக்கூடியது | வழக்கமான பயன்பாடு | sequential-analysis-இல் |
|---|---|---|---|
| **தொடர்முறை நிகழ்தகவு விகிதச் சோதனைகள்** (sequential probability ratio tests) (Wald 1945) | ஒவ்வொரு கவனிப்புக்குப் பிறகும் | ஓர் எளிய கருதுகோளுக்கு எதிராக இன்னொன்று, சராசரியாக மிகக் குறைந்த கவனிப்புகள்: தரக் கட்டுப்பாடு, உருவகப்படுத்தல், உளஇயற்பியல் (psychophysics) | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **குழுத் தொடர்முறை வடிவமைப்புகள்** (group sequential designs) (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | சில திட்டமிட்ட இடைக்காலப் பகுப்பாய்வுகளில் | தரவுக் கண்காணிப்புக் குழுவுடன் கூடிய மருத்துவ ஆய்வுகள் | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **எப்போதும்-செல்லுபடியான அனுமானம்** (anytime-valid inference): e-மதிப்புகள், நம்பகத் தொடர்கள், கலவை SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | ஒவ்வொரு கவனிப்புக்குப் பிறகும், எந்தக் காரணத்துக்காகவும் நிறுத்தலாம் | இணையவழி A/B சோதனைகள், கண்காணிப்பு டாஷ்போர்டுகள் | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**இதன் விலை என்ன.** அடிக்கடி பார்ப்பதற்கு, நீங்கள் திட்டமிட்ட விளைவில் கூடுதல்
தரவு தேவை:

* நான்கு பகுப்பாய்வுகள் கொண்ட குழுத் தொடர்முறை வடிவமைப்புக்கு ஒற்றைப்
  பகுப்பாய்வைவிட 1–20% கூடுதல் நோயாளிகள் தேவை;
* இரு விகிதங்களுக்கான எப்போதும்-செல்லுபடியான சோதனைக்கு ஒற்றைப் பகுப்பாய்வின்
  1.3–1.6 மடங்கு பயனர்கள் தேவை.

அதற்கு ஈடாக, பெரிய விளைவு சோதனையை முன்கூட்டியே நிறுத்துகிறது, யாரும் மாதிரி
அளவை முன்கூட்டியே நிர்ணயிக்க வேண்டியதில்லை.

## இது சிக்கல் அல்லாதபோது

நீங்கள் செய்வது நீங்கள் பார்த்ததைச் சார்ந்திருக்கும்போது மட்டுமே எட்டிப்பார்த்தல்
பிழைகளை உயர்த்துகிறது. நீங்கள் டாஷ்போர்டைப் பார்த்தாலும், சோதனையை எப்போதும் அதன்
திட்டமிட்ட அளவு வரை இயக்கி ஒருமுறை மட்டுமே சோதித்தால், நிலையான-மாதிரிச் சோதனை
செல்லுபடியாகும். அந்தச் சூழலில் அதுவே மிகத் திறமையான தேர்வும் ஆகும்.

அடுத்து: [A/B சோதனையை முன்கூட்டியே நிறுத்துங்கள்](ab-testing.md),
[நம்பகத் தொடர்கள்](confidence-sequences.md),
[சொற்களஞ்சியம்](glossary.md).
