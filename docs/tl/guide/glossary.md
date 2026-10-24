---
description: Glosaryo ng mga termino sa sequential analysis at anytime-valid inference - e-value, e-process, confidence sequence, always-valid p-value, mSPRT, alpha spending, information fraction, ARL, SRM, CUPED, e-BH - kasama ang mga kasingkahulugan at ang mga procedure ng sequential-analysis na nagpapatupad sa bawat isa.
language: tl
---

# Glosaryo

> Ito ay salin ng [pahina sa Ingles](../../guide/glossary.md). Hindi pa ito nasusuri ng isang katutubong tagapagsalita ng wika; kung saan magkaiba ang dalawa, ang pahina sa Ingles ang masusunod.

Mga terminong ginagamit sa sequential analysis at sa library na ito.
Nakalagay sa panaklong ang mga karaniwang ginagamit na kasingkahulugan.

**Sequential analysis** (sequential testing, sequential inference).
Estadistika kung saan hindi itinatakda nang maaga ang bilang ng mga
obserbasyon. Pagkatapos ng bawat obserbasyon o grupo ng mga obserbasyon,
nagpapasya ang procedure kung hihinto o magpapatuloy. Itinatag ni Wald
(1945).

**Peeking** (optional stopping, data peeking, continuous monitoring;
pagsilip). Ang paulit-ulit na pagtingin sa isang fixed-sample test at
paghinto kapag significant na ito. Pinalalaki nito ang false-positive
rate; tingnan ang [pagsilip](peeking.md).

**SPRT** (sequential probability ratio test, Wald's test). Iniipon nito
ang log likelihood ratio ng dalawang simpleng hypothesis at humihinto
kapag lumabas ito sa isang interval. `SPRT`; mga truncated na bersiyon:
`TwoSPRT` (2-SPRT ni Lorden) at `kiefer_weiss_plan`. Tingnan ang
[SPRT](sprt.md).

**Group sequential design** (interim analyses, group sequential trial).
Ilang planadong analysis, bawat isa ay may boundary. Pinipili ang mga
boundary para ang kabuuang type I error ay alpha.
`group_sequential_design`. Tingnan ang [mga clinical trial](clinical-trials.md).

**Alpha spending function** (error spending, Lan–DeMets). Sinasabi nito
kung gaano karami sa type I error ang maaaring magamit pagsapit ng bawat
information fraction. Kaunti ang ginagastos ng O'Brien–Fleming-type
spending sa simula, pantay naman ang paggastos ng Pocock-type spending.
`spending="obrien-fleming"`, `"pocock"`, ...

**Information fraction.** Ang bahagi ng planadong statistical information
(mga pasyente, mga event) na naabot sa isang analysis.

**Futility boundary** (non-binding futility). Isang mas mababang boundary:
kapag nasa ibaba nito, inirerekomendang huminto dahil sa kawalan ng
effect. Ang non-binding na boundary ay maaaring balewalain nang hindi
lumalaki ang type I error.

**Anytime-valid inference** (always-valid inference, safe anytime-valid
inference, SAVI). Mga test at interval na nananatili ang mga garantiya sa
bawat sample size nang sabay-sabay, kaya maaari silang bantayan nang
tuloy-tuloy at ihinto sa anumang dahilan.

**E-value** (e-variable, betting score). Isang non-negative na statistic na
ang expectation sa ilalim ng null hypothesis ay hindi hihigit sa 1. Ang
malaking e-value ay ebidensiya laban sa null: ang pag-reject kapag lumampas
ito sa 1/alpha ay may type I error na hindi hihigit sa alpha. Ang output na
`log_e_value` ng maraming procedure.

**E-process** (test martingale, test supermartingale, wealth process).
Isang pagkakasunod-sunod ng mga e-value na nananatiling valid sa mga
stopping time. Ang running maximum nito ay lumalampas sa 1/alpha nang may
probabilidad na hindi hihigit sa alpha sa ilalim ng null (Ville's
inequality).

**Always-valid p-value** (anytime-valid p-value, sequential p-value).
Isang p-value na valid sa anumang stopping time. Ito ang inverse ng running
maximum ng isang e-process. Ang output na `p_value` ng mga anytime-valid
na procedure.

**Confidence sequence** (anytime-valid confidence interval,
always-valid confidence interval, time-uniform confidence interval). Isang
pagkakasunod-sunod ng mga interval na naglalaman ng tunay na halaga sa
lahat ng sample size nang sabay-sabay na may probabilidad na hindi bababa
sa 1 − alpha.
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, at ang mga
output na `lower` at `upper` ng maraming test. Tingnan ang
[mga confidence sequence](confidence-sequences.md).

**mSPRT** (mixture SPRT, Robbins' mixture). Isang SPRT na ang alternative
ay ina-average sa isang prior, na ginagawa itong anytime-valid laban sa
bawat alternative. `NormalMixtureSPRT` (alam ang variance), `TMixtureSPRT`
(hindi alam ang variance).

**Testing by betting.** Ang pagbuo ng mga e-process bilang yaman ng isang
sugarol na tumataya laban sa null hypothesis. `BettingMeanTest`,
`BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal). Isang e-value na pinili para i-maximise
ang inaasahang log growth ng ebidensiya sa ilalim ng alternative.
`TwoProportionTest(method="grow")`.

**Universal inference.** Isang e-value mula sa isang likelihood ratio kung
saan tinatantiya ang alternative mula lamang sa nakaraang datos.
Nananatili itong valid sa ilalim ng mga adaptive design.
`TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). Kinokontrol nito ang false discovery rate
sa maraming e-value, sa ilalim ng anumang dependence. `MultipleTests`,
`e_bh`.

**e-LOND, online FDR.** Kontrol sa false discovery rate sa isang serye ng
mga hypothesis na pinagpapasyahan nang isa-isa. `OnlineFDR`.

**SRM** (sample ratio mismatch). Iba ang nakikitang paghahati ng traffic
sa pagitan ng mga arm kaysa sa naka-configure, isang senyales ng bug sa
experiment. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data, covariate
adjustment, regression adjustment). Binabawasan ang variance ng isang A/B
effect gamit ang isang covariate na sinukat bago ang experiment.
`ABTest(covariate=True)`, `AnytimeLinearModel`.

