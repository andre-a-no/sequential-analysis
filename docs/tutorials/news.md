# A news stream and the market

News arrives at irregular times, in bursts, and some of it moves prices.
Turning text into a number -- a sentiment score, a relevance to the
ticker -- is the job of a language model outside this library. This
tutorial starts where that model stops, with a stream of scored items,
and asks what a strategy needs to know:

1. how the news flow behaves, and when it changes (`fit_hawkes`,
   `HawkesProcess`);
2. what each daily bar knew, without looking ahead (`AsOfJoin`);
3. whether the scores predict returns, tested at any time (`Lagged`
   around `AnytimeLinearModel`);
4. how prices move after good and bad news (`EventStudy`).

## The data

Six years of trading days, simulated. News comes as a Hawkes process:
each item raises the chance of more for a while, so items cluster. From
day 1200 the background rate triples, as in a crisis. Each item has a
true tone, good or bad, and a score in [-1, 1] from the language model,
which is right most of the time. It becomes available some time after
publication -- received, parsed, scored -- and the market drifts after it:
by 0.3% times the tone on the next day and by 0.15% on the day after.

```python
import math
import random

from sequential_analysis.events import simulate_hawkes

def news_flow(seed):
    """News over 1500 trading days in bursts (a Hawkes process); from day 1200, three times the baseline."""
    calm = simulate_hawkes(0.3, 0.6, 1.5, 1200.0, seed=seed)
    busy = simulate_hawkes(0.9, 0.6, 1.5, 1500.0, start=1200.0, seed=seed + 1)
    rnd = random.Random(seed)
    items = []
    for t in calm + busy:
        tone = rnd.choice((-1, 1))  # what the news really says
        score = round(max(-1.0, min(1.0, 0.6 * tone + rnd.gauss(0.0, 0.4))), 3)  # what the model makes of it
        arrived = t + rnd.uniform(0.01, 0.5)  # received, parsed and scored
        items.append({"published": t, "arrived": arrived, "tone": tone, "score": score})
    return items

def market(items, n_days, seed):
    """Daily returns (%): noise, and a drift after news -- 0.3 the next day, 0.15 the day after, times its tone."""
    rnd = random.Random(seed)
    r = [rnd.gauss(0.0, 1.0) for _ in range(n_days + 3)]
    for item in items:
        day = math.ceil(item["arrived"])  # the first bar after the item became available
        for lag, size in ((1, 0.3), (2, 0.15)):
            if day + lag <= n_days:
                r[day + lag] += size * item["tone"]
    return [round(v, 4) for v in r[1:n_days + 1]]  # bars at the end of days 1..n

news = news_flow(seed=4)
returns = market(news, 1500, seed=5)
print(len(news), "news items")
```

```text
990 news items
```

## 1. The news flow

A Hawkes process has a baseline rate mu, a jump alpha that each item
adds to the rate, and a decay beta of that excess. The branching ratio
alpha / beta is the average number of items each item triggers.
`fit_hawkes` finds them by maximum likelihood on a history. Its
likelihood is computed exactly, in one pass:

```python
from sequential_analysis.events import fit_hawkes

history = [x["published"] for x in news if x["published"] < 750]
fit = fit_hawkes(history, start=0.0, end=750.0)
p = fit.parameters
print(f"baseline {p['baseline']:.2f} a day, branching ratio {p['branching']:.2f}, decay {p['decay']:.2f}")
```

```text
baseline 0.25 a day, branching ratio 0.41, decay 1.71
```

The true values are 0.3, 0.4 and 1.5. The fitted `HawkesProcess` then
runs live. For each item it reports the intensity just before and just
after, the expected number of items in a coming window (with `window=`),
and the compensator: the integral of the intensity over the gap before
the item. Under the model the compensators are independent standard
exponentials, whose median is ln 2. When the flow speeds up, they shrink.
A `QuantileEDetector` on them notices, assuming nothing more:

```python
from sequential_analysis.procedures import QuantileEDetector

model, state = fit.model, fit.state
detector = QuantileEDetector(math.log(2.0), p=0.5, arl=1000, direction="decrease")
watch = detector.initial_state()
for x in news:
    if x["published"] < 750:
        continue
    state, out = model.step(state, {"t": x["published"]})
    watch, alarm = detector.step(watch, {"x": out.compensator})
    if alarm.alarm:
        print(f"the news flow changed: alarm at day {x['published']:.1f}")
        break
```

```text
the news flow changed: alarm at day 1295.3
```

The change came on day 1200. The alarm needs about 95 days because the
flow had to differ from the model for long enough. With `arl=1000`, a
false alarm comes on average no sooner than after 1000 items.

## 2. What each bar knew

