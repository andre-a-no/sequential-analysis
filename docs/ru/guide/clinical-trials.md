---
description: Как спланировать и провести промежуточные анализы клинического исследования на Python с групповыми последовательными дизайнами (O'Brien–Fleming, Pocock, расходование альфы по Lan–DeMets, границы бесперспективности) и объёмами выборки для средних, долей и выживаемости, сверенными с rpact, с sequential-analysis.
language: ru
---

# Как спланировать промежуточные анализы клинического исследования?

> Это перевод [страницы на английском языке](../../guide/clinical-trials.md). Перевод ещё не проверен носителем языка; если тексты расходятся, верной считается английская страница.

**Коротко.** Используйте групповой последовательный дизайн (group
sequential design). `group_sequential_design(alpha, fractions, spending=...)`
из `sequential_analysis.group_sequential` вычисляет:

* границы эффективности с расходованием альфы (alpha spending) по
  Lan–DeMets (типа O'Brien–Fleming, типа Pocock и другие);
* необязывающие границы бесперспективности (non-binding futility
  boundaries);
* мощность и ожидаемый объём выборки;
* максимальный объём выборки для средних и долей или число событий для
  выживаемости.

Границы и объёмы выборки совпадают с результатами пакета R rpact. Затем
процедуры критериев (`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) проводят
исследование, пациент за пациентом или событие за событием. Каждый
промежуточный анализ они выполняют, когда достигнута его доля информации
(information fraction).

## Дизайн: четыре анализа, расходование по O'Brien–Fleming

Односторонний α = 0,025, анализы при 25%, 50%, 75% и 100% пациентов,
мощность 90%, с границей бесперспективности:

```python
from sequential_analysis.group_sequential import group_sequential_design

design = group_sequential_design(0.025, [0.25, 0.5, 0.75, 1.0], spending="obrien-fleming",
                                 futility="obrien-fleming", power=0.9)
for k, (t, b, f) in enumerate(zip(design.fractions, design.bounds, design.futility), start=1):
    print(f"analysis {k} at {t:.0%}: efficacy if Z >= {b:.3f}, futility if Z <= {f:.3f}")
print("patients for an effect of 0.3 standard deviations:", design.max_sample_size(effect=0.3, sigma=1.0))
print(f"expected share of the patients used: {design.expected_fraction(0.0):.2f} with no effect, "
      f"{design.expected_fraction(design.drift):.2f} with the planned effect")
```

```text
analysis 1 at 25%: efficacy if Z >= 4.333, futility if Z <= -1.403
analysis 2 at 50%: efficacy if Z >= 2.963, futility if Z <= 0.325
analysis 3 at 75%: efficacy if Z >= 2.359, futility if Z <= 1.291
analysis 4 at 100%: efficacy if Z >= 2.014, futility if Z <= 2.014
patients for an effect of 0.3 standard deviations: 127
expected share of the patients used: 0.59 with no effect, 0.73 with the planned effect
```

## Бинарные конечные точки и выживаемость

```python
binary = group_sequential_design(0.025, [1 / 3, 2 / 3, 1.0], spending="obrien-fleming")
print("patients, response 10% vs 12%, 80% power:",
      binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8))
print("events for a hazard ratio of 0.7, 80% power:", binary.max_events(hazard_ratio=0.7, power=0.8))
print(f"inflation factor over a single analysis: {binary.inflation_factor(0.8):.3f}")
```

```text
patients, response 10% vs 12%, 80% power: 7780
events for a hazard ratio of 0.7, 80% power: 250
inflation factor over a single analysis: 1.013
```

При расходовании по O'Brien–Fleming три анализа требуют на 1,3% больше
пациентов, чем один финальный анализ.

## Проведение исследования

```python
import random

from sequential_analysis.procedures import GroupSequentialProportions

n_max = binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8)
test = GroupSequentialProportions.from_design(binary, n_max)
state, rnd = test.initial_state(), random.Random(3)
for patient in range(n_max):
    arm = patient % 2                                         # 1 treatment, 0 control
    state, out = test.step(state, {"arm": arm, "y": int(rnd.random() < (0.12 if arm else 0.10))})
    if out.analysis:
        print(f"analysis {out.analysis} after {out.n} patients: Z = {out.z:.2f}, bound {out.bound:.2f}")
    if out.decision:
        print("decision:", out.decision)
        break
```

```text
analysis 1 after 2594 patients: Z = 2.14, bound 3.71
analysis 2 after 5187 patients: Z = 2.64, bound 2.51
decision: reject_h0
```

Исследование остановлено в связи с эффективностью на втором анализе, после
двух третей запланированных пациентов.

## Когда анализы проходят не по плану

Комитеты по мониторингу данных (data monitoring committees) редко
собираются ровно при 25% информации:

* `design.at(fractions)` пересчитывает границы для фактически достигнутой
  информации. Расходование альфы сохраняет общий уровень значимости.
* `GroupSequentialMonitor` принимает любую статистику, которую вы
  вычисляете сами (модель Кокса, смешанную модель), в виде значения Z и её
  информацию на каждом заседании.

## А если хочется смотреть после каждого пациента?

Групповой последовательный дизайн допускает только запланированное число
просмотров. Чтобы следить за данными после каждого пациента или события,
используйте процедуру, валидную в любой момент (anytime-valid):
`AnytimeLogRankTest` для выживаемости, `TwoProportionTest` для частоты
ответа, `TMixtureSPRT` для среднего. При запланированном эффекте им нужно
больше пациентов. См. [учебник: исследование с анализом выживаемости](../../tutorials/survival.md).

## Регуляторная практика

Групповые последовательные дизайны с расходованием альфы — устоявшийся
подход в подтверждающих исследованиях, описанный в руководстве ICH E9 и в
руководстве FDA по адаптивным дизайнам (2019). Эта библиотека рассчитывает
дизайны и ведёт проверяемую, возобновляемую запись каждого анализа
(контрольная точка и дайджест её истории). Это не валидированное
программное обеспечение в регуляторном смысле: спонсор, использующий её в
регистрационном досье, должен валидировать её, как любой другой инструмент.

Подробнее: [учебник: групповое последовательное исследование](../../tutorials/group-sequential.md),
где результаты сравниваются с rpact;
[справочник: дизайн и планирование](../../reference/design.md).
