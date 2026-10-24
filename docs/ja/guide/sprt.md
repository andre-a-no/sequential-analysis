---
description: sequential-analysis を使って Python で Wald の逐次確率比検定（SPRT）を実行する方法。誤り率、固定標本サイズの検定と比べた平均サンプルサイズ、および打ち切り型の代替手法（2-SPRT、Kiefer–Weiss 最適プラン）。
language: ja
---

# Python で Wald の SPRT を実行するには？

> このページは[英語版](../../guide/sprt.md)の翻訳です。ネイティブスピーカーによるレビューはまだ受けていません。両者が異なる場合は英語版が優先されます。

**短い答え。** `sequential_analysis.procedures` の `SPRT(family, theta0, theta1, alpha, beta)` は、Wald の逐次確率比検定（sequential probability ratio test、SPRT）を実装しています。これは 2 つの単純仮説のどちらかを、平均的に最少の観測数で判定します。観測を 1 つずつ入力し、最初の判定で止めます。下の例では、同じ誤り率をもつ固定標本サイズの検定の約半分の観測数で済みます。133 個の代わりに平均 65〜76 個です。最大サンプルサイズの保証が必要な場合は、代わりに `TwoSPRT` か `kiefer_weiss_plan` によるプランを使ってください。

## 例：不良率は 10% か 20% か？

ロットは不良率が 10% なら合格、20% なら不合格とし、両方の誤り率を 5% とします。

```python
import random

from sequential_analysis.procedures import SPRT, Bernoulli

test = SPRT(Bernoulli(), theta0=0.10, theta1=0.20, alpha=0.05, beta=0.05)

def inspect_items(rate, seed):
    """Inspect items until the test decides; returns (decision, items inspected)."""
    rnd = random.Random(seed)
    state = test.initial_state()
    while state.decision is None:
        state, out = test.step(state, {"x": int(rnd.random() < rate)})
    return state.decision, state.n

decision, n = inspect_items(0.10, seed=1)
print(f"a good batch: {decision} after {n} items")
```

```text
a good batch: accept_h0 after 108 items
```

多数のロットでの性能はどうでしょうか？

```python
for rate in (0.10, 0.20):
    results = [inspect_items(rate, seed) for seed in range(2000)]
    wrong = sum(d == ("reject_h0" if rate == 0.10 else "accept_h0") for d, _ in results) / len(results)
    average = sum(n for _, n in results) / len(results)
    longest = max(n for _, n in results)
    print(f"defect rate {rate:.0%}: wrong decision {wrong:.1%}, average {average:.0f} items, longest {longest}")
```

```text
defect rate 10%: wrong decision 3.5%, average 76 items, longest 370
defect rate 20%: wrong decision 4.3%, average 65 items, longest 315
```

同じ誤り率をもつ固定標本サイズの検定は、どのロットでも約 133 個を検査します（正規近似）。SPRT は平均で 43〜51% 少ない検査で済みます。ただし、そのサンプルサイズは確率的で上限がなく、平均よりはるかに長くかかるロットもわずかにあります。

閾値は Wald のもので、log((1 − β)/α) と log(β/(1 − α)) です。これらは、停止時のサンプルサイズにかかわらず、実際の誤り率 α′ と β′ が α′ ≤ α/(1 − β)、β′ ≤ β/(1 − α)、α′ + β′ ≤ α + β を満たすことを保証します。尤度比は停止時に閾値を超えて行き過ぎる（overshoot）ため、実際の誤り率は、この例のように名目値を下回ります。これが `SPRT.guarantee == "exact"` の意味です。上限ではなく正確に計算された誤り率が必要な場合は、プランに対して `operating_characteristic` を使います（後述）。

## 最大サンプルサイズが必要な場合

* `TwoSPRT`（Lorden の 2-SPRT）は固定のホライズンまでに停止し、最悪の場合の期待サンプルサイズをほぼ最小にします。
* `sequential_analysis.design` の `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)` は、後ろ向き帰納法により、最大サンプルサイズをもつ最適プランを計算します。`PlanTest` がそれを実行し、`operating_characteristic` はシミュレーションなしでその正確な誤り率と期待サンプルサイズを与えます。
  `examples/07_design_kiefer_weiss.py` を参照してください。
* 観測ごとではなく、計画した数回だけ確認したい場合は、[群逐次デザイン](clinical-trials.md)を使います。

## SPRT が適さない場合

* **仮説が単純仮説でない。** 「率は 10%」対「率はそれ以外の任意の値」は複合対立仮説です。すべての対立仮説に対して常時有効（anytime-valid）な、混合 SPRT（`NormalMixtureSPRT`、`TMixtureSPRT`）またはベッティングによる検定（`BettingMeanTest`）を使ってください。
* **真の値が θ₀ と θ₁ の間にある。** このとき SPRT は最も遅くなり、期待サンプルサイズが固定標本サイズを上回ることがあります。Kiefer–Weiss プランはまさにこの場合のために作られています。

尤度比に基づく手続きで使える分布族：`Gaussian`（分散既知）、`Bernoulli`、`Poisson`、`Exponential`。
