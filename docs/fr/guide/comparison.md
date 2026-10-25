---
description: Comment sequential-analysis se compare aux autres bibliothèques Python et R pour les tests séquentiels, les tests A/B, les plans séquentiels groupés, la détection de ruptures et le filtrage (statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn), et quand utiliser laquelle.
language: fr
---

# Comment se compare-t-elle aux autres bibliothèques ?

> Ceci est une traduction de la [page en anglais](../../guide/comparison.md). Elle n'a pas encore été relue par un locuteur natif ; en cas de divergence, la page en anglais fait foi.

**Réponse courte.** La plupart des bibliothèques couvrent bien une
famille de méthodes. sequential-analysis réunit les principales
familles de l'inférence séquentielle derrière une seule interface :

* les SPRT et les plans optimaux ;
* les plans séquentiels groupés (group sequential designs) ;
* les tests valides à tout instant (anytime-valid) et les suites de
  confiance (confidence sequences) ;
* la détection de ruptures (change detection) ;
* les filtres à espace d'états.

Ce qu'elle apporte au-delà des méthodes elles-mêmes :

* chaque procédure énonce sa garantie (`exact`, `asymptotic`, `model`,
  ...) ;
* chaque exécution peut être sauvegardée et reprise bit à bit ;
* les formats sont spécifiés et exécutés par une seconde implémentation
  en TypeScript ;
* il n'y a aucune dépendance obligatoire.

Si vous n'avez besoin que de l'une des méthodes ci-dessous et utilisez
déjà la bibliothèque qui s'y consacre, continuez à utiliser cette
bibliothèque. Le tableau indique où chaque outil est le choix naturel.
Les descriptions portent sur l'objet principal de chaque bibliothèque,
en octobre 2026, et ne constituent pas une liste complète de ses
fonctionnalités.

| Besoin | Choix naturels | Ce que propose sequential-analysis |
|---|---|---|
| tests à échantillon fixe, régression, puissance | scipy.stats, statsmodels | ce n'est pas son objet |
| plans séquentiels groupés pour une soumission réglementaire | rpact, gsDesign (R) | les mêmes plans, vérifiés par rapport à rpact dans sa suite de tests ; conduit l'essai pas à pas avec des points de reprise |
| suites de confiance, e-valeurs | confseq (Python), safestats (R) | suites de confiance pour des moyennes, des quantiles, des coefficients de régression, des effets à deux échantillons ; e-BH et e-LOND pour de nombreux tests |
| tests A/B sous forme de plateforme avec interface | GrowthBook, Statsig, Eppo, Optimizely (plateformes) | un moteur à intégrer : tests exacts pour la conversion, les métriques bornées et les taux, SRM, FDR sur plusieurs métriques |
| segmentation hors ligne en ruptures d'une série terminée | ruptures (Python), changepoint (R) | détection en ligne pendant que les données arrivent : CUSUM, Shiryaev–Roberts, e-détecteurs, points de rupture bayésiens en ligne |
| filtres de Kalman | filterpy, statsmodels state space | filtres de Kalman, de Kalman robuste, particulaires et HMM, avec lissage et points de reprise |
| GARCH | arch | GARCH(1,1) et GJR ajustés au même maximum qu'arch (vérifié dans les tests), puis exécutés en ligne |
| modèles de Markov cachés | hmmlearn | le filtre en ligne, Baum–Welch en accord avec hmmlearn, EM en ligne |
| prévision | statsmodels, autres | prévisions ETS et AR en accord avec statsmodels, apprises en ligne, avec des intervalles conformes |

## Cas où un autre outil est préférable

* **Une soumission à une autorité réglementaire.** rpact est largement
  utilisé à cette fin, et ses développeurs proposent une documentation
  de validation. sequential-analysis concorde avec lui sur les plans
  qu'elle couvre, mais un promoteur devrait tout de même la valider.
* **Les grandes analyses hors ligne sur des tableaux.** Les
  bibliothèques fondées sur numpy sont plus rapides par observation.
  sequential-analysis est conçue pour traiter une observation à la fois ;
  voir [Vitesse](../../performance.md) pour le coût de chaque procédure.
* **Les méthodes qu'elle n'a pas.** Elle n'a pas encore de test de
  médianes à deux échantillons, ni de processus de Hawkes multivariés,
  ni de modèles ARIMA avec termes de moyenne mobile. Voir le
  [journal des modifications](../../changelog.md) pour ce qui est ajouté.
