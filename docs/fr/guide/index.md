---
description: Guide de l'utilisateur de sequential-analysis, une bibliothèque Python de tests séquentiels et d'inférence valide à tout instant (anytime-valid). Chaque page répond directement à une question, avec du code qui s'exécute et sa sortie.
language: fr
---

# Guide de l'utilisateur

> Ceci est une traduction de la [page en anglais](../../guide/index.md). Elle n'a pas encore été relue par un locuteur natif ; en cas de divergence, la page en anglais fait foi.

Ce guide est organisé selon les questions que l'on se pose. Chaque page
commence par une réponse directe, puis donne un court programme qui
s'exécute tel quel, sa sortie, la garantie sur laquelle repose la
réponse et les cas où la méthode ne s'applique pas. Les
[tutoriels](../../tutorials/ab-test.md) approfondissent chaque sujet.

## La bibliothèque en un paragraphe

**sequential-analysis** est une bibliothèque Python d'inférence
statistique sur des données qui arrivent une observation à la fois. Ses
tests, ses intervalles de confiance et ses détecteurs peuvent être
consultés après chaque observation et arrêtés à tout moment, sans que
leurs taux d'erreur cessent d'être garantis. Elle couvre :

* le SPRT de Wald et les plans séquentiels optimaux ;
* les plans séquentiels groupés (group sequential designs) pour les
  essais cliniques (dépense de l'alpha d'O'Brien–Fleming et de Pocock,
  bornes de futilité) ;
* les tests A/B valides à tout instant (anytime-valid), avec des
  e-valeurs (e-values) et des suites de confiance (confidence sequences) ;
* la détection de ruptures (change-point detection) ;
* les filtres de Kalman, particulaires et de Markov caché ;
* la prévision et la volatilité GARCH.

Chaque exécution peut être sauvegardée sous forme de point de reprise
(checkpoint) JSON et reprise bit à bit en Python, ou poursuivie dans son
exécuteur TypeScript avec les mêmes décisions.

| | |
|---|---|
| Installation | `pip install sequential-analysis` |
| Import | `import sequential_analysis` |
| Python | 3.8 à 3.14, aucune dépendance obligatoire (numpy facultatif) |
| Licence | AGPL-3.0, ou licence commerciale de Novikov Laboratories LLC |
| Sources | <https://github.com/andre-a-no/sequential-analysis> |
| Documentation | <https://andre-a-no.github.io/sequential-analysis/> |

## Questions

**Notions**

* [Pourquoi ne puis-je pas regarder une p-valeur tous les jours ?](peeking.md)
  Les regards répétés (peeking) et les trois familles de méthodes
  séquentielles.
* [Glossaire](glossary.md) : e-valeur, suite de confiance, dépense de
  l'alpha, ARL et les autres termes, avec leurs synonymes.

**Tâches**

* [Comment arrêter un test A/B plus tôt sans gonfler les faux positifs ?](ab-testing.md)
* [Comment obtenir un intervalle de confiance qui reste valide quand on continue à regarder ?](confidence-sequences.md)
* [Comment exécuter le SPRT de Wald en Python ?](sprt.md)
* [Comment planifier les analyses intermédiaires d'un essai clinique ?](clinical-trials.md)
* [Comment détecter un changement dans un flux de mesures ?](change-detection.md)
* [Comment faire des statistiques sur un flux et reprendre après une panne ?](streaming.md)

**Choisir**

* [Quelle méthode pour ma question ?](../../choosing.md) : le tableau complet.
* [Comment se compare-t-elle aux autres bibliothèques ?](comparison.md)
* [Questions fréquentes](faq.md)

## Comment lire les garanties

Chaque procédure possède un attribut `guarantee`. Le guide le cite avec
chaque réponse :

* **exact** : le taux d'erreur est respecté pour toute taille
  d'échantillon sous les hypothèses énoncées.
* **asymptotic** : il est respecté approximativement, et d'autant mieux
  que l'échantillon est grand.
* **model** : les probabilités sont exactes sous le modèle énoncé, mais
  rien n'est affirmé au-delà.
* **approximate** : une approximation, même sous le modèle.
* **none** : la procédure transforme les données et n'affirme rien.
