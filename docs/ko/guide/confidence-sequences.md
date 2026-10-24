---
description: 신뢰 수열(confidence sequence)은 모든 표본 크기에서 동시에 유효한 신뢰구간이어서 계속 모니터링할 수 있습니다. sequential-analysis로 Python에서 유계 평균, 중앙값이나 분위수, 꼬리가 두꺼운 분포의 평균에 대해 신뢰 수열을 계산하는 방법을 설명합니다.
language: ko
---

# 계속 들여다봐도 유효한 신뢰구간은 어떻게 얻나요?

> 이 문서는 [영어 원문](../../guide/confidence-sequences.md)의 번역본입니다. 아직 원어민의 검토를 거치지 않았으며, 두 문서의 내용이 다를 경우 영어 원문이 우선합니다.

**짧은 답.** **신뢰 수열**(confidence sequence)을 사용하세요. 신뢰 수열은
관측값마다 하나씩 만들어지는 구간의 수열로, 모든 표본 크기에서 동시에 참값을
포함할 확률이 적어도 95%입니다. 이를 지켜보다가 충분히 좁아지거나 0을
제외하게 되면 멈추고, 멈춘 시점의 구간을 보고하면 됩니다. 일반적인 95%
신뢰구간은 미리 정한 하나의 표본 크기에서만 95%를 약속합니다.

| 추정 대상 | 가정 | 절차 | 보장 |
|---|---|---|---|
| 유계 데이터의 평균 (비율, 점수, 상한을 둔 매출) | 값이 `[lower, upper]` 안에 있음 | `BettingConfidenceSequence` | exact |
| 중앙값, 90번째 백분위수, 임의의 분위수 | 없음 | `QuantileConfidenceSequence` | exact |
| 꼬리가 두껍거나 이상치가 있는 평균 | 표준편차의 상한 | `CatoniConfidenceSequence` | exact |
| 정규 데이터의 평균, 분산 미지 | 정규성 | `TMixtureSPRT` (`lower`, `upper`) | 정규성하에서 exact |
| 임의 데이터의 평균, 긴 실행 | 유한 분산 | `AsymptoticConfidenceSequence` | asymptotic |
| 두 처리군 간 차이 | [A/B 테스트](ab-testing.md) 참고 | `BoundedABTest`, `ABTest` | exact / asymptotic |

## 일반적인 구간은 지켜보면 실패한다

평균이 0.3인 0/1 변수의 관측값 500개를 뽑고, 30번째부터 관측값마다 교과서적인
95% 구간, 즉 평균 ± 1.96 표준오차를 계산합니다. 100번의 실행 가운데 몇
번에서 구간이 어느 시점에든 참 평균을 놓칠까요?

```python
import math
import random

def stream(seed, n=500, p=0.3):
    rnd = random.Random(seed)
    return [float(rnd.random() < p) for _ in range(n)]

def textbook_ever_misses(xs, truth=0.3):
    total = total2 = 0.0
    for n, x in enumerate(xs, start=1):
        total, total2 = total + x, total2 + x * x
        if n >= 30:
            mean = total / n
            se = math.sqrt(max(total2 / n - mean * mean, 1e-12) / n)
            if abs(mean - truth) > 1.96 * se:
                return True
    return False

runs = [stream(seed) for seed in range(100)]
print(f"textbook interval misses the truth at some n in {sum(map(textbook_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
textbook interval misses the truth at some n in 28% of runs
```

이 구간의 "95%"는 미리 정한 표본 크기에서만 성립합니다. 같은 데이터에 대해
베팅으로 만든 신뢰 수열(Waudby-Smith and Ramdas 2024)은 구성상 어느 n에서든
참값을 놓치는 실행이 최대 5%입니다.

```python
from sequential_analysis.procedures import BettingConfidenceSequence

def sequence_ever_misses(xs, truth=0.3):
    cs = BettingConfidenceSequence(lower=0.0, upper=1.0, alpha=0.05, grid=100)
    state = cs.initial_state()
    for x in xs:
        state, out = cs.step(state, {"x": x})
        if not out.lower <= truth <= out.upper:
            return True
    return False

print(f"confidence sequence misses the truth at some n in {sum(map(sequence_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
confidence sequence misses the truth at some n in 1% of runs
```

## 아무 가정 없이 구하는 지연 시간의 중앙값

지연 시간(latency)은 치우쳐 있고 꼬리가 두꺼워서 평균 ± 표준오차 구간을
믿을 수 없습니다. `QuantileConfidenceSequence`는 동점을 포함해 어떤 분포의
어떤 분위수든 포괄합니다.

```python
from sequential_analysis.procedures import QuantileConfidenceSequence

rnd = random.Random(7)
median = QuantileConfidenceSequence(p=0.5, alpha=0.05)
p90 = QuantileConfidenceSequence(p=0.9, alpha=0.05)
m_state, q_state = median.initial_state(), p90.initial_state()
for _ in range(2000):
    latency = rnd.lognormvariate(math.log(120.0), 0.6)   # milliseconds; true median 120
    m_state, m = median.step(m_state, {"x": latency})
    q_state, q = p90.step(q_state, {"x": latency})
print(f"median: {m.estimate:.1f} ms, 95% confidence sequence [{m.lower:.1f}, {m.upper:.1f}]")
print(f"90th percentile: {q.estimate:.1f} ms, [{q.lower:.1f}, {q.upper:.1f}]")
```

```text
median: 117.3 ms, 95% confidence sequence [111.3, 122.6]
90th percentile: 252.7 ms, [237.9, 272.5]
```

참값은 120 ms와 258.8 ms입니다. 두 구간 모두 2,000개의 모든 표본 크기에서
동시에 성립합니다.

## 주의할 점

* **상한·하한과 상한 절단(cap)은 가정의 일부입니다.** `lower`와 `upper`는
  데이터를 보기 전에 정하세요. 그 범위를 벗어난 값은 거부됩니다.
* **임의의 비유계 데이터의 평균에 대해 정확한 포함 확률을 주는 방법은
  없습니다.** 그런 데이터에는 분위수를 사용하거나, 값에 상한을 두거나,
  표준편차의 상한을 가정하거나(Catoni), 점근적 수열을 받아들이세요.
* **신뢰 수열은 같은 표본 크기에서 단일 구간보다 넓습니다.** 그 폭이 모든
  표본 크기에서 동시에 유효하기 위한 대가입니다.

더 보기: [어떤 방법을 쓸까?](../../choosing.md),
[레퍼런스: 언제든 유효한 방법과 비모수 방법](../../reference/anytime.md).
