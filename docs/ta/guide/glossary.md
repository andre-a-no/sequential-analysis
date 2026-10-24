---
description: தொடர்முறைப் பகுப்பாய்வு (sequential analysis) மற்றும் எப்போதும்-செல்லுபடியான அனுமானத்தின் சொற்களஞ்சியம் - e-value, e-process, confidence sequence, always-valid p-value, mSPRT, alpha spending, information fraction, ARL, SRM, CUPED, e-BH - இணைச்சொற்களுடனும் ஒவ்வொன்றையும் செயல்படுத்தும் sequential-analysis செயல்முறைகளுடனும்.
language: ta
---

# சொற்களஞ்சியம்

> இது [ஆங்கிலப் பக்கத்தின்](../../guide/glossary.md) மொழிபெயர்ப்பு. தமிழைத் தாய்மொழியாகக் கொண்ட ஒருவர் இதை இன்னும் மதிப்பாய்வு செய்யவில்லை; இரண்டுக்கும் இடையே வேறுபாடு இருந்தால், ஆங்கிலப் பக்கமே அதிகாரப்பூர்வமானது.

தொடர்முறைப் பகுப்பாய்விலும் இந்த நூலகத்திலும் பயன்படுத்தப்படும் சொற்கள். பொதுவாகப்
பயன்படும் இணைச்சொற்கள் அடைப்புக்குறிக்குள் தரப்பட்டுள்ளன.

**தொடர்முறைப் பகுப்பாய்வு** (sequential analysis, sequential testing, sequential
inference). கவனிப்புகளின் எண்ணிக்கை முன்கூட்டியே நிர்ணயிக்கப்படாத புள்ளியியல்.
ஒவ்வொரு கவனிப்பு அல்லது கவனிப்புக் குழுவுக்குப் பிறகும், நிறுத்துவதா தொடர்வதா
என்பதைச் செயல்முறை முடிவு செய்கிறது. Wald (1945) இதை நிறுவினார்.

**எட்டிப்பார்த்தல்** (peeking, optional stopping, data peeking, continuous
monitoring). நிலையான-மாதிரிச் சோதனையை மீண்டும் மீண்டும் பார்த்து, அது
முக்கியத்துவம் (significant) அடைந்ததும் நிறுத்துதல். இது தவறான நேர்மறை விகிதத்தை
(false-positive rate) உயர்த்துகிறது; காண்க [எட்டிப்பார்த்தல்](peeking.md).

**SPRT** (sequential probability ratio test, தொடர்முறை நிகழ்தகவு விகிதச் சோதனை,
Wald-இன் சோதனை). இது இரண்டு எளிய கருதுகோள்களின் (simple hypotheses) மடக்கை
இயல்தகவு விகிதத்தை (log likelihood ratio) திரட்டி, அது ஓர் இடைவெளியை விட்டு
வெளியேறும்போது நிற்கிறது. `SPRT`; வெட்டப்பட்ட (truncated) பதிப்புகள் `TwoSPRT`
(Lorden-இன் 2-SPRT) மற்றும் `kiefer_weiss_plan`. காண்க [SPRT](sprt.md).

**குழுத் தொடர்முறை வடிவமைப்பு** (group sequential design, interim analyses, group
sequential trial). சில திட்டமிட்ட பகுப்பாய்வுகள், ஒவ்வொன்றுக்கும் ஓர் எல்லை.
ஒட்டுமொத்த முதல் வகைப் பிழை (type I error) alpha ஆக இருக்கும்படி எல்லைகள்
தேர்ந்தெடுக்கப்படுகின்றன.
`group_sequential_design`. காண்க [மருத்துவ ஆய்வுகள்](clinical-trials.md).

**ஆல்ஃபா செலவிடல் சார்பு** (alpha spending function, error spending, Lan–DeMets).
ஒவ்வொரு தகவல் பின்னத்துக்குள்ளும் முதல் வகைப் பிழையின் எவ்வளவு பகுதியைச்
செலவிடலாம் என்பதை அது கூறுகிறது. O'Brien–Fleming-வகைச் செலவிடல் தொடக்கத்தில்
குறைவாகச் செலவிடுகிறது, Pocock-வகைச் செலவிடல் சீராகச் செலவிடுகிறது.
`spending="obrien-fleming"`, `"pocock"`, ...

**தகவல் பின்னம்** (information fraction). ஒரு பகுப்பாய்வின்போது எட்டப்பட்ட,
திட்டமிட்ட புள்ளியியல் தகவலின் (நோயாளிகள், நிகழ்வுகள்) பங்கு.

