---
description: sequential-analysis 与其他用于序贯检验、A/B 测试、成组序贯设计、变化检测和滤波的 Python 及 R 库（statsmodels、scipy、confseq、rpact、gsDesign、safestats、ruptures、filterpy、arch、hmmlearn）的比较，以及各自的适用场景。
language: zh
---

# 它与其他库相比如何？

> 本页译自[英文原文](../../guide/comparison.md)，尚未经母语人士审校；如两者有出入，以英文页面为准。

**简短回答。** 大多数库只把一类方法做得很好。sequential-analysis 则将序贯推断（sequential inference）的主要几类方法统一在同一个接口之下：

* SPRT 与最优方案；
* 成组序贯设计（group sequential design）；
* 随时有效（anytime-valid）检验与置信序列（confidence sequence）；
* 变化检测；
* 状态空间滤波器。

除方法本身之外，它还提供：

* 每个方法都声明其保证（`exact`、`asymptotic`、`model`、
  ……）；
* 每次运行都可以保存检查点并逐位（bit for bit）精确恢复；
* 数据格式有正式规范，并由第二个 TypeScript 实现执行；
* 没有必需的依赖。

如果你只需要下面其中一种方法，并且已经在使用专门做这件事的库，请继续使用那个库。下表说明了每种工具在哪些场景下是自然之选。各库的描述针对其主要用途，截至 2026 年 10 月，并非其功能的完整列表。

| 需求 | 自然之选 | sequential-analysis 提供的内容 |
|---|---|---|
| 固定样本量检验、回归、检验效能 | scipy.stats、statsmodels | 不是它的用途 |
| 用于监管申报的成组序贯设计 | rpact、gsDesign（R） | 相同的设计，在其测试套件中与 rpact 核对；可带检查点逐步执行试验 |
| 置信序列、e 值 | confseq（Python）、safestats（R） | 均值、分位数、回归系数、两样本效应的置信序列；用于多重检验的 e-BH 和 e-LOND |
| 带用户界面的 A/B 测试平台 | GrowthBook、Statsig、Eppo、Optimizely（平台） | 可嵌入的引擎：转化率、有界指标和率指标的精确检验，SRM，跨指标的 FDR 控制 |
| 对已完成序列的离线变点分割 | ruptures（Python）、changepoint（R） | 数据到达时的在线检测：CUSUM、Shiryaev–Roberts、e 检测器、贝叶斯在线变点 |
| 卡尔曼滤波 | filterpy、statsmodels 状态空间 | 卡尔曼、稳健卡尔曼、粒子滤波和 HMM 滤波，支持平滑和检查点 |
| GARCH | arch | GARCH(1,1) 和 GJR，拟合至与 arch 相同的似然极大值（已在测试中核对），随后在线运行 |
| 隐马尔可夫模型 | hmmlearn | 在线滤波，与 hmmlearn 一致的 Baum–Welch，在线 EM |
| 预测 | statsmodels 等 | 与 statsmodels 一致的 ETS 和 AR 预测，在线学习，附带共形区间（conformal intervals） |

## 其他工具更合适的情况

* **向监管机构申报。** rpact 在这方面被广泛使用，其开发者提供验证文档。sequential-analysis 在其覆盖的设计上与 rpact 一致，但申办方仍需自行对其进行验证。
* **基于数组的大规模离线分析。** 基于 numpy 的库在每个观测上的速度更快。sequential-analysis 是为逐个观测处理而构建的；各方法的开销见[速度](../../performance.md)。
* **它尚未提供的方法。** 目前还没有两样本中位数检验、多元 Hawkes 过程以及带移动平均项的 ARIMA 模型。新增内容见[更新日志](../../changelog.md)。
