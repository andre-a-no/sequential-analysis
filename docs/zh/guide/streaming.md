---
description: 如何在数据流（Kafka、SQL、pandas、传感器）上运行序贯统计，并在崩溃后从中断处精确恢复。使用 sequential-analysis 实现 JSON 检查点、去重投递、用于审计的历史摘要，以及在 Python 或 TypeScript 中继续同一次运行。
language: zh
---

# 如何在数据流上运行统计并在崩溃后恢复？

> 本页译自[英文原文](../../guide/streaming.md)，尚未经母语人士审校；如两者有出入，以英文页面为准。

**简短回答。** 将方法包装在 `Run` 中。然后：

1. 用 `run_sync`（或在有并发生产者时用 `run_async`）向它输入观测。
2. 随时保存 `run.checkpoint()`，频率不限。它是一个普通的 JSON 值，包含状态、随机数状态、数据源位置以及历史的 SHA-256 摘要。
3. 崩溃后，`Run.restore(procedure, checkpoint)` 会精确地逐位继续运行。使用 `Delivery("sequence")` 时，重启后被重复投递的观测会作为重复项丢弃。
4. TypeScript 执行器可以在 JavaScript 中接续同一个检查点。它给出相同的决策和历史摘要，数值一致到最后几位：在 108 个一致性测试用例中有 34 个完全相同，其余的相对误差在 6·10⁻¹³ 以内。

## 崩溃、重启、重放：结果相同

一次针对 300 个读数的监控运行在第 120 个读数后中断。数据源从第 100 个读数开始重放，这正是消息队列在重启后的典型行为。恢复后的运行丢弃它已经见过的 20 个读数，并精确地结束于未中断运行应结束的位置：

```python
import json
import random

from sequential_analysis import Delivery, Observation, Run, run_sync
from sequential_analysis.procedures import BettingConfidenceSequence

rnd = random.Random(5)
readings = [Observation("x", rnd.betavariate(2, 5), seq=i, source="sensor-7") for i in range(300)]

def procedure():
    return BettingConfidenceSequence(lower=0.0, upper=1.0, grid=200)

run = Run(procedure(), delivery=Delivery("sequence"), run_id="sensor-7")
run_sync(run, readings[:120])
saved = json.dumps(run.checkpoint())        # to a file, a database, object storage
del run                                     # the process dies

run = Run.restore(procedure(), json.loads(saved), delivery=Delivery("sequence"))
run_sync(run, readings[100:])               # the source replays from reading 100
print(f"resumed run: {run.t} readings, {run.delivery.duplicates} duplicates dropped")

uninterrupted = Run(procedure(), delivery=Delivery("sequence"), run_id="sensor-7")
run_sync(uninterrupted, readings)
print("same state as an uninterrupted run:", run.state == uninterrupted.state)
print("same history digest:", run.checkpoint()["history_digest"] == uninterrupted.checkpoint()["history_digest"])
print(f"checkpoint size: {len(saved)} bytes")
```

```text
resumed run: 300 readings, 20 duplicates dropped
same state as an uninterrupted run: True
same history digest: True
checkpoint size: 9606 bytes
```

历史摘要（history digest）是对运行所使用的每个观测计算的哈希链。具有相同摘要的两次运行，以相同的顺序看到了相同的数据。审计人员可以按照[规范](../../spec.md)，从观测日志中重新计算它。

## 观测数据从哪里来

| 数据源 | 函数 |
|---|---|
| 值的列表或生成器 | `sources.from_values` |
| CSV 文件 | `sources.from_csv` |
| pandas 或 polars DataFrame | `adapters.from_dataframe` |
| SQL 查询（任意 DB-API 连接） | `adapters.from_sql` |
| Kafka 消息，带已提交的偏移量 | `adapters.from_kafka`、`adapters.kafka_offsets` |
| 同时使用多个数据源 | `sources.interleave`、`sources.merge_ordered` |
| 已记录的观测日志 | `sources.replay` |

来自不同数据源的输入通过**拓扑**（topology）关联起来。`KeyJoin` 按用户将分组与结果连接起来，`TimeAlign` 在时间上对齐两个传感器，`AsOfJoin` 将事件附加到当时已知这些事件的时间条（bar）上。参见[数据源](../../adapters.md)。

## 方法发生变化时

检查点记录了方法的名称、版本和配置。
对于由不同方法、不同配置或算术不同的版本生成的检查点，`Run.restore` 会拒绝并抛出 `IncompatibleCheckpoint`。因此，一次运行绝不会在不知不觉中以不同的数值继续下去。

更多内容：[检查点、日志与后端](../../checkpoints.md)、
[TypeScript 执行器](../../typescript.md)、
[格式规范](../../spec.md)。
