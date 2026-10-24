---
description: sequential-analysis 用户指南。sequential-analysis 是一个用于序贯检验和随时有效推断的 Python 库。每一页直接回答一个问题，并附有可运行的代码及其输出。
language: zh
---

# 用户指南

> 本页译自[英文原文](../../guide/index.md)，尚未经母语人士审校；如两者有出入，以英文页面为准。

本指南按人们常问的问题组织。每页开头直接给出答案，然后给出一段可按原样运行的简短程序及其输出、答案背后的保证，以及该方法不适用的情形。[教程](../../tutorials/ab-test.md)对每个主题有更深入的介绍。

## 一段话介绍本库

**sequential-analysis** 是一个 Python 库，用于对逐个到达的观测数据进行统计推断。它的检验、置信区间和检测器可以在每次观测后查看，并可在任意时刻停止，而其错误率依然成立。它涵盖：

* Wald 的 SPRT 与最优序贯方案；
* 用于临床试验的成组序贯设计（group sequential design）（O'Brien–Fleming 和 Pocock 消耗，无效性界值）；
* 基于 e 值（e-value）和置信序列（confidence sequence）的随时有效（anytime-valid）A/B 检验；
* 变点检测；
* 卡尔曼滤波、粒子滤波和隐马尔可夫滤波；
* 预测与 GARCH 波动率。

每次运行都可以保存为 JSON 检查点，并在 Python 中逐位精确恢复，或在其 TypeScript 执行器中以相同的决策继续运行。

| | |
|---|---|
| 安装 | `pip install sequential-analysis` |
| 导入 | `import sequential_analysis` |
| Python | 3.8 至 3.14，无必需依赖（numpy 可选） |
| 许可证 | AGPL-3.0，或 Novikov Laboratories LLC 提供的商业许可证 |
| 源代码 | <https://github.com/andre-a-no/sequential-analysis> |
| 文档 | <https://andre-a-no.github.io/sequential-analysis/> |

## 问题

**概念**

* [为什么不能每天查看 p 值？](peeking.md) 偷看问题，以及序贯方法的三大类。
* [术语表](glossary.md)：e 值、置信序列、α 消耗、ARL 等术语及其同义词。

**任务**

* [如何提前停止 A/B 测试而不抬高假阳性率？](ab-testing.md)
* [如何获得在反复查看时仍然有效的置信区间？](confidence-sequences.md)
* [如何在 Python 中运行 Wald 的 SPRT？](sprt.md)
* [如何规划临床试验的期中分析？](clinical-trials.md)
* [如何检测测量数据流中的变化？](change-detection.md)
* [如何在数据流上运行统计并在崩溃后恢复？](streaming.md)

**选择**

* [我的问题该用哪种方法？](../../choosing.md)：完整的对照表。
* [它与其他库相比如何？](comparison.md)
* [常见问题](faq.md)

## 如何理解各类保证

每个方法都有一个 `guarantee` 属性。本指南在每个答案中都会引用它：

* **exact：** 在所述假设下，错误率在每个样本量下都成立。
* **asymptotic：** 近似成立，样本越大越准确。
* **model：** 在所述模型下概率是精确的，但超出该模型不作任何声明。
* **approximate：** 即使在模型下也只是近似。
* **none：** 该程序只对数据进行变换，不作任何声明。
