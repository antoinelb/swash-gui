# Baie-des-Bacons

**JULIETTE KIROUAC**

PRÉSENTÉ AU MINISTÈRE DES TRANSPORTS  
DÉPARTEMENT DU PROFESSEUR JACOB STOLLE

27 mai 2025

---

## Sommaire

Ce rapport présente un protocole expérimental détaillé pour l'étude du comportement hydrodynamique d'un brise-lames végétalisé soumis à des houles irrégulières. L'objectif principal est d'évaluer la transmission de la houle, le débordement et la traînée dynamique dans différentes configurations de végétation et de conditions de houle.

L'installation expérimentale se compose d'un canal à houle de 112 mètres de long, équipé d'un générateur de houles à mouvement piston, de jauges de houle de haute précision, de caméras à haute vitesse et de vélocimètres Doppler acoustiques (VDA). Les essais sont réalisés avec un modèle réduit à l'échelle 1:2,18, en respectant les lois de similitude de Froude.

Plusieurs scénarios sont testés, variant la hauteur de houle significative, la période de pic, la profondeur d'eau, ainsi que la présence et la densité de végétation (été, hiver, sans végétation). Chaque test comprend 1000 vagues et certains seront répétés trois fois afin d'assurer la reproductibilité des résultats.

Les données recueillies permettront de quantifier l'influence de la végétation sur la dissipation de l'énergie des vagues et sur la réduction du débordement, tout en validant les modèles numériques existants.

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Problématique](#2-problématique)
3. [Objectifs](#3-objectifs)
4. [Hypothèse](#4-hypothèse)
   - 4.1 [Revue de littérature](#41-revue-de-littérature)
   - 4.2 [Simplifications](#42-simplifications)
5. [Paramètres expérimentaux](#5-paramètres-expérimentaux)
   - 5.1 [Configurations testées](#51-configurations-testées)
   - 5.2 [Répétitions](#52-répétitions)
   - 5.3 [Conditions de test et préparation préliminaire](#53-conditions-de-test-et-préparation-préliminaire)
6. [Déroulement expérimental](#6-déroulement-expérimental)
   - 6.1 [Séquence d'un test typique](#61-séquence-dun-test-typique)
7. [Analyse des résultats](#7-analyse-des-résultats)
   - 7.1 [Analyse des données](#71-analyse-des-données)
   - 7.2 [Validation statistique](#72-validation-statistique)
8. [Conclusion](#8-conclusion)

[Annexe A - Critère de Froude](#annexe-a---critère-de-froude)  
[Annexe B - Calcul de la valeur minimale de H menant au débordement](#annexe-b---calcul-de-la-valeur-minimale-de-h-menant-au-débordement)  
[Annexe C - Cauchy](#annexe-c---cauchy)  
[Annexe D - Diagramme géographique des brise-lames](#annexe-d---diagramme-géographique-des-brise-lames)  
[Annexe E - Diagramme de géométrie du canal](#annexe-e---diagramme-de-géométrie-du-canal)

---

## 1. Introduction

La baie-des-bacons située près de la route 138 présente des risques augmentant d'érosion et d'inondation, surtout dans un contexte d'élévation du niveau d'eau moyen dû au réchauffement climatique, et de fonte de glace. Une solution a été proposée par le ministère du transport en 2019, soit l'installation de 5 brise-lames vivants. Les effets de la végétation sur l'atténuation des vagues est cependant peu connu. Le ministère du transport a alors confié l'évaluation de l'efficacité de cette solution en laboratoire au Laboratoire MARÉE. Ce plan d'expérimentation présente en détails la problématique, l'objectif, la démarche scientifique et l'analyse statistique nécessaires à l'expérimentation.

## 2. Problématique

La baie des Bacons, située sur le territoire de la municipalité de Longue-Rive, est soumise à d'importants enjeux futurs liés à l'érosion côtière et au risque d'inondation. Ces phénomènes, exacerbés par la hausse du niveau marin, l'intensification des tempêtes et la réduction des glaces côtières hivernales, compromettent la stabilité des berges, les infrastructures municipales et les milieux naturels riverains. Dans le cadre d'un mandat confié par le ministère des Transports et de la Mobilité durable (MTMD), une expérimentation à modèle légèrement réduit sur la capacité d'atténuation d'un brise-lame végétatif doit être faite. Cette étude s'inscrit dans une volonté de mieux comprendre les processus physiques à l'œuvre dans la baie et d'orienter les décisions d'aménagement vers des approches durables, intégrées et fondées sur des données scientifiques.

## 3. Objectifs

Évaluer l'influence de la présence de végétation en crête d'un brise-lame, ainsi qu'évaluer la stabilité hydrostatique du brise-lame conçu selon le rapport du ministère du transport. Ces objectifs sont quantifiables selon les paramètres suivants :

- Débordement (q)
- Atténuation des vagues à travers la végétation (Kt, coefficient de traîné, frontal area, bulk resistance)
- Survie des plantes ?
- Culvert stability and planting soil protection on breakwater crest (WSP 2019).

## 4. Hypothèse

Le rosier interne et l'aulne crispé sont deux plantes relativement rigides et denses, elles ont donc un coefficient de traînée suffisamment élevé pour atténuer la transmission des vagues. Il est cependant difficile de prédire s'ils auront une utilité dans le cas de longue période de vagues. Certaines études précédentes semblent indiquer que la période n'a pas d'impact sur l'atténuation des vagues, alors que d'autres oui. Les spécialistes semblent pourtant s'entendre sur l'efficacité de la végétation dans le contexte d'atténuation des vagues :

> "This research confirmed the benefit of tidal flats hosting coastal marshes for attenuating waves, reducing overtopping volumes and lessening damage to dyke structures."
> 
> — Scott Baker, 2022

Le rapport du ministère du transport, quant à lui, prévoit 30 à 50% d'atténuation de la transmission des vagues (WSP 2020, p.60)

### 4.1 Revue de littérature

**Tableau 1 – Résumé des études sur l'atténuation des vagues par la végétation**

| Étude | Méthodologie | Résultats |
|-------|--------------|-----------|
| **Wave attenuation across an artificial salt marsh** | 1:20 length scale, 2D experiment, Spartina alterniflora, no wave absorption, 141 unique tests, 1000 waves/test | Atténuation ∝ densité de végétation, submergence (Rc/H), rigidité. ↓19% sur 1.5 m, ↓9% sur les 3.25 m suivants. Pas de lien avec la période. |
| **Wave attenuation through forests under extreme conditions** (WESENBEECK et al. 2022) | Salix alba (willow), ARC system, 500 waves/test, evanescent wave modes, orientation des feuilles, tapering, densité décroissante avec hauteur | Atténuation ↑ avec hauteur de vague, ↓ avec profondeur d'eau. Réduction du run-up. Corrélation Cd–KC. |
| **Determination of flow resistance caused by non-submerged woody vegetation** (JÄRVELÄ 2004) | Protocol limité aux scénarios non-submergés (h <= H) et aux basses vitesses (U < 1 m/s) | Comparison between leafy and non leafy scenarios using a friction factor. Theory on mechanical design of tree for characteristic dimensions used in drag formulas |
| **Laboratory study on wave attenuation by elastic mangrove model with canopy** (LU et al. 2024) | Kandelia obovata (mangrove) forests with artificial vegetation. 1:20 slope to compensate for early wave steepness. FFT for irregular waves and zero-up crossing method for regular waves. Young modulus scaled using length scale. | There is a significant wave attenuation. Les vagues avec des plus grandes périodes sont moins atténuées. Wave attenuation diminishes with increasing water level until a stabilized wave attenuation rate is achieved. Variation in plant height through the model helped increase attenuation even in the case of water level increase. BP neural network worked better than MNLR and He methods for attenuation prediction. |

### 4.2 Simplifications

- Fixed-bed
- Wave transmission through quarrystone scale effects not neglectable
- Surface tension scale effects not considered as scale factor is small
- La variation de hauteur du lit du fleuve à l'intérieur de 260 m (longueur du canal × NL) est négligeable, soit de 0,4m. Ceci se traduit en une variation d'environ 18cm dans le modèle.
- Noyau perméable

## 5. Paramètres expérimentaux

### 5.1 Configurations testées

- Sans végétation ni brise-lame (témoin)
- Avec brise-lame
- Avec végétation sans feuilles sur la crête
- Avec végétation avec feuilles sur la crête

### 5.2 Répétitions

Certains tests seront répétés 3 fois pour assurer la répétabilité des résultats. Il y a 72 tests à effectuer, ce qui équivaut à environ 100h de simulation. Il faut 30 minutes pour diminuer le niveau d'eau de 1 m. Si chaque test au même niveau d'eau est performé un à la suite de l'autre, il ne faut changer le niveau d'eau que 4 fois, en prenant compte de la présence de végétation. Donc les tests sont d'une durée minimale de 102h sans considérer les manipulations.

Seuls les scénarios menant à du débordement selon les formules empiriques et qui ne déferlent pas avant le brise-lame sont testés (voir Annexe B).

Par la suite, des conditions à plus bas niveau d'eau pourront être testées afin de déterminer le franc-bord minimal nécessaire pour des niveaux de débordement permis (PULLEN et al. 2007, p.15).

Enfin, des tests avec la pierre en amont du brise-lame pourront être faits à la fin du projet si le temps le permet.

### 5.3 Conditions de test et préparation préliminaire

#### 5.3.1 Caractéristiques de l'écoulement

- **Végétation** : (what does it influence)
- **Hauteur de vague (H)** : Valeurs à déterminer lors de la sortie de terrain (voir WSP 2019, p.78). Cette variable a un rôle majeur sur l'énergie transmise par chaque vague. Elle sera utile pour mesurer le facteur de transmission des vagues à travers la végétation.
- **Période de vague (T)** : Valeurs à déterminer lors de la sortie de terrain (voir WSP 2019, p.88). Cette valeur permet également d'évaluer l'énergie d'une vague. Elle est nécessaire, tout comme la hauteur de vague, pour calculer le nombre d'Iribarren et le débit de débordement.
- **Niveau d'eau (h)** : Valeurs à déterminer lors de la sortie de terrain (voir WSP 2020, Annexe A). Il est important de considérer l'élévation du niveau d'eau dû au réchauffement climatique.
- Un facteur d'échelle de 2,18 est choisi (voir Annexe A).
- Rugosité du lit (pour un canal, R généralement compris entre 5 et 30 µm)
- Impulsive wave ? (EurOtop p.22)
- Stresses (ex : impact hugues)

#### 5.3.2 Caractéristiques du canal à houle (Annexe E)

- Longueur : 120 m
- Largeur : 5 m
- Profondeur d'eau : ajustable jusqu'à 5 m
- Générateur de houles :
- Structure pour la réduction du réfléchissement des vagues : à l'extrémité aval du canal

#### 5.3.3 Configuration du brise-lames

- Échelle du modèle : 1:2,18 (similitude de Froude Annexe A)
- Structure : brise-lame avec végétation (rosier et aulne)
- Position : à 70 m, soit un peu plus que deux fois la longueur d'onde maximale prévue (HUGHES 1993)

#### 5.3.4 Instrumentation

- **Jauges de houle (capacitance)** : 3 en amont, 1 au sommet, 2 en aval (40 Hz)
- **Caméra haute vitesse** : vue latérale, ≥ 250 i/s, résolution ≥ 1 MP
- **VDA (ADV)** : 2 positions (avant et végétation), 50 Hz
- **EMCM** : dans la végétation
- **Marqueur** : un drapeau installé sur une branche visible par la caméra du rosier ou de l'aulne

Les instruments suivants ne seront pas utilisés pour les mesures dans le canal, mais ces outils existent et pourraient être utilisés si les données manquent de précision :
- Ultrasonic sensor for overtopping
- LSPIV
- Jauge acoustique (moyen à cause du steepness)

#### 5.3.5 Calibration

- Réinitialisation des niveaux zéro, vérification signal VDA et EMCM, mire pour caméra

## 6. Déroulement expérimental

### 6.1 Séquence d'un test typique

1. Vérifier l'installation du brise-lames et de la végétation
2. Remplir le canal à la profondeur cible
3. Vérifier la calibration des instruments
4. Configurer le générateur de houles (spectre irrégulier, Hm0, Tp, durée)
5. Démarrer les enregistrements (caméra, jauges, VDA, EMCM)
6. Lancer la génération de houles
7. À la fin des 1000 vagues, arrêter le système et sauvegarder les données
8. Changer la configuration végétale si nécessaire
9. Nettoyer les capteurs et la caméra

## 7. Analyse des résultats

L'analyse des résultats visera à quantifier les effets de la végétation sur l'atténuation de la houle et sur le débordement, ainsi qu'à évaluer la stabilité hydrostatique de la structure. Trois volets principaux sont considérés : l'analyse des vagues, l'analyse des débits de débordement, et l'évaluation des effets hydrodynamiques à travers la végétation.

### 7.1 Analyse des données

- **Damping** : la friction due aux murs et au lit du canal devra être évaluée afin de ne pas la considérer dans l'atténuation des vagues par la végétation.

- **Transmission de la houle** : le coefficient de transmission sera évalué selon la formule :
  
  $$K_t = \frac{H_t}{H_i}$$
  
  où $H_t$ est la hauteur de houle en aval du brise-lames et $H_i$ celle en amont.

- **Débit de débordement (q)** : il sera mesuré par la jauge de houle positionnée au sommet du brise-lames et par analyse vidéo. La méthode de franchissement zéro sera utilisée pour identifier les hauteurs de vagues, tandis que la formule empirique d'EurOtop (équation 3 en Annexe B) servira de comparaison.

- **Végétation** : les caméras haute vitesse permettront d'évaluer la déflexion et le comportement dynamique des plantes. Le coefficient de traînée sera estimé à partir des nombres de Reynolds et de Cauchy (voir Annexe C).

- **Données ADV** : elles seront utilisées pour obtenir les vitesses moyennes dans le couvert végétal, les profils de turbulence et les contraintes de Reynolds. Ces données serviront à valider la modélisation des forces de traînée.

- **Erreur expérimentale** : des coefficients de variation seront calculés pour les séries de tests répétés, selon les recommandations de l'EurOtop (PULLEN et al. 2007, section 1.5.1). Les écarts-types et les moyennes seront présentés pour chaque condition testée.

### 7.2 Validation statistique

Une validation expérimentale sera menée selon les étapes suivantes :

- **Normalité et homogénéité des variances** : les distributions seront testées par les tests de Shapiro-Wilk et de Levene afin de valider les conditions d'application des tests paramétriques.

- **Tests d'hypothèses** : des tests t ou ANOVA seront utilisés pour évaluer l'effet significatif de la végétation sur le coefficient de transmission ou le débit de débordement.

- **Régression et modélisation** : les résultats seront comparés aux modèles empiriques et théoriques (PULLEN et al. 2007, CLASH). Des régressions pourront être effectuées pour ajuster un modèle statistique aux données expérimentales.

- **Reproductibilité** : l'écart-type entre répétitions sera calculé pour chaque condition afin de vérifier la robustesse des mesures.

## 8. Conclusion

Ce protocole expérimental détaillé constitue une étape essentielle dans l'évaluation de l'efficacité d'un brise-lames végétalisé sous conditions de houle irrégulière. En combinant l'acquisition de données à haute fréquence à l'aide de jauges de houle, de caméras haute vitesse et de vélocimètres Doppler acoustiques, l'approche proposée permet de quantifier de manière rigoureuse la transmission de la houle, le débordement et les effets hydrodynamiques associés à la végétation.

Les résultats attendus permettront de mieux comprendre le rôle de la végétation – selon sa configuration, sa rigidité et sa densité – dans la réduction de l'énergie des vagues et la limitation des volumes d'eau dépassant la structure. Ce protocole offre également un cadre reproductible pour comparer différentes configurations et appuyer la conception de solutions basées sur la nature dans des contextes de protection côtière.

En définitive, cette démarche contribuera à valider expérimentalement des approches inspirées du génie côtier, en vue d'une intégration plus systématique dans les stratégies d'adaptation aux changements climatiques et de lutte contre l'érosion littorale.

---

## Annexe A - Critère de Froude

Pour évaluer les différents paramètres selon le critère de Froude, il faut évaluer le facteur de longueur.

$$N_L = \frac{H_{p \max}}{H_{m \max}} \quad (1)$$

Avec Hp la hauteur de vague maximale considérée du prototype et Hm la hauteur de vague maximale permise par le canal de vague. Ensuite, il est possible de calculer différents paramètres tel que le temps avec les simplifications données dans le manuel de S. Hughes (HUGHES 1993).

$$N_t = \sqrt{N_L} \quad (2)$$

## Annexe B - Calcul de la valeur minimale de H menant au débordement

L'équation 3 est évaluée numériquement pour chaque scénario donné par le ministère des transports.

$$q = 0,09\sqrt{gH_{m0}^3} \cdot e^{-\left(1,5\frac{R_c}{H_{m0}\gamma_f}\right)} \quad (3)$$

Avec H la hauteur de vague, q le débit de débordement, g la constante de gravité, Rc le franc-bord mesuré à partir de la couche filtre et γ le facteur de friction. Ainsi, il a été trouvé que tous les scénarios de hauteur de vague mènent à du débordement pour le brise-lame de 2m.

## Annexe C - Cauchy

$$Ca_s = \frac{\rho U^2 dL^3}{EI} \quad (4)$$

$$Ca_L = \frac{\rho U^2 AL^2}{EI} \quad (5)$$

## Annexe D - Diagramme géographique des brise-lames

[Diagrammes détaillés des brise-lames dans la baie - pages 10-11 du document original]

## Annexe E - Diagramme de géométrie du canal

[Diagrammes techniques du canal avec dimensions - pages 12-13 du document original]

- Canal de 112 m de long × 5 m de large
- Profondeur ajustable jusqu'à 5 m
- Brise-lame positionné à 69,75 m
- Pente d'enrochement de 29,74°

---

## Références

HUGHES, S. A. (1993). *Physical Models and Laboratory Techniques in Coastal Engineering*. World Scientific.

JÄRVELÄ, Juha (2004). « Determination of flow resistance caused by non-submerged woody vegetation ». In : *International Journal of River Basin Management* 2.1, p. 61-70.

LU, Y. et al. (2024). « Laboratory study on wave attenuation by elastic mangrove model with canopy ». In : *Journal of Marine Science and Engineering* 12.7, p. 1198. DOI : 10.3390/jmse12071198.

PULLEN, T. et al. (2007). *EurOtop : Wave overtopping of sea defences and related structures : Assessment manual*.

WESENBEECK, B. K. van et al. (2022). « Wave attenuation through forests under extreme conditions ». In : *Scientific Reports* 12, p. 1884. DOI : 10.1038/s41598-022-05753-3.

WSP (2019). *Descriptif du milieu physique – Baie des Bacon, Longue-Rive*. Rapport préparé par WSP. 249 pages. Ministère des Transports du Québec.

WSP (2020). *Analyse de solutions à l'érosion et à la submersion côtière dans la baie des Bacon dans la municipalité de Longue-Rive – Rapport d'activités des campagnes de terrain 2018*. Rapport préparé par WSP. 78 pages. Ministère des Transports du Québec.