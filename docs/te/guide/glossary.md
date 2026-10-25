---
description: అనుక్రమ విశ్లేషణ (sequential analysis) మరియు ఎప్పుడైనా-చెల్లుబాటయ్యే అనుమితి పదకోశం - e-value, e-process, confidence sequence, always-valid p-value, mSPRT, alpha spending, information fraction, ARL, SRM, CUPED, e-BH - పర్యాయపదాలు మరియు ప్రతి దానిని అమలు చేసే sequential-analysis విధానాలతో.
language: te
---

# పదకోశం

> ఇది [ఆంగ్ల పేజీ](../../guide/glossary.md)కి అనువాదం. దీనిని ఇంకా తెలుగు మాతృభాషీయులు ఎవరూ సమీక్షించలేదు; రెండింటి మధ్య తేడా ఉన్నచోట ఆంగ్ల పేజీయే ప్రామాణికం.

అనుక్రమ విశ్లేషణలో మరియు ఈ లైబ్రరీలో వాడే పదాలు. సాధారణంగా వాడే పర్యాయపదాలు
కుండలీకరణాలలో ఇవ్వబడ్డాయి.

**అనుక్రమ విశ్లేషణ, Sequential analysis** (sequential testing, sequential inference).
పరిశీలనల సంఖ్య ముందుగా నిర్ణయించబడని గణాంకశాస్త్రం. ప్రతి పరిశీలన లేదా
పరిశీలనల సమూహం తర్వాత, విధానం ఆపాలా కొనసాగించాలా అని నిర్ణయిస్తుంది. Wald
(1945) స్థాపించారు.

**తొంగిచూడటం, Peeking** (optional stopping, data peeking, continuous monitoring).
స్థిర-నమూనా పరీక్షను పదే పదే చూసి, అది ప్రాముఖ్యమైనదిగా (significant) అయినప్పుడు
ఆపడం. ఇది తప్పుడు-పాజిటివ్ రేటును పెంచుతుంది; చూడండి
[తొంగిచూడటం](peeking.md).

