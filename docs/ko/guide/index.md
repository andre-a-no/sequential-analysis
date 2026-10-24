---
description: 순차 검정과 언제든 유효한 추론(anytime-valid inference)을 위한 Python 라이브러리 sequential-analysis의 사용자 가이드. 각 페이지는 하나의 질문에 바로 답하며, 실행되는 코드와 그 출력을 함께 제공합니다.
language: ko
---

# 사용자 가이드

> 이 문서는 [영어 원문](../../guide/index.md)의 번역본입니다. 아직 원어민의 검토를 거치지 않았으며, 두 문서의 내용이 다를 경우 영어 원문이 우선합니다.

이 가이드는 사람들이 실제로 묻는 질문을 기준으로 구성되어 있습니다. 각
페이지는 먼저 질문에 바로 답하고, 이어서 그대로 실행되는 짧은 프로그램과
그 출력, 답의 근거가 되는 보장(guarantee), 그리고 해당 방법이 적용되지
않는 경우를 설명합니다. 각 주제를 더 깊이 다루려면
[튜토리얼](../../tutorials/ab-test.md)을 참고하세요.

## 한 문단으로 보는 라이브러리

**sequential-analysis**는 관측값이 하나씩 차례로 들어오는 데이터에 대한
통계적 추론을 위한 Python 라이브러리입니다. 이 라이브러리의 검정, 신뢰구간,
탐지기는 관측값이 들어올 때마다 확인하고 언제든 중단할 수 있으며, 그래도
오류율이 그대로 유지됩니다. 다루는 범위는 다음과 같습니다.

* Wald의 순차 확률비 검정(SPRT)과 최적 순차 계획;
* 임상시험을 위한 집단 순차 설계(group sequential design)
  (O'Brien–Fleming 및 Pocock 소비 함수, 무익성 경계);
* e-값(e-value)과 신뢰 수열(confidence sequence)을 이용한 언제든 유효한 A/B 테스트;
* 변화점 탐지(change-point detection);
* 칼만 필터, 입자 필터, 은닉 마르코프 필터;
* 예측과 GARCH 변동성.

모든 실행은 JSON 체크포인트로 저장할 수 있고, Python에서 비트 단위까지
똑같이 재개하거나, TypeScript 실행기에서 같은 결정을 내리며 이어갈 수
있습니다.

| | |
|---|---|
| 설치 | `pip install sequential-analysis` |
| 임포트 | `import sequential_analysis` |
| Python | 3.8~3.14, 필수 의존성 없음 (numpy는 선택) |
| 라이선스 | AGPL-3.0 또는 Novikov Laboratories LLC의 상용 라이선스 |
| 소스 | <https://github.com/andre-a-no/sequential-analysis> |
| 문서 | <https://andre-a-no.github.io/sequential-analysis/> |

## 질문

**개념**

* [왜 p-값을 매일 들여다보면 안 되나요?](peeking.md) 엿보기(peeking)와
  순차적 방법의 세 계열.
* [용어집](glossary.md): e-값, 신뢰 수열, 알파 소비(alpha spending),
  ARL 등의 용어와 그 동의어.

**과제**

* [거짓 양성을 늘리지 않고 A/B 테스트를 조기에 중단하려면?](ab-testing.md)
* [계속 들여다봐도 유효한 신뢰구간은 어떻게 얻나요?](confidence-sequences.md)
* [Python에서 Wald의 SPRT를 실행하려면?](sprt.md)
* [임상시험의 중간 분석은 어떻게 계획하나요?](clinical-trials.md)
* [측정값 스트림에서 변화를 탐지하려면?](change-detection.md)
* [스트림에서 통계를 실행하고 장애 후 재개하려면?](streaming.md)

**선택**

* [내 질문에는 어떤 방법이 맞나요?](../../choosing.md): 전체 표.
* [다른 라이브러리와 비교하면 어떤가요?](comparison.md)
* [자주 묻는 질문](faq.md)

## 보장을 읽는 법

모든 절차에는 `guarantee` 속성이 있습니다. 이 가이드는 각 답과 함께 이
속성을 인용합니다.

* **exact:** 명시된 가정하에서 모든 표본 크기에서 오류율이 유지됩니다.
* **asymptotic:** 근사적으로 유지되며, 표본이 클수록 더 잘 유지됩니다.
* **model:** 명시된 모형하에서 확률이 정확하지만, 그 모형을 넘어서는 것은
  주장하지 않습니다.
* **approximate:** 모형하에서도 근사입니다.
* **none:** 절차가 데이터를 변환할 뿐이며 아무것도 주장하지 않습니다.
