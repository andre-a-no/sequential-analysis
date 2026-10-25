---
description: واژه‌نامهٔ اصطلاحات تحلیل دنباله‌ای و استنباط معتبر در هر زمان - مقدار e، فرایند e، دنبالهٔ اطمینان، مقدار p همیشه‌معتبر، mSPRT، مصرف آلفا، کسر اطلاعات، ARL، SRM، CUPED، e-BH - همراه با مترادف‌ها و روال‌های sequential-analysis که هر یک را پیاده‌سازی می‌کنند.
language: fa
---

# واژه‌نامه

> این صفحه ترجمه‌ای از [صفحهٔ انگلیسی](../../guide/glossary.md) است. این ترجمه هنوز توسط یک گویشور بومی بازبینی نشده است؛ هر جا این دو با هم تفاوت داشته باشند، صفحهٔ انگلیسی معتبر است.

اصطلاحاتی که در تحلیل دنباله‌ای و در این کتابخانه به کار می‌روند. مترادف‌های
رایج انگلیسی در پرانتز آمده‌اند.

**تحلیل دنباله‌ای** (sequential analysis، sequential testing، sequential
inference). آماری که در آن تعداد مشاهدات از پیش ثابت نیست. پس از هر مشاهده یا
گروهی از مشاهدات، روال تصمیم می‌گیرد که متوقف شود یا ادامه دهد. بنیان‌گذار آن
Wald (1945) است.

**سرک کشیدن به نتایج** (peeking، optional stopping، data peeking، continuous
monitoring). نگاه کردن مکرر به یک آزمون با اندازهٔ نمونهٔ ثابت و توقف وقتی
معنادار شد. این کار نرخ مثبت کاذب را بالا می‌برد؛ ببینید
[سرک کشیدن](peeking.md).

**SPRT** (sequential probability ratio test، آزمون نسبت احتمال دنباله‌ای،
آزمون والد). لگاریتم نسبت درست‌نمایی (likelihood ratio) دو فرض ساده را
انباشته می‌کند و وقتی از یک بازه خارج شد متوقف می‌شود. `SPRT`؛ نسخه‌های
بریده‌شده `TwoSPRT` (2-SPRT لوردن، Lorden) و `kiefer_weiss_plan`. ببینید
[SPRT](sprt.md).

**طرح دنباله‌ای گروهی** (group sequential design، interim analyses، group
sequential trial). چند تحلیل برنامه‌ریزی‌شده، هر یک با یک مرز. مرزها طوری
انتخاب می‌شوند که خطای نوع اول کلی برابر alpha باشد.
`group_sequential_design`. ببینید [کارآزمایی‌های بالینی](clinical-trials.md).

**تابع مصرف آلفا** (alpha spending function، error spending، Lan–DeMets).
مشخص می‌کند در هر کسر اطلاعات چه مقدار از خطای نوع اول می‌تواند مصرف شود.
مصرف از نوع O'Brien–Fleming در ابتدا اندکی مصرف می‌کند، مصرف از نوع Pocock به
طور یکنواخت. `spending="obrien-fleming"`، `"pocock"`، ...

**کسر اطلاعات** (information fraction). سهمی از اطلاعات آماری
برنامه‌ریزی‌شده (بیماران، رویدادها) که در یک تحلیل به دست آمده است.

**مرز بی‌فایدگی** (futility boundary، non-binding futility). یک مرز پایین:
زیر آن، توقف به دلیل نبود اثر توصیه می‌شود. مرز غیرالزام‌آور را می‌توان بدون
افزایش خطای نوع اول نادیده گرفت.

**استنباط معتبر در هر زمان** (anytime-valid inference، always-valid
inference، safe anytime-valid inference، SAVI). آزمون‌ها و بازه‌هایی که
تضمین‌هایشان در همهٔ اندازه‌های نمونه به‌طور هم‌زمان برقرار است، پس می‌توان
آن‌ها را پیوسته پایش کرد و به هر دلیلی متوقف کرد.

**مقدار e** (e-value، e-variable، betting score). آماره‌ای نامنفی که امید
ریاضی آن تحت فرض صفر حداکثر 1 است. مقدار e بزرگ شاهدی علیه فرض صفر است: رد
کردن وقتی از 1/alpha بیشتر شود، خطای نوع اولی حداکثر برابر alpha دارد. خروجی
`log_e_value` در بسیاری از روال‌ها.

**فرایند e** (e-process، test martingale، test supermartingale، wealth
process). دنباله‌ای از مقادیر e که در زمان‌های توقف معتبر می‌ماند. بیشینهٔ
جاری آن تحت فرض صفر حداکثر با احتمال alpha از 1/alpha عبور می‌کند (نابرابری
Ville).

**مقدار p همیشه‌معتبر** (always-valid p-value، anytime-valid p-value،
sequential p-value). مقدار p که در هر زمان توقفی معتبر است. وارون بیشینهٔ
جاری یک فرایند e است. خروجی `p_value` در روال‌های معتبر در هر زمان.

