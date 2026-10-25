---
description: Как остановить A/B-тест досрочно, не увеличивая долю ложноположительных результатов, на Python. Критерии, валидные в любой момент (anytime-valid), для конверсии и ограниченной выручки, проверка несоответствия соотношения выборок (SRM) и контроль доли ложных открытий по многим метрикам с sequential-analysis.
language: ru
---

# Как остановить A/B-тест досрочно, не увеличивая долю ложноположительных результатов?

> Это перевод [страницы на английском языке](../../guide/ab-testing.md). Перевод ещё не проверен носителем языка; если тексты расходятся, верной считается английская страница.

**Коротко.** Используйте критерий, валидный в любой момент (anytime-valid):
его p-значение и доверительный интервал остаются валидными, как бы часто вы
ни смотрели, поэтому остановиться можно, как только результат стал ясен. В
sequential-analysis:

| Метрика | Процедура | Гарантия |
|---|---|---|
| конверсия (0/1) | `TwoProportionTest` | exact |
| любая ограниченная метрика (выручка с верхним порогом, доля) | `BoundedABTest` | exact |
| события на единицу экспозиции | `RateRatioTest` | exact для пуассоновских счётчиков |
| метрика-отношение (выручка на сессию) | `RatioABTest` | asymptotic |
| среднее с ковариатой, измеренной до эксперимента (CUPED) | `ABTest` | asymptotic |
| распределяется ли трафик так, как задумано? | `SampleRatioMismatch` | exact |
| несколько метрик или групп одновременно | `MultipleTests` (e-BH) | доля ложных открытий (false discovery rate), exact |

Подавайте в процедуру по одному пользователю: `state, out = test.step(state, {...})`.
Действуйте по `out.decision`, когда захотите.

## Конверсия: остановка, когда данные убедительны

Конверсия в контрольной группе 10%, в тестовой 12%. Критерий проверяется
после каждого пользователя и останавливается при первом решении:

```python
import random

from sequential_analysis.procedures import TwoProportionTest

def users(n, rates=(0.10, 0.12), seed=1):
    """(arm, converted) per user; arm 1 is the treatment."""
    rnd = random.Random(seed)
    for _ in range(n):
        arm = int(rnd.random() < 0.5)
        yield arm, int(rnd.random() < rates[arm])

test = TwoProportionTest(alpha=0.05)
state = test.initial_state()
for arm, converted in users(60_000):
    state, out = test.step(state, {"arm": arm, "y": converted})
    if out.decision is not None:
        break
print(f"stopped after {out.n} users: conversion {out.rates[0]:.4f} (treatment) vs {out.rates[1]:.4f}, "
      f"anytime-valid p = {out.p_value:.4f}, decision: {out.decision}")
```

```text
stopped after 16469 users: conversion 0.1259 (treatment) vs 0.1068, anytime-valid p = 0.0496, decision: reject_h0
```

Для сравнения: критерию с фиксированным объёмом выборки и мощностью 80% для
такого прироста нужно около 3850 пользователей на группу, всего 7700, и
смотреть на результат можно только один раз, в конце. Критерий, валидный в
любой момент, платит за свою свободу: для той же мощности ему нужно в
1,3–1,6 раза больше пользователей, чем одному анализу, а этот запуск занял
даже больше. Взамен не нужно заранее фиксировать объём выборки, и можно
смотреть на результат ежедневно и остановиться, как только он стал ясен.
Если эффект больше запланированного, это происходит гораздо раньше.

## Выручка: точный интервал для ограниченной метрики

`BoundedABTest` нужны только границы метрики. Ограничьте выручку сверху
значением, выбранным до начала теста (здесь 30), и доверительная
последовательность (confidence sequence) для разности средних будет точной
при любом распределении:

```python
from sequential_analysis.procedures import BoundedABTest

rnd = random.Random(2)
revenue = BoundedABTest(lower=0.0, upper=30.0, allocation=0.5, input="revenue", grid=300)
state = revenue.initial_state()
for _ in range(20_000):
    arm = int(rnd.random() < 0.5)
    spend = min(rnd.expovariate(1 / (5.0 if arm == 0 else 5.6)), 30.0)   # capped at 30
    state, out = revenue.step(state, {"arm": arm, "revenue": spend})
print(f"after {out.n} users: mean revenue {out.means[0]:.2f} (treatment) vs {out.means[1]:.2f}, "
      f"95% confidence sequence for the difference [{out.lower:.2f}, {out.upper:.2f}]")
```

```text
after 20000 users: mean revenue 5.47 (treatment) vs 4.99, 95% confidence sequence for the difference [-0.30, 1.30]
```

Интервал верен одновременно на всех 20 000 проверках, а не только на
последней. Здесь он всё ещё содержит 0: 20 000 пользователей недостаточно,
чтобы установить прирост около 0,5 для такой шумной метрики, поэтому
эксперимент продолжается.

## Сначала проверьте распределение трафика

Несоответствие соотношения выборок (sample ratio mismatch, SRM) означает, что
фактическое распределение отличается от настроенного, например из-за ошибки
в назначении групп или в логировании. Оценкам эффекта из такого эксперимента
нельзя доверять. Отклонение от 50/50 до 52/48 обнаруживается прямо во время
эксперимента:

```python
from sequential_analysis.procedures import SampleRatioMismatch

srm = SampleRatioMismatch(weights=(0.5, 0.5), alpha=0.001)
state = srm.initial_state()
rnd = random.Random(3)
for _ in range(50_000):
    state, out = srm.step(state, {"arm": int(rnd.random() < 0.52)})
    if out.decision is not None:
        break
print(f"mismatch detected after {out.n} users: split {out.proportions[0]:.3f} / {out.proportions[1]:.3f}")
```

```text
mismatch detected after 4927 users: split 0.470 / 0.530
```

## Много метрик одновременно

Если проверять десять независимых метрик, каждую на уровне 5%, вероятность
хотя бы одного ложного открытия составит около 40%. `MultipleTests`
объединяет e-значения (e-values) всех критериев процедурой e-BH, так что доля
ложных открытий остаётся на уровне `alpha` при любом моменте остановки:

```python
from sequential_analysis.procedures import MultipleTests

metrics = MultipleTests({
    "conversion": TwoProportionTest(input="converted"),
    "revenue": BoundedABTest(lower=0.0, upper=30.0, input="revenue", grid=100),
    "traffic split": SampleRatioMismatch((0.5, 0.5)),
}, alpha=0.05)
state = metrics.initial_state()
rnd = random.Random(4)
for _ in range(15_000):
    arm = int(rnd.random() < 0.5)
    converted = int(rnd.random() < (0.10, 0.13)[arm])
    spend = min(rnd.expovariate(1 / 5.0), 30.0)                          # no effect on revenue
    state, out = metrics.step(state, {"arm": arm, "converted": converted, "revenue": spend})
print("discoveries:", out.rejected)
```

```text
discoveries: ('conversion',)
```

## Подводные камни

* **Рандомизируйте ту единицу, которую анализируете.** Если рандомизируются
  пользователи, подавайте одну запись на пользователя, а не на просмотр
  страницы. Для метрик на сессию используйте `RatioABTest`, который работает
  с суммами по пользователям.
* **Фиксируйте верхний порог ограниченной метрики до начала теста.** Выбор
  порога после просмотра данных лишает гарантию силы.
* **Асимптотическим процедурам нужны большие выборки.** Для `ABTest` и
  `RatioABTest` интервал валиден лишь приближённо и на длинных сериях.
  Предпочитайте точные процедуры, когда они подходят.
* **Адаптивное распределение трафика** (бандиты) требует критерия, который
  остаётся валидным, когда распределение зависит от исходов:
  `TwoProportionTest(method="universal")` или
  `BoundedABTest(propensity_input=...)`. См.
  [учебник, §10](../../tutorials/ab-test.md).

Подробнее: [учебник по A/B-тестам](../../tutorials/ab-test.md) (CUPED,
метрики-отношения, интенсивности, планирование длительности) и
[программа экспериментов](../../tutorials/experiment-programme.md)
(доля ложных открытий по многим экспериментам).
