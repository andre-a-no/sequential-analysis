---
description: Por que conferir um valor-p todo dia infla os falsos positivos em testes A/B e ensaios (o problema do peeking), e as três famílias de métodos sequenciais que o resolvem, em Python com sequential-analysis.
language: pt-BR
---

# Por que não posso olhar um valor-p todo dia?

> Esta é uma tradução da [página em inglês](../../guide/peeking.md). Ainda não foi revisada por um falante nativo; onde as duas divergirem, a página em inglês prevalece.

**Resposta curta.** Um teste de amostra fixa promete uma taxa de falsos
positivos de 5% apenas se você olhar o resultado uma vez, no tamanho
amostral planejado. Se você olhar repetidamente e parar na primeira vez
em que p < 0,05, terá muitas chances de ser enganado. Com 20 olhadas, a
taxa de falsos positivos sobe para cerca de 25%. Os métodos sequenciais
são feitos para serem consultados repetidamente. Com eles, a taxa fica
em 5% ou abaixo, não importa quantas vezes você olhe nem quando pare.

## O problema das olhadas repetidas (peeking), medido

Dois braços com a mesma taxa de conversão de 10% (um teste A/A), 2.000
usuários, 200 repetições. O *peeking* roda o teste z usual para duas
proporções a cada 100 usuários e para no primeiro p < 0,05. O teste
sequencial `TwoProportionTest` é conferido após cada usuário:

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

A olhada única cumpre a sua promessa. Vinte olhadas multiplicam a taxa
de erro por cerca de seis. O teste sequencial, consultado após cada um
dos 2.000 usuários, a mantém em 5%. Essa é a promessa: a sua garantia é
**exata** (`TwoProportionTest.guarantee == "exact"`), uma taxa de falsos
positivos de no máximo 5% em qualquer tamanho amostral, não importa
quantas vezes você olhe. Com 200 repetições, 10 falsos positivos são o
que um 5% exato produz.

## As três famílias de métodos sequenciais

| Família | Você pode olhar | Uso típico | No sequential-analysis |
|---|---|---|---|
| **Testes sequenciais da razão de probabilidades** (sequential probability ratio tests, SPRT; Wald 1945) | após cada observação | uma hipótese simples contra outra, com o menor número médio de observações: controle de qualidade, simulação, psicofísica | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Delineamentos sequenciais em grupos** (group sequential designs; Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | em poucas análises interinas planejadas | ensaios clínicos com um comitê de monitoramento de dados | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Inferência válida a qualquer momento** (anytime-valid inference): valores-e, sequências de confiança, SPRT de mistura (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | após cada observação, parando por qualquer motivo | testes A/B online, painéis de monitoramento | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**O custo.** Olhar com mais frequência exige mais dados para o efeito
planejado:

* um delineamento sequencial em grupos com quatro análises precisa de
  1–20% mais pacientes do que uma análise única;
* um teste válido a qualquer momento para duas proporções precisa de
  1,3 a 1,6 vez os usuários de uma análise única.

Em troca, um efeito grande encerra o experimento mais cedo, e ninguém
precisa fixar o tamanho amostral de antemão.

## Quando este não é o problema

Olhar repetidamente só infla os erros quando o que você faz depende do
que você viu. Se você olha o painel, mas sempre leva o experimento até o
tamanho planejado e testa uma única vez, o teste de amostra fixa é
válido. Nesse caso, ele é também a escolha mais eficiente.

A seguir: [interromper um teste A/B antes do previsto](ab-testing.md),
[sequências de confiança](confidence-sequences.md),
[o glossário](glossary.md).
