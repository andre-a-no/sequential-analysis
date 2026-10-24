---
description: Python で臨床試験の中間解析を計画・実施する方法。群逐次デザイン（O'Brien–Fleming、Pocock、Lan–DeMets のα消費、無益性境界）と、平均・割合・生存時間のサンプルサイズを rpact と照合済みで計算する。sequential-analysis を使用。
language: ja
---

# 臨床試験の中間解析を計画するには？

> このページは[英語版](../../guide/clinical-trials.md)の翻訳です。ネイティブスピーカーによるレビューはまだ受けていません。両者が異なる場合は英語版が優先されます。

**短い答え。** 群逐次デザイン（group sequential design）を使います。
`sequential_analysis.group_sequential` の
`group_sequential_design(alpha, fractions, spending=...)` は次のものを計算します。

* 有効性境界（efficacy boundaries）。Lan–DeMets のα消費（alpha spending）による（O'Brien–Fleming 型、Pocock 型など）
* 非拘束的な無益性境界（non-binding futility boundaries）
* 検出力（power）と期待サンプルサイズ
* 平均と割合に対する最大サンプルサイズ、または生存時間に対するイベント数。

境界とサンプルサイズは R パッケージ rpact と一致します。その後、検定手続き（`GroupSequentialTest`、`GroupSequentialTwoMeans`、`GroupSequentialProportions`、`GroupSequentialLogRank`）が、患者ごと、あるいはイベントごとに試験を実行します。各中間解析（interim analysis）は、その情報分率（information fraction）に達した時点で行われます。

## デザイン：4 回の解析、O'Brien–Fleming 型の消費

片側 α = 0.025、患者の 25%、50%、75%、100% の時点で解析、検出力 90%、無益性境界あり：

```python
from sequential_analysis.group_sequential import group_sequential_design

design = group_sequential_design(0.025, [0.25, 0.5, 0.75, 1.0], spending="obrien-fleming",
                                 futility="obrien-fleming", power=0.9)
for k, (t, b, f) in enumerate(zip(design.fractions, design.bounds, design.futility), start=1):
    print(f"analysis {k} at {t:.0%}: efficacy if Z >= {b:.3f}, futility if Z <= {f:.3f}")
print("patients for an effect of 0.3 standard deviations:", design.max_sample_size(effect=0.3, sigma=1.0))
print(f"expected share of the patients used: {design.expected_fraction(0.0):.2f} with no effect, "
      f"{design.expected_fraction(design.drift):.2f} with the planned effect")
```

```text
analysis 1 at 25%: efficacy if Z >= 4.333, futility if Z <= -1.403
analysis 2 at 50%: efficacy if Z >= 2.963, futility if Z <= 0.325
analysis 3 at 75%: efficacy if Z >= 2.359, futility if Z <= 1.291
analysis 4 at 100%: efficacy if Z >= 2.014, futility if Z <= 2.014
patients for an effect of 0.3 standard deviations: 127
expected share of the patients used: 0.59 with no effect, 0.73 with the planned effect
```

## 二値エンドポイントと生存時間エンドポイント

```python
binary = group_sequential_design(0.025, [1 / 3, 2 / 3, 1.0], spending="obrien-fleming")
print("patients, response 10% vs 12%, 80% power:",
      binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8))
print("events for a hazard ratio of 0.7, 80% power:", binary.max_events(hazard_ratio=0.7, power=0.8))
print(f"inflation factor over a single analysis: {binary.inflation_factor(0.8):.3f}")
```

```text
patients, response 10% vs 12%, 80% power: 7780
events for a hazard ratio of 0.7, 80% power: 250
inflation factor over a single analysis: 1.013
```

O'Brien–Fleming 型の消費では、3 回の解析に必要な患者数は 1 回の最終解析より 1.3% 多いだけです。

## 試験の実施

```python
import random

from sequential_analysis.procedures import GroupSequentialProportions

n_max = binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8)
test = GroupSequentialProportions.from_design(binary, n_max)
state, rnd = test.initial_state(), random.Random(3)
for patient in range(n_max):
    arm = patient % 2                                         # 1 treatment, 0 control
    state, out = test.step(state, {"arm": arm, "y": int(rnd.random() < (0.12 if arm else 0.10))})
    if out.analysis:
        print(f"analysis {out.analysis} after {out.n} patients: Z = {out.z:.2f}, bound {out.bound:.2f}")
    if out.decision:
        print("decision:", out.decision)
        break
```

```text
analysis 1 after 2594 patients: Z = 2.14, bound 3.71
analysis 2 after 5187 patients: Z = 2.64, bound 2.51
decision: reject_h0
```

試験は 2 回目の解析で、計画した患者の 3 分の 2 の時点で有効性により中止されました。

## 解析が計画どおりに行われない場合

データモニタリング委員会（data monitoring committee）が情報のちょうど 25% の時点で開かれることはまれです。

* `design.at(fractions)` は、実際に到達した情報に対して境界を計算し直します。α消費により全体の有意水準は保たれます。
* `GroupSequentialMonitor` は、自分で計算した任意の統計量（Cox モデル、混合モデル）を、各会合での Z 値とその情報量として受け取ります。

## 患者 1 人ごとに見たい場合は？

群逐次デザインで許されるのは、計画した回数の確認だけです。患者やイベントのたびにモニタリングするには、常時有効（anytime-valid）な手続きを使います。生存時間には `AnytimeLogRankTest`、奏効率には `TwoProportionTest`、平均には `TMixtureSPRT` です。計画した効果のもとでは、これらはより多くの患者を必要とします。[チュートリアル：生存時間の試験](../../tutorials/survival.md)を参照してください。

## 規制上の実務

α消費を用いた群逐次デザインは検証的試験で確立された方法であり、ICH E9 ガイドラインと FDA の適応的デザインに関するガイダンス（2019）に記載されています。このライブラリはデザインを計算し、各解析について監査可能で再開可能な記録（チェックポイントとその履歴ダイジェスト）を保持します。規制上の意味でバリデーションされたソフトウェアではありません。申請に使用する治験依頼者（sponsor）は、他のツールと同様にバリデーションを行う必要があります。

さらに詳しく：[チュートリアル：群逐次試験](../../tutorials/group-sequential.md)（数値を rpact と比較しています）、
[リファレンス：デザインと計画](../../reference/design.md)。
