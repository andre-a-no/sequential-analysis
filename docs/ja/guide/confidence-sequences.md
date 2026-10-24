---
description: 信頼系列は、すべてのサンプルサイズで同時に有効な信頼区間であり、継続的にモニタリングできる。有界な平均、中央値や分位点、裾の重い分布の平均について、Python と sequential-analysis で信頼系列を計算する方法。
language: ja
---

# 何度見ても有効なままの信頼区間を得るには？

> このページは[英語版](../../guide/confidence-sequences.md)の翻訳です。ネイティブスピーカーによるレビューはまだ受けていません。両者が異なる場合は英語版が優先されます。

**短い答え。** **信頼系列**（confidence sequence）を使います。これは観測ごとに 1 つずつ得られる区間の列で、少なくとも 95% の確率で、すべてのサンプルサイズにおいて同時に真の値を含みます。それを見続け、十分に狭くなったとき、あるいは 0 を含まなくなったときに止め、止めた時点の区間を報告してかまいません。通常の 95% 信頼区間が 95% を約束するのは、事前に固定した 1 つのサンプルサイズにおいてだけです。

| 推定するもの | 仮定 | 手続き | 保証（guarantee） |
|---|---|---|---|
| 有界なデータの平均（率、スコア、上限を設けた売上） | 値が `[lower, upper]` の範囲内 | `BettingConfidenceSequence` | exact |
| 中央値、90 パーセンタイル、任意の分位点 | なし | `QuantileConfidenceSequence` | exact |
| 裾が重い、または外れ値を含むデータの平均 | 標準偏差の上限 | `CatoniConfidenceSequence` | exact |
| 分散未知の正規データの平均 | 正規性 | `TMixtureSPRT`（`lower`、`upper`） | 正規性のもとで exact |
| 任意のデータの平均、長い実行 | 有限分散 | `AsymptoticConfidenceSequence` | asymptotic |
| 2 群間の差 | [A/B テスト](ab-testing.md)を参照 | `BoundedABTest`、`ABTest` | exact / asymptotic |

## 通常の区間は見続けると破綻する

平均 0.3 の 0/1 変数を 500 個観測し、30 個目以降、観測のたびに教科書どおりの 95% 区間（平均 ± 1.96 標準誤差）を計算します。100 回の実行のうち、ある時点で区間が真の平均を外すのは何回でしょうか？

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

その「95%」は、事前に固定したサンプルサイズでしか成り立ちません。同じデータに対するベッティング（betting）による信頼系列（Waudby-Smith and Ramdas 2024）は、構成上、ある n で外れる実行の割合が高々 5% です。

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

## レイテンシの中央値を、仮定なしで

レイテンシは歪んでいて裾が重いため、平均 ± 標準誤差の区間は信頼できません。`QuantileConfidenceSequence` は、タイ（同順位）を含め、任意の分布の任意の分位点をカバーします。

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

真の値は 120 ms と 258.8 ms です。どちらの区間も、2,000 個のすべてのサンプルサイズで同時に成り立ちます。

## 落とし穴

* **上下限と上限設定は仮定の一部である。** `lower` と `upper` はデータを見る前に選んでください。範囲外の値は拒否されます。
* **任意の非有界なデータの平均に対して正確な被覆を与える方法は存在しない。** そのようなデータには、分位点を使う、値に上限を設ける、標準偏差の上限を仮定する（Catoni）、あるいは漸近的な信頼系列を受け入れる、のいずれかを選びます。
* **信頼系列は、同じサンプルサイズでの 1 つの区間より広い。** その幅は、すべてのサンプルサイズで同時に有効であることの代償です。

さらに詳しく：[どの手法を選ぶか？](../../choosing.md)、
[リファレンス：常時有効およびノンパラメトリックな手法](../../reference/anytime.md)。