**பயனின்மை எல்லை** (futility boundary, non-binding futility). ஒரு கீழ் எல்லை: அதற்குக்
கீழே, விளைவு இல்லாமை காரணமாக நிறுத்துவது பரிந்துரைக்கப்படுகிறது. கட்டுப்படுத்தாத
எல்லையை முதல் வகைப் பிழையை உயர்த்தாமல் புறக்கணிக்கலாம்.

**எப்போதும்-செல்லுபடியான அனுமானம்** (anytime-valid inference, always-valid
inference, safe anytime-valid inference, SAVI). ஒவ்வொரு மாதிரி அளவிலும் ஒரே
நேரத்தில் உத்தரவாதங்கள் நிலைக்கும் சோதனைகளும் இடைவெளிகளும்; எனவே அவற்றைத்
தொடர்ச்சியாகக் கண்காணிக்கலாம், எந்தக் காரணத்துக்காகவும் நிறுத்தலாம்.

**e-மதிப்பு** (e-value, e-variable, betting score). இன்மைக் கருதுகோளின் (null
hypothesis) கீழ் எதிர்பார்ப்பு அதிகபட்சம் 1 ஆக இருக்கும் ஒரு எதிர்மமற்ற
புள்ளியியல். பெரிய e-மதிப்பு இன்மைக் கருதுகோளுக்கு எதிரான சான்று: அது 1/alpha-ஐ
மீறும்போது நிராகரித்தால் முதல் வகைப் பிழை அதிகபட்சம் alpha. பல செயல்முறைகளின்
`log_e_value` வெளியீடு.

**e-செயல்முறை** (e-process, test martingale, test supermartingale, wealth process).
நிறுத்த நேரங்களில் (stopping times) செல்லுபடியாக இருக்கும் e-மதிப்புகளின் தொடர்.
இன்மைக் கருதுகோளின் கீழ் அதன் ஓடும் உச்சம் 1/alpha-ஐக் கடப்பதற்கான நிகழ்தகவு
அதிகபட்சம் alpha (Ville-இன் சமனிலி).

**எப்போதும்-செல்லுபடியான p-மதிப்பு** (always-valid p-value, anytime-valid p-value,
sequential p-value). எந்த நிறுத்த நேரத்திலும் செல்லுபடியாகும் p-மதிப்பு. இது ஒரு
e-செயல்முறையின் ஓடும் உச்சத்தின் தலைகீழ். எப்போதும்-செல்லுபடியான செயல்முறைகளின்
`p_value` வெளியீடு.

**நம்பகத் தொடர்** (confidence sequence, anytime-valid confidence interval,
always-valid confidence interval, time-uniform confidence interval). குறைந்தது
1 − alpha நிகழ்தகவுடன் அனைத்து மாதிரி அளவுகளிலும் ஒரே நேரத்தில் உண்மை மதிப்பைக்
கொண்டிருக்கும் இடைவெளிகளின் தொடர்.
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, மற்றும் பல சோதனைகளின்
`lower`, `upper` வெளியீடுகள். காண்க
[நம்பகத் தொடர்கள்](confidence-sequences.md).

**mSPRT** (mixture SPRT, கலவை SPRT, Robbins-இன் கலவை). மாற்றுக் கருதுகோள் ஒரு முன்
பரவலின் (prior) மீது சராசரியாக்கப்பட்ட SPRT; இதனால் அது ஒவ்வொரு மாற்றுக்கும்
எதிராக எப்போதும்-செல்லுபடியாகிறது. `NormalMixtureSPRT` (அறியப்பட்ட மாறுபாட்டளவு),
`TMixtureSPRT` (அறியப்படாத மாறுபாட்டளவு).

**பந்தயம் மூலம் சோதித்தல்** (testing by betting). இன்மைக் கருதுகோளுக்கு எதிராகப்
பந்தயம் கட்டும் ஒரு சூதாடியின் செல்வமாக e-செயல்முறைகளைக் கட்டமைத்தல்.
`BettingMeanTest`, `BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal, வளர்ச்சி-விகித உகந்த). மாற்றுக் கருதுகோளின் கீழ்
சான்றின் எதிர்பார்க்கப்படும் மடக்கை வளர்ச்சியை அதிகரிக்கத் தேர்ந்தெடுக்கப்பட்ட
e-மதிப்பு. `TwoProportionTest(method="grow")`.

**உலகளாவிய அனுமானம்** (universal inference). கடந்த காலத் தரவிலிருந்து மட்டுமே
மதிப்பிடப்பட்ட மாற்றுடன் கூடிய இயல்தகவு விகிதத்திலிருந்து பெறப்படும் e-மதிப்பு.
தகவமைவு வடிவமைப்புகளின் (adaptive designs) கீழும் இது செல்லுபடியாகிறது.
`TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). எந்தச் சார்புநிலையின் (dependence) கீழும் பல
e-மதிப்புகளின் மீது தவறான கண்டுபிடிப்பு விகிதத்தை (false discovery rate) இது
கட்டுப்படுத்துகிறது. `MultipleTests`, `e_bh`.

