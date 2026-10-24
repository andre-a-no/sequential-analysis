---
description: 逐次解析と常時有効な推論の用語集。e 値、e 過程、信頼系列、常に有効な p 値、mSPRT、α消費、情報分率、ARL、SRM、CUPED、e-BH など。同義語と、それぞれを実装する sequential-analysis の手続きを併記。
language: ja
---

# 用語集

> このページは[英語版](../../guide/glossary.md)の翻訳です。ネイティブスピーカーによるレビューはまだ受けていません。両者が異なる場合は英語版が優先されます。

逐次解析とこのライブラリで使われる用語です。よく使われる同義語を括弧内に示します。

**逐次解析**（sequential analysis。sequential testing、逐次検定。sequential inference、逐次推論）。
観測数を事前に固定しない統計学。各観測または観測のグループの後に、手続きが停止するか継続するかを決めます。Wald（1945）が創始しました。

**のぞき見**（peeking。optional stopping、任意停止。data peeking。continuous monitoring、継続的モニタリング）。
固定標本サイズの検定を繰り返し確認し、有意になった時点で止めること。偽陽性率を押し上げます。[のぞき見](peeking.md)を参照してください。

**SPRT**（sequential probability ratio test、逐次確率比検定。Wald の検定）。2 つの単純仮説の対数尤度比を累積し、それがある区間を出たときに停止します。`SPRT`。打ち切り版として `TwoSPRT`（Lorden の 2-SPRT）と `kiefer_weiss_plan`。[SPRT](sprt.md) を参照してください。

**群逐次デザイン**（group sequential design。interim analyses、中間解析。group sequential trial、群逐次試験）。
計画された少数回の解析で、それぞれに境界があるもの。境界は、全体の第 1 種の過誤が alpha になるように選ばれます。
`group_sequential_design`。[臨床試験](clinical-trials.md)を参照してください。

**α消費関数**（alpha spending function。error spending、エラー消費。Lan–DeMets）。各情報分率までに第 1 種の過誤をどれだけ使ってよいかを定めます。O'Brien–Fleming 型の消費は初期にはわずかしか消費せず、Pocock 型の消費は均等に消費します。`spending="obrien-fleming"`、`"pocock"`、...

**情報分率**（information fraction）。ある解析の時点で到達した、計画された統計的情報量（患者数、イベント数）の割合。

**無益性境界**（futility boundary。non-binding futility、非拘束的な無益性）。下側の境界で、これを下回ると効果がないとして停止することが推奨されます。非拘束的な境界は、第 1 種の過誤を押し上げることなく無視できます。

**常時有効な推論**（anytime-valid inference。always-valid inference、常に有効な推論。safe anytime-valid inference、SAVI）。保証がすべてのサンプルサイズで同時に成り立つ検定と区間。そのため継続的にモニタリングでき、どんな理由で止めてもかまいません。

**e 値**（e-value。e-variable、e 変数。betting score、ベッティングスコア）。帰無仮説のもとでの期待値が高々 1 である非負の統計量。大きな e 値は帰無仮説に反する証拠です。1/alpha を超えたときに棄却すれば、第 1 種の過誤は高々 alpha です。多くの手続きの出力 `log_e_value`。

**e 過程**（e-process。test martingale、検定マルチンゲール。test supermartingale、検定優マルチンゲール。wealth process、富の過程）。
停止時刻においても有効なままの e 値の列。帰無仮説のもとで、その累積最大値が 1/alpha を超える確率は高々 alpha です（Ville の不等式）。

**常に有効な p 値**（always-valid p-value。anytime-valid p-value、常時有効な p 値。sequential p-value、逐次 p 値）。
任意の停止時刻で有効な p 値。e 過程の累積最大値の逆数です。常時有効な手続きの出力 `p_value`。

