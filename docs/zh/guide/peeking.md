---
description: 为什么在 A/B 测试和临床试验中每天查看 p 值会抬高假阳性率（偷看问题），以及解决这一问题的三大类序贯方法，并用 Python 和 sequential-analysis 演示。
language: zh
---

# 为什么不能每天查看 p 值？

> 本页译自[英文原文](../../guide/peeking.md)，尚未经母语人士审校；如两者有出入，以英文页面为准。

**简短回答。** 固定样本量检验只有在你于计划样本量处查看一次结果时，才能保证 5% 的假阳性率。如果你反复查看，并在第一次出现 p < 0.05 时停止，就给了自己许多次被误导的机会。查看 20 次时，假阳性率会升至约 25%。序贯方法正是为反复查看而设计的。使用它们时，无论查看多少次、何时停止，假阳性率都保持在 5% 或以下。

## 偷看问题的实测

两个组的转化率均为 10%（A/A 测试），2,000 名用户，重复 200 次。“偷看”（peeking）做法是每 100 名用户后运行一次常规的两比例 z 检验，并在首次出现 p < 0.05 时停止。序贯的 `TwoProportionTest` 则在每一名用户之后都检查一次：

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

单次查看兑现了它的承诺。查看二十次使错误率增至约六倍。序贯检验即使在 2,000 名用户中的每一名之后都查看，仍将错误率保持在 5%。这就是它的承诺：其保证为 **exact**（`TwoProportionTest.guarantee == "exact"`），即无论查看多少次，在每个样本量下假阳性率至多为 5%。在 200 次重复中，10 次假阳性正是精确的 5% 所对应的结果。

## 序贯方法的三大类

| 类别 | 何时可以查看 | 典型用途 | 在 sequential-analysis 中 |
|---|---|---|---|
| **序贯概率比检验**（sequential probability ratio test，SPRT）（Wald 1945） | 每次观测之后 | 一个简单假设对另一个简单假设，平均所需观测最少：质量控制、模拟、心理物理学 | `SPRT`、`TwoSPRT`、`kiefer_weiss_plan` |
| **成组序贯设计**（group sequential design）（Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983） | 少数几次计划好的期中分析 | 设有数据监查委员会的临床试验 | `group_sequential_design`、`GroupSequentialTest`、`GroupSequentialProportions`、`GroupSequentialLogRank` |
| **随时有效推断**（anytime-valid inference）：e 值、置信序列、混合 SPRT（Robbins 1970, Howard et al. 2021, Ramdas et al. 2023） | 每次观测之后，可出于任何原因停止 | 在线 A/B 测试、监控看板 | `TwoProportionTest`、`BoundedABTest`、`NormalMixtureSPRT`、`BettingConfidenceSequence`、`MultipleTests` |

**代价是什么。** 在计划效应下，查看得越频繁，所需数据就越多：

* 有四次分析的成组序贯设计比单次分析多需 1–20% 的患者；
* 随时有效的两比例检验需要单次分析 1.3–1.6 倍的用户。

作为交换，大的效应会让实验提前停止，而且没有人需要事先确定样本量。

## 什么情况下这不是问题

只有当你的行动取决于你看到的结果时，偷看才会抬高错误率。如果你查看看板，但始终把实验运行到计划的样本量并只检验一次，那么固定样本量检验是有效的。在这种情况下，它也是效率最高的选择。

下一步：[提前停止 A/B 测试](ab-testing.md)、
[置信序列](confidence-sequences.md)、
[术语表](glossary.md)。