**e-LOND, இணையவழி FDR.** ஒவ்வொன்றாக முடிவு செய்யப்படும் கருதுகோள்களின் தொடரின்
மீது தவறான கண்டுபிடிப்பு விகிதக் கட்டுப்பாடு. `OnlineFDR`.

**SRM** (sample ratio mismatch, மாதிரி விகிதப் பொருத்தமின்மை). கிளைகளுக்கு இடையே
கவனிக்கப்பட்ட போக்குவரத்துப் பிரிப்பு அமைக்கப்பட்டதிலிருந்து வேறுபடுதல்; சோதனையில்
உள்ள பிழையின் அறிகுறி. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data, covariate adjustment,
regression adjustment; இணைமாறிச் சரிசெய்தல்). சோதனைக்கு முன் அளக்கப்பட்ட ஓர்
இணைமாறியைக் (covariate) கொண்டு A/B விளைவின் மாறுபாட்டளவைக் குறைக்கிறது.
`ABTest(covariate=True)`, `AnytimeLinearModel`.

**விகித அளவீடு** (ratio metric, delta method). ஒரு பயனருக்கான இரண்டு கூட்டுத்தொகைகளின்
விகிதமாக இருக்கும் அளவீடு, எடுத்துக்காட்டாக ஓர் அமர்வுக்கான வருவாய். `RatioABTest`.

**மாற்றப் புள்ளி கண்டறிதல்** (change-point detection, change detection, quickest
detection, online anomaly detection). ஒரு தொடரோட்டத்தின் பரவல் மாறிய சிறிது நேரத்தில்
எச்சரிக்கை எழுப்புதல். `CUSUM`, `ShiryaevRoberts`, `MeanEDetector`,
`QuantileEDetector`, `BayesianChangePoint`. காண்க
[மாற்றக் கண்டறிதல்](change-detection.md).

**ARL** (average run length, சராசரி ஓட்ட நீளம், ARL₀, mean time to false alarm).
எதுவும் மாறாதபோது ஒரு தவறான எச்சரிக்கை வரை எதிர்பார்க்கப்படும் கவனிப்புகளின்
எண்ணிக்கை. மாற்றக் கண்டறிவிகளின் தவறான-எச்சரிக்கைக் கட்டுப்பாடு.

**e-கண்டறிவி** (e-detector). e-செயல்முறைகளிலிருந்து கட்டப்பட்ட மாற்றக் கண்டறிவி;
சாத்தியமான ஒவ்வொரு மாற்ற நேரத்திலும் ஒன்று தொடங்கப்படுகிறது. அளவுருசாரா
(nonparametric) இன்மைக் கருதுகோளின் கீழ் அதன் ARL உத்தரவாதம் செய்யப்படுகிறது.
`MeanEDetector`, `QuantileEDetector`.

**Kiefer–Weiss சிக்கல்** (Kiefer–Weiss problem). அதிகபட்ச மாதிரி அளவு கொண்ட,
மிகப்பெரிய எதிர்பார்க்கப்படும் மாதிரி அளவைக் குறைக்கும் தொடர்முறைச் சோதனையைக்
கண்டறிதல். `kiefer_weiss_plan`.

**இயக்கப் பண்பு** (operating characteristic). ஒரு திட்டத்தின் பிழை நிகழ்தகவுகளும்
மாதிரி அளவின் பரவலும், உண்மை அளவுருவின் சார்புகளாக. `operating_characteristic`.

**சோதனைப்புள்ளி** (checkpoint). ஓர் ஓட்டம் துல்லியமாகத் தொடரக்கூடிய ஒரு JSON
மதிப்பு. `Run.checkpoint`, `Run.restore`. காண்க [தொடரோட்டச் செயலாக்கம்](streaming.md).

**வரலாற்றுச் செரிமானம்** (history digest). ஓர் ஓட்டம் பயன்படுத்திய கவனிப்புகளின்
மீதான SHA-256 ஹாஷ் சங்கிலி, தணிக்கைக்காக ஒவ்வொரு சோதனைப்புள்ளியிலும்
வைக்கப்படுகிறது.

**உத்தரவாதம்** (guarantee: `exact`, `asymptotic`, `model`, `approximate`, `none`).
இந்த நூலகத்தின் ஒவ்வொரு செயல்முறையும் தான் எதை உறுதியளிக்கிறது என்பதைக் கூறும்
பண்புக்கூறு. காண்க [எந்த முறை?](../../choosing.md).
