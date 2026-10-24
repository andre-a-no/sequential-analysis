---
description: How to detect a change in a stream of sensor readings, latencies or metrics in Python, with CUSUM, Shiryaev–Roberts, nonparametric e-detectors and Bayesian online change-point detection. False alarms controlled through the average run length (ARL), with sequential-analysis.
---

# How do I detect a change in a stream of measurements?

**Short answer.** Use an online change-point detector. It watches the
stream and raises an alarm as soon as the distribution appears to have
changed. Its false alarms are controlled by the **average run length**
(ARL): the expected number of observations to a false alarm while
nothing has changed. In sequential-analysis:

| You know before the change | Procedure | Guarantee |
|---|---|---|
| both distributions (e.g. normal, mean 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| only the mean, and bounds on the values | `MeanEDetector` | exact for every such distribution |
| only a quantile (e.g. the 95th percentile of latency) | `QuantileEDetector` | exact for every distribution |
| a model with unknown parameters, before and after | `BayesianChangePoint` | under the model and prior |

## A sensor whose mean shifts

A temperature sensor reads 70.0 °C with noise of standard deviation
0.5. From reading 600 on, the mean is 70.4. CUSUM with threshold
log(1000) ≈ 6.9 has an ARL of at least 1,000 readings:

```python
import math
import random

from sequential_analysis.procedures import CUSUM, Gaussian

rnd = random.Random(1)
readings = [rnd.gauss(70.0, 0.5) for _ in range(600)] + [rnd.gauss(70.4, 0.5) for _ in range(400)]

detector = CUSUM(Gaussian(sigma=0.5), theta0=70.0, theta1=70.4, threshold=math.log(1000))
state = detector.initial_state()
for t, x in enumerate(readings, start=1):
    state, out = detector.step(state, {"x": x})
    if out.alarm:
        print(f"alarm at reading {t}, {t - 600} readings after the shift")
        break
```

```text
alarm at reading 615, 15 readings after the shift
```

A shift of less than one standard deviation is invisible to the eye in
any single reading. CUSUM accumulates the evidence and finds it.

## When the readings are not normal

CUSUM's ARL holds only if the readings follow the distributions you gave
it. For skewed data (vibration amplitudes, latencies, queue lengths) it
raises false alarms far more often than planned. The e-detectors need
much less:

* `MeanEDetector` needs the mean before the change and bounds on the
  values.
* `QuantileEDetector` needs only a quantile before the change.

Their ARL is at least the target for **every** distribution with that
mean or quantile:

```python
from sequential_analysis.procedures import QuantileEDetector

rnd = random.Random(2)
vibration = [rnd.lognormvariate(0.0, 0.8) for _ in range(800)] + [rnd.lognormvariate(0.5, 0.8) for _ in range(400)]
q95 = math.exp(0.8 * 1.6449)          # the 95th percentile before the change
p95 = QuantileEDetector(q0=q95, p=0.95, arl=1000, direction="increase", statistic="cusum")
state = p95.initial_state()
for t, x in enumerate(vibration, start=1):
    state, out = p95.step(state, {"x": x})
    if out.alarm:
        print(f"the 95th percentile rose: alarm at reading {t}, {t - 800} readings after the change")
        break
```

```text
the 95th percentile rose: alarm at reading 887, 87 readings after the change
```

In practice the quantile before the change is estimated from a calm
period. The guarantee then holds approximately, the better the longer
that period.

## Choosing the ARL

The ARL trades false alarms against delay. At one reading per minute,
an ARL of 1,000 readings means a false alarm every 17 hours or so of
normal operation, per sensor. With 50 sensors that is about 70 a day.
Choose the ARL from the number of false alarms per day you can afford
across all the sensors together: here, an ARL of 1,000,000 readings
brings the 50 sensors down to about one false alarm every two weeks.
That costs less than it seems, because the detection delay grows only
with the logarithm of the ARL. For CUSUM the threshold goes from 6.9 to
13.8, and the delay roughly doubles.

These detectors are monitoring tools, not safety systems. Do not use
them in place of a certified safety instrumented system.

More: [tutorial: process monitoring and change detection](../tutorials/monitoring.md),
[regimes with hidden Markov models](../tutorials/regimes.md),
[reference: change detection](../reference/detection.md).