A daily bar should see the news that had arrived by its close, no more.
`AsOfJoin` attaches to each bar the items that arrived since the
previous bar and are not later than this one: their count and the sum
of their scores, and, with a `half_life`, sums in which older items
count less. An item that arrives after the bar it belongs to waits for
the next one and is counted as late. Give every item the time it became
available, not the time it was published: that is what keeps a backtest
from looking ahead.

```python
from sequential_analysis import AsOfJoin, Observation

stream = [("r", r, float(day)) for day, r in enumerate(returns, start=1)]
stream += [("news", x["score"], x["arrived"]) for x in news]
stream.sort(key=lambda e: (e[2], e[0] == "r"))  # in the order of availability, a bar after news of its moment

join = AsOfJoin("r", "news", half_life=1.0)
bars = []
for i, (name, value, time) in enumerate(stream):
    bars += join.push(Observation(name, value, seq=i, time=time))
print(len(bars), "bars, late items:", join.late)
print(next({k: round(v, 3) for k, v in row.items()} for row in bars if row["news_count"] > 1))
```

```text
1500 bars, late items: 0
{'r': 0.669, 'news_count': 2, 'news_sum': -0.806, 'news_decayed': -0.444, 'news_decayed_count': 1.259}
```

In a live run the same join is the topology:
`Run(procedure, topology=AsOfJoin("r", "news", half_life=1.0))`, fed
the bars and the news as they come. Its state -- items waiting for a
bar, the decayed sums -- is in the run's checkpoints. It is not
confluent: what a bar sees depends on what arrived before it, so a
replay must deliver the two inputs in their original order.

## 3. Do the scores predict returns?

Regress today's return on the scores of the last two bars and test the
two coefficients. `Lagged` provides `news_sum_lag1` and `news_sum_lag2`;
`AnytimeLinearModel` gives an e-value that may be checked every day:

```python
from sequential_analysis import Lagged
from sequential_analysis.procedures import AnytimeLinearModel

test = Lagged(AnytimeLinearModel(input="r", covariates=(), tested=("news_sum_lag1", "news_sum_lag2"),
                                 alpha=0.01), {"news_sum": 2})
state, decided = test.initial_state(), None
for day, row in enumerate(bars, start=1):
    state, out = test.step(state, {"r": row["r"], "news_sum": row["news_sum"]})
    if decided is None and out.ready and out.inner.decision is not None:
        decided = day
print(f"the scores predict returns: decided on day {decided}; "
      f"effects per unit of score {[round(e, 2) for e in out.inner.estimates]}")
```

```text
the scores predict returns: decided on day 611; effects per unit of score [0.34, 0.23]
```

The test needs 611 days of data at the 1% level, though the drift is
built in. Effects of this size are small next to the daily noise. A
backtest that tries many scores, lags and thresholds will find such
effects by chance unless the tests are counted: `OnlineFDR` takes their
e-values and keeps the false discovery rate.

## 4. After good news, after bad news

`EventStudy` averages the cumulative return over the days after an
event, with a confidence sequence for each horizon. Here an event is a
bar whose news adds up to a clearly good (or bad) score. Overlapping
windows would share returns, so by default an event inside the window of
the previous one is skipped and counted:

```python
from sequential_analysis.procedures import EventStudy

for name, sign in (("good", 1), ("bad", -1)):
    study = EventStudy(3, alpha=0.1, start=20)
    state = study.initial_state()
    for row in bars:
        event = int(row["news_count"] > 0 and sign * row["news_sum"] > 0.3)
        state, out = study.step(state, {"r": row["r"], "event": event})
    print(f"{name} news: {out.events} events ({out.skipped} skipped); cumulative return after 1, 2, 3 days "
          + ", ".join(f"{m:+.2f} [{lo:+.2f}, {hi:+.2f}]" for m, lo, hi in zip(out.mean, out.lower, out.upper)))
```

```text
good news: 148 events (58 skipped); cumulative return after 1, 2, 3 days +0.25 [-0.01, +0.52], +0.42 [+0.03, +0.82], +0.49 [-0.00, +0.99]
bad news: 154 events (62 skipped); cumulative return after 1, 2, 3 days -0.27 [-0.52, -0.02], -0.48 [-0.85, -0.11], -0.58 [-1.03, -0.14]
```

The drift is there: about +0.3 then +0.15 after good news, the mirror
after bad news, less where a bar's items disagree. The intervals hold
for all horizons together, at any number of events, asymptotically; 150
events leave them wide. In practice `r` should be the abnormal return:
the return minus what the market explains, for instance the error of a
`DynamicRegression` of the stock on the index.

## Cautions

* **Latency.** The edge in news is mostly in the first minutes. On daily
  bars much of it is already in the price; the simulated drift here is
  generous.
* **The score drifts too.** A new version of the language model changes
  the scores' distribution. A `QuantileEDetector` on the scores notices.
* **Event times.** Use the time an item became available to you. The
  publication time, often a few seconds to hours earlier, makes a
  backtest look better than any live run.
