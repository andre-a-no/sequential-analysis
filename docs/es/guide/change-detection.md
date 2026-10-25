---
description: Cómo detectar un cambio en un flujo de lecturas de sensores, latencias o métricas en Python con CUSUM, Shiryaev–Roberts, detectores e no paramétricos y detección bayesiana de puntos de cambio en línea. Falsas alarmas controladas mediante la longitud media de corrida (ARL), con sequential-analysis.
language: es
---

# ¿Cómo detecto un cambio en un flujo de mediciones?

> Esta es una traducción de la [página en inglés](../../guide/change-detection.md). Aún no ha sido revisada por un hablante nativo; donde ambas difieran, prevalece la página en inglés.

**Respuesta breve.** Use un detector de puntos de cambio en línea
(online change-point detector). Vigila el flujo de datos y da la alarma
en cuanto la distribución parece haber cambiado. Sus falsas alarmas se
controlan mediante la **longitud media de corrida** (average run
length, ARL): el número esperado de observaciones hasta una falsa
alarma mientras nada ha cambiado. En sequential-analysis:

| Qué conoce antes del cambio | Procedimiento | Garantía |
|---|---|---|
| ambas distribuciones (p. ej., normal, media 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exacta: ARL ≥ e^umbral |
| solo la media y cotas para los valores | `MeanEDetector` | exacta para toda distribución de ese tipo |
| solo un cuantil (p. ej., el percentil 95 de la latencia) | `QuantileEDetector` | exacta para toda distribución |
| un modelo con parámetros desconocidos, antes y después | `BayesianChangePoint` | bajo el modelo y la distribución a priori |

## Un sensor cuya media se desplaza

Un sensor de temperatura marca 70.0 °C con un ruido de desviación
típica 0.5. A partir de la lectura 600, la media es 70.4. CUSUM con
umbral log(1000) ≈ 6.9 tiene una ARL de al menos 1000 lecturas:

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

Un desplazamiento de menos de una desviación típica es invisible a
simple vista en cualquier lectura aislada. CUSUM acumula la evidencia y
lo encuentra.

## Cuando las lecturas no son normales

La ARL de CUSUM solo se cumple si las lecturas siguen las distribuciones
que se le indicaron. Con datos asimétricos (amplitudes de vibración,
latencias, longitudes de cola) da falsas alarmas con mucha más
frecuencia de la prevista. Los detectores e (e-detectors) necesitan
mucho menos:

* `MeanEDetector` necesita la media antes del cambio y cotas para los
  valores.
* `QuantileEDetector` solo necesita un cuantil antes del cambio.

Su ARL es al menos la objetivo para **toda** distribución con esa media
o ese cuantil:

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

En la práctica, el cuantil anterior al cambio se estima a partir de un
periodo tranquilo. La garantía se cumple entonces de forma aproximada,
y mejor cuanto más largo sea ese periodo.

## Elegir la ARL

La ARL equilibra falsas alarmas y retardo. Con una lectura por minuto,
una ARL de 1000 lecturas significa una falsa alarma cada 17 horas
aproximadamente de funcionamiento normal, por sensor. Con 50 sensores,
eso son unas 70 al día. Elija la ARL a partir del número de falsas
alarmas diarias que pueda asumir con todos los sensores juntos: aquí,
una ARL de 1 000 000 de lecturas reduce los 50 sensores a alrededor de
una falsa alarma cada dos semanas. Eso cuesta menos de lo que parece,
porque el retardo de detección solo crece con el logaritmo de la ARL.
Para CUSUM, el umbral pasa de 6.9 a 13.8, y el retardo aproximadamente
se duplica.

Estos detectores son herramientas de monitoreo, no sistemas de
seguridad. No los use en lugar de un sistema instrumentado de seguridad
certificado.

Más: [tutorial: monitoreo de procesos y detección de cambios](../../tutorials/monitoring.md),
[regímenes con modelos ocultos de Markov](../../tutorials/regimes.md),
[referencia: detección de cambios](../../reference/detection.md).
