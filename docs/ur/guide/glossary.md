---
description: ترتیبی تجزیے اور anytime-valid inference کی اصطلاحات - e-value، e-process، confidence sequence، always-valid p-value، mSPRT، alpha spending، information fraction، ARL، SRM، CUPED، e-BH - مترادفات اور انہیں نافذ کرنے والے sequential-analysis کے طریقوں کے ساتھ۔
language: ur
---

# اصطلاحات

> یہ [انگریزی صفحے](../../guide/glossary.md) کا ترجمہ ہے۔ ابھی کسی اہلِ زبان نے اس کا جائزہ نہیں لیا؛ جہاں دونوں میں فرق ہو، وہاں انگریزی صفحہ ہی مستند ہے۔

ترتیبی تجزیے میں اور اس لائبریری میں استعمال ہونے والی اصطلاحات۔ عام استعمال کے
مترادفات قوسین میں دیے گئے ہیں۔

**ترتیبی تجزیہ (Sequential analysis)** (sequential testing، sequential inference)۔
شماریات جس میں مشاہدات کی تعداد پہلے سے مقرر نہیں ہوتی۔ ہر مشاہدے یا مشاہدات کے
گروہ کے بعد طریقۂ کار فیصلہ کرتا ہے کہ رکنا ہے یا جاری رکھنا ہے۔ اس کی بنیاد Wald
(1945) نے رکھی۔

**Peeking (بار بار جھانکنا)** (optional stopping، data peeking، continuous monitoring)۔
مقررہ نمونے کے ٹیسٹ کو بار بار دیکھنا اور معنی خیز (significant) ہونے پر رک جانا۔
یہ غلط مثبت شرح بڑھاتا ہے؛ دیکھیں [peeking](peeking.md)۔

