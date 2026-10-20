# Volatility and value at risk

Returns are close to unpredictable; their size is not. Calm days follow
calm days, and a large move is followed by more. GARCH models describe
this: tomorrow's variance is a weighted sum of a baseline, today's squared
surprise and today's variance. The leverage term (GJR) lets falls raise
the variance more than rises, as in equity markets. This tutorial goes
from a history to a live risk figure:

1. fit the model on a history (`fit_garch`): normal or Student t shocks,
   with or without leverage;
2. forecast tomorrow's and the next ten days' risk (`GARCH`);
3. check, while it runs, that the value at risk is breached as rarely as
   promised (`BettingMeanTest`);
4. notice when the market leaves the regime the model was fitted on
   (`QuantileEDetector` on the standardized residuals).

## The data

Twelve years of simulated daily returns, in percent. The variance follows
a GJR-GARCH with Student t shocks (5 degrees of freedom, heavier tails
than the normal). From day 2400 the baseline variance is eight times
larger: a crisis that the model fitted before it does not know.

```python
import math
import random

def returns(n, seed, crisis=None):
    """Daily returns (%): GJR-GARCH with Student t (5) shocks; from day `crisis` the baseline variance is 8 times larger."""
    rnd = random.Random(seed)
    omega, alpha, gamma, beta, df = 0.02, 0.03, 0.10, 0.91, 5.0
    v, out = omega / (1.0 - alpha - beta - 0.5 * gamma), []
    for t in range(n):
        w = omega * (8.0 if crisis is not None and t >= crisis else 1.0)
        z = rnd.gauss(0.0, 1.0) / math.sqrt(rnd.gammavariate(df / 2.0, 2.0 / df)) * math.sqrt((df - 2.0) / df)
        e = math.sqrt(v) * z
        out.append(round(0.04 + e, 4))
        v = w + alpha * e * e + beta * v + (gamma * e * e if e < 0.0 else 0.0)
    return out

r = returns(3000, seed=5, crisis=2400)
```

## 1. Fit on the history

`fit_garch` maximizes the likelihood exactly as the arch package does (the
tests check that it reaches arch's maximum and reproduces its conditional
volatility to 1e-10). `coverage=0.98` makes the reported interval the
central 98%, so its lower end is the 1% value at risk:

```python
from sequential_analysis.garch_fit import fit_garch

fit = fit_garch(r[:1500], distribution="t", asymmetric=True, horizon=10, coverage=0.98)
p = fit.parameters
print({k: round(v, 3) for k, v in p.items() if v is not None})
print(f"half-life of a shock: {math.log(0.5) / math.log(p['persistence']):.0f} days")
normal = fit_garch(r[:1500], horizon=10, coverage=0.98)
print(f"AIC: Student t {fit.aic:.1f}, normal {normal.aic:.1f}")
```

```text
{'mean': -0.011, 'omega': 0.018, 'alpha': 0.023, 'beta': 0.9, 'gamma': 0.148, 'df': 5.262, 'persistence': 0.997, 'unconditional_variance': 5.677}
half-life of a shock: 220 days
AIC: Student t 4641.5, normal 4757.6
```

The Student t fits much better than the normal (AIC lower by 116), and
the leverage term is clearly there (gamma 0.15 against alpha 0.02). The
persistence alpha + beta + gamma / 2 is estimated at 0.997 against a true
0.99: six years of data pin down the size of the reaction to a shock much
better than how long it lasts. The true parameters, with a half-life of
69 days, have a log-likelihood only 4.4 lower than the fitted ones; a
likelihood-ratio test of all six would not reject them.

## 2. Tomorrow's risk, and the next ten days'

The fitted filter continues from the state after the history. After each
return it gives the standard deviation of each of the next `horizon`
returns, the standard deviation of their sum (`cumulative_sd`, exact,
as the returns are uncorrelated) and the interval of the next return:

```python
model, state = fit.model, fit.state
for day in range(1500, 2400):
    state, out = model.step(state, {"r": r[day]})
    if day in (1500, 2000, 2399):
        print(f"day {day}: 1-day 1% VaR {-out.lower[0]:.2f}%, sd of the next 10 days' return {out.cumulative_sd[-1]:.2f}%")
```

