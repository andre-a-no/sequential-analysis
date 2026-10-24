---
description: Como rodar estatística sequencial sobre um fluxo de dados (Kafka, SQL, pandas, sensores) e retomar após uma falha exatamente de onde parou. Checkpoints em JSON, entrega sem duplicatas, um resumo do histórico (history digest) para auditoria e a mesma execução continuada em Python ou TypeScript, com sequential-analysis.
language: pt-BR
---

# Como rodar estatísticas sobre um fluxo de dados e retomar após uma falha?

> Esta é uma tradução da [página em inglês](../../guide/streaming.md). Ainda não foi revisada por um falante nativo; onde as duas divergirem, a página em inglês prevalece.

**Resposta curta.** Envolva o procedimento em um `Run`. Depois:

1. Alimente-o com observações usando `run_sync` (ou `run_async` para
   produtores concorrentes).
2. Salve `run.checkpoint()` com a frequência que quiser. É um valor
   JSON simples com o estado, o estado do gerador aleatório, as posições
   nas fontes e um resumo (digest) SHA-256 do histórico.
3. Após uma falha, `Run.restore(procedure, checkpoint)` continua
   exatamente, bit a bit. Com `Delivery("sequence")`, as observações
   entregues de novo após a reinicialização são descartadas como
   duplicatas.
4. O executor TypeScript pode continuar o mesmo checkpoint em
   JavaScript. Ele dá as mesmas decisões e o mesmo resumo do histórico,
   e números que coincidem até os últimos bits: idênticos em 34 dos 108
   casos de conformidade e com diferença relativa de no máximo 6·10⁻¹³
   nos demais.

## Falha, reinício, reprocessamento: o mesmo resultado

Uma execução de monitoramento sobre 300 leituras é interrompida após
120. A fonte é reprocessada a partir da leitura 100, como uma fila de
mensagens costuma fazer após um reinício. A execução restaurada descarta
as 20 leituras que já viu e termina exatamente onde terminaria uma
execução sem interrupção:

```python
import json
import random

from sequential_analysis import Delivery, Observation, Run, run_sync
from sequential_analysis.procedures import BettingConfidenceSequence

rnd = random.Random(5)
readings = [Observation("x", rnd.betavariate(2, 5), seq=i, source="sensor-7") for i in range(300)]

def procedure():
    return BettingConfidenceSequence(lower=0.0, upper=1.0, grid=200)

run = Run(procedure(), delivery=Delivery("sequence"), run_id="sensor-7")
run_sync(run, readings[:120])
saved = json.dumps(run.checkpoint())        # to a file, a database, object storage
del run                                     # the process dies

run = Run.restore(procedure(), json.loads(saved), delivery=Delivery("sequence"))
run_sync(run, readings[100:])               # the source replays from reading 100
print(f"resumed run: {run.t} readings, {run.delivery.duplicates} duplicates dropped")

uninterrupted = Run(procedure(), delivery=Delivery("sequence"), run_id="sensor-7")
run_sync(uninterrupted, readings)
print("same state as an uninterrupted run:", run.state == uninterrupted.state)
print("same history digest:", run.checkpoint()["history_digest"] == uninterrupted.checkpoint()["history_digest"])
print(f"checkpoint size: {len(saved)} bytes")
```

```text
resumed run: 300 readings, 20 duplicates dropped
same state as an uninterrupted run: True
same history digest: True
checkpoint size: 9606 bytes
```

O resumo do histórico (history digest) é uma cadeia de hashes sobre
todas as observações que a execução usou. Duas execuções com o mesmo
resumo viram os mesmos dados na mesma ordem. Um auditor pode
recalculá-lo a partir do log de observações, seguindo a
[especificação](../../spec.md).

## De onde vêm as observações

| Fonte | Função |
|---|---|
| uma lista ou um gerador de valores | `sources.from_values` |
| um arquivo CSV | `sources.from_csv` |
| um DataFrame do pandas ou do polars | `adapters.from_dataframe` |
| uma consulta SQL (qualquer conexão DB-API) | `adapters.from_sql` |
| mensagens do Kafka, com offsets confirmados | `adapters.from_kafka`, `adapters.kafka_offsets` |
| várias fontes ao mesmo tempo | `sources.interleave`, `sources.merge_ordered` |
| um log de observações gravado | `sources.replay` |

Entradas de fontes diferentes são relacionadas por uma **topologia**.
`KeyJoin` junta uma atribuição e um resultado por usuário, `TimeAlign`
alinha dois sensores no tempo e `AsOfJoin` associa eventos às barras que
já os conheciam. Veja [fontes de dados](../../adapters.md).

## Quando o procedimento muda

Um checkpoint registra o nome, a versão e a configuração do
procedimento. `Run.restore` recusa um checkpoint criado por outro
procedimento, por outra configuração ou por uma versão com aritmética
diferente, e lança `IncompatibleCheckpoint`. Assim, uma execução nunca é
continuada silenciosamente com outros números.

Mais: [checkpoints, logs e backends](../../checkpoints.md),
[executor TypeScript](../../typescript.md),
[especificação dos formatos](../../spec.md).
