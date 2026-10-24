---
description: 如何在 Python 中规划和实施临床试验的期中分析——成组序贯设计（O'Brien–Fleming、Pocock、Lan–DeMets α 消耗、无效性界值），以及均值、比例和生存终点的样本量计算，结果已与 rpact 核对，使用 sequential-analysis。
language: zh
---

# 如何规划临床试验的期中分析？

> 本页译自[英文原文](../../guide/clinical-trials.md)，尚未经母语人士审校；如两者有出入，以英文页面为准。

**简短回答。** 使用成组序贯设计（group sequential design）。
`sequential_analysis.group_sequential` 中的
`group_sequential_design(alpha, fractions, spending=...)` 可计算：

* 有效性界值（efficacy boundaries），采用 Lan–DeMets α 消耗（alpha spending）（O'Brien–Fleming 型、Pocock 型等）；
* 非约束性无效性界值（non-binding futility boundaries）；
* 检验效能（power）和期望样本量；
* 均值和比例终点的最大样本量，或生存终点所需的事件数。

界值和样本量与 R 包 rpact 一致。随后，检验方法（`GroupSequentialTest`、`GroupSequentialTwoMeans`、`GroupSequentialProportions`、`GroupSequentialLogRank`）逐个患者或逐个事件地执行试验，并在达到相应的信息分数（information fraction）时进行每一次期中分析（interim analysis）。

## 设计：四次分析，O'Brien–Fleming 消耗

单侧 α = 0.025，在入组 25%、50%、75% 和 100% 患者时进行分析，检验效能 90%，并设无效性界值：

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

## 二分类终点与生存终点

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

采用 O'Brien–Fleming 消耗时，三次分析只比单次最终分析多需 1.3% 的患者。

## 实施试验

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

试验在第二次分析时因有效而停止，此时入组了计划患者数的三分之二。

## 分析未按计划进行时

数据监查委员会（data monitoring committee）很少恰好在信息量达到 25% 时开会：

* `design.at(fractions)` 根据实际达到的信息量重新计算界值。α 消耗保证总体检验水准不变。
* `GroupSequentialMonitor` 接受你自己计算的任何统计量（Cox 模型、混合模型）在每次会议时的 Z 值及其信息量。

## 如果想在每个患者之后都查看呢？

成组序贯设计只允许计划好的查看次数。若要在每个患者或每个事件之后进行监测，请使用随时有效（anytime-valid）的方法：生存终点用 `AnytimeLogRankTest`，缓解率用 `TwoProportionTest`，均值用 `TMixtureSPRT`。在计划效应下，它们需要更多患者。参见[教程：生存试验](../../tutorials/survival.md)。

## 监管实践

采用 α 消耗的成组序贯设计是确证性试验中公认的做法，ICH E9 指导原则和 FDA 关于适应性设计的指南（2019）中均有描述。本库负责计算设计，并为每次分析保留可审计、可恢复的记录（检查点及其历史摘要）。它不是监管意义上经过验证的软件：在申报中使用它的申办方必须像对待其他任何工具一样对其进行验证。

更多内容：[教程：成组序贯试验](../../tutorials/group-sequential.md)，其中将数值与 rpact 进行了比较；
[参考：设计与规划](../../reference/design.md)。
