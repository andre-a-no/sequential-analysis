---
description: 逐次検定と常時有効な推論のための Python ライブラリ sequential-analysis のユーザーガイド。各ページは 1 つの質問に直接答え、実行できるコードとその出力を示す。
language: ja
---

# ユーザーガイド

> このページは[英語版](../../guide/index.md)の翻訳です。ネイティブスピーカーによるレビューはまだ受けていません。両者が異なる場合は英語版が優先されます。

このガイドは、よく寄せられる質問ごとに構成されています。各ページはまず直接の答えを示し、続いて書かれたとおりに実行できる短いプログラムとその出力、答えの裏付けとなる保証、そしてその手法が適用できない場合を説明します。各テーマのさらに詳しい内容は[チュートリアル](../../tutorials/ab-test.md)にあります。

## ライブラリの概要

**sequential-analysis** は、観測が 1 つずつ届くデータに対する統計的推論のための Python ライブラリです。その検定、信頼区間、検出器は、観測のたびに確認でき、いつ止めても誤り率は保たれます。カバーする範囲：

* Wald の SPRT と最適な逐次プラン
* 臨床試験のための群逐次デザイン（group sequential design）（O'Brien–Fleming 型と Pocock 型の消費、無益性境界）
* e 値（e-value）と信頼系列（confidence sequence）による常時有効（anytime-valid）な A/B テスト
* 変化点検出
* カルマンフィルタ、粒子フィルタ、隠れマルコフフィルタ
* 予測と GARCH ボラティリティ

すべての実行は JSON としてチェックポイントを保存でき、Python でビット単位で完全に再開するか、TypeScript 実行系で同じ判定のまま続行できます。

| | |
|---|---|
| インストール | `pip install sequential-analysis` |
| インポート | `import sequential_analysis` |
| Python | 3.8〜3.14、必須の依存関係なし（numpy は任意） |
| ライセンス | AGPL-3.0、または Novikov Laboratories LLC の商用ライセンス |
| ソース | <https://github.com/andre-a-no/sequential-analysis> |
| ドキュメント | <https://andre-a-no.github.io/sequential-analysis/> |

## 質問

**概念**

* [なぜ p 値を毎日見てはいけないのか？](peeking.md) のぞき見の問題と、逐次手法の 3 つのファミリー。
* [用語集](glossary.md)：e 値、信頼系列、α消費、ARL などの用語とその同義語。

**タスク**

* [偽陽性を増やさずに A/B テストを途中で止めるには？](ab-testing.md)
* [何度見ても有効なままの信頼区間を得るには？](confidence-sequences.md)
* [Python で Wald の SPRT を実行するには？](sprt.md)
* [臨床試験の中間解析を計画するには？](clinical-trials.md)
* [測定値のストリームで変化を検出するには？](change-detection.md)
* [ストリーム上で統計処理を行い、クラッシュ後に再開するには？](streaming.md)

**選択**

* [自分の問いにはどの手法か？](../../choosing.md)：完全な一覧表。
* [他のライブラリと比べてどうか？](comparison.md)
* [よくある質問](faq.md)

## 保証の読み方

すべての手続きは `guarantee` 属性を持っています。ガイドでは各回答にそれを示します。

* **exact：** 述べられた仮定のもとで、誤り率がすべてのサンプルサイズで成り立つ。
* **asymptotic：** 近似的に成り立ち、標本が大きいほど良くなる。
* **model：** 述べられたモデルのもとで確率は正確だが、それを超えることは何も主張しない。
* **approximate：** モデルのもとでも近似である。
* **none：** 手続きはデータを変換するだけで、何も主張しない。