**SPRT** (sequential probability ratio test، ترتیبی احتمالی تناسب ٹیسٹ، Wald's test)۔
یہ دو سادہ مفروضوں (simple hypotheses) کا لاگ امکانی تناسب (log likelihood ratio)
جمع کرتا ہے اور جب وہ ایک وقفے سے باہر نکلتا ہے تو رک جاتا ہے۔ `SPRT`؛ مختصر کیے
گئے (truncated) ورژن `TwoSPRT` (Lorden's 2-SPRT) اور `kiefer_weiss_plan`۔ دیکھیں
[SPRT](sprt.md)۔

**گروہی ترتیبی ڈیزائن (Group sequential design)** (interim analyses، group sequential trial)۔
چند منصوبہ بند تجزیے، ہر ایک کی ایک حد۔ حدیں اس طرح منتخب کی جاتی ہیں کہ مجموعی
ٹائپ I غلطی (type I error) alpha ہو۔ `group_sequential_design`۔ دیکھیں
[کلینیکل ٹرائلز](clinical-trials.md)۔

**الفا اسپینڈنگ فنکشن (Alpha spending function)** (error spending، Lan–DeMets)۔ یہ
بتاتا ہے کہ ہر معلوماتی حصے تک ٹائپ I غلطی کا کتنا حصہ خرچ کیا جا سکتا ہے۔
O'Brien–Fleming قسم کی اسپینڈنگ شروع میں کم خرچ کرتی ہے، Pocock قسم کی اسپینڈنگ
یکساں خرچ کرتی ہے۔ `spending="obrien-fleming"`، `"pocock"`، ...

**معلوماتی حصہ (Information fraction)۔** کسی تجزیے پر حاصل شدہ منصوبہ بند شماریاتی
معلومات (مریض، واقعات) کا حصہ۔

**لاحاصلی کی حد (Futility boundary)** (non-binding futility)۔ ایک نچلی حد: اس سے
نیچے اثر نہ ہونے کی بنا پر رکنے کی سفارش کی جاتی ہے۔ non-binding حد کو ٹائپ I
غلطی بڑھائے بغیر نظر انداز کیا جا سکتا ہے۔

**Anytime-valid استنباط (Anytime-valid inference)** (always-valid inference، safe anytime-valid
inference، SAVI)۔ ایسے ٹیسٹ اور وقفے جن کی ضمانتیں بیک وقت نمونے کے ہر حجم پر لاگو
ہوتی ہیں، اس لیے ان پر مسلسل نظر رکھی جا سکتی ہے اور کسی بھی وجہ سے روکا جا سکتا
ہے۔

**E-value** (e-variable، betting score)۔ ایک غیر منفی (non-negative) شماریہ جس کی
صفری مفروضے (null hypothesis) کے تحت توقع زیادہ سے زیادہ 1 ہے۔ بڑا e-value صفری
مفروضے کے خلاف ثبوت ہے: اس کے 1/alpha سے بڑھ جانے پر رد کرنے میں ٹائپ I غلطی
زیادہ سے زیادہ alpha ہوتی ہے۔ کئی طریقوں کا `log_e_value` آؤٹ پٹ۔

**E-process** (test martingale، test supermartingale، wealth process)۔
e-values کا ایک سلسلہ جو رکنے کے اوقات (stopping times) پر درست رہتا ہے۔ صفری
مفروضے کے تحت اس کا جاری زیادہ سے زیادہ (running maximum) زیادہ سے زیادہ alpha
احتمال کے ساتھ 1/alpha کو عبور کرتا ہے (Ville's inequality)۔

**Always-valid p-value** (anytime-valid p-value، sequential p-value)۔
ایسا p-value جو رکنے کے کسی بھی وقت پر درست ہے۔ یہ e-process کے جاری زیادہ سے
زیادہ کا معکوس (inverse) ہے۔ anytime-valid طریقوں کا `p_value` آؤٹ پٹ۔

**سلسلۂ اعتماد (Confidence sequence)** (anytime-valid confidence interval،
always-valid confidence interval، time-uniform confidence interval)۔ وقفوں کا ایک
سلسلہ جس میں نمونے کے تمام حجموں پر بیک وقت اصل قدر کم از کم 1 − alpha احتمال کے
ساتھ شامل رہتی ہے۔ `BettingConfidenceSequence`، `QuantileConfidenceSequence`،
`CatoniConfidenceSequence`، `AsymptoticConfidenceSequence`، اور کئی ٹیسٹوں کے
`lower` اور `upper` آؤٹ پٹ۔ دیکھیں [سلسلۂ اعتماد](confidence-sequences.md)۔

**mSPRT** (mixture SPRT، Robbins' mixture)۔ ایسا SPRT جس کا متبادل مفروضہ
(alternative) ایک prior پر اوسط لیا جاتا ہے، جس سے یہ ہر متبادل کے خلاف
anytime-valid بن جاتا ہے۔ `NormalMixtureSPRT` (معلوم تغیر)، `TMixtureSPRT`
(نامعلوم تغیر)۔

**شرط کے ذریعے جانچ (Testing by betting)۔** e-processes کو ایسے جواری کی دولت
(wealth) کے طور پر بنانا جو صفری مفروضے کے خلاف شرط لگاتا ہے۔ `BettingMeanTest`،
`BettingConfidenceSequence`، `KernelTwoSampleTest`۔

**GROW** (growth-rate optimal)۔ ایسا e-value جسے متبادل مفروضے کے تحت ثبوت کی متوقع
لاگ نمو کو زیادہ سے زیادہ کرنے کے لیے منتخب کیا جاتا ہے۔
`TwoProportionTest(method="grow")`۔

**Universal inference۔** امکانی تناسب سے بنا e-value، جس میں متبادل مفروضے کا
تخمینہ صرف ماضی کے ڈیٹا سے لگایا جاتا ہے۔ یہ adaptive ڈیزائنوں کے تحت درست رہتا
ہے۔ `TwoProportionTest(method="universal")`۔

**e-BH** (e-Benjamini–Hochberg)۔ یہ متعدد e-values پر، کسی بھی باہمی انحصار کے
تحت، غلط دریافت کی شرح (false discovery rate) کو کنٹرول کرتا ہے۔ `MultipleTests`،
`e_bh`۔

**e-LOND، online FDR۔** ایک ایک کر کے طے کیے جانے والے مفروضوں کے سلسلے پر غلط
دریافت کی شرح کا کنٹرول۔ `OnlineFDR`۔

**SRM** (sample ratio mismatch)۔ بازوؤں کے درمیان ٹریفک کی مشاہدہ شدہ تقسیم کنفیگر
کی گئی تقسیم سے مختلف ہے، جو تجربے میں بگ کی علامت ہے۔ `SampleRatioMismatch`۔

**CUPED** (controlled experiments using pre-experiment data، covariate
adjustment، regression adjustment)۔ تجربے سے پہلے ناپے گئے covariate کے ذریعے A/B
اثر کے تغیر کو کم کرتا ہے۔ `ABTest(covariate=True)`، `AnytimeLinearModel`۔

**تناسبی میٹرک (Ratio metric)** (delta method)۔ ایسی میٹرک جو فی صارف دو مجموعوں
کا تناسب ہو، جیسے فی سیشن آمدنی۔ `RatioABTest`۔

**نقطۂ تبدیلی کا سراغ (Change-point detection)** (change detection، quickest detection،
online anomaly detection)۔ اسٹریم کی تقسیم بدلنے کے فوراً بعد الارم دینا۔ `CUSUM`،
`ShiryaevRoberts`، `MeanEDetector`، `QuantileEDetector`، `BayesianChangePoint`۔
دیکھیں [تبدیلی کا سراغ](change-detection.md)۔

**ARL** (average run length، اوسط رن لمبائی، ARL₀، mean time to false alarm)۔ جب
کچھ نہ بدلا ہو تو جھوٹے الارم تک مشاہدات کی متوقع تعداد۔ تبدیلی کے ڈیٹیکٹرز کا
جھوٹے الارم پر کنٹرول۔

**E-detector۔** e-processes سے بنا تبدیلی کا ڈیٹیکٹر، جس میں تبدیلی کے ہر ممکنہ وقت
پر ایک e-process شروع ہوتا ہے۔ اس کا ARL ایک ناپیرامیٹرک صفری مفروضے کے تحت
ضمانت شدہ ہے۔ `MeanEDetector`، `QuantileEDetector`۔

**Kiefer–Weiss مسئلہ (Kiefer–Weiss problem)۔** نمونے کے زیادہ سے زیادہ حجم والا وہ
ترتیبی ٹیسٹ تلاش کرنا جو سب سے بڑے متوقع نمونے کے حجم کو کم سے کم کرے۔
`kiefer_weiss_plan`۔

**عملی خصوصیت (Operating characteristic)۔** کسی منصوبے کی غلطی کے احتمالات اور
نمونے کے حجم کی تقسیم، اصل پیرامیٹر کے فنکشن کے طور پر۔ `operating_characteristic`۔

**چیک پوائنٹ (Checkpoint)۔** ایک JSON قدر جس سے رن بالکل وہیں سے جاری رہتا ہے۔
`Run.checkpoint`، `Run.restore`۔ دیکھیں [اسٹریمنگ](streaming.md)۔

**History digest۔** رن کے استعمال کردہ مشاہدات پر SHA-256 ہیش چین، جو آڈٹ کے لیے
ہر چیک پوائنٹ میں رکھی جاتی ہے۔

**ضمانت (Guarantee)** (`exact`، `asymptotic`، `model`، `approximate`، `none`)۔
وہ ایٹریبیوٹ جس میں اس لائبریری کا ہر طریقۂ کار بتاتا ہے کہ وہ کیا وعدہ کرتا ہے۔
دیکھیں [کون سا طریقہ؟](../../choosing.md)۔
