---
description: Glossário de termos de análise sequencial e inferência válida a qualquer momento (anytime-valid) - valor-e (e-value), processo-e, sequência de confiança, valor-p sempre válido, mSPRT, gasto de alfa, fração de informação, ARL, SRM, CUPED, e-BH - com sinônimos e os procedimentos do sequential-analysis que implementam cada um.
language: pt-BR
---

# Glossário

> Esta é uma tradução da [página em inglês](../../guide/glossary.md). Ainda não foi revisada por um falante nativo; onde as duas divergirem, a página em inglês prevalece.

Termos usados em análise sequencial e nesta biblioteca. Entre
parênteses estão o termo em inglês e os sinônimos de uso comum.

**Análise sequencial** (sequential analysis; também testes sequenciais,
inferência sequencial: sequential testing, sequential inference).
Estatística em que o número de observações não é fixado de antemão.
Após cada observação ou grupo de observações, o procedimento decide se
para ou continua. Fundada por Wald (1945).

**Olhadas repetidas** (peeking; também parada opcional, monitoramento
contínuo: optional stopping, data peeking, continuous monitoring).
Conferir repetidamente um teste de amostra fixa e parar quando ele dá
significativo. Infla a taxa de falsos positivos; veja
[olhadas repetidas](peeking.md).

**SPRT** (sequential probability ratio test, teste sequencial da razão
de probabilidades, teste de Wald). Acumula o logaritmo da razão de
verossimilhanças de duas hipóteses simples e para quando ele sai de um
intervalo. `SPRT`; versões truncadas: `TwoSPRT` (o 2-SPRT de Lorden) e
`kiefer_weiss_plan`. Veja [SPRT](sprt.md).

**Delineamento sequencial em grupos** (group sequential design; também
análises interinas, ensaio sequencial em grupos: interim analyses, group
sequential trial). Poucas análises planejadas, cada uma com um limite.
Os limites são escolhidos de modo que o erro tipo I global seja alfa.
`group_sequential_design`. Veja [ensaios clínicos](clinical-trials.md).

**Função de gasto de alfa** (alpha spending function; também gasto do
erro, Lan–DeMets: error spending). Indica quanto do erro tipo I pode
ser consumido até cada fração de informação. O gasto tipo
O'Brien–Fleming gasta pouco no início; o tipo Pocock gasta de forma
uniforme. `spending="obrien-fleming"`, `"pocock"`, ...

**Fração de informação** (information fraction). A parcela da
informação estatística planejada (pacientes, eventos) atingida em uma
análise.

**Limite de futilidade** (futility boundary; também futilidade não
vinculante: non-binding futility). Um limite inferior: abaixo dele,
recomenda-se parar por falta de efeito. Um limite não vinculante pode
ser ignorado sem inflar o erro tipo I.

**Inferência válida a qualquer momento** (anytime-valid inference;
também always-valid inference, safe anytime-valid inference, SAVI).
Testes e intervalos cujas garantias valem em todos os tamanhos
amostrais ao mesmo tempo, de modo que podem ser monitorados
continuamente e interrompidos por qualquer motivo.

**Valor-e** (e-value; também variável-e, escore de aposta: e-variable,
betting score). Uma estatística não negativa cuja esperança sob a
hipótese nula é no máximo 1. Um valor-e grande é evidência contra a
nula: rejeitar quando ele passa de 1/alpha tem erro tipo I de no máximo
alfa. A saída `log_e_value` de muitos procedimentos.

**Processo-e** (e-process; também martingal de teste, supermartingal de
teste, processo de riqueza: test martingale, test supermartingale,
wealth process). Uma sequência de valores-e que continua válida em
tempos de parada. O seu máximo acumulado cruza 1/alpha com
probabilidade de no máximo alfa sob a nula (desigualdade de Ville).

**Valor-p sempre válido** (always-valid p-value; também anytime-valid
p-value, valor-p sequencial: sequential p-value). Um valor-p que é
válido em qualquer tempo de parada. É o inverso do máximo acumulado de
um processo-e. A saída `p_value` dos procedimentos válidos a qualquer
momento.

