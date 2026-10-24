---
description: Como interromper um teste A/B antes do previsto sem inflar os falsos positivos, em Python. Testes válidos a qualquer momento (anytime-valid) para conversão e receita limitada, verificação de desbalanceamento da proporção amostral (SRM) e controle da taxa de falsas descobertas em várias métricas, com sequential-analysis.
language: pt-BR
---

# Como interromper um teste A/B antes do previsto sem inflar os falsos positivos?

> Esta é uma tradução da [página em inglês](../../guide/ab-testing.md). Ainda não foi revisada por um falante nativo; onde as duas divergirem, a página em inglês prevalece.

**Resposta curta.** Use um teste válido a qualquer momento
(anytime-valid): o valor-p e o intervalo de confiança dele continuam
válidos não importa quantas vezes você olhe, então você pode parar
assim que o resultado estiver claro. No sequential-analysis:

| Métrica | Procedimento | Garantia |
|---|---|---|
| taxa de conversão (0/1) | `TwoProportionTest` | exata |
| qualquer métrica limitada (receita com teto, proporção) | `BoundedABTest` | exata |
| eventos por unidade de exposição | `RateRatioTest` | exata para contagens de Poisson |
| métrica de razão (receita por sessão) | `RatioABTest` | assintótica |
| média com uma covariável pré-experimento (CUPED) | `ABTest` | assintótica |
| o tráfego está dividido como planejado? | `SampleRatioMismatch` | exata |
| várias métricas ou braços juntos | `MultipleTests` (e-BH) | taxa de falsas descobertas, exata |

Alimente cada procedimento com um usuário por vez:
`state, out = test.step(state, {...})`. Aja com base em `out.decision`
quando quiser.

## Conversão: pare quando os dados forem conclusivos

O controle converte 10% dos usuários, o tratamento 12%. O teste é
consultado após cada usuário e para na sua primeira decisão:

```python
import random

from sequential_analysis.procedures import TwoProportionTest

def users(n, rates=(0.10, 0.12), seed=1):
    """(arm, converted) per user; arm 1 is the treatment."""
    rnd = random.Random(seed)
    for _ in range(n):
        arm = int(rnd.random() < 0.5)
        yield arm, int(rnd.random() < rates[arm])

test = TwoProportionTest(alpha=0.05)
state = test.initial_state()
for arm, converted in users(60_000):
    state, out = test.step(state, {"arm": arm, "y": converted})
    if out.decision is not None:
        break
print(f"stopped after {out.n} users: conversion {out.rates[0]:.4f} (treatment) vs {out.rates[1]:.4f}, "
      f"anytime-valid p = {out.p_value:.4f}, decision: {out.decision}")
```

```text
stopped after 16469 users: conversion 0.1259 (treatment) vs 0.1068, anytime-valid p = 0.0496, decision: reject_h0
```

Para comparação, um teste de amostra fixa com 80% de poder para esse
aumento precisa de cerca de 3.850 usuários por braço, 7.700 no total, e
só pode ser lido uma vez, no final. O teste válido a qualquer momento
paga pela sua liberdade: para atingir o mesmo poder ele precisa de 1,3
a 1,6 vez os usuários de uma análise única, e esta execução precisou de
mais do que isso. Em troca, não há tamanho amostral a fixar de antemão,
e você pode olhar o resultado todo dia e parar assim que ele estiver
claro. Quando o efeito é maior do que o planejado, isso acontece muito
mais cedo.

## Receita: um intervalo exato para uma métrica limitada

O `BoundedABTest` só precisa de limites para a métrica. Ponha na receita
um teto escolhido antes do teste (aqui, 30), e a sequência de confiança
(confidence sequence) para a diferença de médias é exata para qualquer
distribuição:

```python
from sequential_analysis.procedures import BoundedABTest

rnd = random.Random(2)
revenue = BoundedABTest(lower=0.0, upper=30.0, allocation=0.5, input="revenue", grid=300)
state = revenue.initial_state()
for _ in range(20_000):
    arm = int(rnd.random() < 0.5)
    spend = min(rnd.expovariate(1 / (5.0 if arm == 0 else 5.6)), 30.0)   # capped at 30
    state, out = revenue.step(state, {"arm": arm, "revenue": spend})
print(f"after {out.n} users: mean revenue {out.means[0]:.2f} (treatment) vs {out.means[1]:.2f}, "
      f"95% confidence sequence for the difference [{out.lower:.2f}, {out.upper:.2f}]")
```

