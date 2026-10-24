---
description: Como detectar uma mudança em um fluxo de leituras de sensores, latências ou métricas em Python, com CUSUM, Shiryaev–Roberts, detectores-e não paramétricos e detecção bayesiana online de pontos de mudança. Alarmes falsos controlados pelo comprimento médio de corrida (ARL), com sequential-analysis.
language: pt-BR
---

# Como detectar uma mudança em um fluxo de medições?

> Esta é uma tradução da [página em inglês](../../guide/change-detection.md). Ainda não foi revisada por um falante nativo; onde as duas divergirem, a página em inglês prevalece.

**Resposta curta.** Use um detector online de pontos de mudança (online
change-point detector). Ele acompanha o fluxo de dados e dispara um
alarme assim que a distribuição parece ter mudado. Os seus alarmes
falsos são controlados pelo **comprimento médio de corrida** (average
run length, ARL): o número esperado de observações até um alarme falso
enquanto nada mudou. No sequential-analysis:

| O que você sabe antes da mudança | Procedimento | Garantia |
|---|---|---|
| as duas distribuições (p. ex., normal, média 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exata: ARL ≥ e^limiar |
| apenas a média e limites para os valores | `MeanEDetector` | exata para toda distribuição desse tipo |
| apenas um quantil (p. ex., o percentil 95 da latência) | `QuantileEDetector` | exata para toda distribuição |
| um modelo com parâmetros desconhecidos, antes e depois | `BayesianChangePoint` | sob o modelo e a priori |

## Um sensor cuja média se desloca

Um sensor de temperatura lê 70,0 °C com ruído de desvio-padrão 0,5. A
partir da leitura 600, a média é 70,4. O CUSUM com limiar
log(1000) ≈ 6,9 tem um ARL de pelo menos 1.000 leituras:

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

Um deslocamento de menos de um desvio-padrão é invisível a olho nu em
qualquer leitura isolada. O CUSUM acumula a evidência e o encontra.

## Quando as leituras não são normais

O ARL do CUSUM só vale se as leituras seguirem as distribuições que você
informou. Para dados assimétricos (amplitudes de vibração, latências,
tamanhos de fila), ele dispara alarmes falsos com muito mais frequência
do que o planejado. Os detectores-e (e-detectors) precisam de muito
menos:

* `MeanEDetector` precisa da média antes da mudança e de limites para
  os valores.
* `QuantileEDetector` precisa apenas de um quantil antes da mudança.

O ARL deles é pelo menos o valor-alvo para **toda** distribuição com
essa média ou esse quantil:

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

Na prática, o quantil antes da mudança é estimado a partir de um
período calmo. A garantia vale então aproximadamente, e melhor quanto
mais longo for esse período.

## Escolhendo o ARL

O ARL equilibra alarmes falsos e atraso. Com uma leitura por minuto, um
ARL de 1.000 leituras significa um alarme falso a cada 17 horas, mais ou
menos, de operação normal, por sensor. Com 50 sensores, isso dá cerca de
70 por dia. Escolha o ARL a partir do número de alarmes falsos por dia
que você pode tolerar em todos os sensores juntos: aqui, um ARL de
1.000.000 de leituras reduz os 50 sensores a cerca de um alarme falso a
cada duas semanas. Isso custa menos do que parece, porque o atraso de
detecção cresce apenas com o logaritmo do ARL. Para o CUSUM, o limiar
vai de 6,9 para 13,8, e o atraso aproximadamente dobra.

Esses detectores são ferramentas de monitoramento, não sistemas de
segurança. Não os use no lugar de um sistema instrumentado de segurança
certificado.

Mais: [tutorial: monitoramento de processos e detecção de mudanças](../../tutorials/monitoring.md),
[regimes com modelos ocultos de Markov](../../tutorials/regimes.md),
[referência: detecção de mudanças](../../reference/detection.md).
