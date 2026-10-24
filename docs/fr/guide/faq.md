---
description: Questions fréquentes sur sequential-analysis, la bibliothèque Python de tests séquentiels et d'inférence valide à tout instant (anytime-valid) - installation, licence et usage commercial, tests A/B en production, essais cliniques, puissance, vitesse, TypeScript, citation.
language: fr
---

# Questions fréquentes

> Ceci est une traduction de la [page en anglais](../../guide/faq.md). Elle n'a pas encore été relue par un locuteur natif ; en cas de divergence, la page en anglais fait foi.

## À propos de la bibliothèque

### Qu'est-ce que sequential-analysis ?

Une bibliothèque Python d'inférence statistique séquentielle. Ses tests,
ses suites de confiance (confidence sequences) et ses détecteurs peuvent
être consultés après chaque observation et arrêtés à tout moment, sans
perdre leurs garanties sur les erreurs. Elle propose :

* des SPRT ;
* des plans séquentiels groupés (group sequential designs) ;
* des tests A/B valides à tout instant (anytime-valid) ;
* des détecteurs de ruptures (change-point detectors) ;
* des filtres de Kalman, particulaires et de Markov caché ;
* la prévision et GARCH.

Tous fonctionnent derrière une seule interface, avec des points de
reprise (checkpoints) JSON. Elle est développée par Novikov Laboratories
LLC.

### Comment l'installer ? De quoi dépend-elle ?

`pip install sequential-analysis`. Elle nécessite Python 3.8 ou
ultérieur (testée jusqu'à 3.14) et rien d'autre.
`pip install "sequential-analysis[fast]"` ajoute numpy pour les
procédures qui travaillent sur des tableaux. pandas, polars, les clients
Kafka et matplotlib ne sont utilisés que si vous appelez les adaptateurs
ou les fonctions de tracé.

### Est-elle gratuite pour un usage commercial ?

Elle est sous double licence, AGPL-3.0 et licence commerciale. Les usages
suivants sont gratuits sous l'AGPL :

* la recherche et l'enseignement ;
* les projets open source sous AGPL ou GPL v3 ;
* l'usage interne dans une organisation, sans copie remise à des tiers
  ni accès par réseau pour des personnes extérieures.

Un produit à code fermé, ou un service en réseau dont vous ne publiez
pas le code source, nécessite une licence commerciale. Le tableau de
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)
tranche les cas. Demandes de licence : andrei@hobukob.ru.

### Comment la citer ?

[CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff)
dans le dépôt donne la citation, et le bouton *Cite this repository* de
GitHub la convertit en BibTeX ou en APA. Les versions sont archivées sur
Zenodo avec un DOI. Les méthodes et leurs vérifications sont décrites
dans l'[article](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf).

## Utilisation

### Puis-je l'utiliser pour des tests A/B en production ?

Oui, comme moteur statistique. Elle fournit des tests exacts pour :

* la conversion (`TwoProportionTest`) ;
* les métriques bornées (`BoundedABTest`) ;
* les taux (`RateRatioTest`) ;
* la répartition du trafic (`SampleRatioMismatch`) ;
* de nombreuses métriques avec contrôle du taux de fausses découvertes
  (false discovery rate) (`MultipleTests`).

En Python pur, le test de conversion prend environ 10 microsecondes par
utilisateur, le contrôle de répartition 4 et le test de taux 40. Un
point de reprise de chacun occupe 2 à 4 kilo-octets.
`BoundedABTest` conserve une grille et prend 0,1 à 0,5 ms.

La bibliothèque n'est pas une plateforme d'expérimentation :
l'affectation, la collecte des événements et les tableaux de bord sont à
construire vous-même ou à prendre dans une plateforme. Voir
[tests A/B](ab-testing.md).

### Puis-je regarder les résultats tous les jours ?

Oui, avec les procédures valides à tout instant : c'est leur raison
d'être. Avec un plan séquentiel groupé, ne regardez qu'aux analyses
prévues. Avec un test classique à échantillon fixe, regardez une fois.
Voir [regards répétés](peeking.md).

### Un test valide à tout instant est-il moins puissant qu'un test à échantillon fixe ?

