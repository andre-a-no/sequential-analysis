---
description: Cómo detener una prueba A/B antes de tiempo sin inflar los falsos positivos, en Python. Pruebas válidas en cualquier momento (anytime-valid) para conversión e ingresos acotados, control del desajuste de proporción muestral (SRM) y de la tasa de falsos descubrimientos en muchas métricas, con sequential-analysis.
language: es
---

# ¿Cómo detengo una prueba A/B antes de tiempo sin inflar los falsos positivos?

> Esta es una traducción de la [página en inglés](../../guide/ab-testing.md). Aún no ha sido revisada por un hablante nativo; donde ambas difieran, prevalece la página en inglés.

**Respuesta breve.** Use una prueba válida en cualquier momento
(anytime-valid): su valor p y su intervalo de confianza siguen siendo
válidos por mucho que los consulte, así que puede detenerse en cuanto
el resultado esté claro. En sequential-analysis:

| Métrica | Procedimiento | Garantía |
|---|---|---|
| tasa de conversión (0/1) | `TwoProportionTest` | exacta |
| cualquier métrica acotada (ingresos con tope, proporción) | `BoundedABTest` | exacta |
| eventos por unidad de exposición | `RateRatioTest` | exacta para conteos de Poisson |
| métrica de razón (ingresos por sesión) | `RatioABTest` | asintótica |
| media con una covariable previa al experimento (CUPED) | `ABTest` | asintótica |
| ¿se reparte el tráfico como se pretendía? | `SampleRatioMismatch` | exacta |
| varias métricas o brazos a la vez | `MultipleTests` (e-BH) | tasa de falsos descubrimientos, exacta |

Alimente cada procedimiento con un usuario cada vez:
`state, out = test.step(state, {...})`. Actúe según `out.decision`
cuando quiera.

## Conversión: detenerse cuando los datos son concluyentes

El grupo de control convierte al 10 % de los usuarios y el de
tratamiento al 12 %. La prueba se consulta después de cada usuario y se
detiene en su primera decisión:

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

Como comparación, una prueba de tamaño muestral fijo con una potencia
del 80 % para este aumento necesita unos 3850 usuarios por brazo, 7700
en total, y solo puede leerse una vez, al final. La prueba válida en
cualquier momento paga por su libertad: para alcanzar la misma potencia
necesita entre 1.3 y 1.6 veces los usuarios de un análisis único, y
esta ejecución necesitó más que eso. A cambio, no hay que fijar de
antemano un tamaño muestral, y puede mirar el resultado a diario y
detenerse en cuanto esté claro. Cuando el efecto es mayor de lo
previsto, eso ocurre mucho antes.

## Ingresos: un intervalo exacto para una métrica acotada

`BoundedABTest` solo necesita cotas para la métrica. Ponga a los
ingresos un tope elegido antes de la prueba (aquí 30), y la secuencia
de confianza (confidence sequence) para la diferencia de medias es
exacta para cualquier distribución:

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

El intervalo se cumple simultáneamente en cada una de las 20 000
consultas, no solo en la última. Aquí todavía contiene el 0: 20 000
usuarios no bastan para establecer un aumento de alrededor de 0.5 en
una métrica tan ruidosa, así que el experimento continúa.

## Compruebe primero el reparto del tráfico

Un desajuste de proporción muestral (sample ratio mismatch, SRM)
significa que el reparto difiere del configurado, por ejemplo por un
error en la asignación o en el registro de eventos. Las estimaciones
del efecto de un experimento así no son fiables. Un desajuste de 50/50
a 52/48 se detecta mientras el experimento está en marcha:

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

## Muchas métricas a la vez

Probar diez métricas independientes al 5 % cada una da una probabilidad
de alrededor del 40 % de obtener al menos un falso descubrimiento.
`MultipleTests` combina los valores e (e-values) de todas las pruebas
con el procedimiento e-BH, de modo que la tasa de falsos descubrimientos
(false discovery rate) se mantiene en `alpha` en cualquier tiempo de
parada:

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

## Errores frecuentes

* **Aleatorice la unidad que analiza.** Si se aleatorizan usuarios,
  introduzca un registro por usuario, no por vista de página. Para
  métricas por sesión use `RatioABTest`, que trabaja con los totales por
  usuario.
* **Fije el tope de una métrica acotada antes de la prueba.** Elegirlo
  después de ver los datos anula la garantía.
* **Los procedimientos asintóticos necesitan muestras grandes.** Para
  `ABTest` y `RatioABTest` el intervalo solo es aproximadamente válido en
  ejecuciones largas. Prefiera los procedimientos exactos cuando sean
  aplicables.
* **La asignación adaptativa del tráfico** (bandidos) necesita una
  prueba que siga siendo válida cuando el reparto depende de los
  resultados: `TwoProportionTest(method="universal")` o
  `BoundedABTest(propensity_input=...)`. Véase el
  [tutorial, §10](../../tutorials/ab-test.md).

Más: el [tutorial de pruebas A/B](../../tutorials/ab-test.md) (CUPED,
métricas de razón, tasas, planificación de la duración) y
[un programa de experimentos](../../tutorials/experiment-programme.md)
(tasa de falsos descubrimientos sobre muchos experimentos).
