---
description: Cómo se compara sequential-analysis con otras bibliotecas de Python y R para pruebas secuenciales, pruebas A/B, diseños secuenciales por grupos, detección de cambios y filtrado (statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn), y cuándo usar cada una.
language: es
---

# ¿Cómo se compara con otras bibliotecas?

> Esta es una traducción de la [página en inglés](../../guide/comparison.md). Aún no ha sido revisada por un hablante nativo; donde ambas difieran, prevalece la página en inglés.

**Respuesta breve.** La mayoría de las bibliotecas cubren bien una
familia de métodos. sequential-analysis reúne las principales familias
de la inferencia secuencial tras una única interfaz:

* SPRT y planes óptimos;
* diseños secuenciales por grupos (group sequential designs);
* pruebas válidas en cualquier momento (anytime-valid) y secuencias de
  confianza (confidence sequences);
* detección de cambios (change detection);
* filtros de espacio de estados.

Lo que aporta más allá de los propios métodos:

* cada procedimiento declara su garantía (`exact`, `asymptotic`,
  `model`, ...);
* cada ejecución puede guardarse en un punto de control (checkpoint) y
  reanudarse bit a bit;
* los formatos están especificados y los ejecuta una segunda
  implementación en TypeScript;
* no hay dependencias obligatorias.

Si solo necesita uno de los métodos de abajo y ya usa la biblioteca
especializada en él, siga usándola. La tabla indica dónde es cada
herramienta la opción natural. Las descripciones se refieren al
propósito principal de cada biblioteca, a fecha de octubre de 2026, y
no son una lista completa de sus funcionalidades.

| Necesidad | Opciones naturales | Lo que ofrece sequential-analysis |
|---|---|---|
| pruebas de tamaño muestral fijo, regresión, potencia | scipy.stats, statsmodels | no es su propósito |
| diseños secuenciales por grupos para una solicitud regulatoria | rpact, gsDesign (R) | los mismos diseños, contrastados con rpact en su batería de pruebas; lleva el ensayo paso a paso con puntos de control |
| secuencias de confianza, valores e | confseq (Python), safestats (R) | secuencias de confianza para medias, cuantiles, coeficientes de regresión y efectos entre dos muestras; e-BH y e-LOND para muchas pruebas |
| pruebas A/B como plataforma con interfaz de usuario | GrowthBook, Statsig, Eppo, Optimizely (plataformas) | un motor para integrar: pruebas exactas para conversión, métricas acotadas y de tasas, SRM, FDR sobre métricas |
| segmentación fuera de línea por puntos de cambio de una serie terminada | ruptures (Python), changepoint (R) | detección en línea mientras llegan los datos: CUSUM, Shiryaev–Roberts, detectores e, puntos de cambio bayesianos en línea |
| filtros de Kalman | filterpy, statsmodels state space | filtros de Kalman, Kalman robusto, de partículas y HMM, con suavizado y puntos de control |
| GARCH | arch | GARCH(1,1) y GJR ajustados al máximo de arch (comprobado en las pruebas) y ejecutados después en línea |
| modelos ocultos de Markov | hmmlearn | el filtro en línea, Baum–Welch coincidente con hmmlearn, EM en línea |
| predicción | statsmodels, otras | predicciones ETS y AR que coinciden con statsmodels, aprendidas en línea, con intervalos conformes |

## Casos en los que otra herramienta es mejor

* **Una solicitud ante un organismo regulador.** rpact se usa mucho con
  ese fin, y sus desarrolladores ofrecen documentación de validación.
  sequential-analysis coincide con ella en los diseños que cubre, pero
  un promotor tendría que validarla igualmente.
* **Grandes análisis fuera de línea sobre arrays.** Las bibliotecas
  basadas en numpy son más rápidas por observación. sequential-analysis
  está hecha para una observación cada vez; véase
  [Velocidad](../../performance.md) para el coste de cada procedimiento.
* **Métodos que no tiene.** Todavía no tiene una prueba de medianas para
  dos muestras, ni procesos de Hawkes multivariantes, ni modelos ARIMA
  con términos de media móvil. Consulte el [registro de cambios](../../changelog.md)
  para ver lo que se va añadiendo.
