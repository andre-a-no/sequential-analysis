---
description: Python でセンサーの測定値、レイテンシ、メトリクスのストリームにおける変化を検出する方法。CUSUM、Shiryaev–Roberts、ノンパラメトリックな e 検出器、ベイズ型オンライン変化点検出を用い、誤警報を平均ランレングス（ARL）で制御する。sequential-analysis を使用。
language: ja
---

# 測定値のストリームで変化を検出するには？

> このページは[英語版](../../guide/change-detection.md)の翻訳です。ネイティブスピーカーによるレビューはまだ受けていません。両者が異なる場合は英語版が優先されます。

**短い答え。** オンラインの変化点検出器（change-point detector）を使います。検出器はストリームを監視し、分布が変化したように見えた時点ですぐに警報を出します。誤警報は**平均ランレングス**（average run length、ARL）で制御されます。これは、何も変化していないときに誤警報が出るまでの観測数の期待値です。sequential-analysis では次のとおりです。

| 変化の前にわかっていること | 手続き | 保証（guarantee） |
|---|---|---|
| 変化前後の両方の分布（例：正規分布、平均 70 → 71） | `CUSUM`、`ShiryaevRoberts` | exact：ARL ≥ e^threshold |
| 平均と、値の上下限だけ | `MeanEDetector` | そのようなすべての分布に対して exact |
| ある分位点だけ（例：レイテンシの 95 パーセンタイル） | `QuantileEDetector` | すべての分布に対して exact |
| 変化前後でパラメータが未知のモデル | `BayesianChangePoint` | モデルと事前分布のもとで |

## 平均がずれるセンサー

ある温度センサーは標準偏差 0.5 のノイズを伴って 70.0 °C を示します。600 番目の測定値から、平均は 70.4 になります。閾値 log(1000) ≈ 6.9 の CUSUM の ARL は少なくとも 1,000 測定値です。

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

標準偏差 1 つ分に満たないずれは、個々の測定値を見ても目ではわかりません。CUSUM は証拠を蓄積して、それを見つけ出します。

## 測定値が正規分布に従わない場合

CUSUM の ARL が成り立つのは、測定値が与えた分布に従う場合だけです。歪んだデータ（振動の振幅、レイテンシ、キューの長さ）では、計画よりはるかに頻繁に誤警報を出します。e 検出器（e-detector）が必要とする仮定ははるかに少なくて済みます。

* `MeanEDetector` に必要なのは、変化前の平均と値の上下限です。
* `QuantileEDetector` に必要なのは、変化前のある分位点だけです。

その平均または分位点をもつ**すべての**分布に対して、ARL は少なくとも目標値になります。

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

実際には、変化前の分位点は平穏な期間から推定します。その場合、保証は近似的に成り立ち、その期間が長いほど近似は良くなります。

## ARL の選び方

ARL は誤警報と検出遅れのトレードオフです。1 分に 1 測定値の場合、1,000 測定値の ARL は、通常運転中にセンサー 1 台あたりおよそ 17 時間に 1 回の誤警報を意味します。センサーが 50 台あれば、1 日に約 70 回です。ARL は、すべてのセンサーを合わせて 1 日に許容できる誤警報の回数から選んでください。この例では、ARL を 1,000,000 測定値にすると、50 台のセンサーでおよそ 2 週間に 1 回の誤警報まで下がります。検出遅れは ARL の対数に比例してしか増えないため、そのコストは見かけほど大きくありません。CUSUM では閾値が 6.9 から 13.8 になり、遅れはおおよそ 2 倍になります。

これらの検出器は監視ツールであり、安全システムではありません。認証された安全計装システムの代わりに使わないでください。

さらに詳しく：[チュートリアル：プロセス監視と変化検出](../../tutorials/monitoring.md)、
[隠れマルコフモデルによるレジーム](../../tutorials/regimes.md)、
[リファレンス：変化検出](../../reference/detection.md)。
