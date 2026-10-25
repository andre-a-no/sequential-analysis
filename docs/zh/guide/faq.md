---
description: 关于 sequential-analysis（用于序贯检验和随时有效推断的 Python 库）的常见问题——安装、许可证与商业使用、生产环境中的 A/B 测试、临床试验、检验效能、速度、TypeScript、引用方式。
language: zh
---

# 常见问题

> 本页译自[英文原文](../../guide/faq.md)，尚未经母语人士审校；如两者有出入，以英文页面为准。

## 关于本库

### sequential-analysis 是什么？

一个用于序贯统计推断（sequential statistical inference）的 Python 库。它的检验、置信序列（confidence sequence）和检测器可以在每次观测后查看，并可随时停止，而不会失去其误差保证。它包括：

* SPRT；
* 成组序贯设计（group sequential design）；
* 随时有效（anytime-valid）的 A/B 检验；
* 变点检测器；
* 卡尔曼滤波、粒子滤波和隐马尔可夫滤波；
* 预测与 GARCH。

所有这些都在同一个接口下运行，并使用 JSON 检查点。它由 Novikov Laboratories LLC 开发。

### 如何安装？它依赖什么？

`pip install sequential-analysis`。它需要 Python 3.8 或更高版本（已测试到 3.14），除此之外不需要任何东西。`pip install "sequential-analysis[fast]"` 会为基于数组的方法加装 numpy。只有在调用适配器或绘图函数时，才会用到 pandas、polars、Kafka 客户端和 matplotlib。

### 可以免费商用吗？

本库采用 AGPL-3.0 与商业许可证双重授权。以下用途在 AGPL 下免费：

* 研究与教学；
* 采用 AGPL 或 GPL v3 的开源项目；
* 组织内部使用，不向他人提供副本，也不允许组织外人员通过网络访问。

闭源产品，或不公开源代码的网络服务，需要商业许可证。具体情形以
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)
中的表格为准。许可证咨询：andrei@hobukob.ru。

### 如何引用？

仓库中的 [CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff)
给出了引用信息，GitHub 的 *Cite this repository* 按钮可将其转换为 BibTeX 或 APA 格式。各版本均在 Zenodo 存档并带有 DOI。方法及其验证见[论文](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf)。

## 使用

### 可以在生产环境中用于 A/B 测试吗？

可以，作为统计引擎使用。它为以下对象提供精确检验：

* 转化率（`TwoProportionTest`）；
* 有界指标（`BoundedABTest`）；
* 率（`RateRatioTest`）；
* 流量分配（`SampleRatioMismatch`）；
* 带错误发现率控制的多指标检验（`MultipleTests`）。

在纯 Python 下，转化率检验每个用户约需 10 微秒，分配检查约 4 微秒，率检验约 40 微秒。每个检验的检查点占 2–4 KB。
`BoundedABTest` 维护一个网格，每次需要 0.1–0.5 ms。

本库不是实验平台：分组、事件采集和看板需要你自己构建，或取自某个平台。参见 [A/B 测试](ab-testing.md)。

### 可以每天查看结果吗？

可以，使用随时有效的方法即可：它们正是为此设计的。
使用成组序贯设计时，只在计划好的分析时查看。
使用经典的固定样本量检验时，只查看一次。参见[偷看问题](peeking.md)。

### 随时有效检验的检验效能比固定样本量检验低吗？

在固定样本量检验所计划的效应下，是的。要达到相同的检验效能，随时有效的两比例检验需要 1.3–1.6 倍的用户。作为交换，当效应更大时你可以提前停止，而且无需事先确定样本量。只有几次计划查看的成组序贯设计，比单次分析只多需 1–20%。

### 成组序贯还是随时有效：该用哪个？

* **成组序贯**：分析次数少且事先计划，例如有数据监查委员会或固定的发布周期，尤其适用于确证性临床试验。
* **随时有效**：你想持续查看，或者无法事先确定何时查看或停止。

### 支持贝叶斯 A/B 测试吗？

它的 A/B 检验属于频率学派，对错误率有保证。
在适用的地方提供贝叶斯组件：

* `ThompsonAllocation` 按各组为最优的后验概率分配流量，并带有用于上线决策的期望损失规则；
* `BayesianChangePoint` 用于检测变点；
* 预测器通过贝叶斯更新学习其参数。

### 它在临床试验方面经过验证吗？

它的成组序贯设计（界值、检验效能、样本量、事件数）在测试套件中已与 rpact 和 R 的 survival 包进行了核对。它不是监管意义上经过验证的软件。在申报中使用它的申办方需像对待其他任何工具一样对其进行验证。参见[临床试验](clinical-trials.md)。

### 我的指标是重尾的（收入、延迟），该用什么？

* 对于分位数（中位数、第 90 百分位数），使用 `QuantileTest` 或 `QuantileConfidenceSequence`，它们不需要任何假设。
* 对于均值，在事先固定的水平上对取值封顶，并使用 `BoundedABTest` 或 `BettingConfidenceSequence`（精确）。
* 或者，假设标准差有上界，并使用 `CatoniConfidenceSequence`。

本库目前还没有两样本中位数检验。

### 它有多快？

在纯 Python 下，最简单的方法每个观测需要 1–10 微秒：SPRT、CUSUM、成组序贯检验和混合检验、GARCH。
维护网格或整个样本的方法需要 0.1–10 ms，例如基于下注和 Catoni 的置信序列、核检验以及需要学习的预测器。
[速度](../../performance.md)列出了每个方法的开销和检查点大小。

### 可以在 JavaScript 或浏览器中运行吗？

可以。`ts/` 中的 TypeScript 执行器可以运行这些方法，并接续 Python 的检查点。历史摘要和决策完全相同，数值一致到最后几位。参见 [TypeScript 执行器](../../typescript.md)。

### 运行能在崩溃后恢复吗？

可以。`run.checkpoint()` 是普通的 JSON，`Run.restore` 可以逐位精确地继续运行。重复投递的观测会被丢弃。参见[数据流](streaming.md)。

### 文档中的“exact”和“asymptotic”是什么意思？

每个方法的 `guarantee` 属性声明了它的承诺：

* `exact`：在所述假设下，错误率在每个样本量下都成立；
* `asymptotic`：在长时间运行中近似成立；
* `model`：在所述模型下精确成立；
* `approximate`；
* `none`。

在有适用的精确方法时，文档推荐使用精确方法。参见[选择哪种方法？](../../choosing.md)。
