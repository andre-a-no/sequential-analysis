---
description: Python에서 거짓 양성을 늘리지 않고 A/B 테스트를 조기에 중단하는 방법. sequential-analysis로 전환율과 상한이 있는 매출에 대한 언제든 유효한 검정, 표본 비율 불일치(SRM) 점검, 여러 지표에 대한 거짓 발견율(FDR) 제어를 수행합니다.
language: ko
---

# 거짓 양성을 늘리지 않고 A/B 테스트를 조기에 중단하려면?

> 이 문서는 [영어 원문](../../guide/ab-testing.md)의 번역본입니다. 아직 원어민의 검토를 거치지 않았으며, 두 문서의 내용이 다를 경우 영어 원문이 우선합니다.

**짧은 답.** 언제든 유효한(anytime-valid) 검정을 사용하세요. 이런 검정의
p-값과 신뢰구간은 얼마나 자주 들여다보든 유효하므로, 결과가 분명해지는 즉시
중단해도 됩니다. sequential-analysis에서는 다음과 같습니다.

| 지표 | 절차 | 보장 |
|---|---|---|
| 전환율 (0/1) | `TwoProportionTest` | exact |
| 상한·하한이 있는 모든 지표 (상한을 둔 매출, 비율) | `BoundedABTest` | exact |
| 노출 단위당 이벤트 수 | `RateRatioTest` | 포아송 계수에 대해 exact |
| 비율 지표 (세션당 매출) | `RatioABTest` | asymptotic |
| 실험 전 공변량을 활용한 평균 (CUPED) | `ABTest` | asymptotic |
| 트래픽이 의도대로 나뉘었는가? | `SampleRatioMismatch` | exact |
| 여러 지표나 여러 처리군을 함께 | `MultipleTests` (e-BH) | 거짓 발견율, exact |

각 절차에 사용자를 한 명씩 입력하세요: `state, out = test.step(state, {...})`.
`out.decision`에 따른 조치는 원하는 때 언제든 취하면 됩니다.

## 전환율: 데이터가 결론을 낼 때 중단하기

대조군의 전환율은 10%, 처리군은 12%입니다. 검정은 사용자가 한 명 들어올
때마다 확인되며 첫 결정에서 중단됩니다.

```python
import random

from sequential_analysis.procedures import TwoProportionTest

def users(n, rates=(0.10, 0.12), seed=1):
    """(arm, converted) per user; arm 1 is the treatment."""
    rnd = random.Random(seed)
    for _ in range(n):
        arm = int(rnd.random() < 0.5)
        yield arm, int(rnd.random() < rates[arm])

test = TwoProportionTest(alpha=0.05)
state = test.initial_state()
for arm, converted in users(60_000):
    state, out = test.step(state, {"arm": arm, "y": converted})
    if out.decision is not None:
        break
print(f"stopped after {out.n} users: conversion {out.rates[0]:.4f} (treatment) vs {out.rates[1]:.4f}, "
      f"anytime-valid p = {out.p_value:.4f}, decision: {out.decision}")
```

```text
stopped after 16469 users: conversion 0.1259 (treatment) vs 0.1068, anytime-valid p = 0.0496, decision: reject_h0
```

비교하자면, 이 정도의 상승을 검정력(power) 80%로 잡아내는 고정 표본 검정에는
처리군당 약 3,850명, 합계 7,700명이 필요하며, 결과는 마지막에 단 한 번만
볼 수 있습니다. 언제든 유효한 검정은 그 자유의 대가를 치릅니다. 같은
검정력에 도달하려면 단일 분석보다 1.3~1.6배의 사용자가 필요하며, 이번
실행은 그보다도 더 많이 걸렸습니다. 그 대신 표본 크기를 미리 정할 필요가
없고, 결과를 매일 확인하다가 분명해지는 즉시 중단할 수 있습니다. 효과가
계획보다 크면 그 시점은 훨씬 빨리 옵니다.

## 매출: 상한이 있는 지표에 대한 정확한 구간

`BoundedABTest`에는 지표의 상한과 하한만 있으면 됩니다. 테스트 전에 정한
값(여기서는 30)으로 매출에 상한을 두면, 평균 차이에 대한 신뢰 수열(confidence
sequence)은 어떤 분포에서도 정확(exact)합니다.

