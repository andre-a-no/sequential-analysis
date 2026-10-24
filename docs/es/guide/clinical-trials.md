---
description: Cómo planificar y realizar análisis intermedios de un ensayo clínico en Python con diseños secuenciales por grupos (O'Brien–Fleming, Pocock, gasto de alfa de Lan–DeMets, límites de futilidad) y tamaños muestrales para medias, proporciones y supervivencia, contrastados con rpact, con sequential-analysis.
language: es
---

# ¿Cómo planifico los análisis intermedios de un ensayo clínico?

> Esta es una traducción de la [página en inglés](../../guide/clinical-trials.md). Aún no ha sido revisada por un hablante nativo; donde ambas difieran, prevalece la página en inglés.

**Respuesta breve.** Use un diseño secuencial por grupos (group
sequential design).
`group_sequential_design(alpha, fractions, spending=...)`, de
`sequential_analysis.group_sequential`, calcula:

* los límites de eficacia, con la función de gasto de alfa (alpha
  spending) de Lan–DeMets (de tipo O'Brien–Fleming, de tipo Pocock y
  otras);
* límites de futilidad no vinculantes (non-binding futility
  boundaries);
* la potencia y el tamaño muestral esperado;
* el tamaño muestral máximo para medias y proporciones, o el número de
  eventos para supervivencia.

Los límites y los tamaños muestrales coinciden con los del paquete de R
rpact. Los procedimientos de prueba (`GroupSequentialTest`,
`GroupSequentialTwoMeans`, `GroupSequentialProportions`,
`GroupSequentialLogRank`) llevan después el ensayo, paciente a paciente
o evento a evento. Realizan cada análisis intermedio (interim analysis)
cuando se alcanza su fracción de información (information fraction).

## Diseño: cuatro análisis, gasto de O'Brien–Fleming

α unilateral = 0.025, análisis al 25 %, 50 %, 75 % y 100 % de los
pacientes, potencia del 90 %, con un límite de futilidad:

```python
from sequential_analysis.group_sequential import group_sequential_design

design = group_sequential_design(0.025, [0.25, 0.5, 0.75, 1.0], spending="obrien-fleming",
                                 futility="obrien-fleming", power=0.9)
for k, (t, b, f) in enumerate(zip(design.fractions, design.bounds, design.futility), start=1):
    print(f"analysis {k} at {t:.0%}: efficacy if Z >= {b:.3f}, futility if Z <= {f:.3f}")
print("patients for an effect of 0.3 standard deviations:", design.max_sample_size(effect=0.3, sigma=1.0))
print(f"expected share of the patients used: {design.expected_fraction(0.0):.2f} with no effect, "
      f"{design.expected_fraction(design.drift):.2f} with the planned effect")
```

```text
analysis 1 at 25%: efficacy if Z >= 4.333, futility if Z <= -1.403
analysis 2 at 50%: efficacy if Z >= 2.963, futility if Z <= 0.325
analysis 3 at 75%: efficacy if Z >= 2.359, futility if Z <= 1.291
analysis 4 at 100%: efficacy if Z >= 2.014, futility if Z <= 2.014
patients for an effect of 0.3 standard deviations: 127
expected share of the patients used: 0.59 with no effect, 0.73 with the planned effect
```

## Variables de respuesta binarias y de supervivencia

```python
binary = group_sequential_design(0.025, [1 / 3, 2 / 3, 1.0], spending="obrien-fleming")
print("patients, response 10% vs 12%, 80% power:",
      binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8))
print("events for a hazard ratio of 0.7, 80% power:", binary.max_events(hazard_ratio=0.7, power=0.8))
print(f"inflation factor over a single analysis: {binary.inflation_factor(0.8):.3f}")
```

```text
patients, response 10% vs 12%, 80% power: 7780
events for a hazard ratio of 0.7, 80% power: 250
inflation factor over a single analysis: 1.013
```

Con el gasto de O'Brien–Fleming, tres análisis cuestan un 1.3 % más de
pacientes que un único análisis final.

## Realización del ensayo

```python
import random

from sequential_analysis.procedures import GroupSequentialProportions

n_max = binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8)
test = GroupSequentialProportions.from_design(binary, n_max)
state, rnd = test.initial_state(), random.Random(3)
for patient in range(n_max):
    arm = patient % 2                                         # 1 treatment, 0 control
    state, out = test.step(state, {"arm": arm, "y": int(rnd.random() < (0.12 if arm else 0.10))})
    if out.analysis:
        print(f"analysis {out.analysis} after {out.n} patients: Z = {out.z:.2f}, bound {out.bound:.2f}")
    if out.decision:
        print("decision:", out.decision)
        break
```

```text
analysis 1 after 2594 patients: Z = 2.14, bound 3.71
analysis 2 after 5187 patients: Z = 2.64, bound 2.51
decision: reject_h0
```

El ensayo se detuvo por eficacia en el segundo análisis, tras dos
tercios de los pacientes previstos.

## Cuando los análisis no se producen según lo previsto

Los comités de monitoreo de datos (data monitoring committees) rara vez
se reúnen exactamente al 25 % de la información:

* `design.at(fractions)` recalcula los límites para la información
  realmente alcanzada. El gasto de alfa mantiene el nivel global.
* `GroupSequentialMonitor` acepta cualquier estadístico que calcule
  usted mismo (un modelo de Cox, un modelo mixto) como valor Z, junto
  con su información en cada reunión.

## ¿Y si quiere mirar después de cada paciente?

Un diseño secuencial por grupos solo permite el número de consultas
planificado. Para monitorizar después de cada paciente o evento, use un
procedimiento válido en cualquier momento (anytime-valid):
`AnytimeLogRankTest` para supervivencia, `TwoProportionTest` para tasas
de respuesta, `TMixtureSPRT` para una media. Necesitan más pacientes con
el efecto planificado. Véase el
[tutorial: ensayo de supervivencia](../../tutorials/survival.md).

## Práctica regulatoria

Los diseños secuenciales por grupos con gasto de alfa son el enfoque
establecido en los ensayos confirmatorios, descrito en la guía ICH E9 y
en la guía de la FDA sobre diseños adaptativos (2019). Esta biblioteca
calcula los diseños y conserva un registro auditable y reanudable de
cada análisis (el punto de control y su huella del historial). No es
software validado en el sentido regulatorio: un promotor que la use en
una solicitud ante la autoridad tiene que validarla como cualquier otra
herramienta.

Más: [tutorial: ensayo secuencial por grupos](../../tutorials/group-sequential.md),
que compara las cifras con rpact;
[referencia: diseño y planificación](../../reference/design.md).
