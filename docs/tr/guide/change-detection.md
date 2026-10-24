---
description: Sensör okumaları, gecikme süreleri ya da metriklerden oluşan bir akıştaki değişimi Python'da CUSUM, Shiryaev–Roberts, parametrik olmayan e-dedektörler ve Bayesçi çevrim içi değişim noktası tespitiyle bulma. Yanlış alarmlar ortalama çalışma uzunluğu (ARL) ile kontrol edilir, sequential-analysis ile.
language: tr
---

# Bir ölçüm akışındaki değişimi nasıl tespit ederim?

> Bu sayfa [İngilizce sayfanın](../../guide/change-detection.md) çevirisidir. Henüz anadili Türkçe olan biri tarafından gözden geçirilmemiştir; iki metin arasında fark olduğunda İngilizce sayfa esas alınır.

**Kısa yanıt.** Çevrim içi bir değişim noktası dedektörü (online
change-point detector) kullanın. Dedektör akışı izler ve dağılımın
değişmiş göründüğü anda alarm verir. Yanlış alarmları **ortalama
çalışma uzunluğu** (average run length, ARL) ile kontrol edilir: hiçbir
şey değişmemişken yanlış bir alarma kadar beklenen gözlem sayısı.
sequential-analysis'te:

| Değişimden önce bildikleriniz | Prosedür | Garanti |
|---|---|---|
| her iki dağılım (ör. normal, ortalama 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| yalnızca ortalama ve değerlerin sınırları | `MeanEDetector` | bu türden her dağılım için exact |
| yalnızca bir kantil (ör. gecikmenin 95. yüzdeliği) | `QuantileEDetector` | her dağılım için exact |
| değişimden önce ve sonra parametreleri bilinmeyen bir model | `BayesianChangePoint` | model ve önsel dağılım altında |

## Ortalaması kayan bir sensör

Bir sıcaklık sensörü, standart sapması 0,5 olan gürültüyle 70,0 °C
okuyor. 600. okumadan itibaren ortalama 70,4 oluyor. Eşiği
log(1000) ≈ 6,9 olan CUSUM'un ARL'si en az 1.000 okumadır:

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

Bir standart sapmadan küçük bir kayma, tek tek okumaların hiçbirinde
gözle görülmez. CUSUM kanıtı biriktirir ve kaymayı bulur.

## Okumalar normal dağılmadığında

CUSUM'un ARL'si yalnızca okumalar ona verdiğiniz dağılımlara uyuyorsa
geçerlidir. Çarpık veriler (titreşim genlikleri, gecikmeler, kuyruk
uzunlukları) için planlanandan çok daha sık yanlış alarm verir.
E-dedektörler (e-detectors) çok daha azına ihtiyaç duyar:

* `MeanEDetector`, değişimden önceki ortalamaya ve değerlerin
  sınırlarına ihtiyaç duyar.
* `QuantileEDetector` yalnızca değişimden önceki bir kantile ihtiyaç
  duyar.

Bunların ARL'si, o ortalamaya ya da kantile sahip **her** dağılım için
en az hedef değer kadardır:

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

Pratikte değişimden önceki kantil sakin bir dönemden tahmin edilir. Bu
durumda garanti yaklaşık olarak geçerlidir; o dönem ne kadar uzunsa o
kadar iyi.

## ARL'nin seçilmesi

ARL, yanlış alarmlarla gecikme arasında bir denge kurar. Dakikada bir
okumada 1.000 okumalık bir ARL, normal işletimde sensör başına yaklaşık
her 17 saatte bir yanlış alarm demektir. 50 sensörle bu, günde yaklaşık
70 alarm eder. ARL'yi, tüm sensörlerde birlikte günde kaldırabileceğiniz
yanlış alarm sayısına göre seçin: burada 1.000.000 okumalık bir ARL, 50
sensörü yaklaşık iki haftada bir yanlış alarma indirir. Bunun bedeli
göründüğünden azdır, çünkü tespit gecikmesi ARL'nin yalnızca logaritmasıyla
büyür. CUSUM için eşik 6,9'dan 13,8'e çıkar ve gecikme kabaca iki katına
çıkar.

Bu dedektörler emniyet sistemleri değil, izleme araçlarıdır. Onları
sertifikalı bir emniyet enstrümanlı sistemin (safety instrumented
system) yerine kullanmayın.

Daha fazlası: [eğitim: süreç izleme ve değişim tespiti](../../tutorials/monitoring.md),
[gizli Markov modelleriyle rejimler](../../tutorials/regimes.md),
[başvuru: değişim tespiti](../../reference/detection.md).
