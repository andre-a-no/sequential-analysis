---
description: अनुक्रमिक विश्लेषण और anytime-valid inference के शब्दों की शब्दावली - e-value, e-process, confidence sequence, always-valid p-value, mSPRT, alpha spending, information fraction, ARL, SRM, CUPED, e-BH - पर्यायों और उन्हें लागू करने वाली sequential-analysis प्रक्रियाओं के साथ।
language: hi
---

# शब्दावली

> यह [अंग्रेज़ी पृष्ठ](../../guide/glossary.md) का अनुवाद है। इसकी समीक्षा अभी किसी मूल हिंदी भाषी ने नहीं की है; जहाँ दोनों में अंतर हो, वहाँ अंग्रेज़ी पृष्ठ ही प्रामाणिक है।

अनुक्रमिक विश्लेषण में और इस लाइब्रेरी में प्रयुक्त शब्द। आम उपयोग वाले पर्याय
कोष्ठकों में दिए गए हैं।

**अनुक्रमिक विश्लेषण (Sequential analysis)** (sequential testing, sequential inference)।
सांख्यिकी जिसमें प्रेक्षणों की संख्या पहले से तय नहीं होती। हर प्रेक्षण या
प्रेक्षणों के समूह के बाद प्रक्रिया तय करती है कि रुकना है या जारी रखना है।
Wald (1945) ने इसकी नींव रखी।

**Peeking (बार-बार झाँकना)** (optional stopping, data peeking, continuous monitoring)।
निश्चित-सैंपल टेस्ट को बार-बार देखना और सार्थक (significant) होने पर रुक जाना।
यह फ़ॉल्स-पॉज़िटिव दर बढ़ाता है; देखें [peeking](peeking.md)।

