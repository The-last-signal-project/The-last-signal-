[🏠 Documentation](../README.md) > [🎮 GDD](README.md)

# 🧬 Création du personnage

> **Document :** Création du personnage
> **Code :** GDD-010
> **Version :** 1.0.0
> **Statut :** 🟡 En cours de définition

---

## 📑 Table des matières

1. [Présentation](#1--présentation)
2. [Objectifs](#2--objectifs)
3. [Étapes de création](#3--étapes-de-création)
4. [Identité](#4--identité)
5. [Apparence](#5--apparence)
6. [Origine](#6--origine)
7. [Spécialisation initiale](#7--spécialisation-initiale)
8. [Nom du personnage](#8--nom-du-personnage)
9. [Validation](#9--validation)
10. [Création technique](#10--création-technique)
11. [Restrictions](#11--restrictions)
12. [Évolution après la création](#12--évolution-après-la-création)
13. [Liste des paramètres](#13--liste-des-paramètres)
14. [Documents liés](#14--documents-liés)

---

# 1. 📖 Présentation

La création du personnage permet au joueur de définir son personnage avant d'entrer dans le monde de **The Last Signal**.

Elle constitue la première étape de l'expérience du joueur et doit permettre de créer une identité personnalisée tout en respectant les règles et contraintes du jeu.

La création du personnage doit rester cohérente avec l'univers post-apocalyptique du projet.

---

## 2. 🎯 Objectifs

Le système de création doit permettre de :

* créer un personnage unique ;
* définir son identité ;
* personnaliser son apparence ;
* définir les informations nécessaires à son enregistrement ;
* préparer les données nécessaires au serveur ;
* éviter les configurations invalides ;
* garantir la compatibilité avec les systèmes de progression du jeu.

La création ne doit pas donner au joueur un avantage définitif impossible à modifier ou à compenser par la progression normale.

---

## 3. 🛠️ Étapes de création

La création du personnage est organisée en plusieurs étapes.

### Étape 1 — Identité

Le joueur définit les informations principales de son personnage.

### Étape 2 — Apparence

Le joueur personnalise l'apparence de son personnage selon les options disponibles.

### Étape 3 — Origine

Le joueur sélectionne les éventuelles informations d'origine prévues par le jeu.

### Étape 4 — Spécialisation initiale

Si le système le prévoit, le joueur peut effectuer certains choix initiaux.

Ces choix ne doivent pas remplacer les systèmes complets de progression, de compétences et de classes.

### Étape 5 — Vérification

Le jeu vérifie que toutes les informations respectent les règles de création.

### Étape 6 — Confirmation

Le joueur confirme définitivement la création.

Le personnage peut alors être enregistré et devenir disponible dans le monde du jeu.

---

## 4. 🪪 Identité

L'identité du personnage regroupe les informations permettant de le distinguer.

Les données peuvent notamment comprendre :

| Paramètre        | Description                      |
| ---------------- | -------------------------------- |
| Identifiant      | Identifiant unique du personnage |
| Nom              | Nom affiché du personnage        |
| Prénom           | Prénom si utilisé                |
| Genre            | Paramètre éventuel du personnage |
| Origine          | Origine choisie                  |
| Date de création | Date de création du personnage   |

Les paramètres réellement utilisés seront définis par les systèmes techniques et les décisions de conception finales.

---

## 5. 🎨 Apparence

Le joueur peut personnaliser l'apparence de son personnage à partir des options disponibles.

Les paramètres peuvent comprendre :

* morphologie générale ;
* visage ;
* cheveux ;
* couleur des cheveux ;
* yeux ;
* teint ;
* vêtements de départ ;
* accessoires disponibles.

Les options disponibles doivent rester cohérentes avec la direction artistique du jeu.

La personnalisation esthétique ne doit pas modifier directement les statistiques du personnage.

---

## 6. 🌍 Origine

L'origine permet éventuellement de donner au personnage un contexte initial dans l'univers.

Elle peut être liée à :

* une région ;
* une communauté ;
* une histoire ;
* une situation avant le début de l'aventure.

L'origine ne doit pas être confondue avec une classe ou un métier.

Les effets éventuels d'une origine devront être définis séparément et documentés avant leur implémentation.

---

## 7. 🧩 Spécialisation initiale

Le système peut permettre certains choix initiaux permettant au joueur d'orienter son personnage.

Ces choix peuvent concerner :

* une orientation de gameplay ;
* certaines compétences initiales ;
* un équipement de départ ;
* des connaissances initiales.

Ils doivent rester limités afin de ne pas rendre les choix initiaux irréversibles ou excessivement déterminants.

Les systèmes complets de progression et de spécialisation sont définis dans les documents correspondants.

---

## 8. ✏️ Nom du personnage

Le nom du personnage doit respecter les règles définies par le jeu.

Le système doit vérifier :

* la longueur minimale ;
* la longueur maximale ;
* les caractères autorisés ;
* les noms déjà utilisés lorsque l'unicité est nécessaire ;
* les noms interdits ;
* les éventuelles règles spécifiques au serveur.

La validation du nom doit être effectuée côté serveur.

---

## 9. ✅ Validation

Avant la création définitive, le jeu doit vérifier l'ensemble des données.

### Vérifications

* données obligatoires présentes ;
* paramètres valides ;
* nom valide ;
* options disponibles ;
* valeurs autorisées ;
* cohérence des choix ;
* absence d'erreur technique.

Une création invalide ne doit pas être enregistrée.

Le client ne doit pas être considéré comme une source de confiance pour la validation des données.

---

## 10. 💾 Création technique

La création d'un personnage implique plusieurs systèmes.

### Client

Le client :

* affiche l'interface de création ;
* permet la personnalisation ;
* prépare les données ;
* transmet la demande au serveur.

### Serveur

Le serveur :

* reçoit la demande ;
* valide les données ;
* vérifie les règles ;
* génère ou attribue les identifiants nécessaires ;
* initialise le personnage ;
* enregistre les données.

### Base de données

La base de données conserve les informations nécessaires au personnage.

Les données sensibles liées au compte ne doivent pas être inutilement stockées dans les données publiques du personnage.

---

## 11. 🚫 Restrictions

Certaines restrictions peuvent être appliquées lors de la création.

Elles peuvent concerner :

* le nom ;
* les valeurs autorisées ;
* les options d'apparence ;
* les choix initiaux ;
* le nombre de personnages autorisés ;
* les règles propres au compte.

Les restrictions définitives seront déterminées par les règles du jeu et l'architecture du serveur.

---

## 12. 🔄 Évolution après la création

La création du personnage ne constitue que le point de départ.

Après sa création, le personnage pourra évoluer grâce aux différents systèmes du jeu.

Cette évolution pourra notamment concerner :

* son niveau ;
* ses statistiques ;
* ses compétences ;
* ses classes ;
* ses métiers ;
* son équipement ;
* ses relations ;
* sa progression dans le monde.

Ces systèmes sont documentés séparément afin d'éviter de mélanger la création et la progression.

---

## 13. 📋 Liste des paramètres

| Catégorie   | Paramètre               | Obligatoire | Modifiable après création |
| ----------- | ----------------------- | ----------: | ------------------------: |
| Identité    | Nom                     |         Oui |                 À définir |
| Identité    | Prénom                  |   À définir |                 À définir |
| Identité    | Genre                   |   À définir |                 À définir |
| Apparence   | Visage                  |   À définir |                 À définir |
| Apparence   | Cheveux                 |   À définir |                 À définir |
| Apparence   | Yeux                    |   À définir |                 À définir |
| Apparence   | Teint                   |   À définir |                 À définir |
| Apparence   | Vêtements               |   À définir |                 À définir |
| Origine     | Origine                 |   À définir |                 À définir |
| Progression | Spécialisation initiale |   À définir |                 À définir |

> Les paramètres marqués **« À définir »** ne constituent pas encore une décision de gameplay définitive.

---

## 14. 📚 Documents liés

### GDD

* [`01_VISION.md`](01_VISION.md)
* [`02_UNIVERS.md`](02_UNIVERS.md)
* [`03_SCENARIO.md`](03_SCENARIO.md)
* [`05_FACTIONS.md`](05_FACTIONS.md)
* [`06_REGIONS.md`](06_REGIONS.md)
* [`07_VILLES.md`](07_VILLES.md)
* [`09_PERSONNAGES.md`](09_PERSONNAGES.md)
* [`11_PROGRESSION.md`](11_PROGRESSION.md)
* [`12_STATISTIQUES.md`](12_STATISTIQUES.md)
* [`13_COMPETENCES.md`](13_COMPETENCES.md)
* [`14_CLASSES.md`](14_CLASSES.md)
* [`15_GAMEPLAY.md`](15_GAMEPLAY.md)
* [`20_INVENTAIRE.md`](20_INVENTAIRE.md)
* [`21_EQUIPEMENT.md`](21_EQUIPEMENT.md)
* [`29_METIERS.md`](29_METIERS.md)

### Documentation générale

* [`../README.md`](../README.md)
* [`../ROADMAP.md`](../ROADMAP.md)
* [`../ARCHITECTURE.md`](../ARCHITECTURE.md)

---

## 📌 État du document

**Version :** 1.0.0
**Statut :** 🟡 En cours de définition
**Dernière mise à jour :** 16/09/2026

Ce document définit la structure générale du système de création du personnage. Les valeurs, options et règles définitives seront précisées lors de la conception détaillée des systèmes de jeu.

## Navigation

⬅️ [Personnages](09_PERSONNAGES.md)

➡️ [Progression](11_PROGRESSION.md)


----
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />
