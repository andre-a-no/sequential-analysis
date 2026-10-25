---
description: ストリーム（Kafka、SQL、pandas、センサー）上で逐次統計を実行し、クラッシュ後に止まった位置から正確に再開する方法。sequential-analysis による JSON チェックポイント、重複排除された配信、監査用の履歴ダイジェスト、そして Python または TypeScript での同じ実行の続行。
language: ja
---

# ストリーム上で統計処理を行い、クラッシュ後に再開するには？

> このページは[英語版](../../guide/streaming.md)の翻訳です。ネイティブスピーカーによるレビューはまだ受けていません。両者が異なる場合は英語版が優先されます。

**短い答え。** 手続きを `Run` で包みます。そのうえで：

1. `run_sync`（並行するプロデューサーがある場合は `run_async`）で観測を入力します。
2. `run.checkpoint()` を好きなだけ頻繁に保存します。これは、状態、乱数の状態、ソースの位置、履歴の SHA-256 ダイジェストを含むプレーンな JSON 値です。
3. クラッシュ後は、`Run.restore(procedure, checkpoint)` がビット単位で正確に続行します。`Delivery("sequence")` を使うと、再起動後に再配信された観測は重複として破棄されます。
4. TypeScript 実行系は、同じチェックポイントを JavaScript で続行できます。同じ判定と履歴ダイジェストを与え、数値は最後の数ビットまで一致します。108 件の適合性テストケースのうち 34 件では完全に同一で、残りでは相対誤差 6·10⁻¹³ 以内です。

## クラッシュ、再起動、再生：同じ結果

300 個の測定値に対するモニタリングの実行が、120 個目の後で中断されます。メッセージキューが再起動後によく行うように、ソースは 100 個目の測定値から再生されます。復元された実行は、すでに見た 20 個の測定値を破棄し、中断されなかった実行とまったく同じ位置で終わります。

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

履歴ダイジェスト（history digest）は、実行が使用したすべての観測にわたるハッシュチェーンです。同じダイジェストをもつ 2 つの実行は、同じデータを同じ順序で見ています。監査担当者は、[仕様](../../spec.md)に従って観測ログからそれを再計算できます。

## 観測の入手元

| ソース | 関数 |
|---|---|
| 値のリストまたはジェネレータ | `sources.from_values` |
| CSV ファイル | `sources.from_csv` |
| pandas または polars の DataFrame | `adapters.from_dataframe` |
| SQL クエリ（任意の DB-API 接続） | `adapters.from_sql` |
| コミット済みオフセット付きの Kafka メッセージ | `adapters.from_kafka`、`adapters.kafka_offsets` |
| 複数のソースを同時に | `sources.interleave`、`sources.merge_ordered` |
| 記録された観測ログ | `sources.replay` |

異なるソースからの入力は**トポロジー**（topology）によって関連付けられます。`KeyJoin` は割り付けと結果をユーザーで結合し、`TimeAlign` は 2 つのセンサーを時間で揃え、`AsOfJoin` はイベントを、それを知っていたバー（bar）に付け加えます。[データソース](../../adapters.md)を参照してください。

## 手続きが変わった場合

チェックポイントには、手続きの名前、バージョン、設定が記録されます。
`Run.restore` は、異なる手続き、異なる設定、あるいは演算が異なるバージョンで作られたチェックポイントを拒否し、`IncompatibleCheckpoint` を送出します。したがって、実行が別の数値で黙って続行されることはありません。

さらに詳しく：[チェックポイント、ログ、バックエンド](../../checkpoints.md)、
[TypeScript 実行系](../../typescript.md)、
[フォーマットの仕様](../../spec.md)。
