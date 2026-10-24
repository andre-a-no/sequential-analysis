---
description: Python मध्ये sequential-analysis सह Wald ची अनुक्रमिक संभाव्यता गुणोत्तर चाचणी (sequential probability ratio test, SPRT) कशी चालवावी. त्रुटी दर, स्थिर-नमुना चाचणीच्या तुलनेत सरासरी नमुना आकार, आणि छाटलेले पर्याय (2-SPRT, Kiefer–Weiss इष्टतम योजना).
language: mr
---

# Python मध्ये Wald ची SPRT कशी चालवावी?

> हे [इंग्रजी पानाचे](../../guide/sprt.md) भाषांतर आहे. मराठी मातृभाषक व्यक्तीने अद्याप त्याचे पुनरावलोकन केलेले नाही; दोन्हींमध्ये फरक आढळल्यास इंग्रजी पान अधिकृत मानावे.

**थोडक्यात उत्तर.** `sequential_analysis.procedures` मधील
`SPRT(family, theta0, theta1, alpha, beta)` Wald ची अनुक्रमिक संभाव्यता गुणोत्तर
चाचणी (sequential probability ratio test) अंमलात आणते. ती दोन साध्या
परिकल्पनांमध्ये (simple hypotheses) सरासरीने सर्वात कमी निरीक्षणांत निर्णय घेते.
तिला एका वेळी एक निरीक्षण द्या आणि पहिल्या निर्णयावर थांबा. खालील उदाहरणात
तिला समान त्रुटी दर असलेल्या स्थिर-नमुना चाचणीच्या सुमारे निम्मी निरीक्षणे
लागतात: 133 ऐवजी सरासरी 65–76 वस्तू. तुम्हाला हमीपूर्वक कमाल नमुना आकार हवा
असेल तर त्याऐवजी `TwoSPRT` किंवा `kiefer_weiss_plan` मधील योजना वापरा.

## उदाहरण: दोष दर 10% आहे की 20%?

एखाद्या खेपेचा (batch) दोष दर 10% असेल तर ती स्वीकारली जाते आणि 20% असेल तर
नाकारली जाते, दोन्ही त्रुटी दर 5%:

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

अनेक खेपांवर ती कशी कामगिरी करते?

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

समान त्रुटी दर असलेली स्थिर-नमुना चाचणी प्रत्येक खेपेत सुमारे 133 वस्तू तपासते
(सामान्य अंदाजन, normal approximation). SPRT सरासरीने 43–51% कमी तपासते. मात्र
तिचा नमुना आकार यादृच्छिक असतो आणि त्याला वरची मर्यादा नसते, आणि काही खेपांना
सरासरीपेक्षा खूप जास्त वेळ लागतो.

उंबरठे Wald चे आहेत: log((1 − β)/α) आणि log(β/(1 − α)). थांबण्याच्या वेळी
कोणताही नमुना आकार असला तरी, ते हमी देतात की प्रत्यक्ष त्रुटी दर α′ आणि β′
α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) आणि α′ + β′ ≤ α + β यांचे पालन करतात. थांबताना
संभाव्यता गुणोत्तर (likelihood ratio) उंबरठे ओलांडून पुढे जाते (overshoot), त्यामुळे
व्यवहारात दर नाममात्र दरांपेक्षा कमी असतात, जसे इथे. `SPRT.guarantee == "exact"`
चा अर्थ हाच आहे. मर्यादेऐवजी अचूक गणन केलेल्या त्रुटी दरांसाठी, योजनेवर
`operating_characteristic` वापरा (खाली).

## कमाल नमुना आकार हवा असेल तेव्हा

* `TwoSPRT` (Lorden ची 2-SPRT) एका निश्चित क्षितिजापर्यंत (horizon) थांबते आणि
  सर्वात वाईट स्थितीतील अपेक्षित नमुना आकार जवळजवळ किमान करते.
* `sequential_analysis.design` मधील
  `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  पश्चगामी प्रवर्तनाने (backward induction) कमाल नमुना आकारासह इष्टतम योजना
  गणन करते. `PlanTest` ती अंमलात आणते, आणि `operating_characteristic` तिचे अचूक
  त्रुटी दर आणि अपेक्षित नमुना आकार सिम्युलेशनशिवाय देते. पाहा
  `examples/07_design_kiefer_weiss.py`.
* प्रत्येक निरीक्षणानंतर एकदा पाहण्याऐवजी काही नियोजित पाहण्यांसाठी,
  [गट अनुक्रमिक अभिकल्प](clinical-trials.md) वापरा.

## SPRT चुकीचे साधन केव्हा असते

* **परिकल्पना साध्या नसतात.** "दर 10% आहे" विरुद्ध "दर इतर काहीही आहे" ही
  संयुक्त (composite) पर्यायी परिकल्पना आहे. मिश्रण SPRT (`NormalMixtureSPRT`,
  `TMixtureSPRT`) किंवा पैजेद्वारे चाचणी (`BettingMeanTest`) वापरा, ज्या प्रत्येक
  पर्यायाविरुद्ध कधीही-वैध (anytime-valid) आहेत.
* **खरे मूल्य θ₀ आणि θ₁ यांच्या दरम्यान असते.** तेव्हा SPRT सर्वात मंद असते, आणि
  तिचा अपेक्षित नमुना आकार स्थिर-नमुना आकारापेक्षा जास्त होऊ शकतो.
  Kiefer–Weiss योजना नेमकी याच परिस्थितीसाठी बनवलेली आहे.

संभाव्यता-गुणोत्तर कार्यपद्धतींसाठी उपलब्ध कुळे: `Gaussian` (ज्ञात विचरण),
`Bernoulli`, `Poisson`, `Exponential`.