```text
after 20000 users: mean revenue 5.47 (treatment) vs 4.99, 95% confidence sequence for the difference [-0.30, 1.30]
```

O intervalo vale ao mesmo tempo em cada uma das 20.000 consultas, não só
na última. Aqui ele ainda contém o 0: 20.000 usuários não bastam para
estabelecer um aumento de cerca de 0,5 em uma métrica tão ruidosa, então
o experimento continua.

## Verifique primeiro a divisão do tráfego

Um desbalanceamento da proporção amostral (sample ratio mismatch, SRM)
significa que a divisão é diferente da configurada, por exemplo por
causa de um bug na atribuição ou no registro de eventos. Estimativas de
efeito de um experimento assim não são confiáveis. Um desvio de 50/50
para 52/48 é detectado enquanto o experimento está rodando:

```python
from sequential_analysis.procedures import SampleRatioMismatch

srm = SampleRatioMismatch(weights=(0.5, 0.5), alpha=0.001)
state = srm.initial_state()
rnd = random.Random(3)
for _ in range(50_000):
    state, out = srm.step(state, {"arm": int(rnd.random() < 0.52)})
    if out.decision is not None:
        break
print(f"mismatch detected after {out.n} users: split {out.proportions[0]:.3f} / {out.proportions[1]:.3f}")
```

```text
mismatch detected after 4927 users: split 0.470 / 0.530
```

## Muitas métricas ao mesmo tempo

Testar dez métricas independentes a 5% cada dá uma chance de cerca de
40% de pelo menos uma falsa descoberta. O `MultipleTests` combina os
valores-e (e-values) de todos os testes com o procedimento e-BH, de modo
que a taxa de falsas descobertas (false discovery rate) fica em `alpha`
em qualquer tempo de parada:

```python
from sequential_analysis.procedures import MultipleTests

metrics = MultipleTests({
    "conversion": TwoProportionTest(input="converted"),
    "revenue": BoundedABTest(lower=0.0, upper=30.0, input="revenue", grid=100),
    "traffic split": SampleRatioMismatch((0.5, 0.5)),
}, alpha=0.05)
state = metrics.initial_state()
rnd = random.Random(4)
for _ in range(15_000):
    arm = int(rnd.random() < 0.5)
    converted = int(rnd.random() < (0.10, 0.13)[arm])
    spend = min(rnd.expovariate(1 / 5.0), 30.0)                          # no effect on revenue
    state, out = metrics.step(state, {"arm": arm, "converted": converted, "revenue": spend})
print("discoveries:", out.rejected)
```

```text
discoveries: ('conversion',)
```

## Armadilhas

* **Aleatorize a unidade que você analisa.** Se os usuários são
  aleatorizados, envie um registro por usuário, não por visualização de
  página. Para métricas por sessão, use o `RatioABTest`, que trabalha
  com os totais por usuário.
* **Fixe o teto de uma métrica limitada antes do teste.** Escolhê-lo
  depois de ver os dados anula a garantia.
* **Procedimentos assintóticos precisam de amostras grandes.** Para o
  `ABTest` e o `RatioABTest`, o intervalo só é aproximadamente válido em
  execuções longas. Prefira os procedimentos exatos quando eles se
  aplicarem.
* **Alocação adaptativa de tráfego** (bandits) exige um teste que
  continue válido quando a divisão depende dos resultados:
  `TwoProportionTest(method="universal")` ou
  `BoundedABTest(propensity_input=...)`. Veja o
  [tutorial, §10](../../tutorials/ab-test.md).

Mais: o [tutorial de teste A/B](../../tutorials/ab-test.md) (CUPED,
métricas de razão, taxas, planejamento da duração) e
[um programa de experimentos](../../tutorials/experiment-programme.md)
(taxa de falsas descobertas ao longo de muitos experimentos).