**Ratio metric** (delta method). Isang metric na ratio ng dalawang kabuuan
bawat user, gaya ng revenue bawat session. `RatioABTest`.

**Change-point detection** (change detection, quickest detection,
online anomaly detection). Ang pag-a-alarm sa lalong madaling panahon
pagkatapos magbago ang distribution ng isang stream. `CUSUM`,
`ShiryaevRoberts`, `MeanEDetector`, `QuantileEDetector`,
`BayesianChangePoint`. Tingnan ang [change detection](change-detection.md).

**ARL** (average run length, ARL₀, mean time to false alarm). Ang
inaasahang bilang ng mga obserbasyon bago ang isang false alarm kapag
walang nagbago. Ang paraan ng pagkontrol sa false alarm ng mga change
detector.

**E-detector.** Isang change detector na binuo mula sa mga e-process, na
may isang sinisimulan sa bawat posibleng oras ng pagbabago. Garantisado
ang ARL nito sa ilalim ng isang nonparametric na null. `MeanEDetector`,
`QuantileEDetector`.

**Kiefer–Weiss problem.** Ang paghahanap ng sequential test na may maximum
sample size na nagmiminimisa sa pinakamalaking expected sample size.
`kiefer_weiss_plan`.

**Operating characteristic.** Ang mga error probability at ang
distribution ng sample size ng isang plan, bilang mga function ng tunay na
parameter. `operating_characteristic`.

**Checkpoint.** Isang JSON value kung saan nagpapatuloy nang eksakto ang
isang run. `Run.checkpoint`, `Run.restore`. Tingnan ang
[streaming](streaming.md).

**History digest.** Isang SHA-256 hash chain sa mga obserbasyong ginamit
ng isang run, na nakatabi sa bawat checkpoint, para sa audit.

**Guarantee** (`exact`, `asymptotic`, `model`, `approximate`, `none`;
garantiya). Ang attribute kung saan isinasaad ng bawat procedure sa
library na ito kung ano ang ipinapangako nito. Tingnan ang
[Aling pamamaraan?](../../choosing.md).
