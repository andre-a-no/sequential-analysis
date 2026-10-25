---
description: 如何在 Python 中检测传感器读数、延迟或业务指标数据流中的变化——使用 CUSUM、Shiryaev–Roberts、非参数 e 检测器和贝叶斯在线变点检测。借助 sequential-analysis，通过平均运行长度（ARL）控制误报。
language: zh
---

# 如何检测测量数据流中的变化？

> 本页译自[英文原文](../../guide/change-detection.md)，尚未经母语人士审校；如两者有出入，以英文页面为准。

**简短回答。** 使用在线变点检测器（change-point detector）。它持续监视数据流，一旦分布看起来发生了变化就立即报警。其误报由**平均运行长度**（average run length，ARL）控制：在没有任何变化时，直到出现一次误报所需观测数的期望值。在 sequential-analysis 中：

| 变化前你已知的信息 | 方法 | 保证（guarantee） |
|---|---|---|
| 变化前后的两个分布（例如正态分布，均值 70 → 71） | `CUSUM`、`ShiryaevRoberts` | exact：ARL ≥ e^threshold |
| 只知道均值，以及取值的上下界 | `MeanEDetector` | 对所有此类分布均为 exact |
| 只知道某个分位数（例如延迟的第 95 百分位数） | `QuantileEDetector` | 对所有分布均为 exact |
| 变化前后参数未知的模型 | `BayesianChangePoint` | 在模型和先验成立时 |

## 均值发生漂移的传感器

某温度传感器读数为 70.0 °C，噪声标准差为 0.5。从第 600 个读数起，均值变为 70.4。阈值取 log(1000) ≈ 6.9 的 CUSUM，其 ARL 至少为 1,000 个读数：

```python
import math
import random

from sequential_analysis.procedures import CUSUM, Gaussian

rnd = random.Random(1)
readings = [rnd.gauss(70.0, 0.5) for _ in range(600)] + [rnd.gauss(70.4, 0.5) for _ in range(400)]

detector = CUSUM(Gaussian(sigma=0.5), theta0=70.0, theta1=70.4, threshold=math.log(1000))
state = detector.initial_state()
for t, x in enumerate(readings, start=1):
    state, out = detector.step(state, {"x": x})
    if out.alarm:
        print(f"alarm at reading {t}, {t - 600} readings after the shift")
        break
```

```text
alarm at reading 615, 15 readings after the shift
```

不到一个标准差的漂移，在任何单个读数中都无法用肉眼察觉。CUSUM 不断累积证据，从而发现它。

## 读数不服从正态分布时

只有当读数服从你提供给 CUSUM 的分布时，它的 ARL 才成立。对于偏态数据（振动幅度、延迟、队列长度），它的误报频率会远高于计划值。e 检测器（e-detector）所需的假设要少得多：

* `MeanEDetector` 需要变化前的均值以及取值的上下界。
* `QuantileEDetector` 只需要变化前的某个分位数。

对于具有该均值或分位数的**所有**分布，它们的 ARL 都至少达到目标值：

```python
from sequential_analysis.procedures import QuantileEDetector

rnd = random.Random(2)
vibration = [rnd.lognormvariate(0.0, 0.8) for _ in range(800)] + [rnd.lognormvariate(0.5, 0.8) for _ in range(400)]
q95 = math.exp(0.8 * 1.6449)          # the 95th percentile before the change
p95 = QuantileEDetector(q0=q95, p=0.95, arl=1000, direction="increase", statistic="cusum")
state = p95.initial_state()
for t, x in enumerate(vibration, start=1):
    state, out = p95.step(state, {"x": x})
    if out.alarm:
        print(f"the 95th percentile rose: alarm at reading {t}, {t - 800} readings after the change")
        break
```

```text
the 95th percentile rose: alarm at reading 887, 87 readings after the change
```

实践中，变化前的分位数通过一段平稳时期估计。此时保证近似成立，这段时期越长，近似越好。

## 如何选择 ARL

ARL 在误报和检测延迟之间进行权衡。若每分钟一个读数，1,000 个读数的 ARL 意味着每个传感器在正常运行中大约每 17 小时出现一次误报。50 个传感器则约为每天 70 次。应根据所有传感器合计每天能承受的误报次数来选择 ARL：在本例中，将 ARL 设为 1,000,000 个读数，可使 50 个传感器降至大约每两周一次误报。这样做的代价比看起来要小，因为检测延迟只随 ARL 的对数增长。对于 CUSUM，阈值从 6.9 变为 13.8，延迟大约翻倍。

这些检测器是监控工具，而不是安全系统。不要用它们替代经过认证的安全仪表系统。

更多内容：[教程：过程监控与变化检测](../../tutorials/monitoring.md)、
[用隐马尔可夫模型刻画状态切换](../../tutorials/regimes.md)、
[参考：变化检测](../../reference/detection.md)。
