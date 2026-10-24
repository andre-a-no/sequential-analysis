---
description: Paano matukoy ang pagbabago sa isang stream ng sensor reading, latency o metric sa Python, gamit ang CUSUM, Shiryaev–Roberts, mga nonparametric na e-detector at Bayesian online change-point detection. Kinokontrol ang mga false alarm sa pamamagitan ng average run length (ARL), gamit ang sequential-analysis.
language: tl
---

# Paano matukoy ang pagbabago sa isang stream ng mga sukat?

> Ito ay salin ng [pahina sa Ingles](../../guide/change-detection.md). Hindi pa ito nasusuri ng isang katutubong tagapagsalita ng wika; kung saan magkaiba ang dalawa, ang pahina sa Ingles ang masusunod.

**Maikling sagot.** Gumamit ng online change-point detector. Binabantayan
nito ang stream at nag-a-alarm sa sandaling mukhang nagbago ang
distribution. Kinokontrol ang mga false alarm nito ng **average run
length** (ARL): ang inaasahang bilang ng mga obserbasyon bago ang isang
false alarm habang walang nagbabago. Sa sequential-analysis:

| Ang alam mo bago ang pagbabago | Procedure | Garantiya |
|---|---|---|
| ang parehong distribution (hal. normal, mean 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| ang mean lamang, at mga bound sa mga halaga | `MeanEDetector` | exact para sa bawat ganoong distribution |
| isang quantile lamang (hal. ang 95th percentile ng latency) | `QuantileEDetector` | exact para sa bawat distribution |
| isang model na may hindi alam na mga parameter, bago at pagkatapos | `BayesianChangePoint` | sa ilalim ng model at ng prior |

## Isang sensor na lumilipat ang mean

Nagbabasa ang isang temperature sensor ng 70.0 °C na may noise na
standard deviation 0.5. Mula sa reading 600 pataas, ang mean ay 70.4. Ang
CUSUM na may threshold na log(1000) ≈ 6.9 ay may ARL na hindi bababa sa
1,000 reading:

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

Hindi nakikita ng mata sa alinmang iisang reading ang paglipat na mas
mababa sa isang standard deviation. Iniipon ng CUSUM ang ebidensiya at
natutuklasan ito.

## Kapag hindi normal ang mga reading

Nananatili lamang ang ARL ng CUSUM kung sumusunod ang mga reading sa mga
distribution na ibinigay mo rito. Para sa skewed na datos (amplitude ng
vibration, latency, haba ng queue), mas madalas nang husto itong
mag-false alarm kaysa sa pinlano. Mas kaunti nang husto ang kailangan ng
mga e-detector:

* Kailangan ng `MeanEDetector` ang mean bago ang pagbabago at mga bound sa
  mga halaga.
* Kailangan lamang ng `QuantileEDetector` ang isang quantile bago ang
  pagbabago.

Ang ARL nila ay hindi bababa sa target para sa **bawat** distribution na
may ganoong mean o quantile:

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

Sa praktika, tinatantiya ang quantile bago ang pagbabago mula sa isang
tahimik na panahon. Ang garantiya ay nananatili kung gayon nang
humigit-kumulang, at mas mahusay habang mas mahaba ang panahong iyon.

## Pagpili ng ARL

Ipinagpapalit ng ARL ang mga false alarm laban sa delay. Sa isang reading
bawat minuto, ang ARL na 1,000 reading ay nangangahulugang isang false
alarm bawat mga 17 oras ng normal na operasyon, bawat sensor. Sa 50 sensor,
mga 70 iyon bawat araw. Piliin ang ARL batay sa bilang ng false alarm
bawat araw na kaya mong tanggapin sa lahat ng sensor nang magkakasama:
dito, ang ARL na 1,000,000 reading ay nagpapababa sa 50 sensor sa mga isang
false alarm bawat dalawang linggo. Mas mura ito kaysa sa inaakala, dahil
lumalaki lamang ang detection delay ayon sa logarithm ng ARL. Para sa
CUSUM, umaakyat ang threshold mula 6.9 patungong 13.8, at humigit-kumulang
na dumodoble ang delay.

Ang mga detector na ito ay mga monitoring tool, hindi mga safety system.
Huwag gamitin ang mga ito kapalit ng isang certified na safety
instrumented system.

Higit pa: [tutorial: process monitoring at change detection](../../tutorials/monitoring.md),
[mga regime gamit ang hidden Markov model](../../tutorials/regimes.md),
[reference: change detection](../../reference/detection.md).