```text
day 1500: 1-day 1% VaR 1.72%, sd of the next 10 days' return 2.25%
day 2000: 1-day 1% VaR 1.67%, sd of the next 10 days' return 2.20%
day 2399: 1-day 1% VaR 2.32%, sd of the next 10 days' return 2.94%
```

For one day the value at risk is exact under the model. For ten days the
standard deviation is exact, but the law of the sum is a mixture of
scales and not a t, so a ten-day quantile built from it is an
approximation.

## 3. Is the value at risk breached as rarely as promised?

A 1% value at risk should be breached on 1% of days, and, if the model is
right, with probability 1% on each day given everything before. That is
exactly what a test by betting needs: `BettingMeanTest` on the breach
indicators tests that their conditional mean is 0.01, and may be checked
every day. Here it watches the whole run, through the crisis:

```python
from sequential_analysis.procedures import BettingMeanTest, QuantileEDetector

model, state = fit.model, fit.state
test = BettingMeanTest(0.01, 0.0, 1.0, alternative="greater", alpha=0.01)
watch = test.initial_state()
breaches = {"before the crisis": [], "after": []}
value_at_risk, rejected = None, None
for day in range(1500, 3000):
    if value_at_risk is not None:
        breach = int(r[day] < value_at_risk)
        breaches["after" if day >= 2400 else "before the crisis"].append(breach)
        watch, verdict = test.step(watch, {"x": breach})
        if verdict.decision is not None and rejected is None:
            rejected = day
    state, out = model.step(state, {"r": r[day]})
    value_at_risk = out.lower[0]
for period, b in breaches.items():
    print(f"{period}: VaR breached on {sum(b) / len(b):.2%} of {len(b)} days")
print("the test rejected 1% on day", rejected)
```

```text
before the crisis: VaR breached on 0.78% of 899 days
after: VaR breached on 1.83% of 600 days
the test rejected 1% on day None
```

Before the crisis the breach rate is as promised. After it, it is almost
doubled, and yet the test does not reject at the 1% level within 600
days: breaches are rare, so evidence about their rate accumulates slowly.
A 1% value at risk needs years of data to be tested; this is not a
weakness of the test but of the question.

## 4. Noticing the crisis sooner

The standardized residuals z = (r - mu) / sigma are the model's own
check: under the model they are independent with a fixed distribution.
When the market's volatility rises faster than the model expects, |z|
grows. Calibrate a `QuantileEDetector` on the history (the 80th
percentile of |z|) and watch whether |z| exceeds it more often than one
day in five:

```python
history, start = [], fit.model.initial_state()
for x in r[:1500]:
    start, o = fit.model.step(start, {"r": x})
    history.append(abs(o.z))
q80 = sorted(history)[int(0.8 * len(history))]

detector = QuantileEDetector(q80, p=0.8, arl=10000, direction="increase")
model, state, alarm = fit.model, fit.state, detector.initial_state()
for day in range(1500, 3000):
    state, out = model.step(state, {"r": r[day]})
    alarm, signal = detector.step(alarm, {"x": abs(out.z)})
    if signal.alarm:
        print(f"the market left the fitted regime: alarm on day {day}")
        break
```

```text
the market left the fitted regime: alarm on day 2440
```

The alarm comes 40 days after the crisis began, long before the breach
rate could be tested. That is the moment to refit, or to switch to a
model learnt on the stream. The detector's false-alarm guarantee holds
when the residuals are independent with the 80th percentile of |z| at
q80, which the model claims; it was calibrated on the history, so treat
it as approximate.

## What to use when

| Question | Procedure | Guarantee |
|---|---|---|
| tomorrow's volatility and value at risk | `fit_garch`, then `GARCH` | under the model; agrees with arch |
| the volatility of the next h days | `GARCH(horizon=h)`, `cumulative_sd` | standard deviation exact under the model |
| is the value at risk breached too often? | `BettingMeanTest` on breach indicators | exact under the null of correct conditional coverage |
| has the market left the fitted regime? | `QuantileEDetector` or `MeanEDetector` on the residuals | the detector's own, given a calibrated quantile |
| intervals without a volatility model | `ConformalForecast` around a forecaster | long-run coverage for any data |