**SPRT** (sequential probability ratio test, अनुक्रमिक प्रायिकता अनुपात परीक्षण,
Wald's test)। यह दो सरल परिकल्पनाओं (simple hypotheses) का लॉग संभाविता अनुपात
(log likelihood ratio) जमा करता है और जब वह एक अंतराल से बाहर निकलता है तब रुकता
है। `SPRT`; छोटे किए गए (truncated) संस्करण `TwoSPRT` (Lorden's 2-SPRT) और
`kiefer_weiss_plan`। देखें [SPRT](sprt.md)।

**समूह अनुक्रमिक डिज़ाइन (Group sequential design)** (interim analyses, group sequential trial)।
कुछ नियोजित विश्लेषण, हर एक की एक सीमा। सीमाएँ इस तरह चुनी जाती हैं कि समग्र
टाइप I त्रुटि (type I error) alpha हो। `group_sequential_design`। देखें
[क्लिनिकल ट्रायल](clinical-trials.md)।

**अल्फ़ा स्पेंडिंग फ़ंक्शन (Alpha spending function)** (error spending, Lan–DeMets)।
यह बताता है कि हर सूचना अंश तक टाइप I त्रुटि का कितना हिस्सा ख़र्च किया जा सकता
है। O'Brien–Fleming-प्रकार की स्पेंडिंग शुरुआत में कम ख़र्च करती है,
Pocock-प्रकार की स्पेंडिंग समान रूप से ख़र्च करती है। `spending="obrien-fleming"`,
`"pocock"`, ...

**सूचना अंश (Information fraction)।** किसी विश्लेषण पर पहुँची नियोजित सांख्यिकीय
सूचना (मरीज़, इवेंट्स) का हिस्सा।

**निरर्थकता सीमा (Futility boundary)** (non-binding futility)। एक निचली सीमा: इसके
नीचे प्रभाव की कमी के कारण रुकने की सिफ़ारिश की जाती है। non-binding सीमा को
टाइप I त्रुटि बढ़ाए बिना अनदेखा किया जा सकता है।

**Anytime-valid अनुमान (Anytime-valid inference)** (always-valid inference, safe anytime-valid
inference, SAVI)। ऐसे टेस्ट और अंतराल जिनकी गारंटियाँ एक साथ हर सैंपल साइज़ पर
लागू होती हैं, इसलिए उन पर लगातार नज़र रखी जा सकती है और किसी भी कारण से रोका
जा सकता है।

**E-value** (e-variable, betting score)। एक ऋणेतर (non-negative) सांख्यिकी जिसकी
शून्य परिकल्पना (null hypothesis) के अंतर्गत अपेक्षा अधिकतम 1 है। बड़ा e-value
null के विरुद्ध साक्ष्य है: इसके 1/alpha से अधिक होने पर अस्वीकार करने में टाइप I
त्रुटि अधिकतम alpha होती है। कई प्रक्रियाओं का `log_e_value` आउटपुट।

**E-process** (test martingale, test supermartingale, wealth process)।
e-value का एक अनुक्रम जो रुकने के समयों (stopping times) पर वैध रहता है। null के
अंतर्गत इसका चालू अधिकतम (running maximum) अधिकतम alpha प्रायिकता के साथ 1/alpha
को पार करता है (Ville's inequality)।

**Always-valid p-value** (anytime-valid p-value, sequential p-value)।
ऐसा p-value जो किसी भी रुकने के समय पर वैध है। यह e-process के चालू अधिकतम का
व्युत्क्रम (inverse) है। anytime-valid प्रक्रियाओं का `p_value` आउटपुट।

**विश्वास्यता अनुक्रम (Confidence sequence)** (anytime-valid confidence interval,
always-valid confidence interval, time-uniform confidence interval)। अंतरालों का
एक अनुक्रम जिसमें सभी सैंपल साइज़ पर एक साथ वास्तविक मान कम से कम 1 − alpha
प्रायिकता के साथ शामिल रहता है। `BettingConfidenceSequence`,
`QuantileConfidenceSequence`, `CatoniConfidenceSequence`,
`AsymptoticConfidenceSequence`, और कई टेस्टों के `lower` और `upper` आउटपुट।
देखें [विश्वास्यता अनुक्रम](confidence-sequences.md)।

**mSPRT** (mixture SPRT, Robbins' mixture)। ऐसा SPRT जिसकी वैकल्पिक परिकल्पना
(alternative) एक प्रायर पर औसत की जाती है, जिससे यह हर वैकल्पिक परिकल्पना के
विरुद्ध anytime-valid बन जाता है। `NormalMixtureSPRT` (ज्ञात प्रसरण),
`TMixtureSPRT` (अज्ञात प्रसरण)।

**बेटिंग द्वारा परीक्षण (Testing by betting)।** e-process को ऐसे जुआरी की संपत्ति
(wealth) के रूप में बनाना जो शून्य परिकल्पना के विरुद्ध दाँव लगाता है।
`BettingMeanTest`, `BettingConfidenceSequence`, `KernelTwoSampleTest`।

**GROW** (growth-rate optimal)। ऐसा e-value जिसे वैकल्पिक परिकल्पना के अंतर्गत
साक्ष्य की अपेक्षित लॉग वृद्धि को अधिकतम करने के लिए चुना जाता है।
`TwoProportionTest(method="grow")`।

**Universal inference।** संभाविता अनुपात से बना e-value, जिसमें वैकल्पिक परिकल्पना
का अनुमान केवल पिछले डेटा से लगाया जाता है। यह adaptive डिज़ाइनों के अंतर्गत वैध
रहता है। `TwoProportionTest(method="universal")`।

**e-BH** (e-Benjamini–Hochberg)। यह कई e-value पर, किसी भी निर्भरता के अंतर्गत,
मिथ्या खोज दर (false discovery rate) को नियंत्रित करता है। `MultipleTests`,
`e_bh`।

**e-LOND, online FDR।** एक-एक करके तय की जाने वाली परिकल्पनाओं की शृंखला पर मिथ्या
खोज दर का नियंत्रण। `OnlineFDR`।

**SRM** (sample ratio mismatch)। आर्म के बीच ट्रैफ़िक का देखा गया बँटवारा कॉन्फ़िगर
किए गए बँटवारे से अलग है, जो प्रयोग में बग का संकेत है। `SampleRatioMismatch`।

**CUPED** (controlled experiments using pre-experiment data, covariate
adjustment, regression adjustment)। प्रयोग से पहले मापे गए कोवेरिएट से A/B प्रभाव
के प्रसरण को कम करता है। `ABTest(covariate=True)`, `AnytimeLinearModel`।

**अनुपात मेट्रिक (Ratio metric)** (delta method)। ऐसी मेट्रिक जो प्रति उपयोगकर्ता
दो योगों का अनुपात है, जैसे प्रति सेशन रेवेन्यू। `RatioABTest`।

**परिवर्तन-बिंदु पहचान (Change-point detection)** (change detection, quickest detection,
online anomaly detection)। स्ट्रीम का वितरण बदलने के तुरंत बाद अलार्म देना।
`CUSUM`, `ShiryaevRoberts`, `MeanEDetector`, `QuantileEDetector`,
`BayesianChangePoint`। देखें [परिवर्तन पहचान](change-detection.md)।

**ARL** (average run length, औसत रन लंबाई, ARL₀, mean time to false alarm)। कुछ न
बदला हो तब झूठे अलार्म तक प्रेक्षणों की अपेक्षित संख्या। परिवर्तन डिटेक्टरों का
झूठे-अलार्म नियंत्रण।

**E-detector।** e-process से बना परिवर्तन डिटेक्टर, जिसमें हर संभावित परिवर्तन
समय पर एक e-process शुरू होता है। इसका ARL एक नॉनपैरामेट्रिक null के अंतर्गत
गारंटीड है। `MeanEDetector`, `QuantileEDetector`।

**Kiefer–Weiss समस्या (Kiefer–Weiss problem)।** अधिकतम सैंपल साइज़ वाला वह अनुक्रमिक
टेस्ट ढूँढना जो सबसे बड़े अपेक्षित सैंपल साइज़ को न्यूनतम करे।
`kiefer_weiss_plan`।

**ऑपरेटिंग विशेषता (Operating characteristic)।** किसी योजना की त्रुटि प्रायिकताएँ और
सैंपल साइज़ का वितरण, वास्तविक पैरामीटर के फ़ंक्शन के रूप में।
`operating_characteristic`।

**चेकपॉइंट (Checkpoint)।** एक JSON मान जिससे रन ठीक वहीं से जारी रहता है।
`Run.checkpoint`, `Run.restore`। देखें [स्ट्रीमिंग](streaming.md)।

**History digest।** रन द्वारा उपयोग किए गए प्रेक्षणों पर SHA-256 हैश चेन, जो ऑडिट
के लिए हर चेकपॉइंट में रखी जाती है।

**गारंटी (Guarantee)** (`exact`, `asymptotic`, `model`, `approximate`, `none`)।
वह एट्रिब्यूट जिसमें इस लाइब्रेरी की हर प्रक्रिया बताती है कि वह क्या वादा करती
है। देखें [कौन-सी विधि?](../../choosing.md)।
