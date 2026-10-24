---
description: 逐次検定、A/B テスト、群逐次デザイン、変化検出、フィルタリングのための他の Python・R ライブラリ（statsmodels、scipy、confseq、rpact、gsDesign、safestats、ruptures、filterpy、arch、hmmlearn）と sequential-analysis との比較、およびどれをいつ使うべきか。
language: ja
---

# 他のライブラリと比べてどうか？

> このページは[英語版](../../guide/comparison.md)の翻訳です。ネイティブスピーカーによるレビューはまだ受けていません。両者が異なる場合は英語版が優先されます。

**短い答え。** ほとんどのライブラリは、ある 1 つの手法群をうまくカバーしています。sequential-analysis は、逐次推論（sequential inference）の主要な手法群を 1 つのインターフェースの背後にまとめています。

* SPRT と最適プラン
* 群逐次デザイン（group sequential design）
* 常時有効（anytime-valid）な検定と信頼系列（confidence sequence）
* 変化検出
* 状態空間フィルタ。

手法そのもの以外に加わるもの：

* すべての手続きが自らの保証を明示する（`exact`、`asymptotic`、`model`、
  ...）
* すべての実行はチェックポイントを保存し、ビット単位で完全に再開できる
* フォーマットは仕様化されており、TypeScript による第 2 の実装で実行される
* 必須の依存関係がない。

以下の手法のうち 1 つだけが必要で、それを専門とするライブラリをすでに使っているなら、そのライブラリを使い続けてください。下の表は、それぞれのツールがどこで自然な選択になるかを示しています。説明は各ライブラリの主な目的についてのもので（2026 年 10 月時点）、機能の完全な一覧ではありません。

| 必要なこと | 自然な選択 | sequential-analysis が提供するもの |
|---|---|---|
| 固定標本サイズの検定、回帰、検出力 | scipy.stats、statsmodels | 目的外 |
| 規制当局への申請のための群逐次デザイン | rpact、gsDesign（R） | 同じデザイン。テストスイートで rpact と照合済み。チェックポイント付きで試験を 1 ステップずつ実行 |
| 信頼系列、e 値 | confseq（Python）、safestats（R） | 平均、分位点、回帰係数、2 標本の効果に対する信頼系列。多数の検定のための e-BH と e-LOND |
| UI を備えたプラットフォームとしての A/B テスト | GrowthBook、Statsig、Eppo、Optimizely（プラットフォーム） | 組み込み用のエンジン。コンバージョン、有界指標、レート指標の正確な検定、SRM、指標全体での FDR |
| 完了した系列のオフラインでの変化点セグメンテーション | ruptures（Python）、changepoint（R） | データ到着中のオンライン検出：CUSUM、Shiryaev–Roberts、e 検出器、ベイズ型オンライン変化点 |
| カルマンフィルタ | filterpy、statsmodels の状態空間 | カルマン、ロバストカルマン、粒子フィルタ、HMM フィルタ。平滑化とチェックポイント付き |
| GARCH | arch | GARCH(1,1) と GJR を arch と同じ尤度の最大値まで当てはめ（テストで照合済み）、その後オンラインで実行 |
| 隠れマルコフモデル | hmmlearn | オンラインのフィルタ、hmmlearn と一致する Baum–Welch、オンライン EM |
| 予測 | statsmodels など | statsmodels と一致する ETS と AR の予測。オンラインで学習し、コンフォーマル区間（conformal intervals）付き |

## 他のツールのほうが適している場合

* **規制当局への申請。** rpact はその目的で広く使われており、開発者はバリデーション文書を提供しています。sequential-analysis は対応しているデザインについては rpact と一致しますが、治験依頼者はそれでもバリデーションを行う必要があります。
* **配列に対する大規模なオフライン解析。** numpy ベースのライブラリのほうが観測あたりの処理は高速です。sequential-analysis は観測を 1 つずつ処理するために作られています。各手続きのコストは[速度](../../performance.md)を参照してください。
* **備えていない手法。** 中央値の 2 標本検定、多変量 Hawkes 過程、移動平均項を含む ARIMA モデルはまだありません。追加されたものは[変更履歴](../../changelog.md)を参照してください。
