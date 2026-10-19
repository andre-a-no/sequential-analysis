// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
// Commercial licenses for use outside the AGPL: see COMMERCIAL.md
// What each procedure promises: the `guarantee` attribute of the Python procedures (conformance/guarantees.json).

/** The values, from the strongest promise to the weakest (sequential_analysis.core.GUARANTEES). */
export const GUARANTEES = ["exact", "asymptotic", "model", "approximate", "none"] as const;
export type Guarantee = (typeof GUARANTEES)[number];

/** By procedure name; where the guarantee depends on the configuration, by case. */
export const PROCEDURE_GUARANTEES: Record<string, Guarantee | Record<string, Guarantee>> = {
  ab_test: "asymptotic",
  anytime_linear_model: "exact",
  anytime_logrank_test: "exact",
  asymptotic_confidence_sequence: "asymptotic",
  autoregressive: "model",
  bayesian_change_point: "model",
  betting_confidence_sequence: "exact",
  betting_mean_test: "exact",
  bootstrap_particle_filter: "approximate",
  bounded_ab_test: "exact",
  catoni_confidence_sequence: "exact",
  conformal_forecast: "exact",
  cross_correlation: "none",
  cusum: "exact",
  dynamic_regression: "model",
  ema: "none",
  event_study: "asymptotic",
  exponential_smoothing: "model",
  forecast_comparison: "exact",
  garch: "model",
  group_sequential_logrank: "asymptotic",
  group_sequential_monitor: "asymptotic",
  group_sequential_proportions: "asymptotic",
  group_sequential_test: { "known sigma": "exact", "estimated sigma": "asymptotic" },
  group_sequential_two_means: { "known sigma": "exact", "estimated sigma": "asymptotic" },
  hawkes_process: "model",
  hidden_markov_filter: "model",
  kalman_filter: "model",
  kernel_two_sample_test: "exact",
  local_level_kalman: "model",
  mean_difference: "none",
  mean_e_detector: "exact",
  model_averaging: "model",
  multiple_tests: "exact",
  normal_mixture_sprt: "exact",
  online_fdr_elond: "exact",
  online_hmm: "approximate",
  particle_filter: "approximate",
  plan_test: "exact",
  poisson_smoothing: "model",
  quantile_confidence_sequence: "exact",
  quantile_e_detector: "exact",
  quantile_test: "exact",
  rate_ratio_test: "exact",
  ratio_ab_test: "asymptotic",
  robust_kalman_filter: "approximate",
  sample_ratio_mismatch: "exact",
  sequential_sign_test: "exact",
  shiryaev_roberts: "exact",
  sprt: "exact",
  t_mixture_sprt: "exact",
  thompson_allocation: "model",
  two_proportion_test: "exact",
  two_sprt: "exact",
  vector_autoregressive: "model",
};

/** Composite procedures, whose guarantee is the one of the procedure they wrap (not listed in guarantees.json). */
export const COMPOSITE_PROCEDURES: readonly string[] = ["lagged"];
