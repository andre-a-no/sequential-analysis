---
description: Guia do usuário do sequential-analysis, uma biblioteca Python para testes sequenciais e inferência válida a qualquer momento (anytime-valid). Cada página responde diretamente a uma pergunta, com código que roda como está escrito e a sua saída.
language: pt-BR
---

# Guia do usuário

> Esta é uma tradução da [página em inglês](../../guide/index.md). Ainda não foi revisada por um falante nativo; onde as duas divergirem, a página em inglês prevalece.

Este guia está organizado pelas perguntas que as pessoas fazem. Cada
página começa com uma resposta direta e depois traz um programa curto
que roda como está escrito, a sua saída, a garantia por trás da
resposta e os casos em que o método não se aplica. Os
[tutoriais](../../tutorials/ab-test.md) aprofundam cada assunto.

## A biblioteca em um parágrafo

**sequential-analysis** é uma biblioteca Python para inferência
estatística sobre dados que chegam uma observação por vez. Seus testes,
intervalos de confiança e detectores podem ser consultados após cada
observação e interrompidos a qualquer momento, e suas taxas de erro
continuam valendo. Ela cobre:

* o SPRT de Wald e planos sequenciais ótimos;
* delineamentos sequenciais em grupos (group sequential designs) para
  ensaios clínicos (funções de gasto de O'Brien–Fleming e de Pocock,
  limites de futilidade);
* testes A/B válidos a qualquer momento, com valores-e (e-values) e
  sequências de confiança (confidence sequences);
* detecção de pontos de mudança (change-point detection);
* filtros de Kalman, de partículas e de modelos ocultos de Markov;
* previsão (forecasting) e volatilidade GARCH.

Toda execução pode ser salva como checkpoint em JSON e retomada bit a
bit em Python, ou continuada no seu executor TypeScript com as mesmas
decisões.

| | |
|---|---|
| Instalação | `pip install sequential-analysis` |
| Importação | `import sequential_analysis` |
| Python | 3.8 a 3.14, sem dependências obrigatórias (numpy opcional) |
| Licença | AGPL-3.0, ou uma licença comercial da Novikov Laboratories LLC |
| Código-fonte | <https://github.com/andre-a-no/sequential-analysis> |
| Documentação | <https://andre-a-no.github.io/sequential-analysis/> |

## Perguntas

**Conceitos**

* [Por que não posso olhar um valor-p todo dia?](peeking.md) O problema
  do *peeking* e as três famílias de métodos sequenciais.
* [Glossário](glossary.md): valor-e, sequência de confiança, gasto de
  alfa, ARL e os demais termos, com seus sinônimos.

**Tarefas**

* [Como interromper um teste A/B antes do previsto sem inflar os falsos positivos?](ab-testing.md)
* [Como obter um intervalo de confiança que continue válido se eu continuar olhando?](confidence-sequences.md)
* [Como rodar o SPRT de Wald em Python?](sprt.md)
* [Como planejar as análises interinas de um ensaio clínico?](clinical-trials.md)
* [Como detectar uma mudança em um fluxo de medições?](change-detection.md)
* [Como rodar estatísticas sobre um fluxo de dados e retomar após uma falha?](streaming.md)

**Escolha**

* [Qual método para a minha pergunta?](../../choosing.md): a tabela completa.
* [Como ela se compara a outras bibliotecas?](comparison.md)
* [Perguntas frequentes](faq.md)

## Como ler as garantias

Todo procedimento tem um atributo `guarantee`. O guia o cita em cada
resposta:

* **exact:** a taxa de erro vale para qualquer tamanho amostral sob as
  suposições declaradas.
* **asymptotic:** vale aproximadamente, e melhor para amostras maiores.
* **model:** as probabilidades são exatas sob o modelo declarado, mas
  nada é afirmado além dele.
* **approximate:** uma aproximação mesmo sob o modelo.
* **none:** o procedimento transforma os dados e não afirma nada.
