[🏠 Documentation](../README.md) > [🎮 GDD](README.md)
# 🧠 Compétences

**Code GDD :** GDD-013
**Version :** 1.0.0
**Statut :** En cours de développement

## Table des matières

1. [Présentation](#1-présentation)
2. [Objectifs](#2-objectifs)
3. [Principes](#3-principes)
4. [Structure de l'arbre de compétences](#4-structure-de-larbre-de-compétences)
5. [Arbre des compétences](#5-arbre-des-compétences)
6. [Déblocage des compétences](#6-déblocage-des-compétences)
7. [Niveaux des compétences](#7-niveaux-des-compétences)
8. [Compatibilité avec le gameplay](#8-compatibilité-avec-le-gameplay)
9. [Équilibrage](#9-équilibrage)
10. [Interface utilisateur](#10-interface-utilisateur)
11. [Implémentation technique](#11-implémentation-technique)
12. [Liste des compétences](#12-liste-des-compétences)
13. [Documents liés](#13-documents-liés)
14. [État du document](#14-état-du-document)

---

## 1. Présentation

Les compétences permettent au joueur de développer et de spécialiser son personnage au cours de sa progression.

L'arbre de compétences est organisé en **trois grandes branches** :

* ⚔️ **Combat & Tactique**
* ☣️ **Survie & Adaptation**
* 📡 **Infra-Tech & Signal**

Chaque compétence possède :

* un identifiant unique ;
* un nom ;
* un type ;
* un effet défini ;
* une branche et une spécialisation.

L'arbre contient actuellement **34 compétences** :

* **21 compétences actives**
* **13 compétences passives**

---

## 2. Objectifs

Le système de compétences doit permettre :

* de spécialiser les personnages ;
* de proposer plusieurs styles de jeu ;
* de favoriser la complémentarité entre les joueurs ;
* de donner une progression à long terme ;
* de permettre des rôles différents au sein d'un groupe ;
* de créer des choix dans la progression du personnage.

Les compétences doivent rester cohérentes avec l'univers de **The Last Signal**.

---

## 3. Principes

### 3.1 Spécialisation

Les trois branches correspondent à des orientations différentes.

Un joueur peut développer principalement une branche ou répartir ses compétences entre plusieurs branches.

### 3.2 Compétences actives

Les compétences actives doivent être déclenchées volontairement par le joueur.

Elles peuvent avoir :

* un temps de recharge ;
* une durée ;
* une portée ;
* une zone d'effet ;
* des conditions d'utilisation.

Les valeurs précises restent **à définir** pour chaque compétence.

### 3.3 Compétences passives

Les compétences passives produisent leurs effets automatiquement lorsqu'elles sont débloquées.

Elles peuvent modifier les caractéristiques, les résistances, l'efficacité d'objets ou certains systèmes de gameplay.

### 3.4 Identifiants

Chaque compétence possède un identifiant unique au format :

`COMP-XXX`

Exemple :

`COMP-001`

Les identifiants ne doivent pas être réutilisés pour une autre compétence.

---

## 4. Structure de l'arbre de compétences

L'arbre est divisé en trois branches principales.

### Branche 1 — Combat & Tactique

Cette branche concerne :

* les armes à feu ;
* le tir ;
* les explosifs ;
* le combat rapproché ;
* la défense.

### Branche 2 — Survie & Adaptation

Cette branche concerne :

* la condition physique ;
* la résistance ;
* le secourisme ;
* le soutien ;
* la furtivité ;
* la traque.

### Branche 3 — Infra-Tech & Signal

Cette branche concerne :

* le piratage ;
* les communications ;
* les signaux ;
* les drones ;
* les automates ;
* l'ingénierie ;
* la construction.

---

## 5. Arbre des compétences

### ⚔️ Branche 1 : Combat & Tactique

#### 🎯 Tir & Armes à Feu

* **[COMP-001] Tir de suppression** *(Actif)* : Arrose une zone ciblée pour réduire la précision et la vitesse de déplacement des ennemis touchés.
* **[COMP-002] Percée perforante** *(Actif)* : Tir de précision ignorant une portion significative de l'armure physique de la cible.
* **[COMP-003] Recharge tactique** *(Actif)* : Réduit instantanément le temps de rechargement de l'arme équipée et augmente la cadence de tir pendant 4 secondes.
* **[COMP-004] Œil de lynx** *(Passif)* : Augmente la portée maximale de tir et les chances de coup critique à longue distance.
* **[COMP-005] Maîtrise du recul** *(Passif)* : Réduit le relèvement vertical de l'arme lors des tirs continus en rafale.

#### 💣 Guérilla & Explosifs

* **[COMP-006] Mine de proximité** *(Actif)* : Pose une charge dissimulée au sol qui explose au passage d'une cible hostile.
* **[COMP-007] Grenade fumigène** *(Actif)* : Crée un nuage opaque occultant la ligne de vue et désactivant le ciblage des tourelles.
* **[COMP-008] Charge perforante** *(Actif)* : Fixe un explosif à retardement sur une structure, une porte ou un véhicule ennemi.
* **[COMP-009] Manipulation imprudente** *(Passif)* : Augmente le rayon d'impact et les dégâts de tous les explosifs artisanaux.
* **[COMP-010] Shrapnel dévastateur** *(Passif)* : Les explosions appliquent un effet de saignement prolongé aux cibles touchées.

#### 🛡️ Combat Rapproché & Défense

* **[COMP-011] Charge de bouclier** *(Actif)* : Ruée vers l'avant bousculant et étourdissant la première cible rencontrée.
* **[COMP-012] Parade réflexe** *(Actif)* : Bloque momentanément les attaques physiques frontales en réduisant les dégâts reçus.
* **[COMP-013] Cuirassé** *(Passif)* : Augmente la valeur de protection physique globale conférée par l'équipement.
* **[COMP-014] Inébranlable** *(Passif)* : Réduit la durée des effets de contrôle de foule (étourdissements, ralentissements).

### ☣️ Branche 2 : Survie & Adaptation

#### 🧬 Bio-Résistance & Condition Physique

* **[COMP-015] Second souffle** *(Actif)* : Régénère instantanément de l'endurance et stoppe temporairement l'accumulation de fatigue.
* **[COMP-016] Injection d'adrénaline** *(Actif)* : Augmente considérablement la vitesse de déplacement et confère une immunité aux ralentissements pendant 6 secondes.
* **[COMP-017] Métabolisme altéré** *(Passif)* : Augmente la tolérance aux radiations et ralentit la progression de la jauge d'infection toxique.
* **[COMP-018] Estomac de fer** *(Passif)* : Immunise contre les empoisonnements et maladies liés à la consommation d'eau ou de nourriture contaminée.

#### 🚑 Secourisme & Soutien

* **[COMP-019] Kit de suture rapide** *(Actif)* : Stoppe immédiatement les saignements graves et restaure progressivement la santé d'un allié ou de soi-même.
* **[COMP-020] Défibrillateur portatif** *(Actif)* : Réanime un coéquipier tombé au combat avec un pourcentage de santé de base.
* **[COMP-021] Brume stérile** *(Actif)* : Diffuse un nuage curatif soignant continuellement tous les membres du groupe dans la zone.
* **[COMP-022] Transfusion optimisée** *(Passif)* : Augmente de 25 % l'efficacité de tous les consommables médicaux utilisés.

#### 🎒 Furtivité & Traqueur

* **[COMP-023] Camouflage d'ombre** *(Actif)* : Réduit drastiquement le rayon de détection par les monstres et les joueurs hostiles durant un temps limité.
* **[COMP-024] Marquage de proie** *(Actif)* : Révèle la position et la barre de santé d'une cible à travers les obstacles pour toute l'équipe.
* **[COMP-025] Pas feutrés** *(Passif)* : Réduit le bruit généré par le personnage lors des déplacements en course ou en marche.

### 📡 Branche 3 : Infra-Tech & Signal

#### 💻 Piratage & Signaux Radio

* **[COMP-026] Onde IEM** *(Actif)* : Émet une impulsion électromagnétique courte portée désactivant les tourelles automatiques et affaiblissant les boucliers énergétiques.
* **[COMP-027] Interception radio** *(Actif)* : Détecte les communications ou la présence de joueurs hostiles dans un rayon défini autour de l'utilisateur.
* **[COMP-028] Piratage à distance** *(Actif)* : Permet d'interagir à distance avec des portes électroniques, caméras ou terminaux.
* **[COMP-029] Cryptanalyse** *(Passif)* : Simplifie et accélère les séquences de piratage des coffres verrouillés et infrastructures.

#### 🤖 Drones & Automates

* **[COMP-030] Drone recon** *(Actif)* : Déploie un petit drone volant effectuant une reconnaissance de la zone et marquant les menaces sur la carte.
* **[COMP-031] Tourelle portative** *(Actif)* : Place un module de défense automatique tirant sur toute cible hostile à portée.
* **[COMP-032] Accumulateur haute capacité** *(Passif)* : Augmente la durée d'activité et la portée maximale d'opération de tous les drones.

#### 🛠️ Ingénierie & Bâtisseur

* **[COMP-033] Reparatron** *(Actif)* : Restaure la durabilité des fortifications, portes ou véhicules alliés à proximité.
* **[COMP-034] Recyclage efficace** *(Passif)* : Confère des chances d'obtenir des composants de fabrication rares supplémentaires lors du démontage d'objets.

---

## 6. Déblocage des compétences

Le système de déblocage doit permettre au joueur de construire progressivement son arbre de compétences.

Les éléments suivants seront définis lors de la conception détaillée :

* niveau nécessaire ;
* prérequis ;
* nombre de points nécessaires ;
* éventuelles compétences précédentes ;
* restrictions liées à la classe ;
* restrictions liées au matériel ;
* éventuelles conditions particulières.

---

## 7. Niveaux des compétences

Le fonctionnement exact des niveaux de compétences reste à définir.

Une compétence pourra éventuellement :

* posséder plusieurs niveaux ;
* améliorer progressivement son effet ;
* réduire son temps de recharge ;
* augmenter sa durée ;
* augmenter sa portée ;
* améliorer son efficacité.

Les valeurs définitives devront être équilibrées lors des tests de gameplay.

---

## 8. Compatibilité avec le gameplay

Les compétences doivent pouvoir interagir avec les principaux systèmes du jeu :

* combat ;
* survie ;
* exploration ;
* PvE ;
* PvP ;
* équipement ;
* inventaire ;
* métiers ;
* crafting ;
* groupes ;
* guildes ;
* économie ;
* monde persistant ;
* infrastructures ;
* véhicules ;
* drones et automates.

---

## 9. Équilibrage

L'équilibrage des compétences devra prendre en compte :

* la puissance ;
* la fréquence d'utilisation ;
* le temps de recharge ;
* la durée ;
* la portée ;
* le coût éventuel ;
* les conditions d'utilisation ;
* la progression du personnage ;
* les interactions avec les autres compétences ;
* les différences entre PvE et PvP.

---

## 10. Interface utilisateur

L'arbre de compétences devra permettre au joueur de :

* consulter les trois branches ;
* voir les compétences disponibles ;
* identifier les compétences débloquées ;
* identifier les compétences verrouillées ;
* consulter les prérequis ;
* consulter les effets ;
* voir le type de compétence ;
* suivre sa progression ;
* identifier les compétences actives et passives.

---

## 11. Implémentation technique

Les compétences devront être identifiables de manière unique grâce à leur ID `COMP-XXX`.

Le serveur devra rester l'autorité pour les éléments importants liés aux compétences, notamment :

* validation du déblocage ;
* validation de l'utilisation ;
* application des effets ;
* temps de recharge ;
* restrictions ;
* progression.

Le client devra principalement gérer :

* l'affichage ;
* les interactions avec l'interface ;
* les effets visuels ;
* les informations présentées au joueur.

---

## 12. Liste des compétences

| ID       | Compétence                  | Type   | Branche             |
| -------- | --------------------------- | ------ | ------------------- |
| COMP-001 | Tir de suppression          | Actif  | Combat & Tactique   |
| COMP-002 | Percée perforante           | Actif  | Combat & Tactique   |
| COMP-003 | Recharge tactique           | Actif  | Combat & Tactique   |
| COMP-004 | Œil de lynx                 | Passif | Combat & Tactique   |
| COMP-005 | Maîtrise du recul           | Passif | Combat & Tactique   |
| COMP-006 | Mine de proximité           | Actif  | Combat & Tactique   |
| COMP-007 | Grenade fumigène            | Actif  | Combat & Tactique   |
| COMP-008 | Charge perforante           | Actif  | Combat & Tactique   |
| COMP-009 | Manipulation imprudente     | Passif | Combat & Tactique   |
| COMP-010 | Shrapnel dévastateur        | Passif | Combat & Tactique   |
| COMP-011 | Charge de bouclier          | Actif  | Combat & Tactique   |
| COMP-012 | Parade réflexe              | Actif  | Combat & Tactique   |
| COMP-013 | Cuirassé                    | Passif | Combat & Tactique   |
| COMP-014 | Inébranlable                | Passif | Combat & Tactique   |
| COMP-015 | Second souffle              | Actif  | Survie & Adaptation |
| COMP-016 | Injection d'adrénaline      | Actif  | Survie & Adaptation |
| COMP-017 | Métabolisme altéré          | Passif | Survie & Adaptation |
| COMP-018 | Estomac de fer              | Passif | Survie & Adaptation |
| COMP-019 | Kit de suture rapide        | Actif  | Survie & Adaptation |
| COMP-020 | Défibrillateur portatif     | Actif  | Survie & Adaptation |
| COMP-021 | Brume stérile               | Actif  | Survie & Adaptation |
| COMP-022 | Transfusion optimisée       | Passif | Survie & Adaptation |
| COMP-023 | Camouflage d'ombre          | Actif  | Survie & Adaptation |
| COMP-024 | Marquage de proie           | Actif  | Survie & Adaptation |
| COMP-025 | Pas feutrés                 | Passif | Survie & Adaptation |
| COMP-026 | Onde IEM                    | Actif  | Infra-Tech & Signal |
| COMP-027 | Interception radio          | Actif  | Infra-Tech & Signal |
| COMP-028 | Piratage à distance         | Actif  | Infra-Tech & Signal |
| COMP-029 | Cryptanalyse                | Passif | Infra-Tech & Signal |
| COMP-030 | Drone recon                 | Actif  | Infra-Tech & Signal |
| COMP-031 | Tourelle portative          | Actif  | Infra-Tech & Signal |
| COMP-032 | Accumulateur haute capacité | Passif | Infra-Tech & Signal |
| COMP-033 | Reparatron                  | Actif  | Infra-Tech & Signal |
| COMP-034 | Recyclage efficace          | Passif | Infra-Tech & Signal |

---

## 13. Documents liés

* [`01_VISION.md`](01_VISION.md)
* [`10_CREATION_PERSONNAGE.md`](10_CREATION_PERSONNAGE.md)
* [`11_PROGRESSION.md`](11_PROGRESSION.md)
* [`12_STATISTIQUES.md`](12_STATISTIQUES.md)
* [`14_CLASSES.md`](14_CLASSES.md)
* [`15_GAMEPLAY.md`](15_GAMEPLAY.md)
* [`16_COMBAT.md`](16_COMBAT.md)
* [`17_IA.md`](17_IA.md)
* [`20_INVENTAIRE.md`](20_INVENTAIRE.md)
* [`21_EQUIPEMENT.md`](21_EQUIPEMENT.md)
* [`29_METIERS.md`](29_METIERS.md)
* [`30_CRAFT.md`](30_CRAFT.md)
* [`36_GUILDES.md`](36_GUILDES.md)
* [`37_GROUPES.md`](37_GROUPES.md)
* [`39_PVE.md`](39_PVE.md)
* [`40_PVP.md`](40_PVP.md)
* [`44_HUD.md`](44_HUD.md)
* [`45_MENUS.md`](45_MENUS.md)

---

## 14. État du document

**Version actuelle :** 1.0.0

Les **34 compétences** constituent la base actuelle de l'arbre de compétences.

Les éléments détaillés restant à définir sont notamment :

* les prérequis ;
* les niveaux ;
* le coût en points ;
* les dépendances ;
* les temps de recharge définitifs ;
* les valeurs numériques ;
* les interactions détaillées ;
* l'équilibrage PvE/PvP ;
* l'interface finale.

---
## Navigation

⬅️ [Statistiques](12_STATISTIQUES.md)

➡️ [Classes](14_CLASSES.md)


----
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />
