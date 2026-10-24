---
description: Python에서 센서 판독값, 지연 시간, 지표 스트림의 변화를 탐지하는 방법. sequential-analysis의 CUSUM, Shiryaev–Roberts, 비모수 e-탐지기, 베이즈 온라인 변화점 탐지를 다루며, 오경보는 평균 런 길이(ARL)로 제어합니다.
language: ko
---

# 측정값 스트림에서 변화를 탐지하려면?

> 이 문서는 [영어 원문](../../guide/change-detection.md)의 번역본입니다. 아직 원어민의 검토를 거치지 않았으며, 두 문서의 내용이 다를 경우 영어 원문이 우선합니다.

**짧은 답.** 온라인 변화점 탐지기(online change-point detector)를
사용하세요. 탐지기는 스트림을 지켜보다가 분포가 바뀐 것으로 보이는 즉시
경보를 울립니다. 오경보(false alarm)는 **평균 런 길이**(average run length,
ARL)로 제어됩니다. ARL은 아무것도 바뀌지 않았을 때 오경보가 나기까지의 기대
관측 수입니다. sequential-analysis에서는 다음과 같습니다.

| 변화 전에 알고 있는 것 | 절차 | 보장 |
|---|---|---|
| 두 분포 모두 (예: 정규분포, 평균 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| 평균과 값의 상한·하한만 | `MeanEDetector` | 그러한 모든 분포에 대해 exact |
| 분위수 하나만 (예: 지연 시간의 95번째 백분위수) | `QuantileEDetector` | 모든 분포에 대해 exact |
| 변화 전후 모수가 미지인 모형 | `BayesianChangePoint` | 모형과 사전분포하에서 |

## 평균이 이동하는 센서

온도 센서가 표준편차 0.5의 잡음과 함께 70.0 °C를 읽습니다. 600번째
판독값부터 평균은 70.4입니다. 임계값이 log(1000) ≈ 6.9인 CUSUM의 ARL은
적어도 1,000회 판독입니다.

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

표준편차 1보다 작은 이동은 개별 판독값에서는 눈으로 알아볼 수 없습니다.
CUSUM은 증거를 누적해 이를 찾아냅니다.

## 판독값이 정규분포를 따르지 않을 때

CUSUM의 ARL은 판독값이 지정한 분포를 따를 때에만 성립합니다. 치우친
데이터(진동 진폭, 지연 시간, 대기열 길이)에서는 계획보다 훨씬 자주 오경보를
냅니다. e-탐지기(e-detector)에 필요한 것은 훨씬 적습니다.

* `MeanEDetector`에는 변화 전 평균과 값의 상한·하한이 필요합니다.
* `QuantileEDetector`에는 변화 전 분위수 하나만 필요합니다.

이들의 ARL은 그 평균이나 분위수를 갖는 **모든** 분포에 대해 목표값
이상입니다.

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

실제로는 변화 전 분위수를 평온한 기간의 데이터로 추정합니다. 그러면 보장은
근사적으로 성립하며, 그 기간이 길수록 더 잘 성립합니다.

## ARL 선택하기

ARL은 오경보와 탐지 지연 사이의 절충입니다. 1분에 한 번 판독한다면 ARL
1,000회 판독은 센서 하나당 정상 운전 약 17시간마다 오경보 한 번을 뜻합니다.
센서가 50개라면 하루에 약 70건입니다. ARL은 모든 센서를 합쳐 하루에 감당할 수
있는 오경보 수를 기준으로 정하세요. 여기서는 ARL을 1,000,000회 판독으로 하면
50개 센서의 오경보가 약 2주에 한 번으로 줄어듭니다. 탐지 지연은 ARL의
로그만큼만 늘어나므로, 비용은 생각보다 적습니다. CUSUM의 경우 임계값이
6.9에서 13.8로 올라가고 지연은 대략 두 배가 됩니다.

이 탐지기들은 모니터링 도구이지 안전 시스템이 아닙니다. 인증된 안전 계장
시스템(safety instrumented system) 대신 사용하지 마세요.

더 보기: [튜토리얼: 공정 모니터링과 변화 탐지](../../tutorials/monitoring.md),
[은닉 마르코프 모형으로 보는 국면(regime)](../../tutorials/regimes.md),
[레퍼런스: 변화 탐지](../../reference/detection.md).
