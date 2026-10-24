---
description: 순차 분석과 언제든 유효한 추론의 용어집 - e-값, e-과정, 신뢰 수열, 항상 유효한 p-값, mSPRT, 알파 소비, 정보 분율, ARL, SRM, CUPED, e-BH - 동의어와 각 개념을 구현한 sequential-analysis 절차를 함께 소개합니다.
language: ko
---

# 용어집

> 이 문서는 [영어 원문](../../guide/glossary.md)의 번역본입니다. 아직 원어민의 검토를 거치지 않았으며, 두 문서의 내용이 다를 경우 영어 원문이 우선합니다.

순차 분석과 이 라이브러리에서 쓰이는 용어입니다. 흔히 쓰이는 동의어는 괄호
안에 적었습니다.

**순차 분석**(sequential analysis; sequential testing, sequential inference).
관측 수를 미리 고정하지 않는 통계. 관측값 하나 또는 관측값 묶음이 들어올
때마다 절차가 멈출지 계속할지를 결정합니다. Wald(1945)가 창시했습니다.

**엿보기**(peeking; optional stopping, data peeking, continuous monitoring).
고정 표본 검정을 반복해서 들여다보다가 유의해지면 멈추는 것. 거짓
양성률을 부풀립니다. [엿보기](peeking.md)를 참고하세요.

**SPRT**(sequential probability ratio test, 순차 확률비 검정, Wald의 검정).
두 단순 가설의 로그 우도비를 누적하다가 그것이 어떤 구간을 벗어나면
멈춥니다. `SPRT`; 절단된 버전으로 `TwoSPRT`(Lorden의 2-SPRT)와
`kiefer_weiss_plan`. [SPRT](sprt.md)를 참고하세요.

**집단 순차 설계**(group sequential design; interim analyses, group
sequential trial). 미리 계획한 몇 번의 분석으로, 각 분석마다 경계가 있습니다.
경계는 전체 제1종 오류가 alpha가 되도록 정합니다.
`group_sequential_design`. [임상시험](clinical-trials.md)을 참고하세요.

**알파 소비 함수**(alpha spending function; error spending, Lan–DeMets).
각 정보 분율까지 제1종 오류를 얼마나 소진할 수 있는지를 정합니다.
O'Brien–Fleming형 소비는 초기에 적게 쓰고, Pocock형 소비는 고르게 씁니다.
`spending="obrien-fleming"`, `"pocock"`, ...

**정보 분율**(information fraction). 어떤 분석 시점에 도달한, 계획된 통계적
정보(환자, 사건)의 비율.

**무익성 경계**(futility boundary; non-binding futility). 아래쪽 경계로, 그
아래로 내려가면 효과가 없어 중단할 것을 권고합니다. 비구속적(non-binding)
경계는 무시해도 제1종 오류가 부풀지 않습니다.

**언제든 유효한 추론**(anytime-valid inference; always-valid inference, safe
anytime-valid inference, SAVI). 모든 표본 크기에서 동시에 보장이 성립하는
검정과 구간으로, 계속 모니터링하다가 어떤 이유로든 멈출 수 있습니다.

**e-값**(e-value; e-variable, betting score). 귀무가설하에서 기댓값이 최대
1인 음이 아닌 통계량. e-값이 크면 귀무가설에 반하는 증거입니다. e-값이
1/alpha를 넘을 때 기각하면 제1종 오류는 최대 alpha입니다. 여러 절차의
`log_e_value` 출력.

**e-과정**(e-process; test martingale, test supermartingale, wealth
process). 중단 시점(stopping time)에서도 유효한 e-값의 수열. 귀무가설하에서
그 누적 최댓값이 1/alpha를 넘을 확률은 최대 alpha입니다(Ville 부등식).

**항상 유효한 p-값**(always-valid p-value; anytime-valid p-value,
sequential p-value). 어떤 중단 시점에서든 유효한 p-값. e-과정의 누적
최댓값의 역수입니다. 언제든 유효한 절차들의 `p_value` 출력.

**신뢰 수열**(confidence sequence; anytime-valid confidence interval,
always-valid confidence interval, time-uniform confidence interval). 모든
표본 크기에서 동시에 참값을 포함할 확률이 적어도 1 − alpha인 구간의 수열.
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, 그리고 여러
검정의 `lower`와 `upper` 출력.
[신뢰 수열](confidence-sequences.md)을 참고하세요.

