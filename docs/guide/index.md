---
description: User guide to sequential-analysis, a Python library for sequential testing and anytime-valid inference. Each page answers one question directly, with code that runs and its output.
---

# User guide

This guide is organised by the questions people ask. Each page opens
with a direct answer, then gives a short program that runs as written,
its output, the guarantee behind the answer, and the cases where the
method does not apply. The [tutorials](../tutorials/ab-test.md) go
further into each subject.

## The library in one paragraph

**sequential-analysis** is a Python library for statistical inference
on data that arrive one observation at a time. Its tests, confidence
intervals and detectors may be looked at after every observation and
stopped at any moment, and their error rates still hold. It covers:

* Wald's SPRT and optimal sequential plans;
* group sequential designs for clinical trials (O'Brien–Fleming and
  Pocock spending, futility bounds);
* anytime-valid A/B tests with e-values and confidence sequences;
* change-point detection;
* Kalman, particle and hidden Markov filters;
* forecasting and GARCH volatility.

Every run can be checkpointed as JSON and resumed bit for bit in
Python, or continued in its TypeScript executor with the same decisions.

| | |
|---|---|
| Install | `pip install sequential-analysis` |
| Import | `import sequential_analysis` |
| Python | 3.8 to 3.14, no required dependencies (numpy optional) |
| Licence | AGPL-3.0, or a commercial licence from Novikov Laboratories LLC |
| Source | <https://github.com/andre-a-no/sequential-analysis> |
| Documentation | <https://andre-a-no.github.io/sequential-analysis/> |

## Questions

**Concepts**

* [Why can't I look at a p-value every day?](peeking.md) Peeking, and
  the three families of sequential methods.
* [Glossary](glossary.md): e-value, confidence sequence, alpha spending,
  ARL and the other terms, with their synonyms.

**Tasks**

* [How do I stop an A/B test early without inflating false positives?](ab-testing.md)
* [How do I get a confidence interval that stays valid when I keep looking?](confidence-sequences.md)
* [How do I run Wald's SPRT in Python?](sprt.md)
* [How do I plan interim analyses of a clinical trial?](clinical-trials.md)
* [How do I detect a change in a stream of measurements?](change-detection.md)
* [How do I run statistics on a stream and resume after a crash?](streaming.md)

**Choosing**

* [Which method for my question?](../choosing.md): the full table.
* [How does it compare with other libraries?](comparison.md)
* [Frequently asked questions](faq.md)

## How to read the guarantees

Every procedure has a `guarantee` attribute. The guide quotes it with
each answer:

* **exact:** the error rate holds at every sample size under the stated
  assumptions.
* **asymptotic:** it holds approximately, and better for larger samples.
* **model:** the probabilities are exact under the stated model, but
  nothing is claimed beyond it.
* **approximate:** an approximation even under the model.
* **none:** the procedure transforms the data and makes no claim.
