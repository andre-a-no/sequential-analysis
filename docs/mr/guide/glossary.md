---
description: अनुक्रमिक विश्लेषण (sequential analysis) आणि कधीही-वैध अनुमानातील संज्ञांची शब्दसूची - e-value, e-process, confidence sequence, always-valid p-value, mSPRT, alpha spending, information fraction, ARL, SRM, CUPED, e-BH - समानार्थी शब्द आणि प्रत्येक संज्ञा अंमलात आणणाऱ्या sequential-analysis कार्यपद्धतींसह.
language: mr
---

# शब्दसूची

> हे [इंग्रजी पानाचे](../../guide/glossary.md) भाषांतर आहे. मराठी मातृभाषक व्यक्तीने अद्याप त्याचे पुनरावलोकन केलेले नाही; दोन्हींमध्ये फरक आढळल्यास इंग्रजी पान अधिकृत मानावे.

अनुक्रमिक विश्लेषणात आणि या लायब्ररीत वापरल्या जाणाऱ्या संज्ञा. प्रचलित
समानार्थी शब्द कंसात दिले आहेत.

**अनुक्रमिक विश्लेषण** (sequential analysis, sequential testing, sequential inference).
अशी सांख्यिकी ज्यात निरीक्षणांची संख्या आधीपासून ठरलेली नसते. प्रत्येक निरीक्षण
किंवा निरीक्षणांच्या गटानंतर कार्यपद्धती थांबायचे की पुढे चालू ठेवायचे ते ठरवते.
Wald (1945) यांनी पाया घातला.

**डोकावणे** (peeking, optional stopping, data peeking, continuous monitoring).
स्थिर-नमुना चाचणी वारंवार पाहणे आणि ती सार्थ (significant) होताच थांबणे. यामुळे
खोट्या सकारात्मकांचा दर (false-positive rate) फुगतो; पाहा
[डोकावणे](peeking.md).

**SPRT** (sequential probability ratio test, अनुक्रमिक संभाव्यता गुणोत्तर चाचणी,
Wald ची चाचणी). ती दोन साध्या परिकल्पनांचे (simple hypotheses) लॉग संभाव्यता
गुणोत्तर (log likelihood ratio) साठवत जाते आणि ते एका अंतरालाबाहेर गेल्यावर थांबते.
`SPRT`; छाटलेल्या (truncated) आवृत्त्या `TwoSPRT` (Lorden ची 2-SPRT) आणि
`kiefer_weiss_plan`. पाहा [SPRT](sprt.md).

**गट अनुक्रमिक अभिकल्प** (group sequential design, interim analyses, group
sequential trial). काही नियोजित विश्लेषणे, प्रत्येकाची एक सीमा. सीमा अशा निवडल्या
जातात की एकूण प्रकार I त्रुटी (type I error) alpha असेल.
`group_sequential_design`. पाहा [वैद्यकीय चाचण्या](clinical-trials.md).

**अल्फा व्यय फलन** (alpha spending function, error spending, Lan–DeMets). प्रत्येक
माहिती अंशापर्यंत प्रकार I त्रुटीचा किती भाग वापरता येईल ते ते सांगते.
O'Brien–Fleming-प्रकारचा व्यय सुरुवातीला थोडे खर्च करतो, Pocock-प्रकारचा व्यय
समान प्रमाणात खर्च करतो. `spending="obrien-fleming"`, `"pocock"`, ...

**माहिती अंश** (information fraction). एखाद्या विश्लेषणाच्या वेळी गाठलेला नियोजित
सांख्यिकीय माहितीचा (रुग्ण, घटना) हिस्सा.

**निष्फळता सीमा** (futility boundary, non-binding futility). खालची सीमा: तिच्या
खाली गेल्यास परिणामाच्या अभावी थांबण्याची शिफारस केली जाते. अबंधनकारक सीमा प्रकार
I त्रुटी न फुगवता दुर्लक्षित करता येते.

**कधीही-वैध अनुमान** (anytime-valid inference, always-valid inference, safe
anytime-valid inference, SAVI). अशा चाचण्या आणि अंतराल ज्यांच्या हमी एकाच वेळी
प्रत्येक नमुना आकारावर टिकतात, त्यामुळे त्यांच्यावर सतत देखरेख करता येते आणि
कोणत्याही कारणाने थांबवता येतात.

**e-मूल्य** (e-value, e-variable, betting score). एक अऋण सांख्यिकी जिचे शून्य
परिकल्पनेखाली (null hypothesis) अपेक्षित मूल्य जास्तीत जास्त 1 असते. मोठे
e-मूल्य हा शून्य परिकल्पनेविरुद्ध पुरावा आहे: ते 1/alpha पेक्षा जास्त झाल्यावर
नाकारल्यास प्रकार I त्रुटी जास्तीत जास्त alpha असते. अनेक कार्यपद्धतींचे
`log_e_value` आउटपुट.

**e-प्रक्रिया** (e-process, test martingale, test supermartingale, wealth process).
e-मूल्यांचा असा अनुक्रम जो थांबण्याच्या वेळांवर (stopping times) वैध राहतो. शून्य
परिकल्पनेखाली त्याची चालू कमाल 1/alpha ओलांडण्याची संभाव्यता जास्तीत जास्त alpha
असते (Ville ची असमता).

**सदा-वैध p-मूल्य** (always-valid p-value, anytime-valid p-value, sequential
p-value). कोणत्याही थांबण्याच्या वेळी वैध असणारे p-मूल्य. ते e-प्रक्रियेच्या चालू
कमालीचा व्यस्त आहे. कधीही-वैध कार्यपद्धतींचे `p_value` आउटपुट.

