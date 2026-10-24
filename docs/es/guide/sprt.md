---
description: Cómo ejecutar la prueba secuencial de razón de probabilidades de Wald (SPRT) en Python con sequential-analysis. Tasas de error, tamaño muestral medio frente a una prueba de tamaño fijo y las alternativas truncadas (2-SPRT, planes óptimos de Kiefer–Weiss).
language: es
---

# ¿Cómo ejecuto la SPRT de Wald en Python?

> Esta es una traducción de la [página en inglés](../../guide/sprt.md). Aún no ha sido revisada por un hablante nativo; donde ambas difieran, prevalece la página en inglés.

**Respuesta breve.** `SPRT(family, theta0, theta1, alpha, beta)`, de
`sequential_analysis.procedures`, implementa la prueba secuencial de
razón de probabilidades de Wald (sequential probability ratio test,
SPRT). Decide entre dos hipótesis simples con el menor número medio de
observaciones. Aliméntela con una observación cada vez y deténgase en la
primera decisión. En el ejemplo de abajo necesita aproximadamente la
mitad de observaciones que una prueba de tamaño muestral fijo con las
mismas tasas de error: entre 65 y 76 artículos de media en lugar de
133. Si necesita un tamaño muestral máximo garantizado, use en su lugar
`TwoSPRT` o un plan de `kiefer_weiss_plan`.

## Ejemplo: ¿la tasa de defectos es del 10 % o del 20 %?

Un lote se acepta si su tasa de defectos es del 10 % y se rechaza si es
del 20 %, con ambas tasas de error del 5 %:

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

¿Qué tal funciona a lo largo de muchos lotes?

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

Una prueba de tamaño muestral fijo con las mismas tasas de error
inspecciona unos 133 artículos en cada lote (aproximación normal). La
SPRT inspecciona de media entre un 43 % y un 51 % menos. Sin embargo, su
tamaño muestral es aleatorio y no tiene límite superior, y unos pocos
lotes tardan mucho más que la media.

Los umbrales son los de Wald: log((1 − β)/α) y log(β/(1 − α)).
Garantizan, para cualquier tamaño muestral en la parada, que las tasas
de error reales α′ y β′ cumplen α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) y
α′ + β′ ≤ α + β. La razón de verosimilitudes rebasa los umbrales
(overshoot) al detenerse, así que en la práctica las tasas quedan por
debajo de las nominales, como aquí. Ese es el sentido de
`SPRT.guarantee == "exact"`. Para obtener tasas de error calculadas con
exactitud en lugar de acotadas, use `operating_characteristic` sobre un
plan (véase más abajo).

## Cuando necesita un tamaño muestral máximo

* `TwoSPRT` (la 2-SPRT de Lorden) se detiene antes de un horizonte fijo
  y casi minimiza el tamaño muestral esperado en el peor caso.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`,
  en `sequential_analysis.design`, calcula por inducción hacia atrás el
  plan óptimo con un tamaño muestral máximo. `PlanTest` lo ejecuta, y
  `operating_characteristic` da sus tasas de error exactas y su tamaño
  muestral esperado sin simulación. Véase
  `examples/07_design_kiefer_weiss.py`.
* Para unas pocas consultas planificadas en lugar de una por
  observación, use un
  [diseño secuencial por grupos](clinical-trials.md).

## Cuando la SPRT no es la herramienta adecuada

* **Las hipótesis no son simples.** «La tasa es del 10 %» frente a «la
  tasa es cualquier otra» es una alternativa compuesta. Use una SPRT de
  mezcla (mixture SPRT: `NormalMixtureSPRT`, `TMixtureSPRT`) o una prueba
  por apuestas (testing by betting: `BettingMeanTest`), que son válidas
  en cualquier momento frente a toda alternativa.
* **El valor verdadero está entre θ₀ y θ₁.** La SPRT es entonces más
  lenta, y su tamaño muestral esperado puede superar el tamaño muestral
  fijo. El plan de Kiefer–Weiss está pensado precisamente para este
  caso.

Familias disponibles para los procedimientos de razón de
verosimilitudes: `Gaussian` (varianza conocida), `Bernoulli`, `Poisson`,
`Exponential`.
