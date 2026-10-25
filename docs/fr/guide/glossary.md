---
description: Glossaire de l'analyse séquentielle et de l'inférence valide à tout instant (anytime-valid) - e-valeur, e-processus, suite de confiance, p-valeur toujours valide, mSPRT, dépense de l'alpha, fraction d'information, ARL, SRM, CUPED, e-BH - avec les synonymes et les procédures de sequential-analysis qui implémentent chaque notion.
language: fr
---

# Glossaire

> Ceci est une traduction de la [page en anglais](../../guide/glossary.md). Elle n'a pas encore été relue par un locuteur natif ; en cas de divergence, la page en anglais fait foi.

Termes employés en analyse séquentielle et dans cette bibliothèque. Les
synonymes d'usage courant sont donnés entre parenthèses, avec le terme
anglais.

**Analyse séquentielle** (sequential analysis ; tests séquentiels,
inférence séquentielle ; sequential testing, sequential inference).
Statistique dans laquelle le nombre d'observations n'est pas fixé à
l'avance. Après chaque observation ou groupe d'observations, la
procédure décide d'arrêter ou de continuer. Fondée par Wald (1945).

**Regards répétés** (peeking ; arrêt optionnel, surveillance continue ;
optional stopping, data peeking, continuous monitoring). Consulter un
test à échantillon fixe à plusieurs reprises et arrêter lorsqu'il est
significatif. Cela gonfle le taux de faux positifs ; voir
[regards répétés](peeking.md).

**SPRT** (test séquentiel du rapport de vraisemblance, test de Wald ;
sequential probability ratio test, Wald's test). Il cumule le logarithme
du rapport de vraisemblance de deux hypothèses simples et s'arrête
lorsque celui-ci sort d'un intervalle. `SPRT` ; versions tronquées
`TwoSPRT` (le 2-SPRT de Lorden) et `kiefer_weiss_plan`. Voir
[SPRT](sprt.md).

**Plan séquentiel groupé** (group sequential design ; analyses
intermédiaires, essai séquentiel groupé ; interim analyses, group
sequential trial). Quelques analyses prévues, chacune avec une borne.
Les bornes sont choisies de sorte que l'erreur de première espèce
globale soit alpha. `group_sequential_design`. Voir
[essais cliniques](clinical-trials.md).

**Fonction de dépense de l'alpha** (alpha spending function ; dépense
de l'erreur, Lan–DeMets ; error spending). Elle indique quelle part de
l'erreur de première espèce peut être consommée à chaque fraction
d'information. La dépense de type O'Brien–Fleming dépense peu au début,
celle de type Pocock dépense uniformément.
`spending="obrien-fleming"`, `"pocock"`, ...

**Fraction d'information** (information fraction). La part de
l'information statistique prévue (patients, événements) atteinte lors
d'une analyse.

**Borne de futilité** (futility boundary ; futilité non contraignante,
non-binding futility). Une borne inférieure : en dessous, il est
recommandé d'arrêter pour absence d'effet. Une borne non contraignante
peut être ignorée sans gonfler l'erreur de première espèce.

**Inférence valide à tout instant** (anytime-valid inference ; inférence
toujours valide, always-valid inference, safe anytime-valid inference,
SAVI). Tests et intervalles dont les garanties valent simultanément pour
toutes les tailles d'échantillon, si bien qu'on peut les surveiller en
continu et les arrêter pour n'importe quelle raison.

**E-valeur** (e-value ; e-variable, score de pari, betting score). Une
statistique positive ou nulle dont l'espérance sous l'hypothèse nulle
est au plus 1. Une grande e-valeur est un indice contre l'hypothèse
nulle : rejeter lorsqu'elle dépasse 1/alpha donne une erreur de première
espèce d'au plus alpha. La sortie `log_e_value` de nombreuses
procédures.

**E-processus** (e-process ; martingale de test, surmartingale de test,
processus de richesse ; test martingale, test supermartingale, wealth
process). Une suite d'e-valeurs qui reste valide aux temps d'arrêt. Son
maximum courant franchit 1/alpha avec une probabilité d'au plus alpha
sous l'hypothèse nulle (inégalité de Ville).

**P-valeur toujours valide** (always-valid p-value ; p-valeur valide à
tout instant, p-valeur séquentielle ; anytime-valid p-value, sequential
p-value). Une p-valeur valide à tout temps d'arrêt. C'est l'inverse du
maximum courant d'un e-processus. La sortie `p_value` des procédures
valides à tout instant.

**Suite de confiance** (confidence sequence ; intervalle de confiance
valide à tout instant, intervalle de confiance toujours valide,
intervalle de confiance uniforme en temps ; anytime-valid confidence
interval, always-valid confidence interval, time-uniform confidence
interval). Une suite d'intervalles qui contient la vraie valeur pour
toutes les tailles d'échantillon simultanément avec une probabilité d'au
moins 1 − alpha. `BettingConfidenceSequence`,
`QuantileConfidenceSequence`, `CatoniConfidenceSequence`,
`AsymptoticConfidenceSequence`, ainsi que les sorties `lower` et `upper`
de nombreux tests. Voir [suites de confiance](confidence-sequences.md).

**mSPRT** (SPRT de mélange, mélange de Robbins ; mixture SPRT, Robbins'
mixture). Un SPRT dont l'alternative est moyennée selon une loi a
priori, ce qui le rend valide à tout instant contre toute alternative.
`NormalMixtureSPRT` (variance connue), `TMixtureSPRT` (variance
inconnue).

**Test par pari** (testing by betting). Construction d'e-processus
comme la richesse d'un parieur qui parie contre l'hypothèse nulle.
`BettingMeanTest`, `BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal, optimal en taux de croissance). Une
e-valeur choisie pour maximiser la croissance logarithmique espérée de
l'évidence sous l'alternative. `TwoProportionTest(method="grow")`.

**Inférence universelle** (universal inference). Une e-valeur issue
d'un rapport de vraisemblance dont l'alternative est estimée uniquement
à partir des données passées. Elle reste valide sous des plans
adaptatifs. `TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). Il contrôle le taux de fausses
découvertes (false discovery rate) sur de nombreuses e-valeurs, sous
toute dépendance. `MultipleTests`, `e_bh`.

