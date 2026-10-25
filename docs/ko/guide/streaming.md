---
description: 스트림(Kafka, SQL, pandas, 센서)에서 순차 통계를 실행하고 장애 후 멈춘 지점에서 정확히 재개하는 방법. sequential-analysis의 JSON 체크포인트, 중복 제거 전달, 감사를 위한 이력 다이제스트, 그리고 같은 실행을 Python이나 TypeScript에서 이어가는 기능을 다룹니다.
language: ko
---

# 스트림에서 통계를 실행하고 장애 후 재개하려면?

> 이 문서는 [영어 원문](../../guide/streaming.md)의 번역본입니다. 아직 원어민의 검토를 거치지 않았으며, 두 문서의 내용이 다를 경우 영어 원문이 우선합니다.

**짧은 답.** 절차를 `Run`으로 감싸세요. 그다음:

1. `run_sync`(동시에 여러 생산자가 있다면 `run_async`)로 관측값을
   입력합니다.
2. `run.checkpoint()`를 원하는 만큼 자주 저장합니다. 이는 상태, 난수 상태,
   소스 위치, 이력의 SHA-256 다이제스트를 담은 평범한 JSON 값입니다.
3. 장애가 나면 `Run.restore(procedure, checkpoint)`가 비트 단위까지
   정확히 이어서 실행합니다. `Delivery("sequence")`를 쓰면 재시작 후 다시
   전달된 관측값은 중복으로 처리되어 버려집니다.
4. TypeScript 실행기는 같은 체크포인트를 JavaScript에서 이어갈 수
   있습니다. 결정과 이력 다이제스트가 같고, 수치는 마지막 비트 수준까지
   일치합니다. 108개의 적합성(conformance) 사례 가운데 34개에서는 동일하고,
   나머지에서는 상대 오차 6·10⁻¹³ 이내입니다.

## 장애, 재시작, 재전송: 결과는 같다

판독값 300개에 대한 모니터링 실행이 120개 이후 중단됩니다. 메시지 큐가
재시작 후 흔히 그러듯, 소스는 100번째 판독값부터 다시 전송됩니다. 복원된
실행은 이미 본 판독값 20개를 버리고, 중단 없이 실행했을 때와 정확히 같은
지점에서 끝납니다.

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

이력 다이제스트는 실행이 사용한 모든 관측값에 대한 해시 체인입니다.
다이제스트가 같은 두 실행은 같은 데이터를 같은 순서로 본 것입니다. 감사자는
[명세](../../spec.md)에 따라 관측 로그로부터 이를 다시 계산할 수 있습니다.

## 관측값은 어디에서 오는가

| 소스 | 함수 |
|---|---|
| 값의 리스트나 제너레이터 | `sources.from_values` |
| CSV 파일 | `sources.from_csv` |
| pandas 또는 polars DataFrame | `adapters.from_dataframe` |
| SQL 쿼리 (모든 DB-API 연결) | `adapters.from_sql` |
| 커밋된 오프셋이 있는 Kafka 메시지 | `adapters.from_kafka`, `adapters.kafka_offsets` |
| 여러 소스를 동시에 | `sources.interleave`, `sources.merge_ordered` |
| 기록된 관측 로그 | `sources.replay` |

서로 다른 소스의 입력은 **토폴로지**(topology)로 연결됩니다. `KeyJoin`은
할당과 결과를 사용자 기준으로 결합하고, `TimeAlign`은 두 센서를 시간에 맞춰
정렬하며, `AsOfJoin`은 이벤트를 그 이벤트를 알고 있던 바(bar)에 붙입니다.
[데이터 소스](../../adapters.md)를 참고하세요.

## 절차가 바뀌었을 때

체크포인트에는 절차의 이름, 버전, 설정이 기록됩니다. `Run.restore`는 다른
절차, 다른 설정, 또는 산술이 달라진 버전으로 만든 체크포인트를 거부하고
`IncompatibleCheckpoint`를 발생시킵니다. 따라서 실행이 다른 수치로 조용히
이어지는 일은 결코 없습니다.

더 보기: [체크포인트, 로그, 백엔드](../../checkpoints.md),
[TypeScript 실행기](../../typescript.md),
[형식 명세](../../spec.md).
