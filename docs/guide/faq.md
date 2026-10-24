---
description: Frequently asked questions about sequential-analysis, the Python library for sequential testing and anytime-valid inference - installation, licence and commercial use, A/B testing in production, clinical trials, power, speed, TypeScript, citing.
---

# Frequently asked questions

## About the library

### What is sequential-analysis?

A Python library for sequential statistical inference. Its tests,
confidence sequences and detectors may be checked after every
observation and stopped at any time, without losing their error
guarantees. It has:

* SPRTs;
* group sequential designs;
* anytime-valid A/B tests;
* change-point detectors;
* Kalman, particle and hidden Markov filters;
* forecasting and GARCH.

All of them run behind one interface with JSON checkpoints. It is
developed by Novikov Laboratories LLC.

### How do I install it? What does it depend on?

`pip install sequential-analysis`. It needs Python 3.8 or later (tested
up to 3.14) and nothing else. `pip install "sequential-analysis[fast]"`
adds numpy for the procedures that work on arrays. pandas, polars,
Kafka clients and matplotlib are used only if you call the adapters or
the plotting functions.

### Is it free for commercial use?

It is dual-licensed under AGPL-3.0 and a commercial licence. These uses
are free under the AGPL:

* research and teaching;
* open-source projects under the AGPL or GPL v3;
* internal use in an organisation, with no copies given to others and
  no access over a network for people outside it.

A closed-source product, or a network service whose source you do not
publish, needs a commercial licence. The table in
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)
decides the cases. Licensing enquiries: andrei@hobukob.ru.

### How do I cite it?

[CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff)
in the repository gives the citation, and GitHub's *Cite this
repository* button turns it into BibTeX or APA. Releases are archived on
Zenodo with a DOI. The methods and their checks are described in the
[paper](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf).

## Using it

### Can I use it for A/B tests in production?

Yes, as the statistical engine. It gives exact tests for:

* conversion (`TwoProportionTest`);
* bounded metrics (`BoundedABTest`);
* rates (`RateRatioTest`);
* the traffic split (`SampleRatioMismatch`);
* many metrics with false discovery rate control (`MultipleTests`).

In pure Python the conversion test takes about 10 microseconds per
user, the split check 4 and the rate test 40. A checkpoint of each takes
2–4 kilobytes.
`BoundedABTest` keeps a grid and takes 0.1–0.5 ms.

The library is not an experimentation platform: assignment,
event collection and dashboards are yours to build or take from a
platform. See [A/B tests](ab-testing.md).

### Can I peek at the results every day?

Yes, with the anytime-valid procedures: that is what they are for.
With a group sequential design, look only at the planned analyses.
With a classical fixed-sample test, look once. See [peeking](peeking.md).

### Is an anytime-valid test less powerful than a fixed-sample test?

At the effect a fixed-sample test is planned for, yes. To reach the same
power, an anytime-valid test of two proportions needs 1.3–1.6 times the
users. In exchange you may stop early when the effect is larger, and
you need no sample size fixed in advance. A group sequential design
with a few planned looks costs only 1–20% more than a single analysis.

### Group sequential or anytime-valid: which should I use?

* **Group sequential** if the analyses are few and planned, as with a
  data monitoring committee or a release cycle, and especially for a
  confirmatory clinical trial.
* **Anytime-valid** if you want to look continuously, or cannot say in
  advance when you will look or stop.

### Does it do Bayesian A/B testing?

Its A/B tests are frequentist, with guarantees on error rates.
Bayesian components are available where they fit:

* `ThompsonAllocation` sends traffic by the posterior probability that
  each arm is best, with an expected-loss rule for deployment;
* `BayesianChangePoint` detects change points;
* the forecasters learn their parameters by Bayesian updating.

### Is it validated for clinical trials?

Its group sequential designs (boundaries, power, sample sizes, numbers
of events) are checked against rpact and R's survival package in the
test suite. It is not validated software in the regulatory sense. A
sponsor using it for a submission validates it like any other tool. See
[clinical trials](clinical-trials.md).

### My metric is heavy-tailed (revenue, latency). What should I use?

* For a quantile (median, 90th percentile), use `QuantileTest` or
  `QuantileConfidenceSequence`, which need no assumptions.
* For a mean, cap the values at a level fixed in advance and use
  `BoundedABTest` or `BettingConfidenceSequence` (exact).
* Alternatively, assume a bound on the standard deviation and use
  `CatoniConfidenceSequence`.

A two-sample test of medians is not in the library yet.

### How fast is it?

The simplest procedures take 1–10 microseconds per observation in pure
Python: SPRTs, CUSUM, the group sequential and mixture tests, GARCH.
Those that hold a grid or the whole sample take 0.1–10 ms. Examples are
the betting and Catoni confidence sequences, the kernel test and the
learnt forecasters.
[Speed](../performance.md) lists each procedure's cost and checkpoint
size.

### Can I run it in JavaScript or in the browser?

Yes. The TypeScript executor in `ts/` runs the procedures and continues
Python checkpoints. History digests and decisions are identical, and
the numbers agree to the last bits. See [TypeScript executor](../typescript.md).

### Can a run survive a crash?

Yes. `run.checkpoint()` is plain JSON, and `Run.restore` continues bit
for bit. Observations delivered again are dropped. See
[streaming](streaming.md).

### What do "exact" and "asymptotic" mean in the documentation?

Every procedure's `guarantee` attribute states its promise:

* `exact`: the error rate holds at every sample size under the stated
  assumptions;
* `asymptotic`: approximately, in long runs;
* `model`: exact under the stated model;
* `approximate`;
* `none`.

The documentation recommends the exact procedure where one fits. See
[Which method?](../choosing.md).