**دنبالهٔ اطمینان** (confidence sequence، anytime-valid confidence interval،
always-valid confidence interval، time-uniform confidence interval). دنباله‌ای
از بازه‌ها که با احتمال دست‌کم 1 − alpha مقدار واقعی را در همهٔ اندازه‌های
نمونه به‌طور هم‌زمان در بر دارد.
`BettingConfidenceSequence`، `QuantileConfidenceSequence`،
`CatoniConfidenceSequence`، `AsymptoticConfidenceSequence`، و خروجی‌های
`lower` و `upper` بسیاری از آزمون‌ها. ببینید
[دنباله‌های اطمینان](confidence-sequences.md).

**mSPRT** (mixture SPRT، آمیختهٔ Robbins). یک SPRT که فرض مقابل آن روی یک
توزیع پیشین میانگین‌گیری شده است، و همین آن را در برابر هر فرض مقابلی معتبر در
هر زمان می‌کند. `NormalMixtureSPRT` (واریانس معلوم)، `TMixtureSPRT`
(واریانس نامعلوم).

**آزمون از طریق شرط‌بندی** (testing by betting). ساختن فرایندهای e به‌صورت
ثروت قماربازی که علیه فرض صفر شرط می‌بندد. `BettingMeanTest`،
`BettingConfidenceSequence`، `KernelTwoSampleTest`.

**GROW** (growth-rate optimal، بهینه از نظر نرخ رشد). مقدار e که طوری انتخاب
می‌شود که رشد لگاریتمی مورد انتظار شواهد را تحت فرض مقابل بیشینه کند.
`TwoProportionTest(method="grow")`.

**استنباط جهانی** (universal inference). مقدار e حاصل از یک نسبت درست‌نمایی
که در آن فرض مقابل فقط از داده‌های گذشته برآورد شده است. تحت طرح‌های تطبیقی
معتبر می‌ماند. `TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). نرخ کشف کاذب (false discovery rate) را روی
مقادیر e متعدد، تحت هر نوع وابستگی، کنترل می‌کند. `MultipleTests`، `e_bh`.

**e-LOND، FDR برخط** (online FDR). کنترل نرخ کشف کاذب روی مجموعه‌ای از
فرض‌ها که یکی‌یکی دربارهٔ آن‌ها تصمیم گرفته می‌شود. `OnlineFDR`.

**SRM** (sample ratio mismatch، عدم تطابق نسبت نمونه). تقسیم مشاهده‌شدهٔ
ترافیک میان بازوها با تقسیم پیکربندی‌شده فرق دارد، که نشانهٔ یک باگ در
آزمایش است. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data، covariate
adjustment، regression adjustment). واریانس اثر A/B را با یک متغیر کمکی که
پیش از آزمایش اندازه‌گیری شده کاهش می‌دهد.
`ABTest(covariate=True)`، `AnytimeLinearModel`.

**معیار نسبتی** (ratio metric، delta method). معیاری که نسبت دو مجموع به ازای
هر کاربر است، مانند درآمد به ازای هر نشست. `RatioABTest`.

**تشخیص نقطهٔ تغییر** (change-point detection، change detection، quickest
detection، online anomaly detection). به صدا درآوردن هشدار اندکی پس از تغییر
توزیع یک جریان. `CUSUM`، `ShiryaevRoberts`،
`MeanEDetector`، `QuantileEDetector`، `BayesianChangePoint`. ببینید
[تشخیص تغییر](change-detection.md).

**ARL** (average run length، متوسط طول اجرا، ARL₀، mean time to false alarm).
تعداد مورد انتظار مشاهدات تا یک هشدار کاذب وقتی هیچ چیز تغییر نکرده است.
سازوکار کنترل هشدار کاذب در آشکارسازهای تغییر.

**آشکارساز e** (e-detector). آشکارساز تغییری که از فرایندهای e ساخته شده است،
که یکی از آن‌ها در هر زمان تغییر ممکن آغاز می‌شود. ARL آن تحت یک فرض صفر
ناپارامتری تضمین شده است. `MeanEDetector`، `QuantileEDetector`.

**مسئلهٔ Kiefer–Weiss** (Kiefer–Weiss problem). یافتن آزمون دنباله‌ای با
بیشینهٔ اندازهٔ نمونه که بزرگ‌ترین اندازهٔ نمونهٔ مورد انتظار را کمینه کند.
`kiefer_weiss_plan`.

**مشخصهٔ عملیاتی** (operating characteristic). احتمال‌های خطا و توزیع اندازهٔ
نمونهٔ یک طرح، به‌صورت تابعی از پارامتر واقعی. `operating_characteristic`.

**نقطهٔ بازیابی** (checkpoint). یک مقدار JSON که اجرا دقیقاً از آن ادامه
می‌یابد. `Run.checkpoint`، `Run.restore`. ببینید [پردازش جریانی](streaming.md).

**چکیدهٔ تاریخچه** (history digest). یک زنجیرهٔ هش SHA-256 روی مشاهداتی که
یک اجرا به کار برده است، که در هر نقطهٔ بازیابی برای ممیزی نگه داشته می‌شود.

**تضمین** (guarantee؛ `exact`، `asymptotic`، `model`، `approximate`، `none`).
ویژگی‌ای که هر روال در این کتابخانه در آن بیان می‌کند چه وعده‌ای می‌دهد.
ببینید [کدام روش؟](../../choosing.md).
