# Several series: lead, lag and pairs

Strategies built on several series ask three questions. Does one series
lead another? Can its past improve the other's forecast? Do two prices
move together, and do they still? This tutorial answers them on
simulated daily data:

1. map the correlations at every lag (`CrossCorrelation`);
2. test whether the lead is real, at any time (`Lagged` around
   `AnytimeLinearModel`: a Granger test);
3. forecast both series together (`fit_var`, `VectorAutoRegressive`);
4. follow the hedge ratio of a pair and its spread (`DynamicRegression`);
5. notice when the pair breaks (`QuantileEDetector`).

Nothing here finds money on its own. Real leads are small, short-lived
and quickly traded away. What the procedures add is honest bookkeeping:
a lead is declared only on evidence that stays valid however often you
look, and a broken relationship is noticed instead of averaged in.

## The data

Two daily return series, in percent. The follower `a` repeats 0.3 of the
leader's move two days later, and both have their own noise:

```python
import math
import random

def lead_lag(n, seed, lead=2, effect=0.3):
    """Daily returns (%) of a leader b and a follower a, which repeats a part of b's move `lead` days later."""
    rnd = random.Random(seed)
    b = [round(rnd.gauss(0.0, 1.0), 4) for _ in range(n)]
    a = [round((effect * b[t - lead] if t >= lead else 0.0) + rnd.gauss(0.0, 1.0), 4) for t in range(n)]
    return a, b

a, b = lead_lag(1500, seed=1)
```

## 1. Which series leads, and by how much

`CrossCorrelation` keeps the correlation of a_t with b_{t-lag} for every
lag from -L to L. A positive lag with a large correlation says that `b`
leads `a` by that many steps. With `forgetting` below 1 it follows a
relationship that drifts:

```python
from sequential_analysis.procedures import CrossCorrelation

cc = CrossCorrelation("a", "b", max_lag=5)
state = cc.initial_state()
for x, y in zip(a, b):
    state, out = cc.step(state, {"a": x, "b": y})
print("lead:", out.lead, "correlation:", round(out.correlation, 3))
print({lag: round(r, 2) for lag, r in zip(out.lags, out.correlations)})
```

```text
lead: 2 correlation: 0.305
{-5: 0.01, -4: 0.03, -3: 0.05, -2: -0.0, -1: 0.01, 0: 0.04, 1: 0.01, 2: 0.31, 3: 0.04, 4: 0.01, 5: -0.01}
```

The map is descriptive. Out of eleven correlations, the largest is
large partly by selection, and with a hundred pairs of series one of
them will always look like a lead. The next step tests it.

## 2. Is the lead real?

The Granger question: does b's past improve the forecast of a once a's
own past is used? It is a regression of a_t on a's lags (nuisance) and
b's lags (tested). `AnytimeLinearModel` tests the tested coefficients
with an e-value that may be checked every day. `Lagged` feeds it the
lags: with `{"a": 3, "b": 3}` it receives `a_lag1` to `a_lag3` and
`b_lag1` to `b_lag3` besides today's `a`:

```python
from sequential_analysis import Lagged, lag_name
from sequential_analysis.procedures import AnytimeLinearModel

def granger(p):
    own = tuple(lag_name("a", j) for j in range(1, p + 1))
    other = tuple(lag_name("b", j) for j in range(1, p + 1))
    return Lagged(AnytimeLinearModel(input="a", covariates=own, tested=other, alpha=0.01), {"a": p, "b": p})

def first_rejection(test, a, b):
    state = test.initial_state()
    for day, (x, y) in enumerate(zip(a, b)):
        state, out = test.step(state, {"a": x, "b": y})
        if out.ready and out.inner.decision is not None:
            return day, out.inner
    return None, out.inner

day, result = first_rejection(granger(3), a, b)
print(f"b leads a: decided on day {day}; effects of b's lags {[round(e, 2) for e in result.estimates]}")

a0, b0 = lead_lag(1500, seed=2, effect=0.0)
day0, result0 = first_rejection(granger(3), a0, b0)
print(f"no lead: decided {day0}; e-value after 1500 days {math.exp(result0.log_e_value):.2f}")
```

```text
b leads a: decided on day 272; effects of b's lags [0.05, 0.31, 0.01]
no lead: decided None; e-value after 1500 days 0.00
```

The test decides after 272 days and puts the effect on the second lag.
On a pair with no lead it never decides, though it was looked at every
day. The level, 1%, holds at any stopping time when the regression
model holds: errors normal with a constant variance. Returns have
heavier tails than that, so treat the level as approximate on real
data.

Testing many pairs or many lags multiplies the chances of a false lead.
`OnlineFDR` takes the log e-values of a stream of such tests and keeps
the false discovery rate in check
([programme tutorial](experiment-programme.md)).

## 3. Forecast both together

A vector autoregression forecasts every series from the recent past of
all of them. `fit_var` fits it on a history by least squares, as
statsmodels does, and chooses the order by AIC. The fitted model
continues live from the state after the history:

