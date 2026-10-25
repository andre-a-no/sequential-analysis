---
description: Почему ежедневная проверка p-значения увеличивает долю ложноположительных результатов в A/B-тестах и исследованиях (проблема подглядывания, peeking), и три семейства последовательных методов, которые её решают, на Python с sequential-analysis.
language: ru
---

# Почему нельзя смотреть на p-значение каждый день?

> Это перевод [страницы на английском языке](../../guide/peeking.md). Перевод ещё не проверен носителем языка; если тексты расходятся, верной считается английская страница.

**Коротко.** Критерий с фиксированным объёмом выборки обещает долю
ложноположительных результатов 5%, только если посмотреть на результат один
раз, при запланированном объёме выборки. Если смотреть многократно и
останавливаться при первом p < 0,05, у случайности появляется много шансов
вас обмануть. При 20 просмотрах доля ложноположительных результатов
вырастает примерно до 25%. Последовательные методы (sequential methods)
рассчитаны на многократные просмотры. С ними эта доля остаётся не выше 5%,
как бы часто вы ни смотрели и когда бы ни остановились.

## Проблема подглядывания в цифрах

Две группы с одинаковой конверсией 10% (A/A-тест), 2000 пользователей,
200 повторений. «Подглядывание» (peeking) — это обычный z-критерий для двух
долей после каждых 100 пользователей с остановкой при первом p < 0,05.
Последовательный `TwoProportionTest` проверяется после каждого отдельного
пользователя:

```python
import math
import random

from sequential_analysis.procedures import TwoProportionTest

def a_a_test(seed, users=2000):
    """Alternating arms, both converting 10% of the time: any 'effect' is a false positive."""
    rnd = random.Random(seed)
    return [(user % 2, int(rnd.random() < 0.10)) for user in range(users)]

def peeking(data, looks):
    """The z-test for two proportions after every len(data) / looks users; True if it ever rejects."""
    successes, trials, every = [0, 0], [0, 0], len(data) // looks
    for i, (arm, y) in enumerate(data, start=1):
        successes[arm] += y
        trials[arm] += 1
        if i % every == 0:
            pooled = sum(successes) / sum(trials)
            se = math.sqrt(pooled * (1 - pooled) * (1 / trials[0] + 1 / trials[1]))
            if se > 0 and abs(successes[1] / trials[1] - successes[0] / trials[0]) / se > 1.96:
                return True
    return False

def sequential(data):
    """The anytime-valid test, looked at after every user; True if it ever rejects."""
    test = TwoProportionTest(alpha=0.05)
    state = test.initial_state()
    for arm, y in data:
        state, out = test.step(state, {"arm": arm, "y": y})
        if out.decision is not None:
            return True
    return False

runs = [a_a_test(seed) for seed in range(200)]
print(f"z-test, one look at the end:   {sum(peeking(r, 1) for r in runs) / len(runs):.1%} false positives")
print(f"z-test, 20 looks:              {sum(peeking(r, 20) for r in runs) / len(runs):.1%}")
print(f"TwoProportionTest, 2000 looks: {sum(sequential(r) for r in runs) / len(runs):.1%}")
```

```text
z-test, one look at the end:   4.5% false positives
z-test, 20 looks:              28.0%
TwoProportionTest, 2000 looks: 5.0%
```

Единственный просмотр выполняет своё обещание. Двадцать просмотров
увеличивают вероятность ошибки примерно в шесть раз. Последовательный
критерий, просматриваемый после каждого из 2000 пользователей, удерживает её
на уровне 5%. В этом и состоит обещание: его гарантия — **exact**
(`TwoProportionTest.guarantee == "exact"`), то есть доля ложноположительных
результатов не выше 5% при любом объёме выборки, как бы часто вы ни смотрели.
При 200 повторениях 10 ложноположительных результатов — именно то, что даёт
точный уровень 5%.

## Три семейства последовательных методов

| Семейство | Когда можно смотреть | Типичное применение | В sequential-analysis |
|---|---|---|---|
| **Последовательные критерии отношения вероятностей** (sequential probability ratio tests; Wald 1945) | после каждого наблюдения | одна простая гипотеза против другой, наименьшее среднее число наблюдений: контроль качества, моделирование, психофизика | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Групповые последовательные дизайны** (group sequential designs; Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | в нескольких запланированных промежуточных анализах | клинические исследования с комитетом по мониторингу данных | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Вывод, валидный в любой момент** (anytime-valid inference): e-значения, доверительные последовательности, смешанный SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | после каждого наблюдения, остановка по любой причине | онлайн A/B-тесты, дашборды мониторинга | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**Чем за это платят.** Чем чаще вы смотрите, тем больше данных нужно при
запланированном эффекте:

* групповому последовательному дизайну с четырьмя анализами нужно на 1–20%
  больше пациентов, чем одному анализу;
* критерию для двух долей, валидному в любой момент, нужно в 1,3–1,6 раза
  больше пользователей, чем одному анализу.

Взамен большой эффект позволяет остановить эксперимент досрочно, и никому не
нужно заранее фиксировать объём выборки.

## Когда проблема не в этом

Подглядывание увеличивает вероятность ошибок, только если ваши действия
зависят от увиденного. Если вы смотрите на дашборд, но всегда доводите
эксперимент до запланированного объёма и проверяете гипотезу один раз,
критерий с фиксированным объёмом выборки валиден. В этом случае он к тому же
самый эффективный.

Далее: [досрочная остановка A/B-теста](ab-testing.md),
[доверительные последовательности](confidence-sequences.md),
[глоссарий](glossary.md).
