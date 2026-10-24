---
description: 置信序列是在所有样本量下同时有效的置信区间，因此可以持续监测。本页介绍如何在 Python 中使用 sequential-analysis 为有界均值、中位数或分位数，以及重尾分布的均值计算置信序列。
language: zh
---

# 如何获得在反复查看时仍然有效的置信区间？

> 本页译自[英文原文](../../guide/confidence-sequences.md)，尚未经母语人士审校；如两者有出入，以英文页面为准。

**简短回答。** 使用**置信序列**（confidence sequence）。它是一列区间，每次观测之后给出一个，并以至少 95% 的概率在所有样本量下同时包含真值。你可以一直观察它，在它足够窄或不再包含零时停止，并报告停止时的区间。通常的 95% 置信区间只在一个事先固定的样本量下才兑现 95% 的承诺。

| 估计对象 | 假设 | 方法 | 保证（guarantee） |
|---|---|---|---|
| 有界数据的均值（比率、评分、封顶的收入） | 取值在 `[lower, upper]` 内 | `BettingConfidenceSequence` | exact |
| 中位数、第 90 百分位数、任意分位数 | 无 | `QuantileConfidenceSequence` | exact |
| 重尾或含离群值数据的均值 | 标准差的上界 | `CatoniConfidenceSequence` | exact |
| 方差未知的正态数据的均值 | 正态性 | `TMixtureSPRT`（`lower`、`upper`） | 正态性下为 exact |
| 任意数据的均值，长时间运行 | 方差有限 | `AsymptoticConfidenceSequence` | asymptotic |
| 两个实验组之间的差异 | 见 [A/B 测试](ab-testing.md) | `BoundedABTest`、`ABTest` | exact / asymptotic |

## 通常的区间经不起反复查看

抽取 500 个均值为 0.3 的 0/1 变量观测值，从第 30 个开始，在每次观测后计算教科书式的 95% 区间：均值 ± 1.96 倍标准误。在 100 次运行中，有多少次区间会在某个时刻未覆盖真实均值？

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

它的“95%”只在事先固定的样本量下成立。对同样的数据，基于下注（betting）构造的置信序列（Waudby-Smith and Ramdas 2024）按其构造，在某个 n 处未覆盖真值的运行比例至多为 5%：

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

## 中位数延迟，完全不需要假设

延迟数据是偏态且重尾的，因此“均值 ± 标准误”的区间对它们并不可信。`QuantileConfidenceSequence` 适用于任何分布的任何分位数，包括存在结（ties）的情形：

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

真值分别为 120 ms 和 258.8 ms。两个区间在全部 2,000 个样本量下同时成立。

## 常见陷阱

* **上下界和封顶值是假设的一部分。** 应在看到数据之前选定 `lower` 和 `upper`。超出范围的值会被拒绝。
* **对于任意无界数据的均值，没有任何方法能给出精确覆盖。** 对此类数据，可以改用分位数、对取值封顶、假设标准差有上界（Catoni），或者接受渐近置信序列。
* **在相同样本量下，置信序列比单个区间更宽。** 这个宽度是同时在所有样本量下有效的代价。

更多内容：[选择哪种方法？](../../choosing.md)、
[参考：随时有效与非参数方法](../../reference/anytime.md)。
