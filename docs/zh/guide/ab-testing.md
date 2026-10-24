---
description: 如何在 Python 中提前停止 A/B 测试而不抬高假阳性率。使用 sequential-analysis 进行转化率与有界收入的随时有效检验、样本比例不匹配检查，以及多指标的错误发现率控制。
language: zh
---

# 如何提前停止 A/B 测试而不抬高假阳性率？

> 本页译自[英文原文](../../guide/ab-testing.md)，尚未经母语人士审校；如两者有出入，以英文页面为准。

**简短回答。** 使用随时有效（anytime-valid）的检验：无论查看多少次，它的 p 值和置信区间都保持有效，因此结果一旦明确即可停止。在 sequential-analysis 中：

| 指标 | 方法 | 保证（guarantee） |
|---|---|---|
| 转化率（0/1） | `TwoProportionTest` | exact |
| 任意有界指标（封顶的收入、占比） | `BoundedABTest` | exact |
| 单位暴露量的事件数 | `RateRatioTest` | 对泊松计数为 exact |
| 比率指标（每次会话收入） | `RatioABTest` | asymptotic |
| 带实验前协变量的均值（CUPED） | `ABTest` | asymptotic |
| 流量分配是否符合预期？ | `SampleRatioMismatch` | exact |
| 同时检验多个指标或多个实验组 | `MultipleTests`（e-BH） | 错误发现率，exact |

每次向方法输入一个用户：`state, out = test.step(state, {...})`。
随时可以根据 `out.decision` 采取行动。

## 转化率：数据足以下结论时即停止

对照组转化率为 10%，实验组为 12%。每来一个用户就查看一次检验，并在首次得出决策时停止：

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

作为对比，要以 80% 的检验效能（power）检测这一提升，固定样本量检验约需每组 3,850 名用户、总计 7,700 名，而且只能在最后读取一次结果。随时有效检验为它的自由付出了代价：要达到相同的检验效能，它需要单次分析 1.3–1.6 倍的用户，而这次运行用得比这还多。作为交换，无需事先确定样本量，你可以每天查看结果，并在结果明确时立即停止。当效应大于计划值时，停止会早得多。

## 收入：有界指标的精确区间

`BoundedABTest` 只需要指标的上下界。在测试开始前选定收入的封顶值（此处为 30），则均值之差的置信序列（confidence sequence）对任何分布都是精确的：

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

该区间同时在全部 20,000 次查看中成立，而不仅仅是在最后一次。这里它仍然包含 0：对于噪声如此大的指标，20,000 名用户不足以确认约 0.5 的提升，因此实验继续进行。

## 先检查流量分配

样本比例不匹配（sample ratio mismatch，SRM）是指实际流量分配与配置不一致，例如由分组或日志记录中的缺陷引起。这类实验得出的效应估计不可信。从 50/50 偏移到 52/48 的不匹配能在实验运行期间被发现：

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

## 同时检验多个指标

以各自 5% 的水平检验十个相互独立的指标，至少出现一次错误发现的概率约为 40%。`MultipleTests` 用 e-BH 方法合并所有检验的 e 值（e-value），使错误发现率（false discovery rate，FDR）在任何停止时刻都保持在 `alpha`：

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

## 常见陷阱

* **对分析单元进行随机化。** 如果按用户随机分组，就每个用户输入一条记录，而不是每次页面浏览一条。对于按会话计算的指标，请使用 `RatioABTest`，它基于用户层面的汇总值。
* **在测试前固定有界指标的封顶值。** 看到数据后再选择会使保证失效。
* **渐近方法需要大样本。** 对于 `ABTest` 和 `RatioABTest`，区间只在长时间运行中近似有效。适用时请优先选择精确方法。
* **自适应流量分配**（多臂老虎机，bandits）需要在分配比例依赖于结果时仍保持有效的检验：
  `TwoProportionTest(method="universal")` 或
  `BoundedABTest(propensity_input=...)`。参见
  [教程第 10 节](../../tutorials/ab-test.md)。

更多内容：[A/B 测试教程](../../tutorials/ab-test.md)（CUPED、比率指标、率、实验时长规划）以及
[一组实验的整体管理](../../tutorials/experiment-programme.md)（跨多个实验的错误发现率）。
