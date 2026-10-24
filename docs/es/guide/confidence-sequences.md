---
description: Las secuencias de confianza (confidence sequences) son intervalos de confianza que siguen siendo válidos con todos los tamaños muestrales a la vez, por lo que pueden vigilarse de forma continua. Cómo calcularlas en Python para una media acotada, una mediana o un cuantil y una media con colas pesadas, con sequential-analysis.
language: es
---

# ¿Cómo obtengo un intervalo de confianza que siga siendo válido aunque lo consulte una y otra vez?

> Esta es una traducción de la [página en inglés](../../guide/confidence-sequences.md). Aún no ha sido revisada por un hablante nativo; donde ambas difieran, prevalece la página en inglés.

**Respuesta breve.** Use una **secuencia de confianza** (confidence
sequence). Es una sucesión de intervalos, uno después de cada
observación, que contiene el valor verdadero con todos los tamaños
muestrales simultáneamente con una probabilidad de al menos el 95 %.
Puede vigilarla, detenerse cuando sea lo bastante estrecha o excluya el
cero, y comunicar el intervalo en el que se detuvo. Un intervalo de
confianza del 95 % habitual promete ese 95 % solo para un único tamaño
muestral fijado de antemano.

| Qué estima | Supuesto | Procedimiento | Garantía |
|---|---|---|---|
| media de datos acotados (tasas, puntuaciones, ingresos con tope) | valores en `[lower, upper]` | `BettingConfidenceSequence` | exacta |
| mediana, percentil 90, cualquier cuantil | ninguno | `QuantileConfidenceSequence` | exacta |
| media con colas pesadas o valores atípicos | una cota para la desviación típica | `CatoniConfidenceSequence` | exacta |
| media de datos normales, varianza desconocida | normalidad | `TMixtureSPRT` (`lower`, `upper`) | exacta bajo normalidad |
| media de cualquier cosa, ejecuciones largas | varianza finita | `AsymptoticConfidenceSequence` | asintótica |
| diferencia entre dos brazos | véase [pruebas A/B](ab-testing.md) | `BoundedABTest`, `ABTest` | exacta / asintótica |

## El intervalo habitual falla cuando se vigila

Genere 500 observaciones de una variable 0/1 con media 0.3 y, a partir
de la trigésima, calcule después de cada una el intervalo del 95 % de
los libros de texto: la media ± 1.96 errores típicos. ¿En cuántas de
100 ejecuciones deja el intervalo fuera la media verdadera en algún
momento?

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

Su «95 %» solo se cumple para un tamaño muestral fijado de antemano. La
secuencia de confianza por apuestas (betting) para los mismos datos
(Waudby-Smith and Ramdas 2024) falla en algún n en como mucho el 5 % de
las ejecuciones, por construcción:

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

## Una mediana de latencia, sin ningún supuesto

Las latencias son asimétricas y de colas pesadas, así que un intervalo
de media ± error típico no es fiable para ellas.
`QuantileConfidenceSequence` cubre cualquier cuantil de cualquier
distribución, empates incluidos:

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

Los valores verdaderos son 120 ms y 258.8 ms. Ambos intervalos se
cumplen simultáneamente con los 2000 tamaños muestrales.

## Errores frecuentes

* **Las cotas y los topes forman parte del supuesto.** Elija `lower` y
  `upper` antes de ver los datos. Un valor fuera de ellos se rechaza.
* **Ningún método da una cobertura exacta para la media de datos no
  acotados arbitrarios.** Para esos datos use un cuantil, ponga un tope
  a los valores, suponga una cota para la desviación típica (Catoni) o
  acepte una secuencia asintótica.
* **Las secuencias de confianza son más anchas que un intervalo único**
  con el mismo tamaño muestral. La anchura es el precio de ser válidas
  con todos los tamaños muestrales a la vez.

Más: [¿Qué método?](../../choosing.md),
[referencia: inferencia válida en cualquier momento y no paramétrica](../../reference/anytime.md).
