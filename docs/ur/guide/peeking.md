---
description: A/B ٹیسٹ اور ٹرائلز میں ہر روز p-value دیکھنے سے غلط مثبت نتائج کیوں بڑھتے ہیں (peeking کا مسئلہ)، اور اسے درست کرنے والے ترتیبی طریقوں کے تین خاندان، Python میں sequential-analysis کے ساتھ۔
language: ur
---

# میں ہر روز p-value کیوں نہیں دیکھ سکتا؟

> یہ [انگریزی صفحے](../../guide/peeking.md) کا ترجمہ ہے۔ ابھی کسی اہلِ زبان نے اس کا جائزہ نہیں لیا؛ جہاں دونوں میں فرق ہو، وہاں انگریزی صفحہ ہی مستند ہے۔

**مختصر جواب۔** مقررہ نمونے کا ٹیسٹ (fixed-sample test) 5% غلط مثبت شرح
(false-positive rate) کا وعدہ صرف اسی وقت کرتا ہے جب آپ نتیجہ صرف ایک بار،
منصوبہ بند نمونے کے حجم (sample size) پر دیکھیں۔ اگر آپ بار بار دیکھیں اور پہلی
بار p < 0.05 ہوتے ہی رک جائیں تو آپ کو دھوکا کھانے کے کئی مواقع ملتے ہیں۔ 20 بار
دیکھنے پر غلط مثبت شرح تقریباً 25% تک بڑھ جاتی ہے۔ ترتیبی طریقے (sequential
methods) بار بار دیکھے جانے ہی کے لیے بنے ہیں۔ ان کے ساتھ شرح 5% یا اس سے کم
رہتی ہے، چاہے آپ کتنی ہی بار دیکھیں اور جب بھی رکیں۔

## peeking کا مسئلہ، ناپ کر

دو بازو (arms) جن کی کنورژن شرح یکساں 10% ہے (ایک A/A ٹیسٹ)، 2,000 صارفین، 200
تکرار۔ "Peeking" ہر 100 صارفین کے بعد معمول کا two-proportion z-test چلاتا ہے اور
پہلی بار p < 0.05 ہونے پر رک جاتا ہے۔ ترتیبی `TwoProportionTest` ہر ایک صارف کے
بعد جانچا جاتا ہے:

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

ایک بار دیکھنا اپنا وعدہ پورا کرتا ہے۔ بیس بار دیکھنے سے غلطی کی شرح تقریباً چھ
گنا ہو جاتی ہے۔ ترتیبی ٹیسٹ، جسے 2,000 میں سے ہر صارف کے بعد دیکھا گیا، اسے 5% پر
رکھتا ہے۔ یہی وعدہ ہے: اس کی ضمانت **exact** ہے
(`TwoProportionTest.guarantee == "exact"`)، یعنی ہر نمونے کے حجم پر زیادہ سے زیادہ
5% غلط مثبت شرح، چاہے آپ کتنی ہی بار دیکھیں۔ 200 تکرار میں 10 غلط مثبت نتائج
بالکل وہی ہیں جو ایک exact 5% دیتا ہے۔

## ترتیبی طریقوں کے تین خاندان

| خاندان | آپ کب دیکھ سکتے ہیں | عام استعمال | sequential-analysis میں |
|---|---|---|---|
| **ترتیبی احتمالی تناسب ٹیسٹ (sequential probability ratio tests)** (Wald 1945) | ہر مشاہدے کے بعد | ایک سادہ مفروضہ بمقابلہ دوسرا، اوسطاً سب سے کم مشاہدات: کوالٹی کنٹرول، سمیولیشن، سائیکوفزکس | `SPRT`، `TwoSPRT`، `kiefer_weiss_plan` |
| **گروہی ترتیبی ڈیزائن (group sequential designs)** (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | چند منصوبہ بند عبوری تجزیوں (interim analyses) پر | ڈیٹا مانیٹرنگ کمیٹی والے کلینیکل ٹرائلز | `group_sequential_design`، `GroupSequentialTest`، `GroupSequentialProportions`، `GroupSequentialLogRank` |
| **Anytime-valid استنباط (anytime-valid inference)**: e-value، سلسلۂ اعتماد (confidence sequences)، mixture SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | ہر مشاہدے کے بعد، کسی بھی وجہ سے رکتے ہوئے | آن لائن A/B ٹیسٹ، مانیٹرنگ ڈیش بورڈ | `TwoProportionTest`، `BoundedABTest`، `NormalMixtureSPRT`، `BettingConfidenceSequence`، `MultipleTests` |

**اس کی قیمت کیا ہے۔** زیادہ بار دیکھنے کے لیے، اس اثر پر جس کی آپ نے منصوبہ بندی
کی تھی، زیادہ ڈیٹا درکار ہوتا ہے:

* چار تجزیوں والے گروہی ترتیبی ڈیزائن کو ایک تجزیے کے مقابلے میں 1–20% زیادہ
  مریض درکار ہوتے ہیں؛
* دو تناسبوں (proportions) کے anytime-valid ٹیسٹ کو ایک تجزیے کے 1.3–1.6 گنا
  صارفین درکار ہوتے ہیں۔

بدلے میں، بڑا اثر تجربے کو جلد روک دیتا ہے، اور کسی کو نمونے کا حجم پہلے سے مقرر
نہیں کرنا پڑتا۔

## جب یہ مسئلہ نہیں ہے

Peeking غلطیاں صرف اسی وقت بڑھاتا ہے جب آپ کا عمل اس پر منحصر ہو کہ آپ نے کیا
دیکھا۔ اگر آپ ڈیش بورڈ دیکھتے ہیں لیکن تجربے کو ہمیشہ اس کے منصوبہ بند حجم تک
چلاتے ہیں اور ایک بار ٹیسٹ کرتے ہیں، تو مقررہ نمونے کا ٹیسٹ درست ہے۔ اس صورت میں
یہ سب سے مؤثر (efficient) انتخاب بھی ہے۔

اگلا: [A/B ٹیسٹ کو جلد روکیں](ab-testing.md)،
[سلسلۂ اعتماد](confidence-sequences.md)،
[اصطلاحات](glossary.md)۔
