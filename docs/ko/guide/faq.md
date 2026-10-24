---
description: 순차 검정과 언제든 유효한 추론을 위한 Python 라이브러리 sequential-analysis에 대해 자주 묻는 질문 - 설치, 라이선스와 상업적 사용, 운영 환경의 A/B 테스트, 임상시험, 검정력, 속도, TypeScript, 인용.
language: ko
---

# 자주 묻는 질문

> 이 문서는 [영어 원문](../../guide/faq.md)의 번역본입니다. 아직 원어민의 검토를 거치지 않았으며, 두 문서의 내용이 다를 경우 영어 원문이 우선합니다.

## 라이브러리에 대해

### sequential-analysis란 무엇인가요?

순차적 통계 추론을 위한 Python 라이브러리입니다. 이 라이브러리의 검정, 신뢰
수열(confidence sequence), 탐지기는 관측값마다 확인하고 언제든 중단할 수
있으며, 그래도 오류 보장을 잃지 않습니다. 다음을 포함합니다.

* SPRT;
* 집단 순차 설계(group sequential design);
* 언제든 유효한(anytime-valid) A/B 테스트;
* 변화점 탐지기;
* 칼만 필터, 입자 필터, 은닉 마르코프 필터;
* 예측과 GARCH.

모두 JSON 체크포인트를 지원하는 하나의 인터페이스로 동작합니다. 개발은
Novikov Laboratories LLC가 맡고 있습니다.

### 어떻게 설치하나요? 무엇에 의존하나요?

`pip install sequential-analysis`. Python 3.8 이상(3.14까지 테스트)만 있으면
되고 그 밖에는 아무것도 필요하지 않습니다.
`pip install "sequential-analysis[fast]"`는 배열로 작동하는 절차를 위해
numpy를 추가합니다. pandas, polars, Kafka 클라이언트, matplotlib는 어댑터나
플로팅 함수를 호출할 때에만 사용됩니다.

### 상업적으로 무료로 쓸 수 있나요?

AGPL-3.0과 상용 라이선스의 이중 라이선스입니다. 다음 용도는 AGPL에 따라
무료입니다.

* 연구와 교육;
* AGPL 또는 GPL v3 하의 오픈 소스 프로젝트;
* 조직 내부 사용 (다른 사람에게 사본을 제공하지 않고, 조직 외부 사람에게
  네트워크를 통한 접근을 제공하지 않는 경우).

비공개 소스 제품, 또는 소스를 공개하지 않는 네트워크 서비스에는 상용
라이선스가 필요합니다. 구체적인 경우는
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)의
표에 따라 결정됩니다. 라이선스 문의: andrei@hobukob.ru.

### 어떻게 인용하나요?

저장소의
[CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff)에
인용 정보가 있으며, GitHub의 *Cite this repository* 버튼으로 BibTeX이나
APA 형식으로 변환할 수 있습니다. 릴리스는 DOI와 함께 Zenodo에 보관됩니다.
방법과 그 검증은
[논문](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf)에
설명되어 있습니다.

## 사용하기

### 운영 환경의 A/B 테스트에 쓸 수 있나요?

네, 통계 엔진으로서 쓸 수 있습니다. 다음에 대한 정확한(exact) 검정을
제공합니다.

* 전환율 (`TwoProportionTest`);
* 유계 지표 (`BoundedABTest`);
* 발생률 (`RateRatioTest`);
* 트래픽 분할 (`SampleRatioMismatch`);
* 거짓 발견율(false discovery rate) 제어를 포함한 다중 지표 (`MultipleTests`).

순수 Python에서 전환율 검정은 사용자당 약 10마이크로초, 분할 점검은 4,
발생률 검정은 40마이크로초가 걸립니다. 각각의 체크포인트는 2~4킬로바이트입니다.
`BoundedABTest`는 격자를 유지하며 0.1~0.5 ms가 걸립니다.

이 라이브러리는 실험 플랫폼이 아닙니다. 할당, 이벤트 수집, 대시보드는 직접
만들거나 플랫폼에서 가져와야 합니다. [A/B 테스트](ab-testing.md)를
참고하세요.

### 결과를 매일 엿봐도 되나요?

네, 언제든 유효한 절차라면 됩니다. 그것이 바로 이 절차들의 용도입니다. 집단
순차 설계에서는 계획한 분석 시점에만 보세요. 고전적인 고정 표본 검정에서는
한 번만 보세요. [엿보기](peeking.md)를 참고하세요.

### 언제든 유효한 검정은 고정 표본 검정보다 검정력이 낮나요?

