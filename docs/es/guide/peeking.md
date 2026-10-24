---
description: Por qué consultar un valor p todos los días infla los falsos positivos en pruebas A/B y ensayos (el problema del peeking), y las tres familias de métodos secuenciales que lo resuelven, en Python con sequential-analysis.
language: es
---

# ¿Por qué no puedo mirar un valor p todos los días?

> Esta es una traducción de la [página en inglés](../../guide/peeking.md). Aún no ha sido revisada por un hablante nativo; donde ambas difieran, prevalece la página en inglés.

**Respuesta breve.** Una prueba de tamaño muestral fijo promete una
tasa de falsos positivos del 5 % solo si mira el resultado una vez, con
el tamaño muestral planificado. Si mira repetidamente y se detiene la
primera vez que p < 0.05, tiene muchas oportunidades de equivocarse.
Con 20 consultas, la tasa de falsos positivos sube a alrededor del 25 %.
Los métodos secuenciales están hechos para consultarse repetidamente.
Con ellos la tasa se mantiene en el 5 % o por debajo, por mucho que
mire y cuando quiera que se detenga.

## El problema de las consultas repetidas (peeking), medido

Dos brazos con la misma tasa de conversión del 10 % (una prueba A/A),
2000 usuarios, 200 repeticiones. El *peeking* ejecuta la prueba z
habitual para dos proporciones cada 100 usuarios y se detiene en el
primer p < 0.05. La prueba secuencial `TwoProportionTest` se consulta
después de cada usuario:

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

La consulta única cumple su promesa. Veinte consultas multiplican la
tasa de error aproximadamente por seis. La prueba secuencial, consultada
después de cada uno de los 2000 usuarios, la mantiene en el 5 %. Esa es
la promesa: su garantía es **exacta**
(`TwoProportionTest.guarantee == "exact"`), una tasa de falsos positivos de como mucho el 5 % con
cualquier tamaño muestral, por mucho que se consulte. Con 200
repeticiones, 10 falsos positivos es lo que da un 5 % exacto.

## Las tres familias de métodos secuenciales

| Familia | Puede consultar | Uso típico | En sequential-analysis |
|---|---|---|---|
| **Pruebas secuenciales de razón de probabilidades** (sequential probability ratio tests, SPRT; Wald 1945) | después de cada observación | una hipótesis simple contra otra, con el menor número medio de observaciones: control de calidad, simulación, psicofísica | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Diseños secuenciales por grupos** (group sequential designs; Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | en unos pocos análisis intermedios planificados | ensayos clínicos con un comité de monitoreo de datos | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Inferencia válida en cualquier momento** (anytime-valid inference): valores e, secuencias de confianza, SPRT de mezcla (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | después de cada observación, deteniéndose por cualquier motivo | pruebas A/B en línea, paneles de monitoreo | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**Lo que cuesta.** Consultar más a menudo exige más datos para el
efecto que se planificó:

* un diseño secuencial por grupos con cuatro análisis necesita entre un
  1 % y un 20 % más de pacientes que un análisis único;
* una prueba válida en cualquier momento para dos proporciones necesita
  entre 1.3 y 1.6 veces los usuarios de un análisis único.

A cambio, un efecto grande detiene el experimento antes de tiempo, y
nadie tiene que fijar el tamaño muestral de antemano.

## Cuando este no es el problema

Las consultas repetidas solo inflan los errores cuando lo que usted hace
depende de lo que ha visto. Si mira el panel pero siempre lleva el
experimento hasta el tamaño planificado y hace la prueba una sola vez,
la prueba de tamaño muestral fijo es válida. En ese caso es además la
opción más eficiente.

Siguiente: [detener una prueba A/B antes de tiempo](ab-testing.md),
[secuencias de confianza](confidence-sequences.md),
[el glosario](glossary.md).