```python
from sequential_analysis.forecasting import fit_ar, fit_var

records = [{"a": x, "b": y} for x, y in zip(a, b)]
fit = fit_var(records[:1000], ("a", "b"), max_order=5)
print("order chosen by AIC:", fit.parameters["order"])
print("effect of b two days ago on a:", round(fit.parameters["coefficients"][1][0][1], 2))

def mean_absolute_error(model, state, rows, error):
    total = 0.0
    for x in rows:
        state, out = model.step(state, x)
        total += abs(error(out))
    return total / len(rows)

joint = mean_absolute_error(fit.model, fit.state, records[1000:], lambda o: o.error[0])
ar = fit_ar([{"y": x} for x in a[:1000]], 3)
alone = mean_absolute_error(ar.model, ar.state, [{"y": x} for x in a[1000:]], lambda o: o.error)
print(f"mean absolute error of a, days 1000-1499: {joint:.3f} with b's past, {alone:.3f} without")
```

```text
order chosen by AIC: 2
effect of b two days ago on a: 0.33
mean absolute error of a, days 1000-1499: 0.781 with b's past, 0.802 without
```

`coefficients[j][i][k]` is the effect of series k at lag j + 1 on
series i. The gain in accuracy is small, as it should be: b's past
explains about 8% of a's variance here.

Without a history, `VectorAutoRegressive(("a", "b"), 2,
forgetting=0.99)` learns the coefficients and the noise covariance on
the stream. Its one-step forecasts are multivariate Student t, exact
under the model; with one series it is `AutoRegressive`.

## 4. A pair and its spread

Two prices that share a driver move together: y = alpha + beta x +
spread, with a spread that returns to zero. Pairs trading bets on the
return. Both alpha and beta drift. Here the log prices are random walks,
beta drifts slowly, and on day 1500 the relationship breaks: the spread
stops returning.

```python
def pair(n, seed, breaks_at=None):
    rnd = random.Random(seed)
    x, beta, spread, out = 4.0, 1.5, 0.0, []
    for t in range(n):
        x += rnd.gauss(0.0, 0.01)
        beta += rnd.gauss(0.0, 0.0005)
        if breaks_at is not None and t >= breaks_at:
            spread += rnd.gauss(0.0, 0.01)
        else:
            spread = 0.9 * spread + rnd.gauss(0.0, 0.01)
        out.append({"x": round(x, 5), "y": round(0.2 + beta * x + spread, 5), "beta": beta})
    return out

prices = pair(2000, seed=3, breaks_at=1500)
```

`DynamicRegression` is the regression with drifting coefficients: the
dynamic linear model of West and Harrison, with a discount factor for
the drift and the noise variance learnt alongside. Its standardized
one-step error `z` is the spread in units of its own uncertainty, the
usual trading signal:

```python
from sequential_analysis.procedures import DynamicRegression

hedge = DynamicRegression(("x",), discount=0.999)
state, zs, betas = hedge.initial_state(), [], []
for row in prices:
    state, out = hedge.step(state, {"x": row["x"], "y": row["y"]})
    zs.append(out.z)
    betas.append(out.coefficients[1])
for day in (300, 800, 1400):
    print(f"day {day}: hedge ratio {betas[day]:.3f}, true {prices[day]['beta']:.3f}")
calm = zs[200:1500]
print(f"days with |z| > 2 before the break: {sum(abs(z) > 2 for z in calm) / len(calm):.1%}")
```

```text
day 300: hedge ratio 1.730, true 1.481
day 800: hedge ratio 1.527, true 1.493
day 1400: hedge ratio 1.492, true 1.484
days with |z| > 2 before the break: 5.1%
```

The hedge ratio needs a few hundred days to settle: the prices move
little, so x carries little information about beta. A larger discount
(closer to 1) follows the drift more slowly and estimates more steadily.
About 5% of days have |z| > 2, as for a normal spread.

## 5. When the pair breaks

After the break the spread wanders off and |z| stays large. A detector
on |z| notices it. `QuantileEDetector` assumes nothing about the
distribution, only the quantile before the change. Calibrate it on the
calm period: the 80th percentile of |z|, then watch whether |z| exceeds
it more often than one day in five:

```python
from sequential_analysis.procedures import QuantileEDetector

history = sorted(abs(z) for z in zs[300:1200])
q80 = history[int(0.8 * len(history))]
detector = QuantileEDetector(q80, p=0.8, arl=10000, direction="increase")
state = detector.initial_state()
for day in range(1200, 2000):
    state, out = detector.step(state, {"x": abs(zs[day])})
    if out.alarm:
        print(f"the pair broke: alarm on day {day}")
        break
```

```text
the pair broke: alarm on day 1571
```

The alarm comes 71 days after the break. The detector's false-alarm
guarantee (an average of at least 10,000 days between false alarms)
assumes independent observations; a mean-reverting spread makes |z|
autocorrelated, so on such data the guarantee is approximate, and the
threshold was calibrated on a history, not known. Stop trading the pair
at the alarm, refit, and decide again.

## What to use when

| Question | Procedure | Guarantee |
|---|---|---|
| which lag, roughly? | `CrossCorrelation` | descriptive |
| is the lead real? | `Lagged` + `AnytimeLinearModel`; many pairs: `OnlineFDR` | exact under the regression model |
| forecast several series | `fit_var`, `VectorAutoRegressive` | under the model |
| hedge ratio, spread | `DynamicRegression` | under the model |
| has the relationship broken? | `QuantileEDetector` or `MeanEDetector` on the spread | approximate for dependent data |
