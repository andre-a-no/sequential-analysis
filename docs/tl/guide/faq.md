---
description: Mga madalas itanong tungkol sa sequential-analysis, ang Python library para sa sequential testing at anytime-valid inference - pag-install, lisensiya at commercial na paggamit, A/B testing sa production, mga clinical trial, power, bilis, TypeScript, pagsipi.
language: tl
---

# Mga madalas itanong

> Ito ay salin ng [pahina sa Ingles](../../guide/faq.md). Hindi pa ito nasusuri ng isang katutubong tagapagsalita ng wika; kung saan magkaiba ang dalawa, ang pahina sa Ingles ang masusunod.

## Tungkol sa library

### Ano ang sequential-analysis?

Isang Python library para sa sequential statistical inference. Ang mga
test, confidence sequence at detector nito ay maaaring suriin pagkatapos
ng bawat obserbasyon at ihinto anumang oras, nang hindi nawawala ang
kanilang mga garantiya sa error. Mayroon itong:

* mga SPRT;
* mga group sequential design;
* mga anytime-valid na A/B test;
* mga change-point detector;
* mga Kalman filter, particle filter at hidden Markov filter;
* forecasting at GARCH.

Lahat ng ito ay tumatakbo sa likod ng iisang interface na may mga JSON
checkpoint. Dinidebelop ito ng Novikov Laboratories LLC.

### Paano ito i-install? Saan ito nakadepende?

`pip install sequential-analysis`. Kailangan nito ng Python 3.8 o mas bago
(sinubok hanggang 3.14) at wala nang iba pa.
`pip install "sequential-analysis[fast]"` ay nagdaragdag ng numpy para sa
mga procedure na gumagana sa mga array. Ginagamit lamang ang pandas, polars,
mga Kafka client at matplotlib kung tatawagin mo ang mga adapter o ang mga
plotting function.

### Libre ba ito para sa commercial na paggamit?

Dual-licensed ito sa ilalim ng AGPL-3.0 at ng isang commercial licence.
Libre ang mga paggamit na ito sa ilalim ng AGPL:

* pananaliksik at pagtuturo;
* mga open-source na proyekto sa ilalim ng AGPL o GPL v3;
* panloob na paggamit sa isang organisasyon, nang walang kopyang
  ibinibigay sa iba at walang access sa network para sa mga taong nasa
  labas nito.

Ang isang closed-source na produkto, o isang network service na hindi mo
inilalathala ang source, ay nangangailangan ng commercial licence. Ang
talahanayan sa
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)
ang nagpapasya sa mga kaso. Mga tanong tungkol sa lisensiya:
andrei@hobukob.ru.

### Paano ito sipiin?

Ibinibigay ng [CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff)
sa repository ang citation, at ginagawa itong BibTeX o APA ng button na
*Cite this repository* ng GitHub. Naka-archive ang mga release sa Zenodo na
may DOI. Inilalarawan ang mga pamamaraan at ang mga pagsusuri sa mga ito sa
[paper](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf).

## Paggamit nito

### Magagamit ko ba ito para sa mga A/B test sa production?

Oo, bilang statistical engine. Nagbibigay ito ng mga eksaktong test para
sa:

* conversion (`TwoProportionTest`);
* mga bounded na metric (`BoundedABTest`);
* mga rate (`RateRatioTest`);
* ang paghahati ng traffic (`SampleRatioMismatch`);
* maraming metric na may kontrol sa false discovery rate (`MultipleTests`).

Sa pure Python, ang conversion test ay tumatagal nang mga 10 microsecond
bawat user, ang split check ay 4 at ang rate test ay 40. Ang isang
checkpoint ng bawat isa ay 2–4 kilobyte.
Nagtatabi ng grid ang `BoundedABTest` at tumatagal nang 0.1–0.5 ms.

Hindi experimentation platform ang library: ikaw ang bubuo ng assignment,
event collection at mga dashboard, o kukunin mo ang mga ito mula sa isang
platform. Tingnan ang [mga A/B test](ab-testing.md).

### Puwede ko bang silipin ang mga resulta araw-araw?

Oo, gamit ang mga anytime-valid na procedure: iyan ang layunin nila. Sa
isang group sequential design, tumingin lamang sa mga planadong analysis.
Sa isang klasikong fixed-sample test, tumingin nang isang beses. Tingnan
ang [pagsilip](peeking.md).

### Mas mahina ba ang power ng anytime-valid test kaysa sa fixed-sample test?

