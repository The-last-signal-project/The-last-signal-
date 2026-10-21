[🏠 Documentation](../README.md) > [🎮 GDD](README.md)
# 🏙️ Villes

> **Document :** Villes
> **Code :** GDD-007
> **Version :** 1.0.0
> **Statut :** 🟡 En cours de rédaction

---

## 📖 Table des matières

1. [Présentation](#1--présentation)
2. [Rôle des villes](#2--rôle-des-villes)
3. [Types de villes et implantations](#3--types-de-villes-et-implantations)
4. [Structure d'une ville](#4--structure-dune-ville)
5. [Population](#5--population)
6. [Services](#6--services)
7. [Ressources](#7--ressources)
8. [Dangers](#8--dangers)
9. [Factions](#9--factions)
10. [Exploration](#10--exploration)
11. [Histoire et narration](#11--histoire-et-narration)
12. [État et évolution des villes](#12--état-et-évolution-des-villes)
13. [Liste des villes](#13--liste-des-villes)
14. [Fiche détaillée d'une ville](#14--fiche-détaillée-dune-ville)
15. [Documents liés](#15--documents-liés)

---

## 1. 🌍 Présentation

Les villes sont des lieux importants du monde de **The Last Signal Online**.

Elles représentent les anciennes zones de civilisation ainsi que les nouveaux lieux de regroupement des survivants.

Une ville peut être :

* habitée ;
* partiellement habitée ;
* abandonnée ;
* détruite ;
* contaminée ;
* occupée par une faction ;
* transformée en zone dangereuse.

Les villes peuvent jouer un rôle important dans l'exploration, le commerce, les quêtes et la narration.

---

## 2. 🎯 Rôle des villes

Les villes permettent notamment de :

* fournir des lieux de regroupement ;
* proposer des ressources ;
* permettre certaines interactions avec les PNJ ;
* développer les factions ;
* proposer des quêtes ;
* raconter l'histoire du monde ;
* servir de points de repère ;
* fournir des lieux d'exploration ;
* permettre au joueur de se préparer avant une expédition.

Toutes les villes ne doivent cependant pas avoir les mêmes fonctions.

Certaines peuvent être des lieux relativement sûrs tandis que d'autres peuvent être entièrement abandonnées.

---

## 3. 🏘️ Types de villes et implantations

Les implantations peuvent prendre différentes formes.

### 🏙️ Grande ville

Ancienne zone urbaine importante.

Elle peut contenir :

* de nombreux bâtiments ;
* des infrastructures ;
* plusieurs quartiers ;
* des ressources variées ;
* des zones contaminées ;
* des installations importantes.

---

### 🏘️ Petite ville

Implantation plus réduite comportant généralement moins de bâtiments et de services.

Elle peut servir de point intermédiaire entre plusieurs régions.

---

### 🏚️ Village

Petite implantation comprenant généralement quelques habitations et infrastructures.

Un village peut être :

* habité par des survivants ;
* abandonné ;
* détruit ;
* occupé par une faction.

---

### 🏕️ Camp de survivants

Installation créée après la catastrophe.

Les camps peuvent servir de :

* refuge ;
* point de ravitaillement ;
* lieu de commerce ;
* lieu de rassemblement ;
* point de départ pour l'exploration.

---

### 🏭 Implantation industrielle

Zone principalement composée d'usines, entrepôts ou autres infrastructures industrielles.

Ces lieux peuvent contenir des ressources et technologies utiles.

---

### 🪖 Base militaire

Ancienne installation militaire.

Elle peut contenir :

* équipements militaires ;
* archives ;
* armes ;
* véhicules ;
* installations sécurisées ;
* informations sur la catastrophe.

---

### 🧪 Installation scientifique

Centre de recherche ou laboratoire.

Ces lieux peuvent être particulièrement importants pour comprendre l'origine de la catastrophe.

---

## 4. 🧩 Structure d'une ville

Chaque ville doit posséder au minimum :

| Élément          | Description                         |
| ---------------- | ----------------------------------- |
| Identifiant      | Identifiant unique                  |
| Nom              | Nom officiel                        |
| Région           | Région dans laquelle elle se trouve |
| Type             | Type d'implantation                 |
| État             | État actuel de la ville             |
| Contamination    | Niveau de contamination             |
| Population       | Population actuelle                 |
| Faction          | Faction dominante, si applicable    |
| Services         | Services disponibles                |
| Ressources       | Ressources présentes                |
| Dangers          | Principaux dangers                  |
| Histoire         | Histoire de la ville                |
| Lieux importants | Lieux remarquables                  |

---

## 5. 👥 Population

La population d'une ville dépend de son état et de son histoire.

Une ville peut contenir :

* des survivants ;
* des PNJ ;
* des marchands ;
* des membres de factions ;
* des groupes hostiles ;
* des créatures.

Certaines villes peuvent être totalement inhabitées.

La population peut également évoluer au cours du temps.

---

## 6. 🛠️ Services

Certaines villes peuvent proposer différents services.

Exemples :

* commerce ;
* réparation ;
* artisanat ;
* stockage ;
* soins ;
* informations ;
* missions ;
* hébergement ;
* amélioration d'équipement.

La disponibilité des services dépend de l'état de la ville.

Une ville détruite ne peut évidemment pas proposer les mêmes services qu'un camp de survivants fonctionnel.

---

## 7. ⛏️ Ressources

Les villes peuvent contenir différentes ressources.

Exemples :

* nourriture ;
* médicaments ;
* matériaux ;
* métaux ;
* composants électroniques ;
* carburant ;
* objets techniques.

Les ressources disponibles dépendent notamment :

* du type de ville ;
* de son état ;
* de sa région ;
* de son niveau de contamination ;
* des événements qui s'y sont produits.

---

## 8. ⚠️ Dangers

Les villes peuvent présenter différents dangers.

Ils peuvent provenir :

* de la contamination ;
* des créatures ;
* de bâtiments instables ;
* d'anomalies ;
* de factions hostiles ;
* de pièges ;
* d'événements.

Une ville abandonnée n'est donc pas nécessairement une ville sûre.

---

## 9. ⚔️ Factions

Certaines villes peuvent être contrôlées ou influencées par une faction.

Une faction peut :

* contrôler la ville ;
* protéger la ville ;
* exploiter ses ressources ;
* commercer avec les joueurs ;
* imposer certaines règles ;
* être hostile aux joueurs.

Le contrôle d'une ville peut éventuellement évoluer au cours du jeu.

Les détails des factions sont définis dans `05_FACTIONS.md`.

---

## 10. 🧭 Exploration

Les villes doivent encourager l'exploration.

Le joueur peut y découvrir :

* des bâtiments ;
* des ressources ;
* des documents ;
* des survivants ;
* des objets ;
* des passages cachés ;
* des installations ;
* des secrets ;
* des événements.

Les bâtiments importants peuvent posséder leur propre contenu.

---

## 11. 📜 Histoire et narration

Les villes constituent des éléments importants de la narration environnementale.

Le joueur peut comprendre leur histoire grâce à :

* l'état des bâtiments ;
* les objets abandonnés ;
* les documents ;
* les survivants ;
* les installations ;
* les traces de combat ;
* les messages ;
* les événements ;
* les signaux radio.

Une ville peut ainsi raconter une partie de l'histoire du monde sans nécessiter une narration directe.

---

## 12. 🔄 État et évolution des villes

Les villes peuvent évoluer au cours du temps.

Une ville peut notamment :

* être reconstruite ;
* être abandonnée ;
* perdre sa population ;
* accueillir de nouveaux survivants ;
* changer de faction ;
* être contaminée ;
* être affectée par un événement ;
* devenir plus sûre ;
* devenir plus dangereuse.

Les changements doivent rester cohérents avec la chronologie et les événements du monde.

---

## 13. 🗺️ Liste des villes

La liste définitive des villes sera établie progressivement.

| ID       | Nom       | Région    | Type      | État      | Statut |
| -------- | --------- | --------- | --------- | --------- | ------ |
| CITY-001 | À définir | À définir | À définir | À définir | 🟡     |
| CITY-002 | À définir | À définir | À définir | À définir | 🟡     |
| CITY-003 | À définir | À définir | À définir | À définir | 🟡     |
| CITY-004 | À définir | À définir | À définir | À définir | 🟡     |

> Les villes définitives devront être validées avec la carte, les régions, le scénario et la chronologie.

---

## 14. 📋 Fiche détaillée d'une ville

Chaque ville définitive devra utiliser cette structure.

### [Nom de la ville]

**ID :** CITY-XXX
**Région :** À définir
**Type :** À définir
**État :** À définir
**Contamination :** À définir

### Description

Description générale de la ville.

### Histoire

Histoire de la ville avant et après la catastrophe.

### Population

Description de la population actuelle.

### Faction

Faction présente ou dominante.

### Services

Services disponibles.

### Ressources

Ressources disponibles.

### Dangers

Principaux dangers.

### Lieux importants

Liste des principaux lieux de la ville.

### Secrets

Éléments cachés pouvant être découverts.

### Événements

Événements pouvant se produire dans la ville.

### Connexions

Régions et villes accessibles depuis cette ville.

---

## 15. 📚 Documents liés

### GDD

* [`01_VISION.md`](./01_VISION.md) — Vision générale du projet.
* [`02_UNIVERS.md`](./02_UNIVERS.md) — Univers et fonctionnement du monde.
* [`03_SCENARIO.md`](./03_SCENARIO.md) — Histoire et scénario.
* [`04_CHRONOLOGIE.md`](./04_CHRONOLOGIE.md) — Chronologie des événements.
* [`05_FACTIONS.md`](./05_FACTIONS.md) — Factions présentes dans le monde.
* [`06_REGIONS.md`](./06_REGIONS.md) — Régions du monde.
* [`07_VILLES.md`](./07_VILLES.md) — Villes et implantations.
* [`08_DONJONS.md`](./08_DONJONS.md) — Donjons et lieux dangereux.
* [`32_CARTE.md`](./32_CARTE.md) — Carte du monde.
* [`33_BIOMES.md`](./33_BIOMES.md) — Biomes.
* [`34_METEO.md`](./34_METEO.md) — Météo.
* [`35_JOUR_NUIT.md`](./35_JOUR_NUIT.md) — Cycle jour/nuit.

### Documentation générale

* [`../README.md`](../README.md) — Documentation générale.
* [`../ROADMAP.md`](../ROADMAP.md) — Feuille de route du projet.
* [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — Architecture du projet.

### Documents liés au monde

* [`../lore/`](../lore/) — Documents consacrés à l'univers et au lore.
* [`../gameplay/`](../gameplay/) — Documents consacrés aux mécaniques de gameplay.

---

## 📌 État du document

**Version :** 1.0.0
**Statut :** 🟡 En cours de rédaction

Les villes individuelles seront définies progressivement en fonction de la conception des régions et de la carte du monde.

---

## Navigation

⬅️ [Regions](06_REGIONS.md)

➡️ [Donjons](08_DONJONS.md)


----
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />
