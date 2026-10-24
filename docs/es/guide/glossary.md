---
description: Glosario de términos de análisis secuencial e inferencia válida en cualquier momento (anytime-valid) - valor e (e-value), proceso e, secuencia de confianza, valor p siempre válido, mSPRT, gasto de alfa, fracción de información, ARL, SRM, CUPED, e-BH - con sinónimos y los procedimientos de sequential-analysis que implementan cada uno.
language: es
---

# Glosario

> Esta es una traducción de la [página en inglés](../../guide/glossary.md). Aún no ha sido revisada por un hablante nativo; donde ambas difieran, prevalece la página en inglés.

Términos usados en el análisis secuencial y en esta biblioteca. Entre
paréntesis se dan el término inglés y los sinónimos de uso común.

**Análisis secuencial** (sequential analysis; también pruebas
secuenciales, inferencia secuencial: sequential testing, sequential
inference). Estadística en la que el número de observaciones no se fija
de antemano. Después de cada observación o grupo de observaciones, el
procedimiento decide si detenerse o continuar. Fundado por Wald (1945).

**Consultas repetidas** (peeking; también parada opcional, monitoreo
continuo: optional stopping, data peeking, continuous monitoring).
Consultar repetidamente una prueba de tamaño muestral fijo y detenerse
cuando resulta significativa. Infla la tasa de falsos positivos; véase
[consultas repetidas](peeking.md).

**SPRT** (sequential probability ratio test, prueba secuencial de razón
de probabilidades, prueba de Wald). Acumula el logaritmo de la razón de
verosimilitudes de dos hipótesis simples y se detiene cuando sale de un
intervalo. `SPRT`; versiones truncadas: `TwoSPRT` (la 2-SPRT de Lorden)
y `kiefer_weiss_plan`. Véase [SPRT](sprt.md).

**Diseño secuencial por grupos** (group sequential design; también
análisis intermedios, ensayo secuencial por grupos: interim analyses,
group sequential trial). Unos pocos análisis planificados, cada uno con
un límite. Los límites se eligen de modo que el error de tipo I global
sea alfa. `group_sequential_design`. Véase
[ensayos clínicos](clinical-trials.md).

**Función de gasto de alfa** (alpha spending function; también gasto
del error, Lan–DeMets: error spending). Indica qué parte del error de
tipo I puede consumirse hasta cada fracción de información. El gasto de
tipo O'Brien–Fleming gasta poco al principio; el de tipo Pocock gasta
de forma uniforme. `spending="obrien-fleming"`, `"pocock"`, ...

**Fracción de información** (information fraction). La proporción de la
información estadística planificada (pacientes, eventos) alcanzada en un
análisis.

**Límite de futilidad** (futility boundary; también futilidad no
vinculante: non-binding futility). Un límite inferior: por debajo de
él, se recomienda detener el estudio por falta de efecto. Un límite no
vinculante puede ignorarse sin inflar el error de tipo I.

**Inferencia válida en cualquier momento** (anytime-valid inference;
también always-valid inference, safe anytime-valid inference, SAVI).
Pruebas e intervalos cuyas garantías se cumplen con todos los tamaños
muestrales a la vez, de modo que pueden vigilarse de forma continua y
detenerse por cualquier motivo.

**Valor e** (e-value; también variable e, puntuación de apuesta:
e-variable, betting score). Un estadístico no negativo cuya esperanza
bajo la hipótesis nula es como mucho 1. Un valor e grande es evidencia
contra la nula: rechazar cuando supera 1/alpha tiene un error de tipo I
de como mucho alfa. La salida `log_e_value` de muchos procedimientos.

**Proceso e** (e-process; también martingala de prueba, supermartingala
de prueba, proceso de riqueza: test martingale, test supermartingale,
wealth process). Una sucesión de valores e que sigue siendo válida en
los tiempos de parada. Su máximo acumulado cruza 1/alpha con
probabilidad de como mucho alfa bajo la nula (desigualdad de Ville).

**Valor p siempre válido** (always-valid p-value; también anytime-valid
p-value, valor p secuencial: sequential p-value). Un valor p que es
válido en cualquier tiempo de parada. Es el inverso del máximo acumulado
de un proceso e. La salida `p_value` de los procedimientos válidos en
cualquier momento.

**Secuencia de confianza** (confidence sequence; también intervalo de
confianza válido en cualquier momento, siempre válido o uniforme en el
tiempo: anytime-valid confidence interval, always-valid confidence
interval, time-uniform confidence interval). Una sucesión de intervalos
que contiene el valor verdadero con todos los tamaños muestrales
simultáneamente con probabilidad de al menos 1 − alpha.
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, y las
salidas `lower` y `upper` de muchas pruebas. Véase
[secuencias de confianza](confidence-sequences.md).

**mSPRT** (mixture SPRT, SPRT de mezcla, mezcla de Robbins: Robbins'
mixture). Una SPRT cuya alternativa se promedia sobre una distribución a
priori, lo que la hace válida en cualquier momento frente a toda
alternativa. `NormalMixtureSPRT` (varianza conocida), `TMixtureSPRT`
(varianza desconocida).

**Pruebas por apuestas** (testing by betting). Construir procesos e como
la riqueza de un jugador que apuesta contra la hipótesis nula.
`BettingMeanTest`, `BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal, óptimo en tasa de crecimiento). Un valor
e elegido para maximizar el crecimiento logarítmico esperado de la
evidencia bajo la alternativa. `TwoProportionTest(method="grow")`.

**Inferencia universal** (universal inference). Un valor e a partir de
una razón de verosimilitudes en la que la alternativa se estima solo
con datos pasados. Sigue siendo válido bajo diseños adaptativos.
`TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). Controla la tasa de falsos
descubrimientos sobre muchos valores e, bajo cualquier dependencia.
`MultipleTests`, `e_bh`.

**e-LOND, FDR en línea** (online FDR). Control de la tasa de falsos
descubrimientos sobre una serie de hipótesis que se deciden una a una.
`OnlineFDR`.

**SRM** (sample ratio mismatch, desajuste de proporción muestral). El
reparto observado del tráfico entre brazos difiere del configurado,
señal de un error en el experimento. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data; también
ajuste por covariables, ajuste por regresión: covariate adjustment,
regression adjustment). Reduce la varianza de un efecto A/B mediante una
covariable medida antes del experimento. `ABTest(covariate=True)`,
`AnytimeLinearModel`.

**Métrica de razón** (ratio metric; también método delta: delta
method). Una métrica que es el cociente de dos sumas por usuario, como
los ingresos por sesión. `RatioABTest`.

**Detección de puntos de cambio** (change-point detection; también
detección de cambios, detección más rápida, detección de anomalías en
línea: change detection, quickest detection, online anomaly detection).
Dar la alarma poco después de que cambie la distribución de un flujo de
datos. `CUSUM`, `ShiryaevRoberts`, `MeanEDetector`, `QuantileEDetector`,
`BayesianChangePoint`. Véase [detección de cambios](change-detection.md).

**ARL** (average run length, longitud media de corrida, ARL₀, tiempo
medio hasta una falsa alarma: mean time to false alarm). El número
esperado de observaciones hasta una falsa alarma cuando nada ha
cambiado. El control de falsas alarmas de los detectores de cambios.

**Detector e** (e-detector). Un detector de cambios construido a partir
de procesos e, uno iniciado en cada posible instante de cambio. Su ARL
está garantizada bajo una hipótesis nula no paramétrica.
`MeanEDetector`, `QuantileEDetector`.

**Problema de Kiefer–Weiss** (Kiefer–Weiss problem). Encontrar la
prueba secuencial con un tamaño muestral máximo que minimiza el mayor
tamaño muestral esperado. `kiefer_weiss_plan`.

**Característica operativa** (operating characteristic). Las
probabilidades de error y la distribución del tamaño muestral de un
plan, como funciones del parámetro verdadero.
`operating_characteristic`.

**Punto de control** (checkpoint). Un valor JSON a partir del cual una
ejecución continúa de forma exacta. `Run.checkpoint`, `Run.restore`.
Véase [flujos de datos](streaming.md).

**Huella del historial** (history digest). Una cadena de hashes SHA-256
sobre las observaciones que ha usado una ejecución, guardada en cada
punto de control, para auditoría.

**Garantía** (guarantee: `exact`, `asymptotic`, `model`, `approximate`,
`none`). El atributo con el que cada procedimiento de esta biblioteca
declara lo que promete. Véase [¿Qué método?](../../choosing.md).
