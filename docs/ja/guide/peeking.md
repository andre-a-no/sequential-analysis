---
description: A/B テストや臨床試験で p 値を毎日確認すると偽陽性が増える理由（のぞき見の問題）と、それを解決する逐次手法の 3 つのファミリーを、Python と sequential-analysis で示す。
language: ja
---

# なぜ p 値を毎日見てはいけないのか？

> このページは[英語版](../../guide/peeking.md)の翻訳です。ネイティブスピーカーによるレビューはまだ受けていません。両者が異なる場合は英語版が優先されます。

**短い答え。** 固定標本サイズの検定が偽陽性率 5% を約束するのは、計画したサンプルサイズで結果を 1 回だけ見る場合に限られます。繰り返し見て、初めて p < 0.05 になった時点で止めると、だまされる機会を何度も得ることになります。20 回見ると、偽陽性率は約 25% に上がります。逐次手法は、繰り返し見ることを前提に作られています。逐次手法を使えば、何度見ても、いつ止めても、偽陽性率は 5% 以下に保たれます。

## のぞき見の問題を測ってみる

コンバージョン率がともに 10% の 2 群（A/A テスト）、ユーザー 2,000 人、200 回の繰り返し。「のぞき見」（peeking）では、100 人ごとに通常の 2 標本の割合の z 検定を行い、最初に p < 0.05 になった時点で止めます。逐次的な `TwoProportionTest` は、ユーザー 1 人ごとに確認します。

```python
import math
import random

from sequential_analysis.procedures import TwoProportionTest

def a_a_test(seed, users=2000):
    """Alternating arms, both converting 10% of the time: any 'effect' is a false positive."""
    rnd = random.Random(seed)
    return [(user % 2, int(rnd.random() < 0.10)) for user in range(users)]

def peeking(data, looks):
    """The z-test for two proportions after every len(data) / looks users; True if it ever rejects."""
    successes, trials, every = [0, 0], [0, 0], len(data) // looks
    for i, (arm, y) in enumerate(data, start=1):
        successes[arm] += y
        trials[arm] += 1
        if i % every == 0:
            pooled = sum(successes) / sum(trials)
            se = math.sqrt(pooled * (1 - pooled) * (1 / trials[0] + 1 / trials[1]))
            if se > 0 and abs(successes[1] / trials[1] - successes[0] / trials[0]) / se > 1.96:
                return True
    return False

def sequential(data):
    """The anytime-valid test, looked at after every user; True if it ever rejects."""
    test = TwoProportionTest(alpha=0.05)
    state = test.initial_state()
    for arm, y in data:
        state, out = test.step(state, {"arm": arm, "y": y})
        if out.decision is not None:
            return True
    return False

runs = [a_a_test(seed) for seed in range(200)]
print(f"z-test, one look at the end:   {sum(peeking(r, 1) for r in runs) / len(runs):.1%} false positives")
print(f"z-test, 20 looks:              {sum(peeking(r, 20) for r in runs) / len(runs):.1%}")
print(f"TwoProportionTest, 2000 looks: {sum(sequential(r) for r in runs) / len(runs):.1%}")
```

```text
z-test, one look at the end:   4.5% false positives
z-test, 20 looks:              28.0%
TwoProportionTest, 2000 looks: 5.0%
```

1 回だけ見る場合は約束が守られています。20 回見ると誤り率は約 6 倍になります。逐次検定は、2,000 人のユーザーの 1 人ごとに見ても 5% に保ちます。これがその約束です。保証は **exact**（`TwoProportionTest.guarantee == "exact"`）であり、何度見ても、すべてのサンプルサイズで偽陽性率は高々 5% です。200 回の繰り返しで偽陽性が 10 回というのは、正確な 5% から期待されるとおりの結果です。

## 逐次手法の 3 つのファミリー

| ファミリー | 見てよいタイミング | 典型的な用途 | sequential-analysis では |
|---|---|---|---|
| **逐次確率比検定**（sequential probability ratio test、SPRT）（Wald 1945） | 観測のたび | 単純仮説対単純仮説、平均的に最少の観測数：品質管理、シミュレーション、精神物理学 | `SPRT`、`TwoSPRT`、`kiefer_weiss_plan` |
| **群逐次デザイン**（group sequential design）（Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983） | 計画された少数回の中間解析 | データモニタリング委員会を置く臨床試験 | `group_sequential_design`、`GroupSequentialTest`、`GroupSequentialProportions`、`GroupSequentialLogRank` |
| **常時有効な推論**（anytime-valid inference）：e 値、信頼系列、混合 SPRT（Robbins 1970, Howard et al. 2021, Ramdas et al. 2023） | 観測のたび、どんな理由で止めてもよい | オンライン A/B テスト、モニタリングダッシュボード | `TwoProportionTest`、`BoundedABTest`、`NormalMixtureSPRT`、`BettingConfidenceSequence`、`MultipleTests` |

**コスト。** 計画した効果のもとでは、頻繁に見るほど多くのデータが必要になります。

* 4 回の解析を行う群逐次デザインは、1 回の解析より 1〜20% 多くの患者を必要とします。
* 2 つの割合の常時有効な検定は、1 回の解析の 1.3〜1.6 倍のユーザーを必要とします。

その代わり、効果が大きければ実験は早く終わり、誰もサンプルサイズを事前に決める必要がありません。

## これが問題にならない場合

のぞき見が誤りを増やすのは、見た結果によって行動を変える場合だけです。ダッシュボードを見ても、常に計画したサイズまで実験を続けて 1 回だけ検定するなら、固定標本サイズの検定は有効です。その場合は、それが最も効率の良い選択でもあります。

次へ：[A/B テストを途中で止める](ab-testing.md)、
[信頼系列](confidence-sequences.md)、
[用語集](glossary.md)。
