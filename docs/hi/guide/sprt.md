---
description: Python में sequential-analysis के साथ Wald का अनुक्रमिक प्रायिकता अनुपात परीक्षण (SPRT) कैसे चलाएँ। त्रुटि दरें, निश्चित-सैंपल टेस्ट की तुलना में औसत सैंपल साइज़, और truncated विकल्प (2-SPRT, Kiefer–Weiss इष्टतम योजनाएँ)।
language: hi
---

# Python में Wald का SPRT कैसे चलाएँ?

> यह [अंग्रेज़ी पृष्ठ](../../guide/sprt.md) का अनुवाद है। इसकी समीक्षा अभी किसी मूल हिंदी भाषी ने नहीं की है; जहाँ दोनों में अंतर हो, वहाँ अंग्रेज़ी पृष्ठ ही प्रामाणिक है।

**संक्षिप्त उत्तर।** `sequential_analysis.procedures` का
`SPRT(family, theta0, theta1, alpha, beta)` Wald के अनुक्रमिक प्रायिकता अनुपात
परीक्षण (sequential probability ratio test) को लागू करता है। यह औसतन सबसे कम
प्रेक्षणों के साथ दो सरल परिकल्पनाओं (simple hypotheses) के बीच निर्णय करता है।
इसे एक बार में एक प्रेक्षण दें और पहले निर्णय पर रुकें। नीचे के उदाहरण में इसे
समान त्रुटि दरों वाले निश्चित-सैंपल टेस्ट के लगभग आधे प्रेक्षण चाहिए: 133 के
बजाय औसतन 65–76 आइटम। अगर आपको गारंटीड अधिकतम सैंपल साइज़ चाहिए, तो इसके बजाय
`TwoSPRT` या `kiefer_weiss_plan` से मिली योजना इस्तेमाल करें।

## उदाहरण: दोष दर 10% है या 20%?

एक बैच स्वीकार किया जाता है अगर उसकी दोष दर (defect rate) 10% है और अस्वीकार
किया जाता है अगर 20% है, दोनों त्रुटि दरें 5%:

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

कई बैचों पर यह कैसा प्रदर्शन करता है?

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

समान त्रुटि दरों वाला निश्चित-सैंपल टेस्ट हर बैच में लगभग 133 आइटम जाँचता है
(normal सन्निकटन)। SPRT औसतन 43–51% कम जाँचता है। लेकिन इसका सैंपल साइज़
यादृच्छिक (random) है और इसकी कोई ऊपरी सीमा नहीं है, और कुछ बैच औसत से कहीं
अधिक समय लेते हैं।

थ्रेशोल्ड Wald के हैं: log((1 − β)/α) और log(β/(1 − α))। वे रुकने पर किसी भी
सैंपल साइज़ के लिए गारंटी देते हैं कि वास्तविक त्रुटि दरें α′ और β′ शर्तें
α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) और α′ + β′ ≤ α + β पूरी करती हैं। रुकते समय
संभाविता अनुपात (likelihood ratio) थ्रेशोल्ड से आगे निकल जाता है (overshoot),
इसलिए व्यवहार में दरें नाममात्र (nominal) दरों से कम होती हैं, जैसा यहाँ है।
`SPRT.guarantee == "exact"` का यही अर्थ है। केवल सीमाबद्ध करने के बजाय ठीक-ठीक
गणना की गई त्रुटि दरों के लिए, किसी योजना पर `operating_characteristic`
इस्तेमाल करें (नीचे)।

## जब आपको अधिकतम सैंपल साइज़ चाहिए

* `TwoSPRT` (Lorden's 2-SPRT) एक निश्चित क्षितिज (horizon) तक रुक जाता है और
  सबसे ख़राब स्थिति (worst case) के अपेक्षित सैंपल साइज़ को लगभग न्यूनतम करता है।
* `sequential_analysis.design` में
  `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  backward induction द्वारा अधिकतम सैंपल साइज़ वाली इष्टतम योजना की गणना करता
  है। `PlanTest` इसे चलाता है, और `operating_characteristic` बिना सिमुलेशन के
  इसकी exact त्रुटि दरें और अपेक्षित सैंपल साइज़ देता है। देखें
  `examples/07_design_kiefer_weiss.py`।
* हर प्रेक्षण पर एक बार के बजाय कुछ नियोजित बार देखने के लिए,
  [समूह अनुक्रमिक डिज़ाइन](clinical-trials.md) इस्तेमाल करें।

## जब SPRT ग़लत टूल है

* **परिकल्पनाएँ सरल नहीं हैं।** "दर 10% है" बनाम "दर कुछ और है" एक संयुक्त
  (composite) वैकल्पिक परिकल्पना है। mixture SPRT (`NormalMixtureSPRT`,
  `TMixtureSPRT`) या बेटिंग द्वारा टेस्ट (`BettingMeanTest`) इस्तेमाल करें,
  जो हर वैकल्पिक परिकल्पना के विरुद्ध anytime-valid हैं।
* **वास्तविक मान θ₀ और θ₁ के बीच है।** तब SPRT सबसे धीमा होता है, और इसका
  अपेक्षित सैंपल साइज़ निश्चित-सैंपल आकार से अधिक हो सकता है। Kiefer–Weiss
  योजना ठीक इसी स्थिति के लिए बनी है।

संभाविता-अनुपात प्रक्रियाओं के लिए उपलब्ध परिवार (families): `Gaussian` (ज्ञात
प्रसरण), `Bernoulli`, `Poisson`, `Exponential`।
