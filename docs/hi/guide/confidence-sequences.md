---
description: विश्वास्यता अनुक्रम (confidence sequences) ऐसे विश्वास्यता अंतराल हैं जो एक साथ हर सैंपल साइज़ पर वैध रहते हैं, इसलिए उन पर लगातार नज़र रखी जा सकती है। Python में सीमित माध्य, माध्यिका या क्वांटाइल, और भारी टेल वाले माध्य के लिए इनकी गणना कैसे करें, sequential-analysis के साथ।
language: hi
---

# ऐसा विश्वास्यता अंतराल कैसे पाएँ जो बार-बार देखने पर भी वैध रहे?

> यह [अंग्रेज़ी पृष्ठ](../../guide/confidence-sequences.md) का अनुवाद है। इसकी समीक्षा अभी किसी मूल हिंदी भाषी ने नहीं की है; जहाँ दोनों में अंतर हो, वहाँ अंग्रेज़ी पृष्ठ ही प्रामाणिक है।

**संक्षिप्त उत्तर।** **विश्वास्यता अनुक्रम (confidence sequence)** इस्तेमाल करें।
यह अंतरालों का एक अनुक्रम है, हर प्रेक्षण के बाद एक, जिसमें सभी सैंपल साइज़
पर एक साथ वास्तविक मान कम से कम 95% प्रायिकता के साथ शामिल रहता है। आप इस पर
नज़र रख सकते हैं, जब यह काफ़ी संकरा हो जाए या शून्य को बाहर कर दे तब रुक सकते
हैं, और जिस अंतराल पर रुके उसे रिपोर्ट कर सकते हैं। सामान्य 95% विश्वास्यता
अंतराल (confidence interval) 95% का वादा केवल पहले से तय किए गए एक सैंपल
साइज़ पर करता है।

| आप क्या अनुमान लगाते हैं | मान्यता | प्रक्रिया | गारंटी |
|---|---|---|---|
| सीमित (bounded) डेटा का माध्य (दरें, स्कोर, कैप किया गया रेवेन्यू) | मान `[lower, upper]` में | `BettingConfidenceSequence` | exact |
| माध्यिका (median), 90वाँ पर्सेंटाइल, कोई भी क्वांटाइल | कोई नहीं | `QuantileConfidenceSequence` | exact |
| भारी टेल (heavy tails) या आउटलायर वाला माध्य | मानक विचलन पर एक सीमा | `CatoniConfidenceSequence` | exact |
| normal डेटा का माध्य, प्रसरण (variance) अज्ञात | normality | `TMixtureSPRT` (`lower`, `upper`) | normality के अंतर्गत exact |
| किसी भी चीज़ का माध्य, लंबे रन | परिमित प्रसरण | `AsymptoticConfidenceSequence` | asymptotic |
| दो आर्म के बीच अंतर | देखें [A/B टेस्ट](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## देखते रहने पर सामान्य अंतराल विफल होता है

माध्य 0.3 वाले एक 0/1 चर के 500 प्रेक्षण लें, और 30वें से आगे हर एक के बाद
पाठ्यपुस्तक वाला 95% अंतराल निकालें: माध्य ± 1.96 मानक त्रुटियाँ (standard
errors)। 100 रनों में से कितनों में अंतराल किसी बिंदु पर वास्तविक माध्य से
चूक जाता है?

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

इसका "95%" केवल पहले से तय सैंपल साइज़ पर लागू होता है। उसी डेटा के लिए
बेटिंग (betting) से बना विश्वास्यता अनुक्रम (Waudby-Smith and Ramdas 2024)
अपनी संरचना से ही अधिकतम 5% रनों में किसी n पर चूकता है:

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

## माध्यिका लेटेंसी, बिना किसी मान्यता के

लेटेंसी तिरछी (skewed) और भारी टेल वाली होती हैं, इसलिए माध्य ± मानक त्रुटि
वाला अंतराल उनके लिए भरोसेमंद नहीं है। `QuantileConfidenceSequence` किसी भी
वितरण के किसी भी क्वांटाइल को कवर करता है, बराबर मानों (ties) सहित:

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

वास्तविक मान 120 ms और 258.8 ms हैं। दोनों अंतराल सभी 2,000 सैंपल साइज़ पर एक
साथ वैध हैं।

## सावधानियाँ

* **सीमाएँ और कैप मान्यता का हिस्सा हैं।** `lower` और `upper` डेटा देखने से
  पहले चुनें। उनके बाहर का मान अस्वीकार कर दिया जाता है।
* **कोई भी विधि मनमाने असीमित (unbounded) डेटा के माध्य के लिए exact कवरेज नहीं
  देती।** ऐसे डेटा के लिए क्वांटाइल इस्तेमाल करें, मानों को कैप करें, मानक
  विचलन पर एक सीमा मानें (Catoni), या asymptotic अनुक्रम स्वीकार करें।
* **विश्वास्यता अनुक्रम एक अकेले अंतराल से चौड़े होते हैं**, उसी सैंपल साइज़
  पर। यह चौड़ाई एक साथ हर सैंपल साइज़ पर वैध होने की कीमत है।

और: [कौन-सी विधि?](../../choosing.md),
[संदर्भ: anytime-valid और नॉनपैरामेट्रिक](../../reference/anytime.md)।
