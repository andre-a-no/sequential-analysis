---
description: Sequências de confiança (confidence sequences) são intervalos de confiança que continuam válidos em todos os tamanhos amostrais ao mesmo tempo, por isso podem ser monitorados continuamente. Como calculá-las em Python para uma média limitada, uma mediana ou um quantil e uma média com caudas pesadas, com sequential-analysis.
language: pt-BR
---

# Como obter um intervalo de confiança que continue válido se eu continuar olhando?

> Esta é uma tradução da [página em inglês](../../guide/confidence-sequences.md). Ainda não foi revisada por um falante nativo; onde as duas divergirem, a página em inglês prevalece.

**Resposta curta.** Use uma **sequência de confiança** (confidence
sequence). É uma sequência de intervalos, um após cada observação, que
contém o valor verdadeiro em todos os tamanhos amostrais simultaneamente
com probabilidade de pelo menos 95%. Você pode acompanhá-la, parar
quando ela estiver estreita o bastante ou excluir o zero, e relatar o
intervalo em que parou. Um intervalo de confiança de 95% usual promete
95% apenas em um único tamanho amostral fixado de antemão.

| O que você estima | Suposição | Procedimento | Garantia |
|---|---|---|---|
| média de dados limitados (taxas, notas, receita com teto) | valores em `[lower, upper]` | `BettingConfidenceSequence` | exata |
| mediana, percentil 90, qualquer quantil | nenhuma | `QuantileConfidenceSequence` | exata |
| média com caudas pesadas ou outliers | um limite para o desvio-padrão | `CatoniConfidenceSequence` | exata |
| média de dados normais, variância desconhecida | normalidade | `TMixtureSPRT` (`lower`, `upper`) | exata sob normalidade |
| média de qualquer coisa, execuções longas | variância finita | `AsymptoticConfidenceSequence` | assintótica |
| diferença entre dois braços | veja [testes A/B](ab-testing.md) | `BoundedABTest`, `ABTest` | exata / assintótica |

## O intervalo usual falha quando é acompanhado

Gere 500 observações de uma variável 0/1 com média 0,3 e, a partir da
30ª, calcule após cada uma o intervalo de 95% dos livros-texto: a média
± 1,96 erros-padrão. Em quantas de 100 execuções o intervalo deixa de
cobrir a média verdadeira em algum momento?

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

O seu "95%" vale apenas em um tamanho amostral fixado de antemão. A
sequência de confiança por apostas (betting) para os mesmos dados
(Waudby-Smith and Ramdas 2024) falha em algum n em no máximo 5% das
execuções, por construção:

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

## Uma mediana de latência, sem nenhuma suposição

Latências são assimétricas e têm caudas pesadas, então um intervalo de
média ± erro-padrão não é confiável para elas.
`QuantileConfidenceSequence` cobre qualquer quantil de qualquer
distribuição, empates incluídos:

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

Os valores verdadeiros são 120 ms e 258,8 ms. Os dois intervalos valem
em todos os 2.000 tamanhos amostrais ao mesmo tempo.

## Armadilhas

* **Limites e tetos fazem parte da suposição.** Escolha `lower` e
  `upper` antes de ver os dados. Um valor fora deles é recusado.
* **Nenhum método dá cobertura exata para a média de dados ilimitados
  arbitrários.** Para esses dados, use um quantil, ponha um teto nos
  valores, suponha um limite para o desvio-padrão (Catoni) ou aceite
  uma sequência assintótica.
* **Sequências de confiança são mais largas do que um intervalo único**
  no mesmo tamanho amostral. A largura é o preço de ser válida em todos
  os tamanhos amostrais ao mesmo tempo.

Mais: [Qual método?](../../choosing.md),
[referência: inferência válida a qualquer momento e não paramétrica](../../reference/anytime.md).
