---
description: Guía de usuario de sequential-analysis, una biblioteca de Python para pruebas secuenciales e inferencia válida en cualquier momento (anytime-valid). Cada página responde directamente a una pregunta, con código que se ejecuta tal cual y su salida.
language: es
---

# Guía de usuario

> Esta es una traducción de la [página en inglés](../../guide/index.md). Aún no ha sido revisada por un hablante nativo; donde ambas difieran, prevalece la página en inglés.

Esta guía está organizada según las preguntas que se hace la gente. Cada
página empieza con una respuesta directa y luego ofrece un programa
breve que se ejecuta tal como está escrito, su salida, la garantía en la
que se apoya la respuesta y los casos en los que el método no es
aplicable. Los [tutoriales](../../tutorials/ab-test.md) profundizan en cada
tema.

## La biblioteca en un párrafo

**sequential-analysis** es una biblioteca de Python para la inferencia
estadística sobre datos que llegan de una observación en una. Sus
pruebas, intervalos de confianza y detectores pueden consultarse después
de cada observación y detenerse en cualquier momento, y sus tasas de
error se siguen cumpliendo. Abarca:

* la SPRT de Wald y los planes secuenciales óptimos;
* los diseños secuenciales por grupos (group sequential designs) para
  ensayos clínicos (funciones de gasto de O'Brien–Fleming y de Pocock,
  límites de futilidad);
* las pruebas A/B válidas en cualquier momento, con valores e (e-values)
  y secuencias de confianza (confidence sequences);
* la detección de puntos de cambio (change-point detection);
* los filtros de Kalman, de partículas y de modelos ocultos de Markov;
* la predicción (forecasting) y la volatilidad GARCH.

Cada ejecución puede guardarse como punto de control (checkpoint) en JSON
y reanudarse bit a bit en Python, o continuarse en su ejecutor de
TypeScript con las mismas decisiones.

| | |
|---|---|
| Instalación | `pip install sequential-analysis` |
| Importación | `import sequential_analysis` |
| Python | 3.8 a 3.14, sin dependencias obligatorias (numpy opcional) |
| Licencia | AGPL-3.0, o una licencia comercial de Novikov Laboratories LLC |
| Código fuente | <https://github.com/andre-a-no/sequential-analysis> |
| Documentación | <https://andre-a-no.github.io/sequential-analysis/> |

## Preguntas

**Conceptos**

* [¿Por qué no puedo mirar un valor p todos los días?](peeking.md) El
  problema del *peeking* y las tres familias de métodos secuenciales.
* [Glosario](glossary.md): valor e, secuencia de confianza, gasto de
  alfa, ARL y los demás términos, con sus sinónimos.

**Tareas**

* [¿Cómo detengo una prueba A/B antes de tiempo sin inflar los falsos positivos?](ab-testing.md)
* [¿Cómo obtengo un intervalo de confianza que siga siendo válido aunque lo consulte una y otra vez?](confidence-sequences.md)
* [¿Cómo ejecuto la SPRT de Wald en Python?](sprt.md)
* [¿Cómo planifico los análisis intermedios de un ensayo clínico?](clinical-trials.md)
* [¿Cómo detecto un cambio en un flujo de mediciones?](change-detection.md)
* [¿Cómo ejecuto estadísticas sobre un flujo de datos y las reanudo tras una caída?](streaming.md)

**Elegir**

* [¿Qué método para mi pregunta?](../../choosing.md): la tabla completa.
* [¿Cómo se compara con otras bibliotecas?](comparison.md)
* [Preguntas frecuentes](faq.md)

## Cómo leer las garantías

Cada procedimiento tiene un atributo `guarantee`. La guía lo cita en
cada respuesta:

* **exact:** la tasa de error se cumple con cualquier tamaño muestral
  bajo los supuestos indicados.
* **asymptotic:** se cumple de forma aproximada, y mejor cuanto mayores
  son las muestras.
* **model:** las probabilidades son exactas bajo el modelo indicado,
  pero no se afirma nada fuera de él.
* **approximate:** una aproximación incluso bajo el modelo.
* **none:** el procedimiento transforma los datos y no garantiza nada.