**Sequência de confiança** (confidence sequence; também intervalo de
confiança válido a qualquer momento, sempre válido ou uniforme no
tempo: anytime-valid confidence interval, always-valid confidence
interval, time-uniform confidence interval). Uma sequência de
intervalos que contém o valor verdadeiro em todos os tamanhos amostrais
simultaneamente com probabilidade de pelo menos 1 − alpha.
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, e as saídas
`lower` e `upper` de muitos testes. Veja
[sequências de confiança](confidence-sequences.md).

**mSPRT** (mixture SPRT, SPRT de mistura, mistura de Robbins: Robbins'
mixture). Um SPRT cuja alternativa é ponderada por uma distribuição a
priori, o que o torna válido a qualquer momento contra toda
alternativa. `NormalMixtureSPRT` (variância conhecida), `TMixtureSPRT`
(variância desconhecida).

**Testes por apostas** (testing by betting). Construir processos-e como
a riqueza de um apostador que aposta contra a hipótese nula.
`BettingMeanTest`, `BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal, ótimo em taxa de crescimento). Um valor-e
escolhido para maximizar o crescimento logarítmico esperado da evidência
sob a alternativa. `TwoProportionTest(method="grow")`.

**Inferência universal** (universal inference). Um valor-e obtido de
uma razão de verossimilhanças em que a alternativa é estimada apenas com
dados passados. Continua válido sob delineamentos adaptativos.
`TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). Controla a taxa de falsas descobertas
sobre muitos valores-e, sob qualquer dependência. `MultipleTests`,
`e_bh`.

**e-LOND, FDR online** (online FDR). Controle da taxa de falsas
descobertas sobre uma série de hipóteses decididas uma a uma.
`OnlineFDR`.

**SRM** (sample ratio mismatch, desbalanceamento da proporção amostral).
A divisão observada do tráfego entre os braços difere da configurada,
sinal de um bug no experimento. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data; também
ajuste por covariáveis, ajuste por regressão: covariate adjustment,
regression adjustment). Reduz a variância de um efeito A/B com uma
covariável medida antes do experimento. `ABTest(covariate=True)`,
`AnytimeLinearModel`.

**Métrica de razão** (ratio metric; também método delta: delta method).
Uma métrica que é a razão de duas somas por usuário, como a receita por
sessão. `RatioABTest`.

**Detecção de pontos de mudança** (change-point detection; também
detecção de mudanças, detecção mais rápida, detecção online de
anomalias: change detection, quickest detection, online anomaly
detection). Disparar um alarme logo depois que a distribuição de um
fluxo de dados muda. `CUSUM`, `ShiryaevRoberts`, `MeanEDetector`,
`QuantileEDetector`, `BayesianChangePoint`. Veja
[detecção de mudanças](change-detection.md).

**ARL** (average run length, comprimento médio de corrida, ARL₀, tempo
médio até um alarme falso: mean time to false alarm). O número esperado
de observações até um alarme falso quando nada mudou. O controle de
alarmes falsos dos detectores de mudança.

**Detector-e** (e-detector). Um detector de mudanças construído a partir
de processos-e, um iniciado em cada instante possível de mudança. O seu
ARL é garantido sob uma hipótese nula não paramétrica.
`MeanEDetector`, `QuantileEDetector`.

**Problema de Kiefer–Weiss** (Kiefer–Weiss problem). Encontrar o teste
sequencial com um tamanho amostral máximo que minimiza o maior tamanho
amostral esperado. `kiefer_weiss_plan`.

**Característica de operação** (operating characteristic). As
probabilidades de erro e a distribuição do tamanho amostral de um
plano, como funções do parâmetro verdadeiro.
`operating_characteristic`.

**Checkpoint** (ponto de verificação). Um valor JSON a partir do qual
uma execução continua exatamente. `Run.checkpoint`, `Run.restore`. Veja
[fluxos de dados](streaming.md).

**Resumo do histórico** (history digest). Uma cadeia de hashes SHA-256
sobre as observações que uma execução usou, guardada em todo
checkpoint, para auditoria.

**Garantia** (guarantee: `exact`, `asymptotic`, `model`, `approximate`,
`none`). O atributo em que cada procedimento desta biblioteca declara o
que promete. Veja [Qual método?](../../choosing.md).
