---
description: A/B 테스트와 임상시험에서 p-값을 매일 확인하면 왜 거짓 양성이 늘어나는지(엿보기 문제, peeking problem), 그리고 이를 해결하는 순차적 방법의 세 계열을 sequential-analysis와 함께 Python으로 설명합니다.
language: ko
---

# 왜 p-값을 매일 들여다보면 안 되나요?

> 이 문서는 [영어 원문](../../guide/peeking.md)의 번역본입니다. 아직 원어민의 검토를 거치지 않았으며, 두 문서의 내용이 다를 경우 영어 원문이 우선합니다.

**짧은 답.** 고정 표본 검정(fixed-sample test)이 약속하는 5%의 거짓
양성률(false-positive rate)은 계획한 표본 크기에서 결과를 단 한 번 볼 때에만
성립합니다. 반복해서 들여다보다가 처음으로 p < 0.05가 되는 순간 멈추면, 속을
기회가 여러 번 생깁니다. 20번 들여다보면 거짓 양성률은 약 25%로 올라갑니다.
순차적 방법(sequential methods)은 반복해서 들여다보도록 만들어졌습니다. 이
방법을 쓰면 얼마나 자주 보든, 언제 멈추든 거짓 양성률이 5% 이하로 유지됩니다.

## 엿보기 문제를 직접 측정하기

두 처리군의 전환율은 똑같이 10%이고(A/A 테스트), 사용자 2,000명, 반복
200회입니다. "엿보기(peeking)"는 사용자 100명마다 일반적인 두 비율 z-검정을
실행하고 처음으로 p < 0.05가 되면 멈춥니다. 순차 검정인
`TwoProportionTest`는 사용자가 한 명 들어올 때마다 확인합니다.

```python
import math
import random

from sequential_analysis.procedures import TwoProportionTest

def a_a_test(seed, users=2000):
    """Alternating arms, both converting 10% of the time: any 'effect' is a false positive."""
    rnd = random.Random(seed)
    return [(user % 2, int(rnd.random() < 0.10)) for user in range(users)]

def peeking(data, looks):
    """The z-test for two proportions after every len(data) / looks users; True if it ever rejects."""
    successes, trials, every = [0, 0], [0, 0], len(data) // looks
    for i, (arm, y) in enumerate(data, start=1):
        successes[arm] += y
        trials[arm] += 1
        if i % every == 0:
            pooled = sum(successes) / sum(trials)
            se = math.sqrt(pooled * (1 - pooled) * (1 / trials[0] + 1 / trials[1]))
            if se > 0 and abs(successes[1] / trials[1] - successes[0] / trials[0]) / se > 1.96:
                return True
    return False

def sequential(data):
    """The anytime-valid test, looked at after every user; True if it ever rejects."""
    test = TwoProportionTest(alpha=0.05)
    state = test.initial_state()
    for arm, y in data:
        state, out = test.step(state, {"arm": arm, "y": y})
        if out.decision is not None:
            return True
    return False

runs = [a_a_test(seed) for seed in range(200)]
print(f"z-test, one look at the end:   {sum(peeking(r, 1) for r in runs) / len(runs):.1%} false positives")
print(f"z-test, 20 looks:              {sum(peeking(r, 20) for r in runs) / len(runs):.1%}")
print(f"TwoProportionTest, 2000 looks: {sum(sequential(r) for r in runs) / len(runs):.1%}")
```

```text
z-test, one look at the end:   4.5% false positives
z-test, 20 looks:              28.0%
TwoProportionTest, 2000 looks: 5.0%
```

한 번만 보는 검정은 약속을 지킵니다. 20번 들여다보면 오류율이 약 6배로
늘어납니다. 순차 검정은 2,000명의 사용자 한 명 한 명마다 확인했는데도 5%를
유지합니다. 이것이 바로 그 약속입니다. 이 검정의 보장은 **exact**
(`TwoProportionTest.guarantee == "exact"`)로, 얼마나 자주 보든 모든 표본
크기에서 거짓 양성률이 최대 5%입니다. 200회 반복에서 거짓 양성 10건은 정확히
5%일 때 예상되는 수치입니다.

## 순차적 방법의 세 계열

| 계열 | 확인할 수 있는 시점 | 대표적 용도 | sequential-analysis에서 |
|---|---|---|---|
| **순차 확률비 검정(sequential probability ratio test)** (Wald 1945) | 관측값마다 | 단순 가설 대 단순 가설, 평균적으로 가장 적은 관측 수: 품질 관리, 시뮬레이션, 정신물리학 | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **집단 순차 설계(group sequential design)** (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | 미리 계획한 몇 번의 중간 분석에서 | 자료 모니터링 위원회가 있는 임상시험 | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **언제든 유효한 추론(anytime-valid inference)**: e-값, 신뢰 수열, 혼합 SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | 관측값마다, 어떤 이유로든 중단 가능 | 온라인 A/B 테스트, 모니터링 대시보드 | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**비용.** 더 자주 들여다보려면 계획한 효과 크기에서 더 많은 데이터가
필요합니다.

* 분석이 네 번인 집단 순차 설계는 단일 분석보다 환자가 1~20% 더
  필요합니다;
* 두 비율에 대한 언제든 유효한 검정은 단일 분석의 1.3~1.6배의 사용자가
  필요합니다.

그 대신 효과가 크면 실험이 일찍 끝나고, 아무도 표본 크기를 미리 정할 필요가
없습니다.

## 이것이 문제가 되지 않는 경우

엿보기가 오류를 부풀리는 것은 본 내용에 따라 행동이 달라질 때뿐입니다.
대시보드를 보더라도 항상 계획한 크기까지 실험을 진행하고 한 번만 검정한다면,
고정 표본 검정은 유효합니다. 그 경우에는 고정 표본 검정이 가장 효율적인
선택이기도 합니다.

다음: [A/B 테스트 조기 중단](ab-testing.md),
[신뢰 수열](confidence-sequences.md),
[용어집](glossary.md).
