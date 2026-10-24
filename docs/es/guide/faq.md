---
description: Preguntas frecuentes sobre sequential-analysis, la biblioteca de Python para pruebas secuenciales e inferencia válida en cualquier momento (anytime-valid) - instalación, licencia y uso comercial, pruebas A/B en producción, ensayos clínicos, potencia, velocidad, TypeScript, cómo citarla.
language: es
---

# Preguntas frecuentes

> Esta es una traducción de la [página en inglés](../../guide/faq.md). Aún no ha sido revisada por un hablante nativo; donde ambas difieran, prevalece la página en inglés.

## Sobre la biblioteca

### ¿Qué es sequential-analysis?

Una biblioteca de Python para la inferencia estadística secuencial. Sus
pruebas, secuencias de confianza (confidence sequences) y detectores
pueden consultarse después de cada observación y detenerse en cualquier
momento sin perder sus garantías sobre el error. Incluye:

* SPRT;
* diseños secuenciales por grupos (group sequential designs);
* pruebas A/B válidas en cualquier momento (anytime-valid);
* detectores de puntos de cambio;
* filtros de Kalman, de partículas y de modelos ocultos de Markov;
* predicción y GARCH.

Todos funcionan tras una única interfaz con puntos de control
(checkpoints) en JSON. La desarrolla Novikov Laboratories LLC.

### ¿Cómo se instala? ¿De qué depende?

`pip install sequential-analysis`. Necesita Python 3.8 o posterior
(probada hasta la 3.14) y nada más.
`pip install "sequential-analysis[fast]"` añade numpy para los
procedimientos que trabajan con arrays. pandas, polars, los clientes de
Kafka y matplotlib solo se usan si llama a los adaptadores o a las
funciones de gráficos.

### ¿Es gratuita para uso comercial?

Tiene doble licencia: AGPL-3.0 y una licencia comercial. Estos usos son
gratuitos bajo la AGPL:

* investigación y docencia;
* proyectos de código abierto bajo la AGPL o la GPL v3;
* uso interno en una organización, sin entregar copias a terceros y sin
  acceso por red para personas ajenas a ella.

Un producto de código cerrado, o un servicio en red cuyo código fuente
no publique, necesita una licencia comercial. La tabla de
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)
decide cada caso. Consultas sobre licencias: andrei@hobukob.ru.

### ¿Cómo se cita?

[CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff),
en el repositorio, da la cita, y el botón *Cite this repository* de
GitHub la convierte a BibTeX o APA. Las versiones se archivan en Zenodo
con un DOI. Los métodos y sus comprobaciones se describen en el
[artículo](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf).

## Uso

### ¿Puedo usarla para pruebas A/B en producción?

Sí, como motor estadístico. Ofrece pruebas exactas para:

* la conversión (`TwoProportionTest`);
* métricas acotadas (`BoundedABTest`);
* tasas (`RateRatioTest`);
* el reparto del tráfico (`SampleRatioMismatch`);
* muchas métricas con control de la tasa de falsos descubrimientos
  (`MultipleTests`).

En Python puro, la prueba de conversión tarda unos 10 microsegundos por
usuario, la comprobación del reparto 4 y la prueba de tasas 40. Un
punto de control de cada una ocupa entre 2 y 4 kilobytes.
`BoundedABTest` mantiene una rejilla y tarda entre 0.1 y 0.5 ms.

La biblioteca no es una plataforma de experimentación: la asignación,
la recogida de eventos y los paneles los construye usted o los toma de
una plataforma. Véase [pruebas A/B](ab-testing.md).

### ¿Puedo consultar los resultados todos los días?

Sí, con los procedimientos válidos en cualquier momento: para eso
existen. Con un diseño secuencial por grupos, consulte solo en los
análisis planificados. Con una prueba clásica de tamaño muestral fijo,
consulte una sola vez. Véase [consultas repetidas (peeking)](peeking.md).

### ¿Es una prueba válida en cualquier momento menos potente que una prueba de tamaño muestral fijo?

