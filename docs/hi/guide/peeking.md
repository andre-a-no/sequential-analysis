---
description: A/B टेस्ट और ट्रायल में हर दिन p-value देखने से फ़ॉल्स पॉज़िटिव क्यों बढ़ते हैं (peeking की समस्या), और इसे ठीक करने वाली अनुक्रमिक विधियों के तीन परिवार, Python में sequential-analysis के साथ।
language: hi
---

# मैं हर दिन p-value क्यों नहीं देख सकता?

> यह [अंग्रेज़ी पृष्ठ](../../guide/peeking.md) का अनुवाद है। इसकी समीक्षा अभी किसी मूल हिंदी भाषी ने नहीं की है; जहाँ दोनों में अंतर हो, वहाँ अंग्रेज़ी पृष्ठ ही प्रामाणिक है।

**संक्षिप्त उत्तर।** एक निश्चित-सैंपल टेस्ट (fixed-sample test) 5% फ़ॉल्स-पॉज़िटिव
दर (false-positive rate) का वादा तभी करता है जब आप परिणाम को सिर्फ़ एक बार,
नियोजित सैंपल साइज़ (sample size) पर देखें। अगर आप बार-बार देखते हैं और
पहली बार p < 0.05 होते ही रुक जाते हैं, तो आपको धोखा खाने के कई मौके मिलते
हैं। 20 बार देखने पर फ़ॉल्स-पॉज़िटिव दर लगभग 25% तक बढ़ जाती है। अनुक्रमिक
विधियाँ (sequential methods) बार-बार देखे जाने के लिए ही बनी हैं। उनके साथ
दर 5% या उससे कम रहती है, चाहे आप कितनी भी बार देखें और कभी भी रुकें।

## peeking की समस्या, मापी हुई

दो आर्म (arms) जिनकी कन्वर्ज़न दर एक ही 10% है (एक A/A टेस्ट), 2,000 उपयोगकर्ता,
200 पुनरावृत्तियाँ। "Peeking" हर 100 उपयोगकर्ताओं के बाद सामान्य two-proportion
z-test चलाता है और पहली बार p < 0.05 होने पर रुक जाता है। अनुक्रमिक
`TwoProportionTest` हर एक उपयोगकर्ता के बाद जाँचा जाता है:

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

एक बार देखना अपना वादा निभाता है। बीस बार देखने से त्रुटि दर लगभग छह गुना
हो जाती है। अनुक्रमिक टेस्ट, जिसे 2,000 में से हर उपयोगकर्ता के बाद देखा गया,
इसे 5% पर रखता है। यही वादा है: इसकी गारंटी **exact** है
(`TwoProportionTest.guarantee == "exact"`), यानी हर सैंपल साइज़ पर अधिकतम 5%
फ़ॉल्स-पॉज़िटिव दर, चाहे आप कितनी भी बार देखें। 200 पुनरावृत्तियों में 10
फ़ॉल्स पॉज़िटिव ठीक वही हैं जो एक exact 5% देता है।

## अनुक्रमिक विधियों के तीन परिवार

| परिवार | आप कब देख सकते हैं | सामान्य उपयोग | sequential-analysis में |
|---|---|---|---|
| **अनुक्रमिक प्रायिकता अनुपात परीक्षण (sequential probability ratio tests)** (Wald 1945) | हर प्रेक्षण के बाद | एक सरल परिकल्पना बनाम दूसरी, औसतन सबसे कम प्रेक्षण: गुणवत्ता नियंत्रण, सिमुलेशन, साइकोफ़िज़िक्स | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **समूह अनुक्रमिक डिज़ाइन (group sequential designs)** (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | कुछ नियोजित अंतरिम विश्लेषणों (interim analyses) पर | डेटा मॉनिटरिंग कमेटी वाले क्लिनिकल ट्रायल | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Anytime-valid अनुमान (anytime-valid inference)**: e-value, विश्वास्यता अनुक्रम (confidence sequences), mixture SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | हर प्रेक्षण के बाद, किसी भी कारण से रुकते हुए | ऑनलाइन A/B टेस्ट, मॉनिटरिंग डैशबोर्ड | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**इसकी कीमत क्या है।** अधिक बार देखने के लिए, उस प्रभाव पर जिसकी आपने योजना
बनाई थी, अधिक डेटा चाहिए:

* चार विश्लेषणों वाले समूह अनुक्रमिक डिज़ाइन को एक विश्लेषण की तुलना में
  1–20% अधिक मरीज़ चाहिए;
* दो अनुपातों (proportions) के anytime-valid टेस्ट को एक विश्लेषण के
  1.3–1.6 गुना उपयोगकर्ता चाहिए।

बदले में, बड़ा प्रभाव प्रयोग को जल्दी रोक देता है, और किसी को सैंपल साइज़
पहले से तय नहीं करना पड़ता।

## जब यह समस्या नहीं है

Peeking त्रुटियाँ तभी बढ़ाता है जब आपका कदम इस पर निर्भर करे कि आपने क्या
देखा। अगर आप डैशबोर्ड देखते हैं पर प्रयोग को हमेशा उसके नियोजित आकार तक
चलाते हैं और एक बार टेस्ट करते हैं, तो निश्चित-सैंपल टेस्ट वैध है। उस स्थिति
में यह सबसे कुशल (efficient) चुनाव भी है।

आगे: [A/B टेस्ट को जल्दी रोकें](ab-testing.md),
[विश्वास्यता अनुक्रम](confidence-sequences.md),
[शब्दावली](glossary.md)।
