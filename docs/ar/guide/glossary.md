---
description: مسرد مصطلحات التحليل التتابعي والاستدلال الصالح في أي وقت - قيمة e، وعملية e، ومتتالية الثقة، والقيمة الاحتمالية الصالحة دائمًا، وmSPRT، وإنفاق ألفا، ونسبة المعلومات، وARL، وSRM، وCUPED، وe-BH - مع المرادفات وإجراءات sequential-analysis التي تطبّق كلًّا منها.
language: ar
---

# مسرد المصطلحات

> هذه ترجمة [للصفحة الإنجليزية](../../guide/glossary.md). لم يراجعها متحدث أصلي باللغة بعد؛ وحيثما اختلفت الصفحتان، فالصفحة الإنجليزية هي المرجع المعتمد.

مصطلحات مستخدمة في التحليل التتابعي وفي هذه المكتبة. وتُذكر بين قوسين
المرادفات الشائعة الاستعمال بالإنجليزية.

**التحليل التتابعي** (sequential analysis، sequential testing، sequential
inference). إحصاء لا يكون فيه عدد المشاهدات محدّدًا مسبقًا. فبعد كل مشاهدة
أو مجموعة مشاهدات، يقرّر الإجراء التوقف أو الاستمرار. أسّسه Wald (1945).

**التلصّص على النتائج** (peeking، optional stopping، data peeking،
continuous monitoring). النظر في اختبار بحجم عينة ثابت مرارًا والتوقف حين
يصبح دالًّا إحصائيًا. وهو يضخّم معدل النتائج الإيجابية الكاذبة؛ انظر
[التلصّص على النتائج](peeking.md).

**SPRT** (sequential probability ratio test، اختبار نسبة الاحتمال التتابعي،
اختبار Wald). يراكم لوغاريتم نسبة الإمكان (likelihood ratio) بين فرضيتين
بسيطتين ويتوقف حين يغادر فترة معيّنة. `SPRT`؛ والصيغ المقتطعة `TwoSPRT`
(اختبار 2-SPRT لـ Lorden) و`kiefer_weiss_plan`. انظر [SPRT](sprt.md).

**التصميم التتابعي الجماعي** (group sequential design، interim analyses،
group sequential trial). عدد قليل من التحليلات المخطط لها، لكلٍّ منها حدّ.
وتُختار الحدود بحيث يكون الخطأ الكلي من النوع الأول مساويًا لـ alpha.
`group_sequential_design`. انظر [التجارب السريرية](clinical-trials.md).

**دالة إنفاق ألفا** (alpha spending function، error spending، Lan–DeMets).
تحدّد مقدار الخطأ من النوع الأول الذي يجوز استهلاكه عند كل نسبة معلومات.
الإنفاق من نوع O'Brien–Fleming ينفق قليلًا في البداية، والإنفاق من نوع
Pocock ينفق بالتساوي. `spending="obrien-fleming"`، `"pocock"`، ...

**نسبة المعلومات** (information fraction). حصة المعلومات الإحصائية المخطط
لها (المرضى، الأحداث) التي بُلغت عند تحليل ما.

**حدّ عدم الجدوى** (futility boundary، non-binding futility). حدّ أدنى:
إذا نزلت الإحصاءة تحته، يُوصى بالتوقف لغياب الأثر. ويجوز تجاهل الحد غير
الملزِم دون تضخيم الخطأ من النوع الأول.

**الاستدلال الصالح في أي وقت** (anytime-valid inference، always-valid
inference، safe anytime-valid inference، SAVI). اختبارات وفترات تصحّ
ضماناتها عند كل أحجام العينة في آن واحد، فيمكن مراقبتها باستمرار وإيقافها
لأي سبب.

**قيمة e** (e-value، e-variable، betting score). إحصاءة غير سالبة لا يتجاوز
توقّعها في ظل فرضية العدم 1. وقيمة e الكبيرة دليل ضد فرضية العدم: فالرفض
حين تتجاوز 1/alpha له خطأ من النوع الأول لا يزيد على alpha. وهي المُخرَج
`log_e_value` في كثير من الإجراءات.

**عملية e** (e-process، test martingale، test supermartingale، wealth
process). متتالية من قيم e تبقى صالحة عند أزمنة التوقف. ويعبر حدّها الأقصى
الجاري 1/alpha باحتمال لا يزيد على alpha في ظل فرضية العدم (متباينة Ville).

**القيمة الاحتمالية الصالحة دائمًا** (always-valid p-value، anytime-valid
p-value، sequential p-value). قيمة احتمالية صالحة عند أي زمن توقف. وهي
مقلوب الحد الأقصى الجاري لعملية e. وهي المُخرَج `p_value` في الإجراءات
الصالحة في أي وقت.

