---
description: Доверительные последовательности (confidence sequences) — это доверительные интервалы, которые валидны одновременно при всех объёмах выборки, поэтому за ними можно следить непрерывно. Как вычислить их на Python для среднего ограниченной величины, медианы или квантиля и среднего с тяжёлыми хвостами с sequential-analysis.
language: ru
---

# Как получить доверительный интервал, который остаётся валидным, сколько бы я ни смотрел на данные?

> Это перевод [страницы на английском языке](../../guide/confidence-sequences.md). Перевод ещё не проверен носителем языка; если тексты расходятся, верной считается английская страница.

**Коротко.** Используйте **доверительную последовательность (confidence
sequence)**. Это последовательность интервалов, по одному после каждого
наблюдения, которая с вероятностью не менее 95% содержит истинное значение
одновременно при всех объёмах выборки. За ней можно следить, остановиться,
когда она достаточно узкая или не содержит нуля, и указать в отчёте интервал
на момент остановки. Обычный 95%-ный доверительный интервал обещает 95%
только при одном объёме выборки, зафиксированном заранее.

| Что оценивается | Допущение | Процедура | Гарантия |
|---|---|---|---|
| среднее ограниченных данных (доли, баллы, выручка с верхним порогом) | значения в `[lower, upper]` | `BettingConfidenceSequence` | exact |
| медиана, 90-й процентиль, любой квантиль | нет | `QuantileConfidenceSequence` | exact |
| среднее с тяжёлыми хвостами или выбросами | граница для стандартного отклонения | `CatoniConfidenceSequence` | exact |
| среднее нормальных данных при неизвестной дисперсии | нормальность | `TMixtureSPRT` (`lower`, `upper`) | exact при нормальности |
| среднее чего угодно, длинные серии | конечная дисперсия | `AsymptoticConfidenceSequence` | asymptotic |
| разность между двумя группами | см. [A/B-тесты](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## Обычный интервал не выдерживает наблюдения

Возьмём 500 наблюдений величины 0/1 со средним 0,3 и, начиная с 30-го,
после каждого вычислим учебный 95%-ный интервал: среднее ± 1,96 стандартной
ошибки. В скольких из 100 запусков интервал в какой-то момент не накроет
истинное среднее?

```python
import math
import random

def stream(seed, n=500, p=0.3):
    rnd = random.Random(seed)
    return [float(rnd.random() < p) for _ in range(n)]

def textbook_ever_misses(xs, truth=0.3):
    total = total2 = 0.0
    for n, x in enumerate(xs, start=1):
        total, total2 = total + x, total2 + x * x
        if n >= 30:
            mean = total / n
            se = math.sqrt(max(total2 / n - mean * mean, 1e-12) / n)
            if abs(mean - truth) > 1.96 * se:
                return True
    return False

runs = [stream(seed) for seed in range(100)]
print(f"textbook interval misses the truth at some n in {sum(map(textbook_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
textbook interval misses the truth at some n in 28% of runs
```

Его «95%» выполняются только при объёме выборки, зафиксированном заранее.
Доверительная последовательность для тех же данных, построенная через ставки
(betting; Waudby-Smith and Ramdas 2024), по построению промахивается при
каком-либо n не более чем в 5% запусков:

```python
from sequential_analysis.procedures import BettingConfidenceSequence

def sequence_ever_misses(xs, truth=0.3):
    cs = BettingConfidenceSequence(lower=0.0, upper=1.0, alpha=0.05, grid=100)
    state = cs.initial_state()
    for x in xs:
        state, out = cs.step(state, {"x": x})
        if not out.lower <= truth <= out.upper:
            return True
    return False

print(f"confidence sequence misses the truth at some n in {sum(map(sequence_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
confidence sequence misses the truth at some n in 1% of runs
```

## Медиана задержки без каких-либо допущений

Распределения задержек скошены и имеют тяжёлые хвосты, поэтому интервалу
«среднее ± стандартная ошибка» для них нельзя доверять.
`QuantileConfidenceSequence` покрывает любой квантиль любого распределения,
включая распределения с совпадающими значениями:

```python
from sequential_analysis.procedures import QuantileConfidenceSequence

rnd = random.Random(7)
median = QuantileConfidenceSequence(p=0.5, alpha=0.05)
p90 = QuantileConfidenceSequence(p=0.9, alpha=0.05)
m_state, q_state = median.initial_state(), p90.initial_state()
for _ in range(2000):
    latency = rnd.lognormvariate(math.log(120.0), 0.6)   # milliseconds; true median 120
    m_state, m = median.step(m_state, {"x": latency})
    q_state, q = p90.step(q_state, {"x": latency})
print(f"median: {m.estimate:.1f} ms, 95% confidence sequence [{m.lower:.1f}, {m.upper:.1f}]")
print(f"90th percentile: {q.estimate:.1f} ms, [{q.lower:.1f}, {q.upper:.1f}]")
```

```text
median: 117.3 ms, 95% confidence sequence [111.3, 122.6]
90th percentile: 252.7 ms, [237.9, 272.5]
```

Истинные значения — 120 мс и 258,8 мс. Оба интервала выполняются
одновременно при всех 2000 объёмах выборки.

## Подводные камни

* **Границы и пороги — часть допущения.** Выбирайте `lower` и `upper` до
  того, как увидите данные. Значение за их пределами отклоняется.
* **Ни один метод не даёт точного покрытия для среднего произвольных
  неограниченных данных.** Для таких данных используйте квантиль, ограничьте
  значения, примите границу для стандартного отклонения (Catoni) или
  согласитесь на асимптотическую последовательность.
* **Доверительные последовательности шире одиночного интервала** при том же
  объёме выборки. Ширина — это цена валидности одновременно при всех объёмах
  выборки.

Подробнее: [Какой метод выбрать?](../../choosing.md),
[справочник: вывод, валидный в любой момент, и непараметрические методы](../../reference/anytime.md).
