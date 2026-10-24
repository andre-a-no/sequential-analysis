---
description: Como o sequential-analysis se compara a outras bibliotecas Python e R para testes sequenciais, testes A/B, delineamentos sequenciais em grupos, detecção de mudanças e filtragem (statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn), e quando usar cada uma.
language: pt-BR
---

# Como ela se compara a outras bibliotecas?

> Esta é uma tradução da [página em inglês](../../guide/comparison.md). Ainda não foi revisada por um falante nativo; onde as duas divergirem, a página em inglês prevalece.

**Resposta curta.** A maioria das bibliotecas cobre bem uma família de
métodos. O sequential-analysis reúne as principais famílias da
inferência sequencial atrás de uma única interface:

* SPRTs e planos ótimos;
* delineamentos sequenciais em grupos (group sequential designs);
* testes válidos a qualquer momento (anytime-valid) e sequências de
  confiança (confidence sequences);
* detecção de mudanças (change detection);
* filtros de espaço de estados.

O que ele acrescenta além dos próprios métodos:

* todo procedimento declara a sua garantia (`exact`, `asymptotic`,
  `model`, ...);
* toda execução pode ser salva em checkpoint e retomada bit a bit;
* os formatos são especificados e executados por uma segunda
  implementação em TypeScript;
* não há dependências obrigatórias.

Se você precisa de apenas um dos métodos abaixo e já usa a biblioteca
especializada nele, continue usando essa biblioteca. A tabela indica
onde cada ferramenta é a escolha natural. As descrições se referem ao
propósito principal de cada biblioteca, em outubro de 2026, e não são
uma lista completa dos seus recursos.

| Necessidade | Escolhas naturais | O que o sequential-analysis oferece |
|---|---|---|
| testes de amostra fixa, regressão, poder | scipy.stats, statsmodels | não é o seu propósito |
| delineamentos sequenciais em grupos para uma submissão regulatória | rpact, gsDesign (R) | os mesmos delineamentos, conferidos com o rpact na sua suíte de testes; conduz o ensaio passo a passo com checkpoints |
| sequências de confiança, valores-e | confseq (Python), safestats (R) | sequências de confiança para médias, quantis, coeficientes de regressão e efeitos de duas amostras; e-BH e e-LOND para muitos testes |
| testes A/B como plataforma com interface | GrowthBook, Statsig, Eppo, Optimizely (plataformas) | um motor para embutir: testes exatos para conversão, métricas limitadas e de taxa, SRM, FDR sobre métricas |
| segmentação offline por pontos de mudança de uma série encerrada | ruptures (Python), changepoint (R) | detecção online enquanto os dados chegam: CUSUM, Shiryaev–Roberts, detectores-e, pontos de mudança bayesianos online |
| filtros de Kalman | filterpy, statsmodels state space | filtros de Kalman, Kalman robusto, de partículas e HMM, com suavização e checkpoints |
| GARCH | arch | GARCH(1,1) e GJR ajustados ao máximo do arch (conferido nos testes), depois executados online |
| modelos ocultos de Markov | hmmlearn | o filtro online, Baum–Welch coincidente com o hmmlearn, EM online |
| previsão | statsmodels, outras | previsões ETS e AR coincidentes com o statsmodels, aprendidas online, com intervalos conformes |

## Casos em que outra ferramenta é melhor

* **Uma submissão a um órgão regulador.** O rpact é amplamente usado
  para esse fim, e os seus desenvolvedores oferecem documentação de
  validação. O sequential-analysis coincide com ele nos delineamentos
  que cobre, mas um patrocinador ainda teria de validá-lo.
* **Grandes análises offline sobre arrays.** Bibliotecas baseadas em
  numpy são mais rápidas por observação. O sequential-analysis é feito
  para uma observação por vez; veja [Velocidade](../../performance.md)
  para o custo de cada procedimento.
* **Métodos que ele não tem.** Ainda não há teste de medianas para duas
  amostras, nem processos de Hawkes multivariados, nem modelos ARIMA
  com termos de média móvel. Veja o [changelog](../../changelog.md) para
  o que vai sendo acrescentado.
