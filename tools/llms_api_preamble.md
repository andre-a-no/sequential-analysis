# sequential-analysis {version}: API reference for AI assistants

> Python library for sequential statistical inference: tests, confidence sequences and detectors that may be checked after every observation and stopped at any time with their error guarantees intact (SPRT, group sequential designs, anytime-valid A/B tests, change detection, Kalman/particle/HMM filters, forecasting, GARCH).

This file is generated from the code of version {version} by tools/make_llms_api.py. The constructors, guarantees, input names and output fields below are the library's own; when writing code, use them rather than names recalled from other libraries. The user guide with worked examples is at {site}guide/, and llms.txt at {site}llms.txt lists the documentation.

## How the library is used

- Install `pip install sequential-analysis`; import `sequential_analysis`. Python 3.8 or later, no required dependencies (`pip install "sequential-analysis[fast]"` adds numpy for the array-heavy procedures).
- Procedures are in `sequential_analysis.procedures`. Each is a pure transition: `state = proc.initial_state()`, then for each observation `state, out = proc.step(state, x)`, where `x` is a dict keyed by the procedure's input names (listed below; most default to `"x"`, A/B tests to `"arm"` and `"y"`). There is no `fit`/`predict` or array API on procedures: feed observations one at a time, in order.
- `out` is a frozen dataclass with the output fields listed below. Tests report `out.decision`: None while undecided, then `"reject_h0"` or `"accept_h0"` (`procedures.REJECT_H0`, `procedures.ACCEPT_H0`). Change detectors report `out.alarm`. Many tests also give `p_value` (anytime-valid), `log_e_value` and `lower`/`upper` (a confidence sequence).
- `alpha` is the error rate of the whole run, however often it is looked at; it is not spent per look.
- For streams use `Run(proc, topology=..., delivery=..., consumers=[...])` and `run_sync(run, observations)`, where each observation is `Observation(input_name, value, seq=..., key=..., source=...)`. A topology relates inputs: `KeyJoin(("arm", "y"))` joins an assignment and an outcome by `key`. `run.state` is the current state, `Recorder()` as a consumer collects the outputs.
- `run.checkpoint()` is a JSON value; `Run.restore(proc, checkpoint)` continues the run bit for bit and refuses a checkpoint of another procedure, configuration or version (`IncompatibleCheckpoint`).
- Each procedure states its promise in `proc.guarantee`:
{guarantees}
  Prefer an exact procedure where one answers the question.

## Which procedure for which question

- Conversion rate A vs B, looked at any time: `TwoProportionTest`. Bounded metric (capped revenue, a share): `BoundedABTest`. Events per unit of exposure: `RateRatioTest`. Ratio metric (revenue per session): `RatioABTest`. Mean with a pre-experiment covariate (CUPED): `ABTest(covariate=True)`. Traffic split: `SampleRatioMismatch`. Several metrics or arms: `MultipleTests` (e-BH). A series of experiments: `OnlineFDR`.
- A few planned interim analyses (clinical trials): `group_sequential_design(...)`, then `GroupSequentialTest`, `GroupSequentialTwoMeans`, `GroupSequentialProportions` or `GroupSequentialLogRank` built with `.from_design(design, n_max)` (for the log-rank test, the number of events instead of `n_max`); any statistic: `GroupSequentialMonitor`.
- Simple hypothesis against simple hypothesis, fewest observations: `SPRT(family, theta0, theta1, alpha, beta)`; with a maximum sample size `TwoSPRT` or `kiefer_weiss_plan` + `PlanTest`. Families: `Gaussian(sigma)`, `Bernoulli()`, `Poisson()`, `Exponential()`.
- Mean, anytime-valid: normal with known variance `NormalMixtureSPRT`, unknown variance `TMixtureSPRT`, bounded data `BettingMeanTest` / `BettingConfidenceSequence`, a bound on the standard deviation `CatoniConfidenceSequence`, long runs of anything `AsymptoticConfidenceSequence`. Median or any quantile: `QuantileTest`, `QuantileConfidenceSequence`. Are two groups distributed alike: `KernelTwoSampleTest`. Regression coefficients: `AnytimeLinearModel`. Survival: `AnytimeLogRankTest`.
- Change detection: `CUSUM`, `ShiryaevRoberts` (known distributions), `MeanEDetector`, `QuantileEDetector` (nonparametric), `BayesianChangePoint`.
- Filtering: `KalmanFilter`, `LocalLevelKalman`, `RobustKalmanFilter`, `HiddenMarkovFilter`, `OnlineHMM`, `ParticleFilter`, `BootstrapParticleFilter`.
- Forecasting: `ExponentialSmoothing`, `AutoRegressive`, `PoissonSmoothing`, `ModelAveraging`, `ConformalForecast`, `ForecastComparison`; several series `VectorAutoRegressive`, `CrossCorrelation`, `DynamicRegression`; events `HawkesProcess`, `EventStudy`; volatility `GARCH` (fit with `fit_garch`).
- Not in the library: a two-sample test of medians, multivariate Hawkes processes, ARIMA with moving-average terms.
