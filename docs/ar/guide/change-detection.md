---
description: كيف تكشف تغيّرًا في تدفق من قراءات المستشعرات أو أزمنة الاستجابة أو المقاييس في Python، باستخدام CUSUM وShiryaev–Roberts والكواشف اللامعلمية من نوع e والكشف البايزي الفوري عن نقاط التغيّر. الإنذارات الكاذبة مضبوطة عبر متوسط طول التشغيل (ARL)، باستخدام sequential-analysis.
language: ar
---

# كيف أكشف تغيّرًا في تدفق من القياسات؟

> هذه ترجمة [للصفحة الإنجليزية](../../guide/change-detection.md). لم يراجعها متحدث أصلي باللغة بعد؛ وحيثما اختلفت الصفحتان، فالصفحة الإنجليزية هي المرجع المعتمد.

**الإجابة المختصرة.** استخدم كاشفًا فوريًا لنقاط التغيّر (online
change-point detector). يراقب التدفق ويطلق إنذارًا حالما يبدو أن التوزيع
قد تغيّر. وتُضبط إنذاراته الكاذبة عبر **متوسط طول التشغيل** (average run
length, ARL): العدد المتوقع من المشاهدات حتى إنذار كاذب ما دام شيء لم
يتغيّر. في sequential-analysis:

| ما تعرفه قبل التغيّر | الإجراء | الضمان |
|---|---|---|
| التوزيعان كلاهما (مثلًا طبيعي، المتوسط 70 → 71) | `CUSUM`، `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| المتوسط فقط، وحدود للقيم | `MeanEDetector` | exact لكل توزيع من هذا النوع |
| كمّيّة فقط (مثلًا المئين الـ 95 لزمن الاستجابة) | `QuantileEDetector` | exact لكل توزيع |
| نموذج بمعلمات مجهولة، قبل التغيّر وبعده | `BayesianChangePoint` | في ظل النموذج والتوزيع المسبق |

## مستشعر ينزاح متوسطه

يقرأ مستشعر حرارة 70.0 °C مع ضجيج انحرافه المعياري 0.5. وابتداءً من
القراءة 600 يصبح المتوسط 70.4. اختبار CUSUM بعتبة log(1000) ≈ 6.9 له
متوسط طول تشغيل لا يقل عن 1,000 قراءة:

```python
import math
import random

from sequential_analysis.procedures import CUSUM, Gaussian

rnd = random.Random(1)
readings = [rnd.gauss(70.0, 0.5) for _ in range(600)] + [rnd.gauss(70.4, 0.5) for _ in range(400)]

detector = CUSUM(Gaussian(sigma=0.5), theta0=70.0, theta1=70.4, threshold=math.log(1000))
state = detector.initial_state()
for t, x in enumerate(readings, start=1):
    state, out = detector.step(state, {"x": x})
    if out.alarm:
        print(f"alarm at reading {t}, {t - 600} readings after the shift")
        break
```

```text
alarm at reading 615, 15 readings after the shift
```

الانزياح الذي يقل عن انحراف معياري واحد لا تراه العين في أي قراءة
منفردة. أما CUSUM فيراكم الأدلة ويعثر عليه.

## حين لا تكون القراءات طبيعية التوزيع

لا يصحّ متوسط طول التشغيل في CUSUM إلا إذا اتبعت القراءات التوزيعات التي
أُعطيت له. ومع البيانات الملتوية (سعات الاهتزاز، أزمنة الاستجابة، أطوال
الطوابير) يطلق إنذارات كاذبة أكثر بكثير مما خُطّط له. أما الكواشف من نوع
e (e-detectors) فتحتاج إلى أقل من ذلك بكثير:

* يحتاج `MeanEDetector` إلى المتوسط قبل التغيّر وإلى حدود للقيم.
* يحتاج `QuantileEDetector` إلى كمّيّة واحدة فقط قبل التغيّر.

ومتوسط طول التشغيل لديها لا يقل عن الهدف **لكل** توزيع له ذلك المتوسط أو
تلك الكمّيّة:

```python
from sequential_analysis.procedures import QuantileEDetector

rnd = random.Random(2)
vibration = [rnd.lognormvariate(0.0, 0.8) for _ in range(800)] + [rnd.lognormvariate(0.5, 0.8) for _ in range(400)]
q95 = math.exp(0.8 * 1.6449)          # the 95th percentile before the change
p95 = QuantileEDetector(q0=q95, p=0.95, arl=1000, direction="increase", statistic="cusum")
state = p95.initial_state()
for t, x in enumerate(vibration, start=1):
    state, out = p95.step(state, {"x": x})
    if out.alarm:
        print(f"the 95th percentile rose: alarm at reading {t}, {t - 800} readings after the change")
        break
```

```text
the 95th percentile rose: alarm at reading 887, 87 readings after the change
```

عمليًا تُقدَّر الكمّيّة قبل التغيّر من فترة هادئة. ويصحّ الضمان عندئذ
تقريبًا، وكلما طالت تلك الفترة كان أفضل.

## اختيار متوسط طول التشغيل

يوازن متوسط طول التشغيل بين الإنذارات الكاذبة والتأخير. بمعدل قراءة واحدة
في الدقيقة، يعني ARL قدره 1,000 قراءة إنذارًا كاذبًا كل 17 ساعة تقريبًا
من التشغيل العادي، لكل مستشعر. ومع 50 مستشعرًا يصبح ذلك نحو 70 إنذارًا
في اليوم. اختر ARL بحسب عدد الإنذارات الكاذبة في اليوم الذي تتحمّله عبر
جميع المستشعرات معًا: هنا، ARL قدره 1,000,000 قراءة يخفّض المستشعرات
الـ 50 إلى نحو إنذار كاذب واحد كل أسبوعين. وكلفة ذلك أقل مما تبدو، لأن
تأخير الكشف لا ينمو إلا مع لوغاريتم ARL. ففي CUSUM ترتفع العتبة من 6.9
إلى 13.8، ويتضاعف التأخير تقريبًا.

هذه الكواشف أدوات مراقبة، وليست أنظمة سلامة. لا تستخدمها بديلًا عن نظام
أجهزة سلامة (safety instrumented system) معتمد.

المزيد: [درس تعليمي: مراقبة العمليات وكشف التغيّر](../../tutorials/monitoring.md)،
[تبدّل حالات النظام (regimes) باستخدام نماذج ماركوف المخفية](../../tutorials/regimes.md)،
[المرجع: كشف التغيّر](../../reference/detection.md).