**SPRT** (sequential probability ratio test, అనుక్రమ లైకలిహుడ్ నిష్పత్తి పరీక్ష,
Wald's test). ఇది రెండు సరళ పరికల్పనల (simple hypothesis) లాగ్ లైకలిహుడ్ నిష్పత్తిని
(log likelihood ratio) పోగుచేసి, అది ఒక అంతరాన్ని వదిలినప్పుడు ఆగుతుంది. `SPRT`;
కత్తిరించిన (truncated) రూపాలు `TwoSPRT` (Lorden's 2-SPRT) మరియు `kiefer_weiss_plan`.
చూడండి [SPRT](sprt.md).

**సమూహ అనుక్రమ రూపకల్పన, Group sequential design** (interim analyses, group sequential trial).
కొన్ని ప్రణాళిక చేసిన విశ్లేషణలు, ప్రతి దానికి ఒక సరిహద్దు. మొత్తం మొదటి రకం
దోషం (type I error) alpha అయ్యేలా సరిహద్దులు ఎంచుకోబడతాయి.
`group_sequential_design`. చూడండి [క్లినికల్ ట్రయల్స్](clinical-trials.md).

**ఆల్ఫా వ్యయ ఫంక్షన్, Alpha spending function** (error spending, Lan–DeMets).
ప్రతి సమాచార భిన్నం వరకు మొదటి రకం దోషంలో ఎంత వాడుకోవచ్చో ఇది చెబుతుంది.
O'Brien–Fleming-రకం వ్యయం మొదట్లో కొంచెమే ఖర్చు చేస్తుంది, Pocock-రకం వ్యయం
సమానంగా ఖర్చు చేస్తుంది. `spending="obrien-fleming"`, `"pocock"`, ...

**సమాచార భిన్నం, Information fraction.** ఒక విశ్లేషణ వద్ద చేరిన, ప్రణాళిక చేసిన
గణాంక సమాచారం (రోగులు, సంఘటనలు) యొక్క వాటా.

**నిష్ఫలత సరిహద్దు, Futility boundary** (non-binding futility). ఒక దిగువ సరిహద్దు:
దాని కింద, ప్రభావం లేకపోవడం వల్ల ఆపడం సిఫార్సు చేయబడుతుంది. బంధనరహిత
(non-binding) సరిహద్దును మొదటి రకం దోషాన్ని పెంచకుండా విస్మరించవచ్చు.

**ఎప్పుడైనా-చెల్లుబాటయ్యే అనుమితి, Anytime-valid inference** (always-valid inference, safe anytime-valid
inference, SAVI). హామీలు అన్ని నమూనా పరిమాణాల వద్ద ఒకేసారి నిలిచే పరీక్షలు మరియు
అంతరాలు, కాబట్టి వాటిని నిరంతరం పర్యవేక్షించవచ్చు మరియు ఏ కారణంతోనైనా ఆపవచ్చు.

**e-విలువ, E-value** (e-variable, betting score). శూన్య పరికల్పన (null hypothesis)
కింద అంచనా విలువ (expectation) గరిష్ఠంగా 1 అయిన రుణేతర గణాంకం. పెద్ద e-విలువ
శూన్య పరికల్పనకు వ్యతిరేకంగా సాక్ష్యం: అది 1/alpha ను మించినప్పుడు తిరస్కరిస్తే
మొదటి రకం దోషం గరిష్ఠంగా alpha. అనేక విధానాల `log_e_value` అవుట్‌పుట్.

**e-ప్రక్రియ, E-process** (test martingale, test supermartingale, wealth process).
ఆపే సమయాల (stopping time) వద్ద చెల్లుబాటులో ఉండే e-విలువల శ్రేణి. శూన్య పరికల్పన
కింద దాని నడుస్తున్న గరిష్ఠం గరిష్ఠంగా alpha సంభావ్యతతో 1/alpha ను దాటుతుంది
(Ville అసమానత, Ville's inequality).

**ఎల్లప్పుడూ-చెల్లుబాటయ్యే p-విలువ, Always-valid p-value** (anytime-valid p-value, sequential p-value).
ఏ ఆపే సమయం వద్దనైనా చెల్లుబాటయ్యే p-విలువ. ఇది ఒక e-ప్రక్రియ యొక్క నడుస్తున్న
గరిష్ఠానికి విలోమం (inverse). ఎప్పుడైనా-చెల్లుబాటయ్యే విధానాల `p_value` అవుట్‌పుట్.

**విశ్వాస శ్రేణి, Confidence sequence** (anytime-valid confidence interval,
always-valid confidence interval, time-uniform confidence interval). కనీసం
1 − alpha సంభావ్యతతో అన్ని నమూనా పరిమాణాల వద్ద ఏకకాలంలో నిజమైన విలువను
కలిగి ఉండే అంతరాల శ్రేణి.
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, మరియు అనేక పరీక్షల
`lower` మరియు `upper` అవుట్‌పుట్‌లు. చూడండి
[విశ్వాస శ్రేణులు](confidence-sequences.md).

**mSPRT** (mixture SPRT, మిశ్రమ SPRT, Robbins' mixture). ప్రత్యామ్నాయ పరికల్పనను
ఒక పూర్వ విభాజనం (prior) పై సగటు చేసిన SPRT, ఇది దానిని ప్రతి ప్రత్యామ్నాయానికి
వ్యతిరేకంగా ఎప్పుడైనా-చెల్లుబాటయ్యేదిగా చేస్తుంది. `NormalMixtureSPRT` (తెలిసిన
విస్తృతి), `TMixtureSPRT` (తెలియని విస్తృతి).

**పందెం ద్వారా పరీక్ష, Testing by betting.** శూన్య పరికల్పనకు వ్యతిరేకంగా పందెం
కాసే జూదగాడి సంపదగా e-ప్రక్రియలను నిర్మించడం. `BettingMeanTest`,
`BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal, వృద్ధి-రేటు అనుకూలతమ). ప్రత్యామ్నాయ పరికల్పన కింద
సాక్ష్యం యొక్క ఆశించిన లాగ్ వృద్ధిని గరిష్ఠం చేయడానికి ఎంచుకున్న e-విలువ.
`TwoProportionTest(method="grow")`.

**సార్వత్రిక అనుమితి, Universal inference.** గత డేటా నుండి మాత్రమే అంచనా వేసిన
ప్రత్యామ్నాయంతో లైకలిహుడ్ నిష్పత్తి నుండి వచ్చే e-విలువ. అనుకూల రూపకల్పనల
(adaptive design) కింద కూడా ఇది చెల్లుబాటులో ఉంటుంది. `TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). ఇది ఏ ఆధారపడటం (dependence) కిందనైనా అనేక
e-విలువలపై తప్పుడు ఆవిష్కరణ రేటును (false discovery rate) నియంత్రిస్తుంది.
`MultipleTests`, `e_bh`.

**e-LOND, ఆన్‌లైన్ FDR.** ఒక్కొక్కటిగా నిర్ణయించబడే పరికల్పనల శ్రేణిపై తప్పుడు
ఆవిష్కరణ రేటు నియంత్రణ. `OnlineFDR`.

**SRM** (sample ratio mismatch, నమూనా నిష్పత్తి అసమతుల్యత). శాఖల మధ్య ట్రాఫిక్
యొక్క గమనించిన విభజన కాన్ఫిగర్ చేసిన దానికి భిన్నంగా ఉండటం, ప్రయోగంలో బగ్‌కు
సంకేతం. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data, covariate
adjustment, regression adjustment). ప్రయోగానికి ముందు కొలిచిన కోవేరియేట్‌తో A/B
ప్రభావం యొక్క విస్తృతిని తగ్గిస్తుంది.
`ABTest(covariate=True)`, `AnytimeLinearModel`.

**నిష్పత్తి మెట్రిక్, Ratio metric** (delta method). ప్రతి వినియోగదారుకు రెండు
మొత్తాల నిష్పత్తి అయిన మెట్రిక్, ఉదాహరణకు సెషన్‌కు ఆదాయం. `RatioABTest`.

**మార్పు-బిందువు గుర్తింపు, Change-point detection** (change detection, quickest detection,
online anomaly detection). ఒక ప్రవాహం యొక్క విభాజనం మారిన కొద్దిసేపటికే అలారం
ఇవ్వడం. `CUSUM`, `ShiryaevRoberts`,
`MeanEDetector`, `QuantileEDetector`, `BayesianChangePoint`. చూడండి
[మార్పు గుర్తింపు](change-detection.md).

**ARL** (average run length, సగటు రన్ పొడవు, ARL₀, mean time to false alarm). ఏదీ
మారనప్పుడు ఒక తప్పుడు అలారం వరకు ఆశించిన పరిశీలనల సంఖ్య. మార్పు డిటెక్టర్ల
తప్పుడు-అలారం నియంత్రణ.

**e-డిటెక్టర్, E-detector.** e-ప్రక్రియల నుండి నిర్మించిన మార్పు డిటెక్టర్, ప్రతి
సాధ్యమైన మార్పు సమయం వద్ద ఒకటి ప్రారంభించబడుతుంది. అపరామితీయ (nonparametric)
శూన్య పరికల్పన కింద దాని ARL హామీ ఇవ్వబడుతుంది. `MeanEDetector`, `QuantileEDetector`.

**Kiefer–Weiss సమస్య.** గరిష్ఠ నమూనా పరిమాణంతో, అతిపెద్ద ఆశించిన నమూనా
పరిమాణాన్ని కనిష్ఠం చేసే అనుక్రమ పరీక్షను కనుగొనడం.
`kiefer_weiss_plan`.

**నిర్వహణ లక్షణం, Operating characteristic.** ఒక ప్రణాళిక యొక్క దోష సంభావ్యతలు
మరియు నమూనా పరిమాణం యొక్క విభాజనం, నిజమైన పరామితి యొక్క ప్రమేయాలుగా (function).
`operating_characteristic`.

**చెక్‌పాయింట్, Checkpoint.** ఒక రన్ ఖచ్చితంగా కొనసాగే JSON విలువ.
`Run.checkpoint`, `Run.restore`. చూడండి [స్ట్రీమింగ్](streaming.md).

**హిస్టరీ డైజెస్ట్, History digest.** ఒక రన్ వాడిన పరిశీలనలపై SHA-256 హ్యాష్
గొలుసు, ఆడిట్ కోసం ప్రతి చెక్‌పాయింట్‌లో ఉంచబడుతుంది.

**హామీ, Guarantee** (`exact`, `asymptotic`, `model`, `approximate`, `none`).
ఈ లైబ్రరీలోని ప్రతి విధానం తాను ఏమి వాగ్దానం చేస్తుందో ప్రకటించే లక్షణం.
చూడండి [ఏ పద్ధతి?](../../choosing.md).