**e-LOND, FDR en ligne** (online FDR). Contrôle du taux de fausses
découvertes sur une série d'hypothèses décidées une à une. `OnlineFDR`.

**SRM** (sample ratio mismatch ; déséquilibre de répartition). La
répartition observée du trafic entre les bras diffère de celle qui a été
configurée, signe d'un bogue dans l'expérience. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data ; ajustement
sur covariable, ajustement par régression ; covariate adjustment,
regression adjustment). Réduit la variance d'un effet A/B à l'aide d'une
covariable mesurée avant l'expérience. `ABTest(covariate=True)`,
`AnytimeLinearModel`.

**Métrique de ratio** (ratio metric ; méthode delta, delta method). Une
métrique qui est le rapport de deux sommes par utilisateur, comme le
revenu par session. `RatioABTest`.

**Détection de ruptures** (change-point detection ; détection de
changements, détection la plus rapide, détection d'anomalies en ligne ;
change detection, quickest detection, online anomaly detection).
Déclencher une alarme peu après que la distribution d'un flux a changé.
`CUSUM`, `ShiryaevRoberts`, `MeanEDetector`, `QuantileEDetector`,
`BayesianChangePoint`. Voir
[détection de changements](change-detection.md).

**ARL** (average run length ; période opérationnelle moyenne, ARL₀,
temps moyen avant fausse alarme ; mean time to false alarm). Le nombre
espéré d'observations avant une fausse alarme lorsque rien n'a changé.
Le contrôle des fausses alarmes des détecteurs de changements.

**E-détecteur** (e-detector). Un détecteur de changements construit à
partir d'e-processus, un démarré à chaque instant de changement
possible. Son ARL est garantie sous une hypothèse nulle non
paramétrique. `MeanEDetector`, `QuantileEDetector`.

**Problème de Kiefer–Weiss** (Kiefer–Weiss problem). Trouver le test
séquentiel à taille d'échantillon maximale qui minimise la plus grande
espérance de la taille d'échantillon. `kiefer_weiss_plan`.

**Caractéristique opérationnelle** (operating characteristic). Les
probabilités d'erreur et la distribution de la taille d'échantillon
d'un plan, en fonction de la vraie valeur du paramètre.
`operating_characteristic`.

**Point de reprise** (checkpoint). Une valeur JSON à partir de laquelle
une exécution reprend exactement. `Run.checkpoint`, `Run.restore`. Voir
[flux](streaming.md).

**Empreinte de l'historique** (history digest). Une chaîne de hachage
SHA-256 sur les observations qu'une exécution a utilisées, conservée
dans chaque point de reprise, à des fins d'audit.

**Garantie** (guarantee ; `exact`, `asymptotic`, `model`, `approximate`,
`none`). L'attribut dans lequel chaque procédure de cette bibliothèque
énonce ce qu'elle promet. Voir [Quelle méthode ?](../../choosing.md).
