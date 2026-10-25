---
description: Comment exécuter des statistiques séquentielles sur un flux (Kafka, SQL, pandas, capteurs) et reprendre après une panne exactement là où elles se sont arrêtées. Points de reprise JSON, livraison dédupliquée, empreinte de l'historique pour l'audit, et la même exécution poursuivie en Python ou en TypeScript, avec sequential-analysis.
language: fr
---

# Comment faire des statistiques sur un flux et reprendre après une panne ?

> Ceci est une traduction de la [page en anglais](../../guide/streaming.md). Elle n'a pas encore été relue par un locuteur natif ; en cas de divergence, la page en anglais fait foi.

**Réponse courte.** Enveloppez la procédure dans un `Run`. Ensuite :

1. Fournissez-lui les observations avec `run_sync` (ou `run_async` pour
   des producteurs concurrents).
2. Sauvegardez `run.checkpoint()` aussi souvent que vous le souhaitez.
   C'est un point de reprise (checkpoint) : une simple valeur JSON
   contenant l'état, l'état du générateur aléatoire, les positions dans
   les sources et une empreinte SHA-256 de l'historique (history
   digest).
3. Après une panne, `Run.restore(procedure, checkpoint)` reprend
   exactement, bit à bit. Avec `Delivery("sequence")`, les observations
   livrées une seconde fois après le redémarrage sont écartées comme
   doublons.
4. L'exécuteur TypeScript peut poursuivre le même point de reprise en
   JavaScript. Il donne les mêmes décisions et la même empreinte
   d'historique, et des nombres qui concordent jusqu'aux derniers bits :
   identiques dans 34 des 108 cas de conformité, à moins de 6·10⁻¹³ en
   valeur relative dans les autres.

## Panne, redémarrage, rejeu : le même résultat

Une exécution de surveillance sur 300 mesures est interrompue après 120.
La source est rejouée à partir de la mesure 100, comme le fait
typiquement une file de messages après un redémarrage. L'exécution
restaurée écarte les 20 mesures qu'elle a déjà vues et se termine
exactement là où se serait terminée une exécution ininterrompue :

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

L'empreinte de l'historique est une chaîne de hachage sur chaque
observation que l'exécution a utilisée. Deux exécutions ayant la même
empreinte ont vu les mêmes données dans le même ordre. Un auditeur peut
la recalculer à partir du journal des observations, en suivant la
[spécification](../../spec.md).

## D'où viennent les observations

| Source | Fonction |
|---|---|
| une liste ou un générateur de valeurs | `sources.from_values` |
| un fichier CSV | `sources.from_csv` |
| un DataFrame pandas ou polars | `adapters.from_dataframe` |
| une requête SQL (toute connexion DB-API) | `adapters.from_sql` |
| des messages Kafka, avec offsets validés (committed) | `adapters.from_kafka`, `adapters.kafka_offsets` |
| plusieurs sources à la fois | `sources.interleave`, `sources.merge_ordered` |
| un journal d'observations enregistré | `sources.replay` |

Les entrées provenant de sources différentes sont reliées par une
**topologie**. `KeyJoin` joint une affectation et un résultat par
utilisateur, `TimeAlign` aligne deux capteurs dans le temps, et
`AsOfJoin` rattache des événements aux barres qui en avaient
connaissance. Voir [sources de données](../../adapters.md).

## Quand la procédure change

Un point de reprise enregistre le nom, la version et la configuration de
la procédure. `Run.restore` refuse un point de reprise créé par une
autre procédure, une autre configuration ou une version dont
l'arithmétique diffère, et lève `IncompatibleCheckpoint`. Une exécution
n'est donc jamais poursuivie silencieusement avec d'autres nombres.

Pour aller plus loin : [points de reprise, journaux et backends](../../checkpoints.md),
[exécuteur TypeScript](../../typescript.md),
[spécification des formats](../../spec.md).
