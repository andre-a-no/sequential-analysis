---
description: Python에서 임상시험의 중간 분석을 계획하고 수행하는 방법. sequential-analysis의 집단 순차 설계(O'Brien–Fleming, Pocock, Lan–DeMets 알파 소비 함수, 무익성 경계)와 평균·비율·생존 분석의 표본 크기를 다루며, 결과는 rpact와 대조해 검증되었습니다.
language: ko
---

# 임상시험의 중간 분석은 어떻게 계획하나요?

> 이 문서는 [영어 원문](../../guide/clinical-trials.md)의 번역본입니다. 아직 원어민의 검토를 거치지 않았으며, 두 문서의 내용이 다를 경우 영어 원문이 우선합니다.

**짧은 답.** 집단 순차 설계(group sequential design)를 사용하세요.
`sequential_analysis.group_sequential`의
`group_sequential_design(alpha, fractions, spending=...)`는 다음을
계산합니다.

* Lan–DeMets 알파 소비(alpha spending)에 따른 유효성 경계(efficacy
  boundary) (O'Brien–Fleming형, Pocock형 등);
* 비구속적 무익성 경계(non-binding futility boundary);
* 검정력과 기대 표본 크기;
* 평균과 비율에 대한 최대 표본 크기, 또는 생존 분석의 사건 수.

경계와 표본 크기는 R 패키지 rpact와 일치합니다. 그런 다음 검정 절차
(`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`)가 환자 한 명씩,
또는 사건 하나씩 시험을 진행합니다. 각 중간 분석(interim analysis)은 해당
정보 분율(information fraction)에 도달했을 때 수행됩니다.

## 설계: 분석 4회, O'Brien–Fleming 소비 함수

단측 α = 0.025, 환자의 25%, 50%, 75%, 100% 시점에서 분석, 검정력 90%,
무익성 경계 포함:

```python
from sequential_analysis.group_sequential import group_sequential_design

design = group_sequential_design(0.025, [0.25, 0.5, 0.75, 1.0], spending="obrien-fleming",
                                 futility="obrien-fleming", power=0.9)
for k, (t, b, f) in enumerate(zip(design.fractions, design.bounds, design.futility), start=1):
    print(f"analysis {k} at {t:.0%}: efficacy if Z >= {b:.3f}, futility if Z <= {f:.3f}")
print("patients for an effect of 0.3 standard deviations:", design.max_sample_size(effect=0.3, sigma=1.0))
print(f"expected share of the patients used: {design.expected_fraction(0.0):.2f} with no effect, "
      f"{design.expected_fraction(design.drift):.2f} with the planned effect")
```

```text
analysis 1 at 25%: efficacy if Z >= 4.333, futility if Z <= -1.403
analysis 2 at 50%: efficacy if Z >= 2.963, futility if Z <= 0.325
analysis 3 at 75%: efficacy if Z >= 2.359, futility if Z <= 1.291
analysis 4 at 100%: efficacy if Z >= 2.014, futility if Z <= 2.014
patients for an effect of 0.3 standard deviations: 127
expected share of the patients used: 0.59 with no effect, 0.73 with the planned effect
```

## 이분형 및 생존 평가변수

```python
binary = group_sequential_design(0.025, [1 / 3, 2 / 3, 1.0], spending="obrien-fleming")
print("patients, response 10% vs 12%, 80% power:",
      binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8))
print("events for a hazard ratio of 0.7, 80% power:", binary.max_events(hazard_ratio=0.7, power=0.8))
print(f"inflation factor over a single analysis: {binary.inflation_factor(0.8):.3f}")
```

```text
patients, response 10% vs 12%, 80% power: 7780
events for a hazard ratio of 0.7, 80% power: 250
inflation factor over a single analysis: 1.013
```

O'Brien–Fleming 소비 함수를 쓰면 세 번의 분석에 드는 비용은 단일 최종
분석보다 환자 1.3% 증가입니다.

## 시험 진행하기

```python
import random

from sequential_analysis.procedures import GroupSequentialProportions

n_max = binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8)
test = GroupSequentialProportions.from_design(binary, n_max)
state, rnd = test.initial_state(), random.Random(3)
for patient in range(n_max):
    arm = patient % 2                                         # 1 treatment, 0 control
    state, out = test.step(state, {"arm": arm, "y": int(rnd.random() < (0.12 if arm else 0.10))})
    if out.analysis:
        print(f"analysis {out.analysis} after {out.n} patients: Z = {out.z:.2f}, bound {out.bound:.2f}")
    if out.decision:
        print("decision:", out.decision)
        break
```

```text
analysis 1 after 2594 patients: Z = 2.14, bound 3.71
analysis 2 after 5187 patients: Z = 2.64, bound 2.51
decision: reject_h0
```

시험은 계획한 환자의 3분의 2가 들어온 뒤, 두 번째 분석에서 유효성으로
중단되었습니다.

## 분석이 계획대로 이루어지지 않을 때

자료 모니터링 위원회(data monitoring committee)가 정확히 정보의 25%
시점에 회의하는 경우는 드뭅니다.

* `design.at(fractions)`는 실제로 도달한 정보에 맞춰 경계를 다시
  계산합니다. 알파 소비 덕분에 전체 유의수준이 유지됩니다.
* `GroupSequentialMonitor`는 직접 계산한 임의의 통계량(Cox 모형, 혼합
  모형)을 회의마다 Z 값과 그 정보량으로 받습니다.

## 환자마다 확인하고 싶다면?

집단 순차 설계는 계획한 횟수만큼만 확인할 수 있습니다. 환자나 사건마다
모니터링하려면 언제든 유효한(anytime-valid) 절차를 사용하세요. 생존 분석에는
`AnytimeLogRankTest`, 반응률에는 `TwoProportionTest`, 평균에는
`TMixtureSPRT`가 있습니다. 이 절차들은 계획한 효과에서 더 많은 환자가
필요합니다. [튜토리얼: 생존 시험](../../tutorials/survival.md)을 참고하세요.

## 규제 실무

알파 소비 함수를 사용하는 집단 순차 설계는 확증 시험(confirmatory trial)에서
확립된 접근법으로, ICH E9 가이드라인과 FDA의 적응형 설계 가이던스(2019)에
기술되어 있습니다. 이 라이브러리는 설계를 계산하고 각 분석에 대해 감사
가능하고 재개 가능한 기록(체크포인트와 그 이력 다이제스트)을 남깁니다. 다만
규제상 의미의 밸리데이션된 소프트웨어는 아닙니다. 허가 신청에 이를 사용하는
의뢰자(sponsor)는 다른 도구와 마찬가지로 직접 밸리데이션해야 합니다.

더 보기: rpact와 수치를 비교하는
[튜토리얼: 집단 순차 시험](../../tutorials/group-sequential.md);
[레퍼런스: 설계와 계획](../../reference/design.md).
