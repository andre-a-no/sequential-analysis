---
description: Python-இல் மருத்துவ ஆய்வின் (clinical trial) இடைக்காலப் பகுப்பாய்வுகளைத் திட்டமிட்டு இயக்குவது எப்படி - குழுத் தொடர்முறை வடிவமைப்புகள் (O'Brien–Fleming, Pocock, Lan–DeMets ஆல்ஃபா செலவிடல், பயனின்மை எல்லைகள்), சராசரிகள், விகிதங்கள் மற்றும் உயிர்பிழைப்புக்கான (survival) மாதிரி அளவுகள், rpact உடன் சரிபார்க்கப்பட்டவை, sequential-analysis உடன்.
language: ta
---

# மருத்துவ ஆய்வின் இடைக்காலப் பகுப்பாய்வுகளைத் திட்டமிடுவது எப்படி?

> இது [ஆங்கிலப் பக்கத்தின்](../../guide/clinical-trials.md) மொழிபெயர்ப்பு. தமிழைத் தாய்மொழியாகக் கொண்ட ஒருவர் இதை இன்னும் மதிப்பாய்வு செய்யவில்லை; இரண்டுக்கும் இடையே வேறுபாடு இருந்தால், ஆங்கிலப் பக்கமே அதிகாரப்பூர்வமானது.

**சுருக்கமான பதில்.** குழுத் தொடர்முறை வடிவமைப்பைப் (group sequential design)
பயன்படுத்துங்கள். `sequential_analysis.group_sequential`-இல் உள்ள
`group_sequential_design(alpha, fractions, spending=...)` கணக்கிடுவன:

* செயல்திறன் எல்லைகள் (efficacy boundaries), Lan–DeMets ஆல்ஃபா செலவிடலுடன்
  (alpha spending) (O'Brien–Fleming வகை, Pocock வகை மற்றும் பிற);
* கட்டுப்படுத்தாத (non-binding) பயனின்மை எல்லைகள் (futility boundaries);
* திறன் (power) மற்றும் எதிர்பார்க்கப்படும் மாதிரி அளவு;
* சராசரிகள் மற்றும் விகிதங்களுக்கான அதிகபட்ச மாதிரி அளவு, அல்லது உயிர்பிழைப்புப்
  (survival) பகுப்பாய்வுக்கான நிகழ்வுகளின் எண்ணிக்கை.

எல்லைகளும் மாதிரி அளவுகளும் R தொகுப்பு rpact உடன் ஒத்துப்போகின்றன. பின்னர் சோதனைச்
செயல்முறைகள் (`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) ஆய்வை நோயாளிக்கு நோயாளி
அல்லது நிகழ்வுக்கு நிகழ்வு இயக்குகின்றன. ஒவ்வொரு இடைக்காலப் பகுப்பாய்வையும்
(interim analysis) அதன் தகவல் பின்னம் (information fraction) எட்டப்பட்டதும்
அவை செய்கின்றன.

## வடிவமைப்பு: நான்கு பகுப்பாய்வுகள், O'Brien–Fleming செலவிடல்

ஒருபக்க (one-sided) α = 0.025, நோயாளிகளின் 25%, 50%, 75% மற்றும் 100%-இல்
பகுப்பாய்வுகள், 90% திறன், ஒரு பயனின்மை எல்லையுடன்:

```python
from sequential_analysis.group_sequential import group_sequential_design

design = group_sequential_design(0.025, [0.25, 0.5, 0.75, 1.0], spending="obrien-fleming",
                                 futility="obrien-fleming", power=0.9)
for k, (t, b, f) in enumerate(zip(design.fractions, design.bounds, design.futility), start=1):
    print(f"analysis {k} at {t:.0%}: efficacy if Z >= {b:.3f}, futility if Z <= {f:.3f}")
print("patients for an effect of 0.3 standard deviations:", design.max_sample_size(effect=0.3, sigma=1.0))
print(f"expected share of the patients used: {design.expected_fraction(0.0):.2f} with no effect, "
      f"{design.expected_fraction(design.drift):.2f} with the planned effect")
```

```text
analysis 1 at 25%: efficacy if Z >= 4.333, futility if Z <= -1.403
analysis 2 at 50%: efficacy if Z >= 2.963, futility if Z <= 0.325
analysis 3 at 75%: efficacy if Z >= 2.359, futility if Z <= 1.291
analysis 4 at 100%: efficacy if Z >= 2.014, futility if Z <= 2.014
patients for an effect of 0.3 standard deviations: 127
expected share of the patients used: 0.59 with no effect, 0.73 with the planned effect
```

## இருநிலை (binary) மற்றும் உயிர்பிழைப்பு இறுதிப்புள்ளிகள் (endpoints)

```python
binary = group_sequential_design(0.025, [1 / 3, 2 / 3, 1.0], spending="obrien-fleming")
print("patients, response 10% vs 12%, 80% power:",
      binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8))
print("events for a hazard ratio of 0.7, 80% power:", binary.max_events(hazard_ratio=0.7, power=0.8))
print(f"inflation factor over a single analysis: {binary.inflation_factor(0.8):.3f}")
```

```text
patients, response 10% vs 12%, 80% power: 7780
events for a hazard ratio of 0.7, 80% power: 250
inflation factor over a single analysis: 1.013
```

O'Brien–Fleming செலவிடலுடன், மூன்று பகுப்பாய்வுகளுக்கு ஒற்றை இறுதிப்
பகுப்பாய்வைவிட 1.3% கூடுதல் நோயாளிகள் தேவை.

## ஆய்வை இயக்குதல்

```python
import random

from sequential_analysis.procedures import GroupSequentialProportions

n_max = binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8)
test = GroupSequentialProportions.from_design(binary, n_max)
state, rnd = test.initial_state(), random.Random(3)
for patient in range(n_max):
    arm = patient % 2                                         # 1 treatment, 0 control
    state, out = test.step(state, {"arm": arm, "y": int(rnd.random() < (0.12 if arm else 0.10))})
    if out.analysis:
        print(f"analysis {out.analysis} after {out.n} patients: Z = {out.z:.2f}, bound {out.bound:.2f}")
    if out.decision:
        print("decision:", out.decision)
        break
```

```text
analysis 1 after 2594 patients: Z = 2.14, bound 3.71
analysis 2 after 5187 patients: Z = 2.64, bound 2.51
decision: reject_h0
```

திட்டமிட்ட நோயாளிகளில் மூன்றில் இரண்டு பங்குக்குப் பிறகு, இரண்டாவது பகுப்பாய்வில்
செயல்திறனுக்காக (efficacy) ஆய்வு நிறுத்தப்பட்டது.

## பகுப்பாய்வுகள் திட்டமிட்டபடி நடக்காதபோது

தரவுக் கண்காணிப்புக் குழுக்கள் (data monitoring committees) தகவலின் சரியாக 25%-இல்
கூடுவது அரிது:

* `design.at(fractions)` உண்மையில் எட்டப்பட்ட தகவலுக்கான எல்லைகளை மீண்டும்
  கணக்கிடுகிறது. ஆல்ஃபா செலவிடல் ஒட்டுமொத்த நிலையைப் பாதுகாக்கிறது.
* `GroupSequentialMonitor` நீங்களே கணக்கிடும் எந்தப் புள்ளியியலையும் (ஒரு Cox
  மாதிரியுரு, ஒரு கலப்பு மாதிரியுரு (mixed model)) ஒவ்வொரு கூட்டத்திலும் ஒரு Z
  மதிப்பாகவும் அதன் தகவலாகவும் ஏற்கிறது.

## ஒவ்வொரு நோயாளிக்குப் பிறகும் பார்க்க விரும்பினால்?

குழுத் தொடர்முறை வடிவமைப்பு திட்டமிட்ட எண்ணிக்கையிலான பார்வைகளை மட்டுமே
அனுமதிக்கிறது. ஒவ்வொரு நோயாளி அல்லது நிகழ்வுக்குப் பிறகும் கண்காணிக்க,
எப்போதும்-செல்லுபடியான (anytime-valid) செயல்முறையைப் பயன்படுத்துங்கள்:
உயிர்பிழைப்புக்கு `AnytimeLogRankTest`, பதில் விகிதங்களுக்கு `TwoProportionTest`,
ஒரு சராசரிக்கு `TMixtureSPRT`. திட்டமிட்ட விளைவில் அவற்றுக்குக் கூடுதல் நோயாளிகள்
தேவை. காண்க [பயிற்சி: உயிர்பிழைப்பு ஆய்வு](../../tutorials/survival.md).

## ஒழுங்குமுறை நடைமுறை

ஆல்ஃபா செலவிடலுடன் கூடிய குழுத் தொடர்முறை வடிவமைப்புகள் உறுதிப்படுத்தும்
(confirmatory) ஆய்வுகளில் நிலைநிறுத்தப்பட்ட அணுகுமுறை; ICH E9 வழிகாட்டுதலிலும்,
தகவமைவு வடிவமைப்புகள் (adaptive designs) குறித்த FDA வழிகாட்டலிலும் (2019) இவை
விவரிக்கப்பட்டுள்ளன. இந்த நூலகம் வடிவமைப்புகளைக் கணக்கிட்டு, ஒவ்வொரு
பகுப்பாய்வுக்கும் தணிக்கை செய்யக்கூடிய, மீண்டும் தொடரக்கூடிய ஒரு பதிவை
வைத்திருக்கிறது (சோதனைப்புள்ளியும் அதன் வரலாற்றுச் செரிமானமும் (history digest)).
ஒழுங்குமுறை அர்த்தத்தில் இது சரிபார்க்கப்பட்ட (validated) மென்பொருள் அல்ல: ஒரு
சமர்ப்பிப்பில் (submission) இதைப் பயன்படுத்தும் ஆதரவாளர் (sponsor) வேறு எந்தக்
கருவியையும் போலவே இதைச் சரிபார்க்க வேண்டும்.

மேலும்: [பயிற்சி: குழுத் தொடர்முறை ஆய்வு](../../tutorials/group-sequential.md),
இது எண்களை rpact உடன் ஒப்பிடுகிறது;
[குறிப்புதவி: வடிவமைப்பும் திட்டமிடலும்](../../reference/design.md).