```python
from sequential_analysis.procedures import BoundedABTest

rnd = random.Random(2)
revenue = BoundedABTest(lower=0.0, upper=30.0, allocation=0.5, input="revenue", grid=300)
state = revenue.initial_state()
for _ in range(20_000):
    arm = int(rnd.random() < 0.5)
    spend = min(rnd.expovariate(1 / (5.0 if arm == 0 else 5.6)), 30.0)   # capped at 30
    state, out = revenue.step(state, {"arm": arm, "revenue": spend})
print(f"after {out.n} users: mean revenue {out.means[0]:.2f} (treatment) vs {out.means[1]:.2f}, "
      f"95% confidence sequence for the difference [{out.lower:.2f}, {out.upper:.2f}]")
```

```text
after 20000 users: mean revenue 5.47 (treatment) vs 4.99, 95% confidence sequence for the difference [-0.30, 1.30]
```

이 구간은 마지막 시점뿐 아니라 20,000번의 모든 확인 시점에서 동시에
성립합니다. 여기서는 구간이 여전히 0을 포함합니다. 이처럼 잡음이 큰 지표에서
약 0.5의 상승을 입증하기에 20,000명은 충분하지 않으므로 실험은 계속됩니다.

## 트래픽 분할부터 확인하기

표본 비율 불일치(sample ratio mismatch)란 실제 분할이 설정과 다르다는
뜻으로, 예를 들어 할당이나 로깅의 버그 때문에 생깁니다. 이런 실험에서 나온
효과 추정치는 믿을 수 없습니다. 50/50에서 52/48로의 불일치는 실험이 진행되는
동안 잡아낼 수 있습니다.

```python
from sequential_analysis.procedures import SampleRatioMismatch

srm = SampleRatioMismatch(weights=(0.5, 0.5), alpha=0.001)
state = srm.initial_state()
rnd = random.Random(3)
for _ in range(50_000):
    state, out = srm.step(state, {"arm": int(rnd.random() < 0.52)})
    if out.decision is not None:
        break
print(f"mismatch detected after {out.n} users: split {out.proportions[0]:.3f} / {out.proportions[1]:.3f}")
```

```text
mismatch detected after 4927 users: split 0.470 / 0.530
```

## 여러 지표를 한꺼번에

서로 독립인 지표 열 개를 각각 5%로 검정하면 적어도 하나의 거짓 발견이 나올
확률이 약 40%입니다. `MultipleTests`는 모든 검정의 e-값(e-value)을 e-BH
절차로 결합하므로, 어떤 중단 시점에서든 거짓 발견율(false discovery rate)이
`alpha` 이하로 유지됩니다.

```python
from sequential_analysis.procedures import MultipleTests

metrics = MultipleTests({
    "conversion": TwoProportionTest(input="converted"),
    "revenue": BoundedABTest(lower=0.0, upper=30.0, input="revenue", grid=100),
    "traffic split": SampleRatioMismatch((0.5, 0.5)),
}, alpha=0.05)
state = metrics.initial_state()
rnd = random.Random(4)
for _ in range(15_000):
    arm = int(rnd.random() < 0.5)
    converted = int(rnd.random() < (0.10, 0.13)[arm])
    spend = min(rnd.expovariate(1 / 5.0), 30.0)                          # no effect on revenue
    state, out = metrics.step(state, {"arm": arm, "converted": converted, "revenue": spend})
print("discoveries:", out.rejected)
```

```text
discoveries: ('conversion',)
```

## 주의할 점

* **분석 단위를 무작위 배정하세요.** 사용자를 무작위 배정했다면 페이지
  뷰가 아니라 사용자당 하나의 레코드를 입력하세요. 세션당 지표에는 사용자별
  합계로 작동하는 `RatioABTest`를 사용하세요.
* **상한이 있는 지표의 상한은 테스트 전에 정하세요.** 데이터를 본 뒤에
  정하면 보장이 무효가 됩니다.
* **점근적(asymptotic) 절차에는 큰 표본이 필요합니다.** `ABTest`와
  `RatioABTest`의 구간은 긴 실행에서만 근사적으로 유효합니다. 적용할 수
  있다면 정확한(exact) 절차를 선택하세요.
* **적응형 트래픽 할당**(밴딧)에는 분할이 결과에 따라 달라져도 유효한
  검정이 필요합니다:
  `TwoProportionTest(method="universal")` 또는
  `BoundedABTest(propensity_input=...)`.
  [튜토리얼 §10](../../tutorials/ab-test.md)을 참고하세요.

더 보기: [A/B 테스트 튜토리얼](../../tutorials/ab-test.md)(CUPED, 비율
지표, 발생률, 기간 계획)과
[실험 프로그램](../../tutorials/experiment-programme.md)
(여러 실험에 걸친 거짓 발견율).