Sa effect na pinaplano para sa fixed-sample test, oo. Para maabot ang
parehong power, ang isang anytime-valid test ng dalawang proporsiyon ay
nangangailangan ng 1.3–1.6 na beses ng mga user. Bilang kapalit, puwede
kang huminto nang maaga kapag mas malaki ang effect, at hindi mo
kailangang magtakda ng sample size nang maaga. Ang isang group sequential
design na may ilang planadong pagtingin ay nagkakahalaga lamang ng 1–20%
na higit kaysa sa iisang analysis.

### Group sequential o anytime-valid: alin ang dapat kong gamitin?

* **Group sequential** kung kaunti at planado ang mga analysis, gaya ng
  sa isang data monitoring committee o isang release cycle, at lalo na
  para sa isang confirmatory clinical trial.
* **Anytime-valid** kung gusto mong tumingin nang tuloy-tuloy, o hindi mo
  masabi nang maaga kung kailan ka titingin o hihinto.

### Gumagawa ba ito ng Bayesian A/B testing?

Frequentist ang mga A/B test nito, na may mga garantiya sa error rate.
May mga Bayesian na bahagi kung saan angkop ang mga ito:

* nagpapadala ang `ThompsonAllocation` ng traffic ayon sa posterior
  probability na ang bawat arm ang pinakamahusay, na may expected-loss rule
  para sa deployment;
* tinutukoy ng `BayesianChangePoint` ang mga change point;
* natututunan ng mga forecaster ang kanilang mga parameter sa pamamagitan
  ng Bayesian updating.

### Validated ba ito para sa mga clinical trial?

Ang mga group sequential design nito (mga boundary, power, sample size,
bilang ng mga event) ay sinusuri laban sa rpact at sa survival package ng R
sa test suite. Hindi ito validated software sa regulatoryong kahulugan.
Ang isang sponsor na gagamit nito para sa isang submission ay magva-validate
nito gaya ng anumang ibang tool. Tingnan ang
[mga clinical trial](clinical-trials.md).

### Heavy-tailed ang metric ko (revenue, latency). Ano ang dapat kong gamitin?

* Para sa isang quantile (median, 90th percentile), gamitin ang
  `QuantileTest` o `QuantileConfidenceSequence`, na hindi nangangailangan
  ng mga assumption.
* Para sa isang mean, lagyan ng cap ang mga halaga sa isang level na
  itinakda nang maaga at gamitin ang `BoundedABTest` o
  `BettingConfidenceSequence` (exact).
* Bilang alternatibo, mag-assume ng bound sa standard deviation at gamitin
  ang `CatoniConfidenceSequence`.

Wala pa sa library ang two-sample test ng mga median.

### Gaano ito kabilis?

Ang pinakasimpleng mga procedure ay tumatagal nang 1–10 microsecond bawat
obserbasyon sa pure Python: mga SPRT, CUSUM, ang mga group sequential at
mixture test, GARCH. Ang mga nagtatabi ng grid o ng buong sample ay
tumatagal nang 0.1–10 ms. Mga halimbawa nito ang betting at Catoni
confidence sequence, ang kernel test at ang mga natututong forecaster.
Inililista ng [Bilis](../../performance.md) ang gastos at laki ng checkpoint
ng bawat procedure.

### Mapapatakbo ko ba ito sa JavaScript o sa browser?

Oo. Ang TypeScript executor sa `ts/` ay nagpapatakbo ng mga procedure at
nagpapatuloy ng mga Python checkpoint. Magkapareho ang mga history digest
at desisyon, at tumutugma ang mga numero hanggang sa mga huling bit.
Tingnan ang [TypeScript executor](../../typescript.md).

### Makaliligtas ba ang isang run sa crash?

Oo. Simpleng JSON ang `run.checkpoint()`, at nagpapatuloy nang bit por bit
ang `Run.restore`. Itinatapon ang mga obserbasyong muling naihatid.
Tingnan ang [streaming](streaming.md).

### Ano ang ibig sabihin ng "exact" at "asymptotic" sa dokumentasyon?

Isinasaad ng attribute na `guarantee` ng bawat procedure ang pangako nito:

* `exact`: nananatili ang error rate sa bawat sample size sa ilalim ng mga
  nakasaad na assumption;
* `asymptotic`: humigit-kumulang, sa mahahabang run;
* `model`: eksakto sa ilalim ng nakasaad na model;
* `approximate`;
* `none`.

Inirerekomenda ng dokumentasyon ang eksaktong procedure kung saan may
angkop. Tingnan ang [Aling pamamaraan?](../../choosing.md).
