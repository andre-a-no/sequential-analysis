---
description: Como planejar e conduzir análises interinas de um ensaio clínico em Python com delineamentos sequenciais em grupos (O'Brien–Fleming, Pocock, gasto de alfa de Lan–DeMets, limites de futilidade) e tamanhos amostrais para médias, proporções e sobrevida, conferidos com o rpact, com sequential-analysis.
language: pt-BR
---

# Como planejar as análises interinas de um ensaio clínico?

> Esta é uma tradução da [página em inglês](../../guide/clinical-trials.md). Ainda não foi revisada por um falante nativo; onde as duas divergirem, a página em inglês prevalece.

**Resposta curta.** Use um delineamento sequencial em grupos (group
sequential design).
`group_sequential_design(alpha, fractions, spending=...)`, de
`sequential_analysis.group_sequential`, calcula:

* os limites de eficácia, com a função de gasto de alfa (alpha
  spending) de Lan–DeMets (tipo O'Brien–Fleming, tipo Pocock e outras);
* limites de futilidade não vinculantes (non-binding futility
  boundaries);
* o poder e o tamanho amostral esperado;
* o tamanho amostral máximo para médias e proporções, ou o número de
  eventos para sobrevida.

Os limites e os tamanhos amostrais coincidem com os do pacote R rpact.
Os procedimentos de teste (`GroupSequentialTest`,
`GroupSequentialTwoMeans`, `GroupSequentialProportions`,
`GroupSequentialLogRank`) conduzem então o ensaio, paciente a paciente
ou evento a evento. Eles realizam cada análise interina (interim
analysis) quando a sua fração de informação (information fraction) é
atingida.

## Delineamento: quatro análises, gasto de O'Brien–Fleming

α unilateral = 0,025, análises em 25%, 50%, 75% e 100% dos pacientes,
poder de 90%, com um limite de futilidade:

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

## Desfechos binários e de sobrevida

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

Com o gasto de O'Brien–Fleming, três análises custam 1,3% a mais de
pacientes do que uma única análise final.

## Conduzindo o ensaio

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

O ensaio parou por eficácia na segunda análise, após dois terços dos
pacientes planejados.

## Quando as análises não acontecem como planejado

Comitês de monitoramento de dados (data monitoring committees)
raramente se reúnem exatamente em 25% da informação:

* `design.at(fractions)` recalcula os limites para a informação
  efetivamente atingida. O gasto de alfa mantém o nível global.
* `GroupSequentialMonitor` recebe qualquer estatística que você mesmo
  calcule (um modelo de Cox, um modelo misto) como um valor Z, junto com
  a sua informação em cada reunião.

## E se você quiser olhar após cada paciente?

Um delineamento sequencial em grupos permite apenas o número planejado
de olhadas. Para monitorar após cada paciente ou evento, use um
procedimento válido a qualquer momento (anytime-valid):
`AnytimeLogRankTest` para sobrevida, `TwoProportionTest` para taxas de
resposta, `TMixtureSPRT` para uma média. Eles precisam de mais pacientes
no efeito planejado. Veja o
[tutorial: ensaio de sobrevida](../../tutorials/survival.md).

## Prática regulatória

Delineamentos sequenciais em grupos com gasto de alfa são a abordagem
consagrada em ensaios confirmatórios, descrita na diretriz ICH E9 e no
guia da FDA sobre delineamentos adaptativos (2019). Esta biblioteca
calcula os delineamentos e mantém um registro auditável e retomável de
cada análise (o checkpoint e o seu resumo do histórico). Ela não é um
software validado no sentido regulatório: um patrocinador que a use em
uma submissão regulatória precisa validá-la como qualquer outra
ferramenta.

Mais: [tutorial: ensaio sequencial em grupos](../../tutorials/group-sequential.md),
que compara os números com o rpact;
[referência: delineamento e planejamento](../../reference/design.md).
