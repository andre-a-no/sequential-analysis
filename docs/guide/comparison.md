---
description: How sequential-analysis compares with other Python and R libraries for sequential testing, A/B testing, group sequential designs, change detection and filtering (statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn), and when to use which.
---

# How does it compare with other libraries?

**Short answer.** Most libraries cover one family of methods well.
sequential-analysis puts the main families of sequential inference
behind one interface:

* SPRTs and optimal plans;
* group sequential designs;
* anytime-valid tests and confidence sequences;
* change detection;
* state-space filters.

What it adds beyond the methods themselves:

* every procedure states its guarantee (`exact`, `asymptotic`, `model`,
  ...);
* every run can be checkpointed and resumed bit for bit;
* the formats are specified and executed by a second implementation in
  TypeScript;
* there are no required dependencies.

If you need only one of the methods below and already use the library
that specialises in it, keep using that library. The table says where
each tool is the natural choice. The descriptions are of each library's
main purpose, as of October 2026, and not a complete list of its
features.

| Need | Natural choices | What sequential-analysis offers |
|---|---|---|
| fixed-sample tests, regression, power | scipy.stats, statsmodels | not its purpose |
| group sequential designs for a regulatory submission | rpact, gsDesign (R) | the same designs, checked against rpact in its test suite; runs the trial step by step with checkpoints |
| confidence sequences, e-values | confseq (Python), safestats (R) | confidence sequences for means, quantiles, regression coefficients, two-sample effects; e-BH and e-LOND for many tests |
| A/B tests as a platform with a UI | GrowthBook, Statsig, Eppo, Optimizely (platforms) | an engine to embed: exact tests for conversion, bounded and rate metrics, SRM, FDR over metrics |
| offline change-point segmentation of a finished series | ruptures (Python), changepoint (R) | online detection while the data arrive: CUSUM, Shiryaev–Roberts, e-detectors, Bayesian online change points |
| Kalman filters | filterpy, statsmodels state space | Kalman, robust Kalman, particle and HMM filters, with smoothing and checkpoints |
| GARCH | arch | GARCH(1,1) and GJR fitted to arch's maximum (checked in the tests), then run online |
| hidden Markov models | hmmlearn | the filter online, Baum–Welch agreeing with hmmlearn, online EM |
| forecasting | statsmodels, others | ETS and AR forecasts agreeing with statsmodels, learnt online, with conformal intervals |

## Cases where another tool is better

* **A submission to a regulator.** rpact is widely used for that
  purpose, and its developers offer validation documentation. sequential-analysis agrees with
  it on the designs it covers, but a sponsor would still have to validate
  it.
* **Large offline analyses on arrays.** numpy-based libraries are faster
  per observation. sequential-analysis is built for one observation at a
  time; see [Speed](../performance.md) for the cost of each procedure.
* **Methods it does not have.** It has no two-sample test of medians
  yet, no multivariate Hawkes processes and no ARIMA models with moving
  average terms. See the [changelog](../changelog.md) for what is added.