**信頼系列**（confidence sequence。anytime-valid confidence interval、常時有効な信頼区間。always-valid confidence interval、常に有効な信頼区間。time-uniform confidence interval、時間一様な信頼区間）。少なくとも 1 − alpha の確率で、すべてのサンプルサイズにおいて同時に真の値を含む区間の列。
`BettingConfidenceSequence`、`QuantileConfidenceSequence`、
`CatoniConfidenceSequence`、`AsymptoticConfidenceSequence`、および多くの検定の出力 `lower` と `upper`。[信頼系列](confidence-sequences.md)を参照してください。

**mSPRT**（mixture SPRT、混合 SPRT。Robbins の混合）。対立仮説を事前分布で平均した SPRT で、これによりすべての対立仮説に対して常時有効になります。`NormalMixtureSPRT`（分散既知）、`TMixtureSPRT`（分散未知）。

**ベッティングによる検定**（testing by betting）。帰無仮説に逆らって賭けるギャンブラーの富として e 過程を構成すること。`BettingMeanTest`、
`BettingConfidenceSequence`、`KernelTwoSampleTest`。

**GROW**（growth-rate optimal、成長率最適）。対立仮説のもとで証拠の期待対数成長を最大にするように選ばれた e 値。
`TwoProportionTest(method="grow")`。

**ユニバーサル推論**（universal inference）。過去のデータのみから対立仮説を推定した尤度比による e 値。適応的デザインのもとでも有効なままです。`TwoProportionTest(method="universal")`。

**e-BH**（e-Benjamini–Hochberg）。任意の依存関係のもとで、多数の e 値にわたる偽発見率を制御します。`MultipleTests`、`e_bh`。

**e-LOND、オンライン FDR**（online FDR）。1 つずつ判定される一連の仮説に対する偽発見率の制御。`OnlineFDR`。

**SRM**（sample ratio mismatch、サンプル比率の不一致）。観測された群間のトラフィック分割が設定と異なること。実験のバグの兆候です。`SampleRatioMismatch`。

**CUPED**（controlled experiments using pre-experiment data、実験前データを用いた対照実験。covariate adjustment、共変量調整。regression adjustment、回帰調整）。実験前に測定した共変量を用いて A/B 効果の分散を減らします。
`ABTest(covariate=True)`、`AnytimeLinearModel`。

**比率指標**（ratio metric。delta method、デルタ法）。セッションあたり売上のように、ユーザーごとの 2 つの合計の比である指標。`RatioABTest`。

**変化点検出**（change-point detection。change detection、変化検出。quickest detection、最速検出。online anomaly detection、オンライン異常検知）。ストリームの分布が変化した後、すぐに警報を出すこと。`CUSUM`、`ShiryaevRoberts`、
`MeanEDetector`、`QuantileEDetector`、`BayesianChangePoint`。[変化検出](change-detection.md)を参照してください。

**ARL**（average run length、平均ランレングス。ARL₀。mean time to false alarm、誤警報までの平均時間）。何も変化していないときに誤警報が出るまでの観測数の期待値。変化検出器の誤警報の制御指標です。

**e 検出器**（e-detector）。e 過程から構成された変化検出器で、変化が起こりうる各時刻に 1 つずつ e 過程を開始します。ARL はノンパラメトリックな帰無仮説のもとで保証されます。`MeanEDetector`、`QuantileEDetector`。

**Kiefer–Weiss 問題**（Kiefer–Weiss problem）。最大サンプルサイズをもつ逐次検定のうち、最大の期待サンプルサイズを最小にするものを求める問題。
`kiefer_weiss_plan`。

**検査特性**（operating characteristic）。プランの誤り確率とサンプルサイズの分布を、真のパラメータの関数として表したもの。`operating_characteristic`。

**チェックポイント**（checkpoint）。実行をそこから正確に続行できる JSON 値。
`Run.checkpoint`、`Run.restore`。[ストリーミング](streaming.md)を参照してください。

**履歴ダイジェスト**（history digest）。実行が使用した観測にわたる SHA-256 ハッシュチェーンで、監査のためにすべてのチェックポイントに保持されます。

**保証**（guarantee。`exact`、`asymptotic`、`model`、`approximate`、`none`）。
このライブラリのすべての手続きが、何を約束するかを示す属性。[どの手法を選ぶか？](../../choosing.md)を参照してください。