Con el efecto para el que se planifica la prueba de tamaño fijo, sí.
Para alcanzar la misma potencia, una prueba válida en cualquier momento
para dos proporciones necesita entre 1.3 y 1.6 veces los usuarios. A
cambio, puede detenerse antes cuando el efecto es mayor, y no necesita
un tamaño muestral fijado de antemano. Un diseño secuencial por grupos
con unas pocas consultas planificadas cuesta solo entre un 1 % y un
20 % más que un análisis único.

### Secuencial por grupos o válido en cualquier momento: ¿cuál debo usar?

* **Secuencial por grupos** si los análisis son pocos y planificados,
  como con un comité de monitoreo de datos o un ciclo de versiones, y
  sobre todo para un ensayo clínico confirmatorio.
* **Válido en cualquier momento** si quiere consultar de forma
  continua, o no puede decir de antemano cuándo consultará o se
  detendrá.

### ¿Hace pruebas A/B bayesianas?

Sus pruebas A/B son frecuentistas, con garantías sobre las tasas de
error. Hay componentes bayesianos disponibles donde encajan:

* `ThompsonAllocation` envía el tráfico según la probabilidad a
  posteriori de que cada brazo sea el mejor, con una regla de pérdida
  esperada para el despliegue;
* `BayesianChangePoint` detecta puntos de cambio;
* los predictores aprenden sus parámetros mediante actualización
  bayesiana.

### ¿Está validada para ensayos clínicos?

Sus diseños secuenciales por grupos (límites, potencia, tamaños
muestrales, números de eventos) se contrastan con rpact y con el paquete
survival de R en la batería de pruebas. No es software validado en el
sentido regulatorio. Un promotor que la use para una solicitud ante la
autoridad la valida como cualquier otra herramienta. Véase
[ensayos clínicos](clinical-trials.md).

### Mi métrica tiene colas pesadas (ingresos, latencia). ¿Qué debo usar?

* Para un cuantil (mediana, percentil 90), use `QuantileTest` o
  `QuantileConfidenceSequence`, que no necesitan supuestos.
* Para una media, ponga a los valores un tope fijado de antemano y use
  `BoundedABTest` o `BettingConfidenceSequence` (exactas).
* Otra opción es suponer una cota para la desviación típica y usar
  `CatoniConfidenceSequence`.

La biblioteca todavía no incluye una prueba de medianas para dos
muestras.

### ¿Qué velocidad tiene?

Los procedimientos más sencillos tardan entre 1 y 10 microsegundos por
observación en Python puro: las SPRT, CUSUM, las pruebas secuenciales
por grupos y de mezcla, GARCH. Los que mantienen una rejilla o la
muestra completa tardan entre 0.1 y 10 ms. Ejemplos son las secuencias
de confianza por apuestas y de Catoni, la prueba de núcleo y los
predictores con aprendizaje.
[Velocidad](../../performance.md) indica el coste de cada procedimiento y
el tamaño de su punto de control.

### ¿Puedo ejecutarla en JavaScript o en el navegador?

Sí. El ejecutor de TypeScript de `ts/` ejecuta los procedimientos y
continúa los puntos de control de Python. Las huellas del historial y
las decisiones son idénticas, y los números coinciden hasta los últimos
bits. Véase [ejecutor de TypeScript](../../typescript.md).

### ¿Puede una ejecución sobrevivir a una caída?

Sí. `run.checkpoint()` es JSON simple, y `Run.restore` continúa bit a
bit. Las observaciones que se vuelven a entregar se descartan. Véase
[flujos de datos](streaming.md).

### ¿Qué significan «exact» y «asymptotic» en la documentación?

El atributo `guarantee` de cada procedimiento indica lo que promete:

* `exact`: la tasa de error se cumple con cualquier tamaño muestral
  bajo los supuestos indicados;
* `asymptotic`: de forma aproximada, en ejecuciones largas;
* `model`: exacta bajo el modelo indicado;
* `approximate`;
* `none`.

La documentación recomienda el procedimiento exacto cuando hay uno
aplicable. Véase [¿Qué método?](../../choosing.md).