**mSPRT**(mixture SPRT, 혼합 SPRT, Robbins' mixture). 대립가설을 사전분포에
대해 평균한 SPRT로, 그 덕분에 모든 대립가설에 대해 언제든 유효합니다.
`NormalMixtureSPRT`(분산 기지), `TMixtureSPRT`(분산 미지).

**베팅에 의한 검정**(testing by betting). 귀무가설에 반대로 베팅하는 도박꾼의
자산으로 e-과정을 구성하는 것. `BettingMeanTest`,
`BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW**(growth-rate optimal, 성장률 최적). 대립가설하에서 증거의 기대 로그
성장을 최대화하도록 고른 e-값. `TwoProportionTest(method="grow")`.

**보편 추론**(universal inference). 과거 데이터만으로 추정한 대립가설을
쓰는 우도비로부터 얻은 e-값. 적응형 설계에서도 유효합니다.
`TwoProportionTest(method="universal")`.

**e-BH**(e-Benjamini–Hochberg). 여러 e-값에 걸쳐, 어떤 의존 구조에서든 거짓
발견율(false discovery rate)을 제어합니다. `MultipleTests`, `e_bh`.

**e-LOND, 온라인 FDR**(online FDR). 하나씩 차례로 결정되는 일련의 가설에 대한
거짓 발견율 제어. `OnlineFDR`.

**SRM**(sample ratio mismatch, 표본 비율 불일치). 처리군 간 트래픽의 관측된
분할이 설정과 다른 것으로, 실험에 버그가 있다는 신호입니다.
`SampleRatioMismatch`.

**CUPED**(controlled experiments using pre-experiment data; covariate
adjustment, regression adjustment, 공변량 보정, 회귀 보정). 실험 전에 측정한
공변량으로 A/B 효과의 분산을 줄입니다.
`ABTest(covariate=True)`, `AnytimeLinearModel`.

**비율 지표**(ratio metric; delta method, 델타 방법). 세션당 매출처럼 사용자별
두 합계의 비로 된 지표. `RatioABTest`.

**변화점 탐지**(change-point detection; change detection, quickest detection,
online anomaly detection). 스트림의 분포가 바뀐 뒤 곧바로 경보를 울리는 것.
`CUSUM`, `ShiryaevRoberts`, `MeanEDetector`, `QuantileEDetector`,
`BayesianChangePoint`. [변화 탐지](change-detection.md)를 참고하세요.

**ARL**(average run length, 평균 런 길이; ARL₀, mean time to false alarm).
아무것도 바뀌지 않았을 때 오경보가 나기까지의 기대 관측 수. 변화 탐지기의
오경보 제어 지표입니다.

**e-탐지기**(e-detector). 가능한 변화 시점마다 하나씩 시작한 e-과정들로
만든 변화 탐지기. 비모수 귀무가설하에서 ARL이 보장됩니다.
`MeanEDetector`, `QuantileEDetector`.

**Kiefer–Weiss 문제**(Kiefer–Weiss problem). 최대 표본 크기가 있는 순차
검정 가운데 기대 표본 크기의 최댓값을 최소화하는 검정을 찾는 문제.
`kiefer_weiss_plan`.

**검사 특성**(operating characteristic). 계획의 오류 확률과 표본 크기의
분포를 참 모수의 함수로 나타낸 것. `operating_characteristic`.

**체크포인트**(checkpoint). 실행을 정확히 이어갈 수 있게 해 주는 JSON 값.
`Run.checkpoint`, `Run.restore`. [스트리밍](streaming.md)을 참고하세요.

**이력 다이제스트**(history digest). 실행이 사용한 관측값에 대한 SHA-256
해시 체인으로, 감사를 위해 모든 체크포인트에 보관됩니다.

**보장**(guarantee; `exact`, `asymptotic`, `model`, `approximate`, `none`).
이 라이브러리의 모든 절차가 자신이 무엇을 약속하는지 명시하는 속성.
[어떤 방법을 쓸까?](../../choosing.md)를 참고하세요.
