---
description: 순차 검정, A/B 테스트, 집단 순차 설계, 변화 탐지, 필터링을 위한 다른 Python 및 R 라이브러리(statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn)와 sequential-analysis의 비교, 그리고 언제 무엇을 쓸지에 대한 안내.
language: ko
---

# 다른 라이브러리와 비교하면 어떤가요?

> 이 문서는 [영어 원문](../../guide/comparison.md)의 번역본입니다. 아직 원어민의 검토를 거치지 않았으며, 두 문서의 내용이 다를 경우 영어 원문이 우선합니다.

**짧은 답.** 대부분의 라이브러리는 한 계열의 방법을 잘 다룹니다.
sequential-analysis는 순차적 추론(sequential inference)의 주요 계열을 하나의
인터페이스 뒤에 모아 둡니다.

* SPRT와 최적 계획;
* 집단 순차 설계(group sequential design);
* 언제든 유효한(anytime-valid) 검정과 신뢰 수열(confidence sequence);
* 변화 탐지;
* 상태공간 필터.

방법 자체 외에 더하는 것:

* 모든 절차가 자신의 보장(`exact`, `asymptotic`, `model`,
  ...)을 명시합니다;
* 모든 실행을 체크포인트로 저장하고 비트 단위까지 똑같이 재개할 수 있습니다;
* 형식이 명세되어 있고, TypeScript로 된 두 번째 구현이 이를 실행합니다;
* 필수 의존성이 없습니다.

아래 방법 가운데 하나만 필요하고 이미 그 분야에 특화된 라이브러리를 쓰고
있다면, 그 라이브러리를 계속 쓰세요. 아래 표는 각 도구가 자연스러운 선택이
되는 곳을 보여 줍니다. 설명은 2026년 10월 기준 각 라이브러리의 주된 목적에
대한 것이며, 기능을 빠짐없이 나열한 것은 아닙니다.

| 필요 | 자연스러운 선택 | sequential-analysis가 제공하는 것 |
|---|---|---|
| 고정 표본 검정, 회귀, 검정력 | scipy.stats, statsmodels | 이 라이브러리의 목적이 아님 |
| 규제 기관 제출용 집단 순차 설계 | rpact, gsDesign (R) | 같은 설계를 제공하며 테스트 스위트에서 rpact와 대조해 검증; 체크포인트와 함께 시험을 단계별로 진행 |
| 신뢰 수열, e-값 | confseq (Python), safestats (R) | 평균, 분위수, 회귀계수, 두 표본 효과에 대한 신뢰 수열; 다중 검정을 위한 e-BH와 e-LOND |
| UI가 있는 플랫폼형 A/B 테스트 | GrowthBook, Statsig, Eppo, Optimizely (플랫폼) | 임베드용 엔진: 전환율, 유계 지표, 발생률 지표에 대한 정확한 검정, SRM, 여러 지표에 걸친 FDR |
| 완료된 시계열의 오프라인 변화점 분할 | ruptures (Python), changepoint (R) | 데이터가 들어오는 동안의 온라인 탐지: CUSUM, Shiryaev–Roberts, e-탐지기, 베이즈 온라인 변화점 |
| 칼만 필터 | filterpy, statsmodels state space | 칼만, 강건 칼만, 입자, HMM 필터 (평활화와 체크포인트 포함) |
| GARCH | arch | arch와 같은 최대점으로 적합한 GARCH(1,1)과 GJR (테스트에서 검증), 이후 온라인으로 실행 |
| 은닉 마르코프 모형 | hmmlearn | 온라인 필터, hmmlearn과 일치하는 Baum–Welch, 온라인 EM |
| 예측 | statsmodels 등 | statsmodels와 일치하는 ETS와 AR 예측, 온라인 학습, 컨포멀(conformal) 구간 포함 |

## 다른 도구가 더 나은 경우

* **규제 기관 제출.** rpact는 그 목적으로 널리 쓰이며, 개발자들이
  밸리데이션 문서를 제공합니다. sequential-analysis는 다루는 설계에서
  rpact와 일치하지만, 의뢰자는 여전히 이를 직접 밸리데이션해야 합니다.
* **배열을 사용하는 대규모 오프라인 분석.** numpy 기반 라이브러리가 관측값당
  더 빠릅니다. sequential-analysis는 관측값을 하나씩 처리하도록 만들어졌습니다.
  각 절차의 비용은 [속도](../../performance.md)를 참고하세요.
* **이 라이브러리에 없는 방법.** 아직 중앙값에 대한 두 표본 검정, 다변량
  Hawkes 과정, 이동평균 항이 있는 ARIMA 모형이 없습니다. 추가되는 내용은
  [변경 이력](../../changelog.md)을 참고하세요.