**विश्वास्यता अनुक्रम** (confidence sequence, anytime-valid confidence interval,
always-valid confidence interval, time-uniform confidence interval). अंतरालांचा
असा अनुक्रम ज्यात खरे मूल्य किमान 1 − alpha संभाव्यतेने सर्व नमुना आकारांवर एकाच
वेळी असते.
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, आणि अनेक चाचण्यांचे
`lower` आणि `upper` आउटपुट. पाहा
[विश्वास्यता अनुक्रम](confidence-sequences.md).

**mSPRT** (mixture SPRT, मिश्रण SPRT, Robbins चे मिश्रण). अशी SPRT जिची पर्यायी
परिकल्पना पूर्व वितरणावर (prior) सरासरी काढलेली असते, ज्यामुळे ती प्रत्येक
पर्यायाविरुद्ध कधीही-वैध होते. `NormalMixtureSPRT` (ज्ञात विचरण), `TMixtureSPRT`
(अज्ञात विचरण).

**पैजेद्वारे चाचणी** (testing by betting). शून्य परिकल्पनेविरुद्ध पैज लावणाऱ्या
जुगाऱ्याची संपत्ती म्हणून e-प्रक्रिया तयार करणे. `BettingMeanTest`,
`BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal, वाढ-दर इष्टतम). पर्यायी परिकल्पनेखाली पुराव्याची
अपेक्षित लॉग वाढ कमाल करण्यासाठी निवडलेले e-मूल्य.
`TwoProportionTest(method="grow")`.

**सार्वत्रिक अनुमान** (universal inference). संभाव्यता गुणोत्तरावरून मिळणारे
e-मूल्य, ज्यात पर्यायी परिकल्पना फक्त भूतकाळातील डेटावरून अंदाजित केलेली असते.
ते अनुकूली अभिकल्पांखाली (adaptive designs) वैध राहते.
`TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). ते कोणत्याही परावलंबनाखाली (dependence) अनेक
e-मूल्यांवर खोट्या शोधांच्या दराचे (false discovery rate) नियंत्रण करते.
`MultipleTests`, `e_bh`.

**e-LOND, ऑनलाइन FDR.** एकेक करून निर्णय घेतल्या जाणाऱ्या परिकल्पनांच्या मालिकेवर
खोट्या शोधांच्या दराचे नियंत्रण. `OnlineFDR`.

**SRM** (sample ratio mismatch, नमुना गुणोत्तर विसंगती). शाखांमधील ट्रॅफिकची
निरीक्षित विभागणी कॉन्फिगर केलेल्यापेक्षा वेगळी असणे, प्रयोगातील बगचे लक्षण.
`SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data, covariate adjustment,
regression adjustment; सहचल समायोजन). प्रयोगापूर्वी मोजलेल्या सहचलाने (covariate)
A/B परिणामाचे विचरण कमी करते.
`ABTest(covariate=True)`, `AnytimeLinearModel`.

**गुणोत्तर मेट्रिक** (ratio metric, delta method). प्रति वापरकर्ता दोन बेरजांचे
गुणोत्तर असलेले मेट्रिक, जसे प्रति सत्र महसूल. `RatioABTest`.

**बदल-बिंदू शोध** (change-point detection, change detection, quickest detection,
online anomaly detection). प्रवाहाचे वितरण बदलल्यानंतर लवकरच इशारा देणे. `CUSUM`,
`ShiryaevRoberts`, `MeanEDetector`, `QuantileEDetector`, `BayesianChangePoint`. पाहा
[बदल शोध](change-detection.md).

**ARL** (average run length, सरासरी धाव लांबी, ARL₀, mean time to false alarm).
काहीही बदललेले नसताना खोट्या इशाऱ्यापर्यंत अपेक्षित निरीक्षणांची संख्या. बदल
शोधकांचे खोट्या इशाऱ्यांवरील नियंत्रण.

**e-शोधक** (e-detector). e-प्रक्रियांपासून बनवलेला बदल शोधक, प्रत्येक संभाव्य
बदलाच्या वेळी एक सुरू केलेली. अप्राचलिक (nonparametric) शून्य परिकल्पनेखाली त्याची
ARL हमीपूर्वक असते. `MeanEDetector`, `QuantileEDetector`.

**Kiefer–Weiss समस्या** (Kiefer–Weiss problem). कमाल नमुना आकार असलेली अशी
अनुक्रमिक चाचणी शोधणे जी सर्वात मोठा अपेक्षित नमुना आकार किमान करते.
`kiefer_weiss_plan`.

**कार्यकारी वैशिष्ट्य** (operating characteristic). योजनेच्या त्रुटी संभाव्यता आणि
नमुना आकाराचे वितरण, खऱ्या प्राचलाची फलने म्हणून. `operating_characteristic`.

**चेकपॉइंट** (checkpoint). असे JSON मूल्य ज्यापासून रन अचूकपणे पुढे चालू होतो.
`Run.checkpoint`, `Run.restore`. पाहा [प्रवाह प्रक्रिया](streaming.md).

**इतिहास डायजेस्ट** (history digest). रनने वापरलेल्या निरीक्षणांवरील SHA-256 हॅश
साखळी, लेखापरीक्षणासाठी प्रत्येक चेकपॉइंटमध्ये ठेवलेली.

**हमी** (guarantee: `exact`, `asymptotic`, `model`, `approximate`, `none`).
तो गुणधर्म ज्यात या लायब्ररीतील प्रत्येक कार्यपद्धती काय वचन देते ते नमूद करते. पाहा
[कोणती पद्धत?](../../choosing.md).
