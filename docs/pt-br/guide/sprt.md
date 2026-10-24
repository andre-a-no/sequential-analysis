---
description: Como rodar o teste sequencial da razão de probabilidades de Wald (SPRT) em Python com sequential-analysis. Taxas de erro, tamanho amostral médio comparado a um teste de amostra fixa e as alternativas truncadas (2-SPRT, planos ótimos de Kiefer–Weiss).
language: pt-BR
---

# Como rodar o SPRT de Wald em Python?

> Esta é uma tradução da [página em inglês](../../guide/sprt.md). Ainda não foi revisada por um falante nativo; onde as duas divergirem, a página em inglês prevalece.

**Resposta curta.** `SPRT(family, theta0, theta1, alpha, beta)`, de
`sequential_analysis.procedures`, implementa o teste sequencial da razão
de probabilidades de Wald (sequential probability ratio test, SPRT).
Ele decide entre duas hipóteses simples com o menor número médio de
observações. Alimente-o com uma observação por vez e pare na primeira
decisão. No exemplo abaixo, ele precisa de cerca de metade das
observações de um teste de amostra fixa com as mesmas taxas de erro:
65–76 itens em média em vez de 133. Se você precisa de um tamanho
amostral máximo garantido, use `TwoSPRT` ou um plano de
`kiefer_weiss_plan`.

## Exemplo: a taxa de defeitos é de 10% ou de 20%?

Um lote é aceito se a sua taxa de defeitos for de 10% e rejeitado se
for de 20%, com as duas taxas de erro em 5%:

```python
import random

from sequential_analysis.procedures import SPRT, Bernoulli

test = SPRT(Bernoulli(), theta0=0.10, theta1=0.20, alpha=0.05, beta=0.05)

def inspect_items(rate, seed):
    """Inspect items until the test decides; returns (decision, items inspected)."""
    rnd = random.Random(seed)
    state = test.initial_state()
    while state.decision is None:
        state, out = test.step(state, {"x": int(rnd.random() < rate)})
    return state.decision, state.n

decision, n = inspect_items(0.10, seed=1)
print(f"a good batch: {decision} after {n} items")
```

```text
a good batch: accept_h0 after 108 items
```

Como ele se sai ao longo de muitos lotes?

```python
for rate in (0.10, 0.20):
    results = [inspect_items(rate, seed) for seed in range(2000)]
    wrong = sum(d == ("reject_h0" if rate == 0.10 else "accept_h0") for d, _ in results) / len(results)
    average = sum(n for _, n in results) / len(results)
    longest = max(n for _, n in results)
    print(f"defect rate {rate:.0%}: wrong decision {wrong:.1%}, average {average:.0f} items, longest {longest}")
```

```text
defect rate 10%: wrong decision 3.5%, average 76 items, longest 370
defect rate 20%: wrong decision 4.3%, average 65 items, longest 315
```

Um teste de amostra fixa com as mesmas taxas de erro inspeciona cerca
de 133 itens em cada lote (aproximação normal). O SPRT inspeciona, em
média, 43–51% menos. O seu tamanho amostral, porém, é aleatório e não
tem limite superior, e alguns lotes levam muito mais tempo do que a
média.

Os limiares são os de Wald: log((1 − β)/α) e log(β/(1 − α)). Eles
garantem, para qualquer tamanho amostral na parada, que as taxas de erro
reais α′ e β′ satisfazem α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) e
α′ + β′ ≤ α + β. A razão de verossimilhanças ultrapassa os limiares
(overshoot) ao parar, então na prática as taxas ficam abaixo das
nominais, como aqui. Esse é o sentido de `SPRT.guarantee == "exact"`.
Para taxas de erro calculadas exatamente em vez de limitadas, use
`operating_characteristic` sobre um plano (veja abaixo).

## Quando você precisa de um tamanho amostral máximo

* `TwoSPRT` (o 2-SPRT de Lorden) para até um horizonte fixo e quase
  minimiza o tamanho amostral esperado no pior caso.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`,
  em `sequential_analysis.design`, calcula por indução retroativa o
  plano ótimo com um tamanho amostral máximo. `PlanTest` o executa, e
  `operating_characteristic` fornece as suas taxas de erro exatas e o
  tamanho amostral esperado sem simulação. Veja
  `examples/07_design_kiefer_weiss.py`.
* Para poucas olhadas planejadas em vez de uma por observação, use um
  [delineamento sequencial em grupos](clinical-trials.md).

## Quando o SPRT é a ferramenta errada

* **As hipóteses não são simples.** "A taxa é de 10%" contra "a taxa é
  qualquer outra" é uma alternativa composta. Use um SPRT de mistura
  (mixture SPRT: `NormalMixtureSPRT`, `TMixtureSPRT`) ou um teste por
  apostas (testing by betting: `BettingMeanTest`), que são válidos a
  qualquer momento contra toda alternativa.
* **O valor verdadeiro está entre θ₀ e θ₁.** O SPRT é então mais lento,
  e o seu tamanho amostral esperado pode superar o tamanho da amostra
  fixa. O plano de Kiefer–Weiss foi feito exatamente para esse caso.

Famílias disponíveis para os procedimentos de razão de
verossimilhanças: `Gaussian` (variância conhecida), `Bernoulli`,
`Poisson`, `Exponential`.
