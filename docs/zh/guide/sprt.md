---
description: 如何在 Python 中使用 sequential-analysis 运行 Wald 序贯概率比检验（SPRT）。错误率、与固定样本量检验相比的平均样本量，以及截断的替代方案（2-SPRT、Kiefer–Weiss 最优方案）。
language: zh
---

# 如何在 Python 中运行 Wald 的 SPRT？

> 本页译自[英文原文](../../guide/sprt.md)，尚未经母语人士审校；如两者有出入，以英文页面为准。

**简短回答。** `sequential_analysis.procedures` 中的 `SPRT(family, theta0, theta1, alpha, beta)` 实现了 Wald 的序贯概率比检验（sequential probability ratio test，SPRT）。它以平均最少的观测在两个简单假设之间作出判断。每次输入一个观测，并在首次得出决策时停止。在下面的例子中，它只需要具有相同错误率的固定样本量检验约一半的观测：平均 65–76 个产品，而不是 133 个。如果你需要有保证的最大样本量，请改用 `TwoSPRT` 或 `kiefer_weiss_plan` 给出的方案。

## 示例：次品率是 10% 还是 20%？

若一批产品的次品率为 10% 则接收，为 20% 则拒收，两类错误率均为 5%：

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

在许多批次上它的表现如何？

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

具有相同错误率的固定样本量检验，每批大约检验 133 个产品（正态近似）。SPRT 平均少检验 43–51%。不过，它的样本量是随机的且没有上限，少数批次所需的时间远长于平均值。

阈值采用 Wald 的取值：log((1 − β)/α) 和 log(β/(1 − α))。它们保证，无论停止时的样本量为多少，实际错误率 α′ 和 β′ 都满足 α′ ≤ α/(1 − β)、β′ ≤ β/(1 − α) 以及 α′ + β′ ≤ α + β。似然比在停止时会越过阈值（overshoot），因此实践中的错误率低于名义值，正如本例所示。这就是 `SPRT.guarantee == "exact"` 的含义。若要精确计算错误率而非仅给出上界，请对方案使用 `operating_characteristic`（见下文）。

## 需要最大样本量时

* `TwoSPRT`（Lorden 的 2-SPRT）在固定的时限内停止，并近乎最小化最坏情况下的期望样本量。
* `sequential_analysis.design` 中的 `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)` 通过逆向归纳计算具有最大样本量的最优方案。`PlanTest` 执行该方案，`operating_characteristic` 无需模拟即可给出其精确的错误率和期望样本量。参见
  `examples/07_design_kiefer_weiss.py`。
* 若只需少数几次计划好的查看，而不是每个观测都查看，请使用[成组序贯设计](clinical-trials.md)。

## SPRT 不适用的情形

* **假设不是简单假设。** “比率为 10%”对“比率为其他任意值”是复合备择假设。请使用混合 SPRT（`NormalMixtureSPRT`、`TMixtureSPRT`）或下注检验（`BettingMeanTest`），它们对所有备择假设都是随时有效（anytime-valid）的。
* **真值位于 θ₀ 和 θ₁ 之间。** 此时 SPRT 最慢，其期望样本量可能超过固定样本量。Kiefer–Weiss 方案正是为这种情形而设计的。

似然比方法可用的分布族：`Gaussian`（方差已知）、`Bernoulli`、`Poisson`、`Exponential`。