**متتالية الثقة** (confidence sequence، anytime-valid confidence interval،
always-valid confidence interval، time-uniform confidence interval).
متتالية من الفترات تحتوي على القيمة الحقيقية عند جميع أحجام العينة في آن
واحد باحتمال لا يقل عن 1 − alpha.
`BettingConfidenceSequence`، `QuantileConfidenceSequence`،
`CatoniConfidenceSequence`، `AsymptoticConfidenceSequence`، والمُخرَجان
`lower` و`upper` في كثير من الاختبارات. انظر
[متتاليات الثقة](confidence-sequences.md).

**mSPRT** (mixture SPRT، مزيج Robbins). اختبار SPRT تُؤخذ فرضيته البديلة
متوسطًا على توزيع مسبق، مما يجعله صالحًا في أي وقت مقابل كل بديل.
`NormalMixtureSPRT` (تباين معلوم)، `TMixtureSPRT`
(تباين مجهول).

**الاختبار بالمراهنة** (testing by betting). بناء عمليات e بوصفها ثروة
مقامر يراهن ضد فرضية العدم. `BettingMeanTest`،
`BettingConfidenceSequence`، `KernelTwoSampleTest`.

**GROW** (growth-rate optimal، الأمثل من حيث معدل النمو). قيمة e تُختار
لتعظيم النمو اللوغاريتمي المتوقع للأدلة في ظل الفرضية البديلة.
`TwoProportionTest(method="grow")`.

**الاستدلال الشامل** (universal inference). قيمة e مأخوذة من نسبة إمكان
تُقدَّر فيها الفرضية البديلة من البيانات السابقة فقط. وتبقى صالحة في ظل
التصاميم التكيفية. `TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). يضبط معدل الاكتشاف الخاطئ (false
discovery rate) عبر قيم e كثيرة، في ظل أي نوع من الاعتماد. `MultipleTests`، `e_bh`.

**e-LOND، FDR الفوري** (online FDR). ضبط معدل الاكتشاف الخاطئ عبر سلسلة من
الفرضيات يُبتّ فيها واحدة تلو الأخرى. `OnlineFDR`.

**SRM** (sample ratio mismatch، عدم تطابق نسبة العينة). يختلف التوزيع
المُشاهَد للحركة بين الأذرع عن التوزيع المضبوط، وهو علامة على خطأ برمجي في
التجربة. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data، covariate
adjustment، regression adjustment). يقلّل تباين أثر A/B باستخدام متغيّر
مصاحب قيس قبل التجربة.
`ABTest(covariate=True)`، `AnytimeLinearModel`.

**مقياس النسبة** (ratio metric، delta method). مقياس هو نسبة بين مجموعين لكل
مستخدم، مثل الإيراد لكل جلسة. `RatioABTest`.

**كشف نقاط التغيّر** (change-point detection، change detection، quickest
detection، online anomaly detection). إطلاق إنذار بعد وقت قصير من تغيّر
توزيع التدفق. `CUSUM`، `ShiryaevRoberts`،
`MeanEDetector`، `QuantileEDetector`، `BayesianChangePoint`. انظر
[كشف التغيّر](change-detection.md).

**ARL** (average run length، متوسط طول التشغيل، ARL₀، mean time to false
alarm). العدد المتوقع من المشاهدات حتى إنذار كاذب حين لا يتغيّر شيء. وهو
وسيلة ضبط الإنذارات الكاذبة في كواشف التغيّر.

**كاشف e** (e-detector). كاشف تغيّر مبني من عمليات e، تبدأ واحدة منها عند كل
زمن تغيّر ممكن. ومتوسط طول التشغيل لديه مضمون في ظل فرضية عدم لامعلمية.
`MeanEDetector`، `QuantileEDetector`.

**مسألة Kiefer–Weiss** (Kiefer–Weiss problem). إيجاد الاختبار التتابعي ذي
الحد الأقصى لحجم العينة الذي يقلّل أكبر حجم عينة متوقع إلى أدنى حد.
`kiefer_weiss_plan`.

**الخاصية التشغيلية** (operating characteristic). احتمالات الخطأ وتوزيع حجم
العينة لخطة ما، بوصفها دوال للمعلمة الحقيقية. `operating_characteristic`.

**نقطة الحفظ** (checkpoint). قيمة JSON يُستأنف منها التشغيل بدقة تامة.
`Run.checkpoint`، `Run.restore`. انظر [معالجة التدفقات](streaming.md).

**ملخص السجل** (history digest). سلسلة تجزئة SHA-256 على المشاهدات التي
استخدمها التشغيل، محفوظة في كل نقطة حفظ، لأغراض التدقيق.

**الضمان** (guarantee؛ `exact`، `asymptotic`، `model`، `approximate`، `none`).
السمة التي يعلن فيها كل إجراء في هذه المكتبة عمّا يَعِد به. انظر
[أي طريقة؟](../../choosing.md).