고정 표본 검정이 계획된 효과 크기에서는 그렇습니다. 같은 검정력에 도달하려면
두 비율에 대한 언제든 유효한 검정은 1.3~1.6배의 사용자가 필요합니다. 그 대신
효과가 더 크면 일찍 멈출 수 있고, 표본 크기를 미리 정할 필요가 없습니다.
계획된 확인 시점이 몇 번뿐인 집단 순차 설계는 단일 분석보다 1~20%만 더
듭니다.

### 집단 순차 설계와 언제든 유효한 방법 중 무엇을 써야 하나요?

* **집단 순차 설계**: 자료 모니터링 위원회나 릴리스 주기처럼 분석 횟수가
  적고 미리 계획되어 있을 때, 특히 확증 임상시험에 적합합니다.
* **언제든 유효한 방법**: 계속 지켜보고 싶을 때, 또는 언제 보거나 멈출지
  미리 말할 수 없을 때 적합합니다.

### 베이즈 A/B 테스트도 하나요?

이 라이브러리의 A/B 테스트는 빈도주의 방식으로, 오류율에 대한 보장을
제공합니다. 적합한 곳에서는 베이즈 구성 요소도 사용할 수 있습니다.

* `ThompsonAllocation`은 각 처리군이 최선일 사후 확률에 따라 트래픽을
  보내며, 배포를 위한 기대 손실 규칙을 갖추고 있습니다;
* `BayesianChangePoint`는 변화점을 탐지합니다;
* 예측기는 베이즈 갱신으로 모수를 학습합니다.

### 임상시험용으로 밸리데이션되었나요?

집단 순차 설계(경계, 검정력, 표본 크기, 사건 수)는 테스트 스위트에서
rpact 및 R의 survival 패키지와 대조해 검증됩니다. 규제상 의미의 밸리데이션된
소프트웨어는 아닙니다. 허가 신청에 이를 사용하는 의뢰자는 다른 도구와
마찬가지로 직접 밸리데이션합니다.
[임상시험](clinical-trials.md)을 참고하세요.

### 지표의 꼬리가 두껍습니다(매출, 지연 시간). 무엇을 써야 하나요?

* 분위수(중앙값, 90번째 백분위수)에는 가정이 필요 없는 `QuantileTest`나
  `QuantileConfidenceSequence`를 사용하세요.
* 평균에는 미리 정한 수준으로 값에 상한을 두고 `BoundedABTest`나
  `BettingConfidenceSequence`(exact)를 사용하세요.
* 또는 표준편차의 상한을 가정하고 `CatoniConfidenceSequence`를 사용하세요.

중앙값에 대한 두 표본 검정은 아직 라이브러리에 없습니다.

### 얼마나 빠른가요?

가장 단순한 절차는 순수 Python에서 관측값당 1~10마이크로초가 걸립니다.
SPRT, CUSUM, 집단 순차 검정과 혼합 검정, GARCH가 여기에 속합니다. 격자나 표본
전체를 유지하는 절차는 0.1~10 ms가 걸립니다. 베팅 및 Catoni 신뢰 수열, 커널
검정, 학습형 예측기가 그 예입니다.
[속도](../../performance.md)에 각 절차의 비용과 체크포인트 크기가 나와
있습니다.

### JavaScript나 브라우저에서 실행할 수 있나요?

네. `ts/`에 있는 TypeScript 실행기가 절차를 실행하고 Python 체크포인트를
이어갑니다. 이력 다이제스트와 결정은 동일하고, 수치는 마지막 비트 수준까지
일치합니다. [TypeScript 실행기](../../typescript.md)를 참고하세요.

### 실행이 장애를 견딜 수 있나요?

네. `run.checkpoint()`는 평범한 JSON이고, `Run.restore`는 비트 단위까지
똑같이 이어서 실행합니다. 다시 전달된 관측값은 버려집니다.
[스트리밍](streaming.md)을 참고하세요.

### 문서에서 "exact"와 "asymptotic"은 무슨 뜻인가요?

모든 절차의 `guarantee` 속성이 그 절차의 약속을 명시합니다.

* `exact`: 명시된 가정하에서 모든 표본 크기에서 오류율이 유지됨;
* `asymptotic`: 긴 실행에서 근사적으로 유지됨;
* `model`: 명시된 모형하에서 정확함;
* `approximate`;
* `none`.

문서는 적합한 정확한 절차가 있으면 그것을 권장합니다.
[어떤 방법을 쓸까?](../../choosing.md)를 참고하세요.