À l'effet pour lequel le test à échantillon fixe est planifié, oui. Pour
atteindre la même puissance, un test valide à tout instant de deux
proportions demande 1,3 à 1,6 fois les utilisateurs. En échange, vous
pouvez arrêter tôt lorsque l'effet est plus grand, et vous n'avez besoin
d'aucune taille d'échantillon fixée à l'avance. Un plan séquentiel groupé
avec quelques regards prévus ne coûte que 1 à 20 % de plus qu'une
analyse unique.

### Séquentiel groupé ou valide à tout instant : lequel choisir ?

* **Séquentiel groupé** si les analyses sont peu nombreuses et prévues,
  comme avec un comité de surveillance des données ou un cycle de
  livraison, et en particulier pour un essai clinique confirmatoire.
* **Valide à tout instant** si vous voulez regarder en continu, ou ne
  pouvez pas dire à l'avance quand vous regarderez ou arrêterez.

### Fait-elle des tests A/B bayésiens ?

Ses tests A/B sont fréquentistes, avec des garanties sur les taux
d'erreur. Des composants bayésiens sont disponibles là où ils
conviennent :

* `ThompsonAllocation` répartit le trafic selon la probabilité a
  posteriori que chaque bras soit le meilleur, avec une règle de perte
  espérée pour le déploiement ;
* `BayesianChangePoint` détecte les points de rupture ;
* les modèles de prévision apprennent leurs paramètres par mise à jour
  bayésienne.

### Est-elle validée pour les essais cliniques ?

Ses plans séquentiels groupés (bornes, puissance, tailles d'échantillon,
nombres d'événements) sont vérifiés par rapport à rpact et au package R
survival dans la suite de tests. Ce n'est pas un logiciel validé au sens
réglementaire. Un promoteur qui l'utilise pour une soumission la valide
comme tout autre outil. Voir [essais cliniques](clinical-trials.md).

### Ma métrique est à queues lourdes (revenu, latence). Que dois-je utiliser ?

* Pour un quantile (médiane, 90e centile), utilisez `QuantileTest` ou
  `QuantileConfidenceSequence`, qui ne demandent aucune hypothèse.
* Pour une moyenne, plafonnez les valeurs à un niveau fixé à l'avance et
  utilisez `BoundedABTest` ou `BettingConfidenceSequence` (exacts).
* Autrement, supposez une borne sur l'écart-type et utilisez
  `CatoniConfidenceSequence`.

Un test de médianes à deux échantillons ne figure pas encore dans la
bibliothèque.

### Quelle est sa vitesse ?

Les procédures les plus simples prennent 1 à 10 microsecondes par
observation en Python pur : les SPRT, CUSUM, les tests séquentiels
groupés et de mélange, GARCH. Celles qui conservent une grille ou
l'échantillon entier prennent 0,1 à 10 ms. C'est le cas par exemple des
suites de confiance par pari et de Catoni, du test à noyau et des
modèles de prévision appris.
[Vitesse](../../performance.md) indique le coût et la taille du point de
reprise de chaque procédure.

### Puis-je l'exécuter en JavaScript ou dans le navigateur ?

Oui. L'exécuteur TypeScript de `ts/` exécute les procédures et poursuit
les points de reprise Python. Les empreintes d'historique et les
décisions sont identiques, et les nombres concordent jusqu'aux derniers
bits. Voir [exécuteur TypeScript](../../typescript.md).

### Une exécution peut-elle survivre à une panne ?

Oui. `run.checkpoint()` est du JSON simple, et `Run.restore` reprend bit
à bit. Les observations livrées une seconde fois sont écartées. Voir
[flux](streaming.md).

### Que signifient « exact » et « asymptotic » dans la documentation ?

L'attribut `guarantee` de chaque procédure énonce sa promesse :

* `exact` : le taux d'erreur est respecté pour toute taille
  d'échantillon sous les hypothèses énoncées ;
* `asymptotic` : approximativement, sur de longues exécutions ;
* `model` : exact sous le modèle énoncé ;
* `approximate` ;
* `none`.

La documentation recommande la procédure exacte lorsqu'il en existe une
qui convient. Voir [Quelle méthode ?](../../choosing.md).
