---
description: Python で A/B テストを偽陽性を増やさずに途中で止める方法。sequential-analysis による、コンバージョン率と有界な売上の常時有効な検定、サンプル比率の不一致（SRM）のチェック、多数の指標にわたる偽発見率の制御。
language: ja
---

# 偽陽性を増やさずに A/B テストを途中で止めるには？

> このページは[英語版](../../guide/ab-testing.md)の翻訳です。ネイティブスピーカーによるレビューはまだ受けていません。両者が異なる場合は英語版が優先されます。

**短い答え。** 常時有効（anytime-valid）な検定を使います。その p 値と信頼区間は何度見ても有効なままなので、結果がはっきりした時点で止めてかまいません。sequential-analysis では次のとおりです。

| 指標 | 手続き | 保証（guarantee） |
|---|---|---|
| コンバージョン率（0/1） | `TwoProportionTest` | exact |
| 任意の有界な指標（上限を設けた売上、割合） | `BoundedABTest` | exact |
| 露出量あたりのイベント数 | `RateRatioTest` | ポアソン計数に対して exact |
| 比率指標（セッションあたり売上） | `RatioABTest` | asymptotic |
| 実験前の共変量を用いた平均（CUPED） | `ABTest` | asymptotic |
| トラフィックは意図どおりに分割されているか？ | `SampleRatioMismatch` | exact |
| 複数の指標や群をまとめて | `MultipleTests`（e-BH） | 偽発見率、exact |

各手続きにはユーザーを 1 人ずつ入力します：`state, out = test.step(state, {...})`。
`out.decision` に基づいて、いつ行動してもかまいません。

## コンバージョン：データが決定的になったら止める

対照群のコンバージョン率は 10%、処置群は 12% です。ユーザーが 1 人増えるたびに検定を確認し、最初に判定が出た時点で止めます。

```python
import random

from sequential_analysis.procedures import TwoProportionTest

def users(n, rates=(0.10, 0.12), seed=1):
    """(arm, converted) per user; arm 1 is the treatment."""
    rnd = random.Random(seed)
    for _ in range(n):
        arm = int(rnd.random() < 0.5)
        yield arm, int(rnd.random() < rates[arm])

test = TwoProportionTest(alpha=0.05)
state = test.initial_state()
for arm, converted in users(60_000):
    state, out = test.step(state, {"arm": arm, "y": converted})
    if out.decision is not None:
        break
print(f"stopped after {out.n} users: conversion {out.rates[0]:.4f} (treatment) vs {out.rates[1]:.4f}, "
      f"anytime-valid p = {out.p_value:.4f}, decision: {out.decision}")
```

```text
stopped after 16469 users: conversion 0.1259 (treatment) vs 0.1068, anytime-valid p = 0.0496, decision: reject_h0
```

比較のために言えば、この上昇を検出力（power）80% で検出する固定標本サイズの検定には、群あたり約 3,850 人、合計 7,700 人が必要で、結果を読めるのは最後の 1 回だけです。常時有効な検定はその自由の代償を払います。同じ検出力に達するには 1 回だけの解析の 1.3〜1.6 倍のユーザーが必要で、今回の実行ではそれ以上かかりました。その代わり、サンプルサイズを事前に決める必要はなく、結果を毎日見て、はっきりした時点ですぐに止められます。効果が計画より大きければ、それはずっと早く起こります。

## 売上：有界な指標に対する正確な区間

`BoundedABTest` に必要なのは指標の上下限だけです。テスト前に決めた値（ここでは 30）で売上に上限を設けると、平均の差に対する信頼系列（confidence sequence）はどんな分布に対しても正確（exact）になります。

