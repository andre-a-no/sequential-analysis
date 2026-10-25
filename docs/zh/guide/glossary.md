---
description: 序贯分析与随时有效推断术语表——e 值、e 过程、置信序列、始终有效 p 值、mSPRT、α 消耗、信息分数、ARL、SRM、CUPED、e-BH——附同义词以及 sequential-analysis 中实现各概念的方法。
language: zh
---

# 术语表

> 本页译自[英文原文](../../guide/glossary.md)，尚未经母语人士审校；如两者有出入，以英文页面为准。

序贯分析和本库中使用的术语。括号中给出常用的同义词。

**序贯分析**（sequential analysis；sequential testing，序贯检验；sequential inference，序贯推断）。
观测数不事先固定的统计方法。在每个观测或每组观测之后，程序决定停止还是继续。由 Wald（1945）创立。

**偷看**（peeking；optional stopping，可选停止；data peeking；continuous monitoring，持续监测）。
对固定样本量检验反复查看，并在显著时停止。它会抬高假阳性率；参见[偷看问题](peeking.md)。

**SPRT**（sequential probability ratio test，序贯概率比检验；Wald 检验）。它累积两个简单假设的对数似然比，并在其离开某个区间时停止。`SPRT`；截断版本有 `TwoSPRT`（Lorden 的 2-SPRT）和 `kiefer_weiss_plan`。参见 [SPRT](sprt.md)。

**成组序贯设计**（group sequential design；interim analyses，期中分析；group sequential trial，成组序贯试验）。
少数几次计划好的分析，每次都有一个界值。界值的选择使总体第一类错误为 alpha。
`group_sequential_design`。参见[临床试验](clinical-trials.md)。

**α 消耗函数**（alpha spending function；error spending，误差消耗；Lan–DeMets）。它规定在每个信息分数下最多可以用掉多少第一类错误。O'Brien–Fleming 型消耗在早期消耗很少，Pocock 型消耗则均匀消耗。`spending="obrien-fleming"`、`"pocock"`、……

**信息分数**（information fraction）。某次分析时已达到的计划统计信息量（患者数、事件数）的比例。

**无效性界值**（futility boundary；non-binding futility，非约束性无效性）。一个下界：低于它时，建议因缺乏效应而停止。非约束性界值可以被忽略，而不会抬高第一类错误。

**随时有效推断**（anytime-valid inference；always-valid inference，始终有效推断；safe anytime-valid inference，SAVI）。其保证在所有样本量下同时成立的检验和区间，因此可以持续监测，并可出于任何原因停止。

**e 值**（e-value；e-variable，e 变量；betting score，下注得分）。一个非负统计量，其在零假设下的期望至多为 1。大的 e 值是反对零假设的证据：在其超过 1/alpha 时拒绝，第一类错误至多为 alpha。即许多方法的 `log_e_value` 输出。

**e 过程**（e-process；test martingale，检验鞅；test supermartingale，检验上鞅；wealth process，财富过程）。
在停时下仍保持有效的一列 e 值。在零假设下，其累计最大值越过 1/alpha 的概率至多为 alpha（Ville 不等式）。

**始终有效 p 值**（always-valid p-value；anytime-valid p-value，随时有效 p 值；sequential p-value，序贯 p 值）。
在任意停时都有效的 p 值。它是 e 过程累计最大值的倒数。即随时有效方法的 `p_value` 输出。

**置信序列**（confidence sequence；anytime-valid confidence interval，随时有效置信区间；always-valid confidence interval，始终有效置信区间；time-uniform confidence interval，时间一致置信区间）。一列区间，以至少 1 − alpha 的概率在所有样本量下同时包含真值。
`BettingConfidenceSequence`、`QuantileConfidenceSequence`、
`CatoniConfidenceSequence`、`AsymptoticConfidenceSequence`，以及许多检验的 `lower` 和 `upper` 输出。参见[置信序列](confidence-sequences.md)。

**mSPRT**（mixture SPRT，混合 SPRT；Robbins 混合）。备择假设在先验上取平均的 SPRT，这使它对所有备择假设都随时有效。`NormalMixtureSPRT`（方差已知）、`TMixtureSPRT`（方差未知）。

**下注检验**（testing by betting）。把 e 过程构造为一个与零假设对赌的赌徒的财富。`BettingMeanTest`、
`BettingConfidenceSequence`、`KernelTwoSampleTest`。

**GROW**（growth-rate optimal，增长率最优）。在备择假设下使证据的期望对数增长最大化的 e 值。
`TwoProportionTest(method="grow")`。

**通用推断**（universal inference）。由似然比构造的 e 值，其中备择假设仅用过去的数据估计。它在适应性设计下仍然有效。`TwoProportionTest(method="universal")`。

**e-BH**（e-Benjamini–Hochberg）。在任意相依结构下控制多个 e 值的错误发现率。`MultipleTests`、`e_bh`。

**e-LOND，在线 FDR**（online FDR）。对逐个判定的一系列假设进行错误发现率控制。`OnlineFDR`。

**SRM**（sample ratio mismatch，样本比例不匹配）。观测到的各组流量分配与配置不一致，这是实验存在缺陷的信号。`SampleRatioMismatch`。

**CUPED**（controlled experiments using pre-experiment data，利用实验前数据的对照实验；covariate adjustment，协变量调整；regression adjustment，回归调整）。利用实验前测得的协变量降低 A/B 效应的方差。
`ABTest(covariate=True)`、`AnytimeLinearModel`。

**比率指标**（ratio metric；delta method，delta 方法）。由每个用户两个求和量之比构成的指标，例如每次会话收入。`RatioABTest`。

**变点检测**（change-point detection；change detection，变化检测；quickest detection，最快检测；online anomaly detection，在线异常检测）。在数据流的分布发生变化后尽快报警。`CUSUM`、`ShiryaevRoberts`、
`MeanEDetector`、`QuantileEDetector`、`BayesianChangePoint`。参见[变化检测](change-detection.md)。

**ARL**（average run length，平均运行长度；ARL₀；mean time to false alarm，平均误报时间）。在没有任何变化时，直到出现一次误报所需观测数的期望值。变化检测器的误报控制指标。

**e 检测器**（e-detector）。由 e 过程构建的变化检测器，在每个可能的变化时刻启动一个 e 过程。其 ARL 在非参数零假设下有保证。`MeanEDetector`、`QuantileEDetector`。

**Kiefer–Weiss 问题**（Kiefer–Weiss problem）。寻找一个具有最大样本量、并使最大期望样本量最小化的序贯检验。
`kiefer_weiss_plan`。

**操作特征**（operating characteristic）。一个方案的错误概率及样本量分布，作为真实参数的函数。`operating_characteristic`。

**检查点**（checkpoint）。一个 JSON 值，运行可以从它精确地继续。
`Run.checkpoint`、`Run.restore`。参见[数据流](streaming.md)。

**历史摘要**（history digest）。对一次运行已使用的观测计算的 SHA-256 哈希链，保存在每个检查点中，用于审计。

**保证**（guarantee；`exact`、`asymptotic`、`model`、`approximate`、`none`）。
本库中每个方法用来声明其承诺的属性。参见[选择哪种方法？](../../choosing.md)。
