---
description: Glossary of sequential analysis and anytime-valid inference terms - e-value, e-process, confidence sequence, always-valid p-value, mSPRT, alpha spending, information fraction, ARL, SRM, CUPED, e-BH - with synonyms and the sequential-analysis procedures that implement each.
---

# Glossary

Terms used in sequential analysis and in this library. Synonyms in
common use are given in brackets.

**Sequential analysis** (sequential testing, sequential inference).
Statistics in which the number of observations is not fixed in
advance. After each observation or group of observations, the
procedure decides whether to stop or continue. Founded by Wald (1945).

**Peeking** (optional stopping, data peeking, continuous monitoring).
Looking at a fixed-sample test repeatedly and stopping when it is
significant. It inflates the false-positive rate; see
[peeking](peeking.md).

**SPRT** (sequential probability ratio test, Wald's test). It
accumulates the log likelihood ratio of two simple hypotheses and stops
when it leaves an interval. `SPRT`; truncated versions `TwoSPRT`
(Lorden's 2-SPRT) and `kiefer_weiss_plan`. See [SPRT](sprt.md).

**Group sequential design** (interim analyses, group sequential trial).
A few planned analyses, each with a boundary. The boundaries are chosen
so that the overall type I error is alpha.
`group_sequential_design`. See [clinical trials](clinical-trials.md).

**Alpha spending function** (error spending, Lan–DeMets). It says how
much of the type I error may be used up by each information fraction.
O'Brien–Fleming-type spending spends little early on, Pocock-type
spending spends evenly. `spending="obrien-fleming"`, `"pocock"`, ...

**Information fraction.** The share of the planned statistical
information (patients, events) reached at an analysis.

**Futility boundary** (non-binding futility). A lower boundary: below
it, stopping for lack of effect is recommended. A non-binding boundary
may be ignored without inflating the type I error.

**Anytime-valid inference** (always-valid inference, safe anytime-valid
inference, SAVI). Tests and intervals whose guarantees hold at every
sample size at once, so they may be monitored continuously and stopped
for any reason.

**E-value** (e-variable, betting score). A non-negative statistic whose
expectation under the null hypothesis is at most 1. A large e-value is
evidence against the null: rejecting when it exceeds 1/alpha has type I
error at most alpha. The `log_e_value` output of many procedures.

**E-process** (test martingale, test supermartingale, wealth process).
A sequence of e-values that stays valid at stopping times. Its running
maximum crosses 1/alpha with probability at most alpha under the null
(Ville's inequality).

**Always-valid p-value** (anytime-valid p-value, sequential p-value).
A p-value that is valid at any stopping time. It is the inverse of the
running maximum of an e-process. The `p_value` output of the
anytime-valid procedures.

**Confidence sequence** (anytime-valid confidence interval,
always-valid confidence interval, time-uniform confidence interval). A
sequence of intervals that contains the true value at all sample sizes
simultaneously with probability at least 1 − alpha.
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, and the
`lower` and `upper` outputs of many tests. See
[confidence sequences](confidence-sequences.md).

**mSPRT** (mixture SPRT, Robbins' mixture). An SPRT whose alternative
is averaged over a prior, which makes it anytime-valid against every
alternative. `NormalMixtureSPRT` (known variance), `TMixtureSPRT`
(unknown variance).

**Testing by betting.** Building e-processes as the wealth of a gambler
who bets against the null hypothesis. `BettingMeanTest`,
`BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal). An e-value chosen to maximise the
expected log growth of evidence under the alternative.
`TwoProportionTest(method="grow")`.

**Universal inference.** An e-value from a likelihood ratio with the
alternative estimated from past data only. It stays valid under
adaptive designs. `TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). It controls the false discovery rate
over many e-values, under any dependence. `MultipleTests`, `e_bh`.

**e-LOND, online FDR.** False discovery rate control over a series of
hypotheses decided one by one. `OnlineFDR`.

**SRM** (sample ratio mismatch). The observed split of traffic between
arms differs from the configured one, a sign of a bug in the
experiment. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data, covariate
adjustment, regression adjustment). Reduces the variance of an A/B
effect with a covariate measured before the experiment.
`ABTest(covariate=True)`, `AnytimeLinearModel`.

**Ratio metric** (delta method). A metric that is a ratio of two sums
per user, such as revenue per session. `RatioABTest`.

**Change-point detection** (change detection, quickest detection,
online anomaly detection). Raising an alarm soon after the
distribution of a stream changes. `CUSUM`, `ShiryaevRoberts`,
`MeanEDetector`, `QuantileEDetector`, `BayesianChangePoint`. See
[change detection](change-detection.md).

**ARL** (average run length, ARL₀, mean time to false alarm). The
expected number of observations to a false alarm when nothing has
changed. The false-alarm control of change detectors.

**E-detector.** A change detector built from e-processes, one started
at every possible change time. Its ARL is guaranteed under a
nonparametric null. `MeanEDetector`, `QuantileEDetector`.

**Kiefer–Weiss problem.** Finding the sequential test with a maximum
sample size that minimises the largest expected sample size.
`kiefer_weiss_plan`.

**Operating characteristic.** The error probabilities and the
distribution of the sample size of a plan, as functions of the true
parameter. `operating_characteristic`.

**Checkpoint.** A JSON value from which a run continues exactly.
`Run.checkpoint`, `Run.restore`. See [streaming](streaming.md).

**History digest.** A SHA-256 hash chain over the observations a run
has used, kept in every checkpoint, for audit.

**Guarantee** (`exact`, `asymptotic`, `model`, `approximate`, `none`).
The attribute in which every procedure in this library states what it
promises. See [Which method?](../choosing.md).