```python
from sequential_analysis.procedures import BoundedABTest

rnd = random.Random(2)
revenue = BoundedABTest(lower=0.0, upper=30.0, allocation=0.5, input="revenue", grid=300)
state = revenue.initial_state()
for _ in range(20_000):
    arm = int(rnd.random() < 0.5)
    spend = min(rnd.expovariate(1 / (5.0 if arm == 0 else 5.6)), 30.0)   # capped at 30
    state, out = revenue.step(state, {"arm": arm, "revenue": spend})
print(f"after {out.n} users: mean revenue {out.means[0]:.2f} (treatment) vs {out.means[1]:.2f}, "
      f"95% confidence sequence for the difference [{out.lower:.2f}, {out.upper:.2f}]")
```

```text
after 20000 users: mean revenue 5.47 (treatment) vs 4.99, 95% confidence sequence for the difference [-0.30, 1.30]
```

この区間は最後の時点だけでなく、20,000 回の確認のすべてで同時に成り立ちます。ここではまだ 0 を含んでいます。これほどノイズの大きい指標では、20,000 人では約 0.5 の上昇を確認するのに足りないため、実験は続きます。

## まずトラフィックの分割を確認する

サンプル比率の不一致（sample ratio mismatch、SRM）とは、割り付けやログ記録のバグなどにより、実際の分割が設定と異なることを指します。そのような実験から得られた効果の推定値は信頼できません。50/50 から 52/48 へのずれは、実験の実行中に検出されます。

```python
from sequential_analysis.procedures import SampleRatioMismatch

srm = SampleRatioMismatch(weights=(0.5, 0.5), alpha=0.001)
state = srm.initial_state()
rnd = random.Random(3)
for _ in range(50_000):
    state, out = srm.step(state, {"arm": int(rnd.random() < 0.52)})
    if out.decision is not None:
        break
print(f"mismatch detected after {out.n} users: split {out.proportions[0]:.3f} / {out.proportions[1]:.3f}")
```

```text
mismatch detected after 4927 users: split 0.470 / 0.530
```

## 多数の指標を同時に

独立な 10 個の指標をそれぞれ 5% で検定すると、少なくとも 1 つの偽発見が生じる確率は約 40% になります。`MultipleTests` はすべての検定の e 値（e-value）を e-BH 法で統合するため、偽発見率（false discovery rate、FDR）は任意の停止時点で `alpha` に保たれます。

```python
from sequential_analysis.procedures import MultipleTests

metrics = MultipleTests({
    "conversion": TwoProportionTest(input="converted"),
    "revenue": BoundedABTest(lower=0.0, upper=30.0, input="revenue", grid=100),
    "traffic split": SampleRatioMismatch((0.5, 0.5)),
}, alpha=0.05)
state = metrics.initial_state()
rnd = random.Random(4)
for _ in range(15_000):
    arm = int(rnd.random() < 0.5)
    converted = int(rnd.random() < (0.10, 0.13)[arm])
    spend = min(rnd.expovariate(1 / 5.0), 30.0)                          # no effect on revenue
    state, out = metrics.step(state, {"arm": arm, "converted": converted, "revenue": spend})
print("discoveries:", out.rejected)
```

```text
discoveries: ('conversion',)
```

## 落とし穴

* **解析する単位で無作為化する。** ユーザー単位で無作為化しているなら、ページビューごとではなくユーザーごとに 1 レコードを入力します。セッション単位の指標には、ユーザーごとの合計で動作する `RatioABTest` を使います。
* **有界な指標の上限はテスト前に決める。** データを見てから選ぶと保証が失われます。
* **漸近的な手続きには大きな標本が必要。** `ABTest` と `RatioABTest` では、区間は長い実行で近似的に有効なだけです。適用できる場合は正確な手続きを優先してください。
* **適応的なトラフィック配分**（バンディット）には、分割が結果に依存しても有効なままの検定が必要です：
  `TwoProportionTest(method="universal")` または
  `BoundedABTest(propensity_input=...)`。
  [チュートリアル §10](../../tutorials/ab-test.md) を参照してください。

さらに詳しく：[A/B テストのチュートリアル](../../tutorials/ab-test.md)（CUPED、比率指標、レート、期間の計画）と
[一連の実験の運用](../../tutorials/experiment-programme.md)（多数の実験にわたる偽発見率）。
