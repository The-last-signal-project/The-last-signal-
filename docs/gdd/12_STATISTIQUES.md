[🏠 Documentation](../README.md) > [🎮 GDD](README.md)

# 📊 Statistiques

> **Document :** Statistiques
> **Code :** GDD-012
> **Version :** 1.1.0
> **Statut :** 🟡 En cours de définition

---

## 📑 Table des matières

1. [Présentation](#1--présentation)
2. [Objectifs](#2--objectifs)
3. [Principes](#3--principes)
4. [Catégories de statistiques](#4--catégories-de-statistiques)
5. [Caractéristiques principales](#5--caractéristiques-principales)
6. [Modificateurs](#6--modificateurs)
7. [Points de vie](#7--points-de-vie)
8. [Défense](#8--défense)
9. [Mana](#9--mana)
10. [Progression](#10--progression)
11. [Bouff](#11--bouff)
12. [Vitesse](#12--vitesse)
13. [Grade](#13--grade)
14. [Génération des statistiques](#14--génération-des-statistiques)
15. [Influence de l'équipement](#15--influence-de-léquipement)
16. [Influence des compétences](#16--influence-des-compétences)
17. [Influence des états](#17--influence-des-états)
18. [Tableau des statistiques](#18--tableau-des-statistiques)
19. [Documents liés](#19--documents-liés)

---

## 1. 📖 Présentation

Les statistiques représentent les caractéristiques numériques utilisées pour décrire l'état et les capacités d'un personnage dans **The Last Signal**.

Le modèle actuel du personnage utilise six caractéristiques principales :

* **FOR** — Force
* **DEX** — Dextérité
* **CON** — Constitution
* **INT** — Intelligence
* **SAG** — Sagesse
* **CHA** — Charisme

À ces caractéristiques s'ajoutent plusieurs statistiques dérivées ou de progression :

* **MOD_*** — modificateurs des caractéristiques ;
* **PV** — points de vie actuels ;
* **PV_MAX** — points de vie maximum ;
* **DEF** — défense ;
* **MANA** — mana actuelle ;
* **MANA_max** — mana maximale ;
* **XP** — expérience ;
* **niv** — niveau ;
* **bouff** — valeur actuelle de bouff ;
* **bouff_max** — valeur maximale de bouff ;
* **vitesse** — vitesse de déplacement ;
* **grade** — grade utilisé lorsque le mode armée est activé.

---

## 2. 🎯 Objectifs

Le système de statistiques doit permettre de :

* représenter les caractéristiques du personnage ;
* différencier les personnages ;
* fournir des valeurs utilisables par les systèmes de jeu ;
* permettre une progression cohérente ;
* calculer les statistiques dérivées ;
* gérer les effets des compétences ;
* gérer les effets de l'équipement ;
* représenter l'état actuel du personnage.

---

## 3. 🧭 Principes

### Cohérence

Chaque statistique doit avoir une fonction clairement définie.

### Utilité

Les statistiques doivent être utilisées par les systèmes de gameplay auxquels elles correspondent.

### Interactions

Les statistiques peuvent être utilisées par plusieurs systèmes du jeu.

### Équilibrage

Les valeurs et formules doivent être équilibrées afin d'éviter qu'une seule caractéristique rende les autres inutiles.

### Lisibilité

Les statistiques importantes doivent être compréhensibles par le joueur.

---

## 4. 🧩 Catégories de statistiques

Les statistiques actuelles peuvent être réparties en plusieurs catégories.

### Caractéristiques principales

* FOR
* DEX
* CON
* INT
* SAG
* CHA

### Modificateurs

* MOD_FOR
* MOD_DEX
* MOD_CON
* MOD_INT
* MOD_SAG
* MOD_CHA

### Combat et état physique

* PV
* PV_MAX
* DEF
* MANA
* MANA_max
* bouff
* bouff_max

### Progression

* XP
* niv

### Déplacement

* vitesse

### Statut particulier

* grade

---

## 5. 💪 Caractéristiques principales

Les six caractéristiques principales sont définies dans `PersoCore` :

```python
STATS = ["FOR", "DEX", "CON", "INT", "SAG", "CHA"]
```

### FOR — Force

Représente la force physique du personnage.

**ID :** `STAT-001`

**Valeur :** générée lors de la création du personnage.

### DEX — Dextérité

Représente l'agilité et la précision du personnage.

**ID :** `STAT-002`

**Valeur :** générée lors de la création du personnage.

### CON — Constitution

Représente la constitution physique du personnage.

**ID :** `STAT-003`

La Constitution intervient actuellement dans le calcul des points de vie maximum :

```text
PV_MAX = (CON // 2) + 12
```

### INT — Intelligence

Représente l'intelligence du personnage.

**ID :** `STAT-004`

**Valeur :** générée lors de la création du personnage.

### SAG — Sagesse

Représente la sagesse du personnage.

**ID :** `STAT-005`

**Valeur :** générée lors de la création du personnage.

### CHA — Charisme

Représente le charisme du personnage.

**ID :** `STAT-006`

**Valeur :** générée lors de la création du personnage.

---

## 6. 📈 Modificateurs

Chaque caractéristique principale possède un modificateur associé.

Les statistiques sont donc accompagnées de :

* `MOD_FOR`
* `MOD_DEX`
* `MOD_CON`
* `MOD_INT`
* `MOD_SAG`
* `MOD_CHA`

Le modificateur est calculé à partir de la valeur de la caractéristique.

La formule actuellement utilisée par `PersoCore` est basée sur la valeur de la statistique et sur la table suivante :

| Plage de valeurs | Modificateur |
| ---------------: | -----------: |
|              1–2 |           -4 |
|              3–4 |           -3 |
|              5–6 |           -2 |
|              7–8 |           -1 |
|             9–10 |            0 |
|            11–12 |           +1 |
|            13–14 |           +2 |
|            15–16 |           +3 |
|            17–18 |           +4 |

La fonction utilisée actuellement est :

```python
def get_modifier(value):
    modifiers = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
    index = (value - 1) // 2
    return modifiers[index] if 0 <= index < len(modifiers) else 0
```

Les valeurs situées en dehors de la plage couverte par cette table retournent actuellement un modificateur de `0`.

---

## 7. ❤️ Points de vie

Le personnage possède deux statistiques liées aux points de vie :

* `PV_MAX` — points de vie maximum ;
* `PV` — points de vie actuels.

La valeur maximale est actuellement calculée à partir de la Constitution :

```text
PV_MAX = (CON // 2) + 12
```

Lors de la génération initiale des statistiques :

```text
PV = PV_MAX
```

Le personnage commence donc avec ses points de vie maximum.

---

## 8. 🛡️ Défense

La défense est représentée par :

`DEF`

La valeur initiale de défense est actuellement calculée à partir du modificateur de Dextérité :

```text
DEF = 10 + MOD_DEX
```

La Dextérité influence donc directement la défense de base du personnage.

Les éventuels bonus supplémentaires provenant de l'équipement, des compétences ou d'autres systèmes restent à définir dans les documents correspondants.

---

## 9. 🔵 Mana

Le personnage possède deux statistiques liées au mana :

* `MANA_max` — mana maximum ;
* `MANA` — mana actuelle.

La valeur actuellement définie dans le code est :

```text
MANA_max = 100
```

Au moment de l'initialisation :

```text
MANA = MANA_max
```

Le personnage commence donc avec **100 points de mana**.

La formule d'évolution de `MANA_max` n'est actuellement pas définie dans l'extrait de code fourni.

---

## 10. 📊 Progression

Le personnage possède deux statistiques liées à sa progression :

### XP

`XP` représente l'expérience accumulée par le personnage.

La valeur initiale est :

```text
XP = 0
```

### Niveau

`niv` représente le niveau actuel du personnage.

La valeur initiale est :

```text
niv = 1
```

La formule permettant de convertir l'XP en niveau n'est pas définie dans l'extrait actuel.

Elle devra être définie dans **11_PROGRESSION.md**.

---

## 11. 🟢 Bouff

Le personnage possède deux valeurs liées à la statistique `bouff` :

* `bouff` — valeur actuelle ;
* `bouff_max` — valeur maximale.

La valeur maximale est actuellement calculée à partir du niveau :

```text
bouff_max = niv × 10
```

La valeur actuelle est ensuite initialisée à sa valeur maximale :

```text
bouff = bouff_max
```

Avec un personnage de niveau 1 :

```text
bouff_max = 10
bouff = 10
```

La signification gameplay exacte de `bouff` devra être précisée dans le système concerné.

---

## 12. 🏃 Vitesse

La vitesse du personnage est actuellement définie par :

```text
vitesse = 0.4
```

Cette valeur est actuellement utilisée comme valeur de vitesse du personnage.

La relation entre cette valeur et :

* la vitesse réelle du déplacement ;
* les statistiques ;
* l'équipement ;
* les compétences ;
* les effets temporaires ;

reste à définir.

---

## 13. 🎖️ Grade

Le personnage possède également une propriété :

```python
self.grade = grade
```

D'après le code fourni, le grade est lié à l'activation du **mode armée**.

La fonction exacte du grade, ses valeurs possibles et ses effets sur les statistiques ne sont pas définis dans l'extrait fourni.

Ces éléments devront donc être spécifiés dans la documentation du système militaire correspondant.

---

## 14. 🎲 Génération des statistiques

Les six statistiques principales sont générées lors de la création du personnage.

Le code actuel utilise :

```python
valeurs = [
    sum(sorted([de.jet_de_des(6, 4)], reverse=True)[:3]) for _ in range(6)
]
```

Les six valeurs obtenues sont ensuite associées aux six statistiques :

```text
FOR
DEX
CON
INT
SAG
CHA
```

Les modificateurs sont ensuite générés pour chacune d'elles.

Enfin, les statistiques dérivées suivantes sont initialisées :

```text
PV_MAX = (CON // 2) + 12
PV = PV_MAX
DEF = 10 + MOD_DEX
```

Les statistiques de progression et de ressources sont ensuite initialisées selon les valeurs actuellement définies :

```text
MANA_max = 100
MANA = MANA_max
XP = 0
niv = 1
bouff_max = niv × 10
bouff = bouff_max
```

> **Remarque :** la génération exacte des caractéristiques dépend de l'implémentation actuelle de `de.jet_de_des(6, 4)`. Ce document ne modifie pas cette logique.

---

## 15. 🎒 Influence de l'équipement

L'équipement pourra modifier certaines statistiques du personnage.

Les statistiques susceptibles d'être modifiées devront être définies dans les documents d'équipement et d'objets.

Les modifications pourront notamment concerner :

* les caractéristiques principales ;
* les modificateurs ;
* les PV ;
* la défense ;
* le mana ;
* la vitesse ;
* d'autres statistiques dérivées.

Les règles définitives sont à définir dans :

* **20_INVENTAIRE.md** ;
* **21_EQUIPEMENT.md** ;
* **22_OBJETS.md**.

---

## 16. 🧠 Influence des compétences

Les compétences peuvent modifier certaines statistiques du personnage.

Elles pourront notamment :

* augmenter une statistique ;
* modifier une statistique dérivée ;
* modifier temporairement une valeur ;
* améliorer une résistance ;
* modifier une capacité d'action.

Le système de compétences est défini dans **13_COMPETENCES.md**.

---

## 17. 🩹 Influence des états

Certaines statistiques peuvent être affectées par l'état du personnage.

Les effets possibles devront être définis dans les systèmes concernés.

Ils peuvent notamment être liés à :

* des blessures ;
* la fatigue ;
* l'environnement ;
* la contamination ;
* des compétences ;
* des objets ;
* des événements.

Les valeurs temporaires et permanentes devront être distinguées lorsque cela sera nécessaire.

---

## 18. 📋 Tableau des statistiques

| ID         | Nom       | Catégorie    | Type       |       Valeur actuelle |
| ---------- | --------- | ------------ | ---------- | --------------------: |
| `STAT-001` | FOR       | Principale   | Permanente |               Générée |
| `STAT-002` | DEX       | Principale   | Permanente |               Générée |
| `STAT-003` | CON       | Principale   | Permanente |               Générée |
| `STAT-004` | INT       | Principale   | Permanente |               Générée |
| `STAT-005` | SAG       | Principale   | Permanente |               Générée |
| `STAT-006` | CHA       | Principale   | Permanente |               Générée |
| `STAT-007` | MOD_FOR   | Modificateur | Calculée   |             Selon FOR |
| `STAT-008` | MOD_DEX   | Modificateur | Calculée   |             Selon DEX |
| `STAT-009` | MOD_CON   | Modificateur | Calculée   |             Selon CON |
| `STAT-010` | MOD_INT   | Modificateur | Calculée   |             Selon INT |
| `STAT-011` | MOD_SAG   | Modificateur | Calculée   |             Selon SAG |
| `STAT-012` | MOD_CHA   | Modificateur | Calculée   |             Selon CHA |
| `STAT-013` | PV_MAX    | Combat       | Calculée   |     `(CON // 2) + 12` |
| `STAT-014` | PV        | Combat       | Variable   |    `PV_MAX` au départ |
| `STAT-015` | DEF       | Combat       | Calculée   |        `10 + MOD_DEX` |
| `STAT-016` | MANA_max  | Ressource    | Variable   |                 `100` |
| `STAT-017` | MANA      | Ressource    | Variable   |  `MANA_max` au départ |
| `STAT-018` | XP        | Progression  | Variable   |                   `0` |
| `STAT-019` | niv       | Progression  | Variable   |                   `1` |
| `STAT-020` | bouff_max | Ressource    | Calculée   |            `niv × 10` |
| `STAT-021` | bouff     | Ressource    | Variable   | `bouff_max` au départ |
| `STAT-022` | vitesse   | Déplacement  | Variable   |                 `0.4` |
| `STAT-023` | grade     | Statut       | Variable   |   Selon le mode armée |

---

## 19. 📚 Documents liés

### GDD

* [`01_VISION.md`](01_VISION.md)
* [`09_PERSONNAGES.md`](09_PERSONNAGES.md)
* [`10_CREATION_PERSONNAGE.md`](10_CREATION_PERSONNAGE.md)
* [`11_PROGRESSION.md`](11_PROGRESSION.md)
* [`13_COMPETENCES.md`](13_COMPETENCES.md)
* [`14_CLASSES.md`](14_CLASSES.md)
* [`15_GAMEPLAY.md`](15_GAMEPLAY.md)
* [`16_COMBAT.md`](16_COMBAT.md)
* [`18_MONSTRES.md`](18_MONSTRES.md)
* [`19_BOSS.md`](19_BOSS.md)
* [`20_INVENTAIRE.md`](20_INVENTAIRE.md)
* [`21_EQUIPEMENT.md`](21_EQUIPEMENT.md)
* [`22_OBJETS.md`](22_OBJETS.md)
* [`29_METIERS.md`](29_METIERS.md)
* [`30_CRAFT.md`](30_CRAFT.md)
* [`31_RECOLTE.md`](31_RECOLTE.md)
* [`33_BIOMES.md`](33_BIOMES.md)
* [`34_METEO.md`](34_METEO.md)
* [`35_JOUR_NUIT.md`](35_JOUR_NUIT.md)

### Documentation générale

* [`../README.md`](../README.md)
* [`../ROADMAP.md`](../ROADMAP.md)
* [`../ARCHITECTURE.md`](../ARCHITECTURE.md)

---

## 📌 État du document

**Version :** 1.1.0
**Statut :** 🟡 En cours de définition

Ce document intègre désormais les statistiques effectivement présentes dans le modèle actuel `PersoCore`.

## Les formules et valeurs qui ne sont pas présentes dans le code fourni restent à définir.

## Navigation

⬅️ [Progression](11_PROGRESSION.md)

➡️ [Compétences](13_COMPETENCES.md)
