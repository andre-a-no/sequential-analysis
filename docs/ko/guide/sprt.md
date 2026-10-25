---
description: sequential-analysis로 Python에서 Wald의 순차 확률비 검정(SPRT)을 실행하는 방법. 오류율, 고정 표본 검정 대비 평균 표본 크기, 그리고 절단된 대안(2-SPRT, Kiefer–Weiss 최적 계획)을 다룹니다.
language: ko
---

# Python에서 Wald의 SPRT를 실행하려면?

> 이 문서는 [영어 원문](../../guide/sprt.md)의 번역본입니다. 아직 원어민의 검토를 거치지 않았으며, 두 문서의 내용이 다를 경우 영어 원문이 우선합니다.

**짧은 답.** `sequential_analysis.procedures`의
`SPRT(family, theta0, theta1, alpha, beta)`는 Wald의 순차 확률비
검정(sequential probability ratio test, SPRT)을 구현합니다. 이 검정은 두
단순 가설 가운데 하나를 평균적으로 가장 적은 관측 수로 결정합니다. 관측값을
하나씩 입력하고 첫 결정에서 멈추세요. 아래 예에서는 같은 오류율을 갖는 고정
표본 검정의 약 절반만큼의 관측이 필요합니다. 평균 133개 대신 65~76개입니다.
최대 표본 크기가 보장되어야 한다면 대신 `TwoSPRT`나 `kiefer_weiss_plan`의
계획을 사용하세요.

## 예: 불량률은 10%인가, 20%인가?

로트(batch)는 불량률이 10%이면 합격, 20%이면 불합격 처리하며, 두 오류율은
모두 5%입니다.

```python
import random

from sequential_analysis.procedures import SPRT, Bernoulli

test = SPRT(Bernoulli(), theta0=0.10, theta1=0.20, alpha=0.05, beta=0.05)

def inspect_items(rate, seed):
    """Inspect items until the test decides; returns (decision, items inspected)."""
    rnd = random.Random(seed)
    state = test.initial_state()
    while state.decision is None:
        state, out = test.step(state, {"x": int(rnd.random() < rate)})
    return state.decision, state.n

decision, n = inspect_items(0.10, seed=1)
print(f"a good batch: {decision} after {n} items")
```

```text
a good batch: accept_h0 after 108 items
```

여러 로트에서는 얼마나 잘 작동할까요?

```python
for rate in (0.10, 0.20):
    results = [inspect_items(rate, seed) for seed in range(2000)]
    wrong = sum(d == ("reject_h0" if rate == 0.10 else "accept_h0") for d, _ in results) / len(results)
    average = sum(n for _, n in results) / len(results)
    longest = max(n for _, n in results)
    print(f"defect rate {rate:.0%}: wrong decision {wrong:.1%}, average {average:.0f} items, longest {longest}")
```

```text
defect rate 10%: wrong decision 3.5%, average 76 items, longest 370
defect rate 20%: wrong decision 4.3%, average 65 items, longest 315
```

같은 오류율을 갖는 고정 표본 검정은 로트마다 약 133개를 검사합니다(정규
근사). SPRT는 평균적으로 43~51% 적게 검사합니다. 다만 표본 크기가 확률적이고
상한이 없어서, 일부 로트는 평균보다 훨씬 오래 걸립니다.

임계값은 Wald의 것으로, log((1 − β)/α)와 log(β/(1 − α))입니다. 이 임계값은
중단 시점의 표본 크기가 얼마이든 실제 오류율 α′와 β′가 α′ ≤ α/(1 − β),
β′ ≤ β/(1 − α), α′ + β′ ≤ α + β를 만족함을 보장합니다. 중단할 때 우도비가
임계값을 넘어서기(overshoot) 때문에, 실제로는 여기서처럼 오류율이 명목값보다
낮습니다. 이것이 `SPRT.guarantee == "exact"`의 의미입니다. 상한이 아니라
정확히 계산된 오류율이 필요하면 계획에 `operating_characteristic`을
사용하세요(아래 참고).

## 최대 표본 크기가 필요할 때

* `TwoSPRT`(Lorden의 2-SPRT)는 고정된 기한(horizon)까지 중단하며, 최악의
  경우 기대 표본 크기를 거의 최소화합니다.
* `sequential_analysis.design`의
  `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`는
  역방향 귀납(backward induction)으로 최대 표본 크기가 있는 최적 계획을
  계산합니다. `PlanTest`가 그 계획을 실행하고,
  `operating_characteristic`은 시뮬레이션 없이 정확한 오류율과 기대 표본
  크기를 제공합니다. `examples/07_design_kiefer_weiss.py`를 참고하세요.
* 관측값마다가 아니라 몇 번의 계획된 시점에만 확인하려면
  [집단 순차 설계](clinical-trials.md)를 사용하세요.

## SPRT가 맞지 않는 경우

* **가설이 단순 가설이 아닐 때.** "비율이 10%이다" 대 "비율이 그 밖의 어떤
  값이다"는 복합 대립가설(composite alternative)입니다. 모든 대립가설에 대해
  언제든 유효한 혼합 SPRT(`NormalMixtureSPRT`, `TMixtureSPRT`)나 베팅에 의한
  검정(`BettingMeanTest`)을 사용하세요.
* **참값이 θ₀와 θ₁ 사이에 있을 때.** 이때 SPRT가 가장 느리며, 기대 표본
  크기가 고정 표본 크기를 넘을 수 있습니다. Kiefer–Weiss 계획은 바로 이
  경우를 위해 만들어졌습니다.

우도비 절차에 사용할 수 있는 분포족: `Gaussian`(분산 기지), `Bernoulli`,
`Poisson`, `Exponential`.
