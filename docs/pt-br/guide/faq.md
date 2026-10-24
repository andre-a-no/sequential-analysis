---
description: Perguntas frequentes sobre o sequential-analysis, a biblioteca Python para testes sequenciais e inferência válida a qualquer momento (anytime-valid) - instalação, licença e uso comercial, testes A/B em produção, ensaios clínicos, poder, velocidade, TypeScript, como citar.
language: pt-BR
---

# Perguntas frequentes

> Esta é uma tradução da [página em inglês](../../guide/faq.md). Ainda não foi revisada por um falante nativo; onde as duas divergirem, a página em inglês prevalece.

## Sobre a biblioteca

### O que é o sequential-analysis?

Uma biblioteca Python para inferência estatística sequencial. Seus
testes, sequências de confiança (confidence sequences) e detectores
podem ser conferidos após cada observação e interrompidos a qualquer
momento, sem perder as suas garantias de erro. Ela tem:

* SPRTs;
* delineamentos sequenciais em grupos (group sequential designs);
* testes A/B válidos a qualquer momento (anytime-valid);
* detectores de pontos de mudança;
* filtros de Kalman, de partículas e de modelos ocultos de Markov;
* previsão e GARCH.

Todos rodam atrás de uma única interface com checkpoints em JSON. Ela é
desenvolvida pela Novikov Laboratories LLC.

### Como instalar? Do que ela depende?

`pip install sequential-analysis`. Ela precisa de Python 3.8 ou
posterior (testada até a 3.14) e de mais nada.
`pip install "sequential-analysis[fast]"` adiciona o numpy para os
procedimentos que trabalham com arrays. pandas, polars, clientes Kafka
e matplotlib só são usados se você chamar os adaptadores ou as funções
de gráficos.

### Ela é gratuita para uso comercial?

Ela tem licença dupla: AGPL-3.0 e uma licença comercial. Estes usos são
gratuitos sob a AGPL:

* pesquisa e ensino;
* projetos de código aberto sob a AGPL ou a GPL v3;
* uso interno em uma organização, sem cópias entregues a terceiros e
  sem acesso pela rede para pessoas de fora dela.

Um produto de código fechado, ou um serviço em rede cujo código-fonte
você não publica, precisa de uma licença comercial. A tabela em
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)
decide os casos. Consultas sobre licenciamento: andrei@hobukob.ru.

### Como citá-la?

[CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff),
no repositório, traz a citação, e o botão *Cite this repository* do
GitHub a converte em BibTeX ou APA. As versões são arquivadas no Zenodo
com um DOI. Os métodos e as suas verificações estão descritos no
[artigo](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf).

## Uso

### Posso usá-la para testes A/B em produção?

Sim, como motor estatístico. Ela fornece testes exatos para:

* conversão (`TwoProportionTest`);
* métricas limitadas (`BoundedABTest`);
* taxas (`RateRatioTest`);
* a divisão do tráfego (`SampleRatioMismatch`);
* muitas métricas com controle da taxa de falsas descobertas
  (`MultipleTests`).

Em Python puro, o teste de conversão leva cerca de 10 microssegundos por
usuário, a verificação da divisão 4 e o teste de taxas 40. Um checkpoint
de cada um ocupa 2–4 kilobytes.
`BoundedABTest` mantém uma grade e leva 0,1–0,5 ms.

A biblioteca não é uma plataforma de experimentação: atribuição, coleta
de eventos e painéis ficam por sua conta, ou vêm de uma plataforma.
Veja [testes A/B](ab-testing.md).

### Posso espiar os resultados todo dia?

Sim, com os procedimentos válidos a qualquer momento: é para isso que
eles servem. Com um delineamento sequencial em grupos, olhe apenas nas
análises planejadas. Com um teste clássico de amostra fixa, olhe uma
vez. Veja [olhadas repetidas (peeking)](peeking.md).

### Um teste válido a qualquer momento tem menos poder do que um teste de amostra fixa?

No efeito para o qual o teste de amostra fixa é planejado, sim. Para
atingir o mesmo poder, um teste válido a qualquer momento para duas
proporções precisa de 1,3 a 1,6 vez os usuários. Em troca, você pode
parar mais cedo quando o efeito é maior, e não precisa de um tamanho
amostral fixado de antemão. Um delineamento sequencial em grupos com
poucas olhadas planejadas custa apenas 1–20% a mais do que uma análise
única.

### Sequencial em grupos ou válido a qualquer momento: qual devo usar?

* **Sequencial em grupos** se as análises forem poucas e planejadas,
  como com um comitê de monitoramento de dados ou um ciclo de releases,
  e especialmente para um ensaio clínico confirmatório.
* **Válido a qualquer momento** se você quer olhar continuamente, ou
  não consegue dizer de antemão quando vai olhar ou parar.

### Ela faz testes A/B bayesianos?

Os seus testes A/B são frequentistas, com garantias sobre as taxas de
erro. Componentes bayesianos estão disponíveis onde fazem sentido:

* `ThompsonAllocation` envia o tráfego segundo a probabilidade a
  posteriori de cada braço ser o melhor, com uma regra de perda esperada
  para a implantação;
* `BayesianChangePoint` detecta pontos de mudança;
* os previsores aprendem os seus parâmetros por atualização bayesiana.

### Ela é validada para ensaios clínicos?

Os seus delineamentos sequenciais em grupos (limites, poder, tamanhos
amostrais, números de eventos) são conferidos com o rpact e com o
pacote survival do R na suíte de testes. Ela não é um software validado
no sentido regulatório. Um patrocinador que a use em uma submissão
regulatória a valida como qualquer outra ferramenta. Veja
[ensaios clínicos](clinical-trials.md).

### Minha métrica tem caudas pesadas (receita, latência). O que devo usar?

* Para um quantil (mediana, percentil 90), use `QuantileTest` ou
  `QuantileConfidenceSequence`, que não precisam de suposições.
* Para uma média, ponha um teto nos valores, em um nível fixado de
  antemão, e use `BoundedABTest` ou `BettingConfidenceSequence`
  (exatos).
* Como alternativa, suponha um limite para o desvio-padrão e use
  `CatoniConfidenceSequence`.

Um teste de medianas para duas amostras ainda não está na biblioteca.

### Quão rápida ela é?

Os procedimentos mais simples levam 1–10 microssegundos por observação
em Python puro: SPRTs, CUSUM, os testes sequenciais em grupos e de
mistura, GARCH. Os que mantêm uma grade ou a amostra inteira levam
0,1–10 ms. Exemplos são as sequências de confiança por apostas e de
Catoni, o teste de kernel e os previsores com aprendizado.
[Velocidade](../../performance.md) lista o custo de cada procedimento e
o tamanho do seu checkpoint.

### Posso rodá-la em JavaScript ou no navegador?

Sim. O executor TypeScript em `ts/` roda os procedimentos e continua
checkpoints do Python. Os resumos do histórico e as decisões são
idênticos, e os números coincidem até os últimos bits. Veja
[executor TypeScript](../../typescript.md).

### Uma execução pode sobreviver a uma falha?

Sim. `run.checkpoint()` é JSON simples, e `Run.restore` continua bit a
bit. Observações entregues de novo são descartadas. Veja
[fluxos de dados](streaming.md).

### O que significam "exact" e "asymptotic" na documentação?

O atributo `guarantee` de cada procedimento declara a sua promessa:

* `exact`: a taxa de erro vale para qualquer tamanho amostral sob as
  suposições declaradas;
* `asymptotic`: aproximadamente, em execuções longas;
* `model`: exata sob o modelo declarado;
* `approximate`;
* `none`.

A documentação recomenda o procedimento exato quando houver um
adequado. Veja [Qual método?](../../choosing.md).
