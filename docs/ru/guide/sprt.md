---
description: Как запустить последовательный критерий отношения вероятностей Вальда (SPRT) на Python с sequential-analysis. Вероятности ошибок, средний объём выборки в сравнении с критерием с фиксированной выборкой и усечённые альтернативы (2-SPRT, оптимальные планы Кифера–Вейсса, Kiefer–Weiss).
language: ru
---

# Как запустить SPRT Вальда в Python?

> Это перевод [страницы на английском языке](../../guide/sprt.md). Перевод ещё не проверен носителем языка; если тексты расходятся, верной считается английская страница.

**Коротко.** `SPRT(family, theta0, theta1, alpha, beta)` из
`sequential_analysis.procedures` реализует последовательный критерий
отношения вероятностей Вальда (sequential probability ratio test, SPRT). Он
выбирает между двумя простыми гипотезами, затрачивая в среднем наименьшее
число наблюдений. Подавайте ему по одному наблюдению и останавливайтесь при
первом решении. В примере ниже ему нужно примерно вдвое меньше наблюдений,
чем критерию с фиксированным объёмом выборки при тех же вероятностях ошибок:
в среднем 65–76 изделий вместо 133. Если нужен гарантированный максимальный
объём выборки, используйте вместо него `TwoSPRT` или план из
`kiefer_weiss_plan`.

## Пример: доля брака 10% или 20%?

Партия принимается, если доля брака 10%, и отклоняется, если 20%; обе
вероятности ошибок 5%:

```python
import random

from sequential_analysis.procedures import SPRT, Bernoulli

test = SPRT(Bernoulli(), theta0=0.10, theta1=0.20, alpha=0.05, beta=0.05)

def inspect_items(rate, seed):
    """Inspect items until the test decides; returns (decision, items inspected)."""
    rnd = random.Random(seed)
    state = test.initial_state()
    while state.decision is None:
        state, out = test.step(state, {"x": int(rnd.random() < rate)})
    return state.decision, state.n

decision, n = inspect_items(0.10, seed=1)
print(f"a good batch: {decision} after {n} items")
```

```text
a good batch: accept_h0 after 108 items
```

Как он работает на множестве партий?

```python
for rate in (0.10, 0.20):
    results = [inspect_items(rate, seed) for seed in range(2000)]
    wrong = sum(d == ("reject_h0" if rate == 0.10 else "accept_h0") for d, _ in results) / len(results)
    average = sum(n for _, n in results) / len(results)
    longest = max(n for _, n in results)
    print(f"defect rate {rate:.0%}: wrong decision {wrong:.1%}, average {average:.0f} items, longest {longest}")
```

```text
defect rate 10%: wrong decision 3.5%, average 76 items, longest 370
defect rate 20%: wrong decision 4.3%, average 65 items, longest 315
```

Критерий с фиксированным объёмом выборки и теми же вероятностями ошибок
проверяет около 133 изделий в каждой партии (нормальное приближение). SPRT
в среднем проверяет на 43–51% меньше. Однако его объём выборки случаен и не
ограничен сверху, и некоторые партии требуют гораздо больше среднего.

Пороги — вальдовские: log((1 − β)/α) и log(β/(1 − α)). Они гарантируют при
любом объёме выборки в момент остановки, что фактические вероятности ошибок
α′ и β′ удовлетворяют α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) и α′ + β′ ≤ α + β.
В момент остановки отношение правдоподобия перескакивает порог, поэтому на
практике вероятности ниже номинальных, как и здесь. Именно в этом смысле
`SPRT.guarantee == "exact"`. Чтобы получить вероятности ошибок, вычисленные
точно, а не ограниченные сверху, используйте `operating_characteristic` для
плана (см. ниже).

## Когда нужен максимальный объём выборки

* `TwoSPRT` (2-SPRT Лордена, Lorden) останавливается не позже
  фиксированного горизонта и почти минимизирует ожидаемый объём выборки в
  худшем случае.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  в `sequential_analysis.design` вычисляет оптимальный план с максимальным
  объёмом выборки методом обратной индукции. `PlanTest` его исполняет, а
  `operating_characteristic` даёт точные вероятности ошибок и ожидаемый
  объём выборки без моделирования. См.
  `examples/07_design_kiefer_weiss.py`.
* Если нужны несколько запланированных просмотров, а не просмотр после
  каждого наблюдения, используйте
  [групповой последовательный дизайн](clinical-trials.md).

## Когда SPRT не подходит

* **Гипотезы не простые.** «Доля равна 10%» против «доля равна чему угодно
  другому» — это сложная альтернатива. Используйте смешанный SPRT
  (mixture SPRT; `NormalMixtureSPRT`, `TMixtureSPRT`) или критерий на
  ставках (`BettingMeanTest`): они валидны в любой момент против любой
  альтернативы.
* **Истинное значение лежит между θ₀ и θ₁.** Тогда SPRT работает медленнее
  всего, и его ожидаемый объём выборки может превысить фиксированный. План
  Kiefer–Weiss построен именно для этого случая.

Семейства распределений для процедур на отношении правдоподобия: `Gaussian`
(известная дисперсия), `Bernoulli`, `Poisson`, `Exponential`.
