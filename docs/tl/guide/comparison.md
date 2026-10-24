---
description: Paano ihahambing ang sequential-analysis sa ibang mga Python at R library para sa sequential testing, A/B testing, group sequential design, change detection at filtering (statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn), at kung kailan gagamitin ang alin.
language: tl
---

# Paano ito ihahambing sa ibang mga library?

> Ito ay salin ng [pahina sa Ingles](../../guide/comparison.md). Hindi pa ito nasusuri ng isang katutubong tagapagsalita ng wika; kung saan magkaiba ang dalawa, ang pahina sa Ingles ang masusunod.

**Maikling sagot.** Karamihan sa mga library ay mahusay na sumasaklaw sa
iisang pamilya ng mga pamamaraan. Inilalagay ng sequential-analysis ang mga
pangunahing pamilya ng sequential inference sa likod ng iisang interface:

* mga SPRT at optimal na plan;
* mga group sequential design;
* mga anytime-valid test at confidence sequence;
* change detection;
* mga state-space filter.

Ang idinadagdag nito lampas sa mga pamamaraan mismo:

* bawat procedure ay nagsasaad ng garantiya nito (`exact`, `asymptotic`,
  `model`, ...);
* bawat run ay maaaring i-checkpoint at ituloy nang bit por bit;
* ang mga format ay may specification at pinatatakbo ng ikalawang
  implementasyon sa TypeScript;
* walang kailangang dependency.

Kung isa lang sa mga pamamaraan sa ibaba ang kailangan mo at gumagamit ka
na ng library na dalubhasa rito, ipagpatuloy ang paggamit ng library na
iyon. Ipinapakita ng talahanayan kung saan natural na pagpipilian ang bawat
tool. Ang mga paglalarawan ay tungkol sa pangunahing layunin ng bawat
library, noong Oktubre 2026, at hindi kumpletong listahan ng mga feature
nito.

| Pangangailangan | Mga natural na pagpipilian | Ang iniaalok ng sequential-analysis |
|---|---|---|
| mga fixed-sample test, regression, power | scipy.stats, statsmodels | hindi ito ang layunin nito |
| mga group sequential design para sa isang regulatory submission | rpact, gsDesign (R) | ang parehong mga design, sinuri laban sa rpact sa test suite nito; pinatatakbo ang trial hakbang-hakbang na may mga checkpoint |
| mga confidence sequence, e-value | confseq (Python), safestats (R) | mga confidence sequence para sa mga mean, quantile, regression coefficient, two-sample effect; e-BH at e-LOND para sa maraming test |
| mga A/B test bilang platform na may UI | GrowthBook, Statsig, Eppo, Optimizely (mga platform) | isang engine na ie-embed: mga eksaktong test para sa conversion, bounded at rate metric, SRM, FDR sa mga metric |
| offline na change-point segmentation ng isang tapos nang series | ruptures (Python), changepoint (R) | online detection habang dumarating ang datos: CUSUM, Shiryaev–Roberts, mga e-detector, Bayesian online change point |
| mga Kalman filter | filterpy, statsmodels state space | Kalman, robust Kalman, particle at HMM filter, na may smoothing at mga checkpoint |
| GARCH | arch | GARCH(1,1) at GJR na naka-fit sa maximum ng arch (sinuri sa mga test), saka pinatatakbo online |
| mga hidden Markov model | hmmlearn | ang filter online, Baum–Welch na tumutugma sa hmmlearn, online EM |
| forecasting | statsmodels, iba pa | mga ETS at AR forecast na tumutugma sa statsmodels, natututunan online, na may mga conformal interval |

## Mga kasong mas mahusay ang ibang tool

* **Isang submission sa isang regulator.** Malawakang ginagamit ang rpact
  para sa layuning iyon, at nag-aalok ang mga developer nito ng validation
  documentation. Tumutugma rito ang sequential-analysis sa mga design na
  saklaw nito, pero kailangan pa ring i-validate ito ng isang sponsor.
* **Malalaking offline na analysis sa mga array.** Mas mabilis bawat
  obserbasyon ang mga library na nakabatay sa numpy. Ginawa ang
  sequential-analysis para sa paisa-isang obserbasyon; tingnan ang
  [Bilis](../../performance.md) para sa gastos ng bawat procedure.
* **Mga pamamaraang wala pa rito.** Wala pa itong two-sample test ng mga
  median, walang multivariate Hawkes process at walang ARIMA model na may
  moving average term. Tingnan ang [changelog](../../changelog.md) para sa
  mga idinadagdag.
