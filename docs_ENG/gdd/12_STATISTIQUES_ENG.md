[🏠 Documentation](../README_ENG.md) > [🎮 GDD](README_ENG.md)

# 📊 Statistics & Attributes

> **Document:** Statistics & Attributes  
> **Code:** GDD-012  
> **Version:** 1.1.0  
> **Status:** 🟡 In progress  
> **Last updated:** October 2026  

---

## 📖 Table of Contents

1. [Overview](#1-overview)
2. [Objectives](#2-objectives)
3. [Design Principles](#3-design-principles)
4. [Statistical Categories](#4-statistical-categories)
5. [Primary Attributes](#5-primary-attributes)
6. [Attribute Modifiers](#6-attribute-modifiers)
7. [Health Points (HP)](#7-health-points-hp)
8. [Defense](#8-defense)
9. [Mana](#9-mana)
10. [Progression Metrics](#10-progression-metrics)
11. [Food & Sustenance (Bouff)](#11-food-sustenance-bouff)
12. [Movement Speed](#12-movement-speed)
13. [Military Rank](#13-military-rank)
14. [Character Attribute Generation](#14-character-attribute-generation)
15. [Equipment Influence](#15-equipment-influence)
16. [Skill Influence](#16-skill-influence)
17. [Status & Environmental Effects](#17-status-environmental-effects)
18. [Statistics Master Table](#18-statistics-master-table)
19. [Related Documents](#19-related-documents)

---

## 1. Overview

Statistics represent the quantitative numerical metrics used to define the physical condition, mental acuity, and operational capabilities of characters in **The Last Signal**.

The active character model implemented in `PersoCore` utilizes six primary core attributes:

* **STR (FOR)** — Strength
* **DEX** — Dexterity
* **CON** — Constitution
* **INT** — Intelligence
* **WIS (SAG)** — Wisdom
* **CHA** — Charisma

Complementing these core attributes are several derived combat, resource, and progression statistics:

* **MOD_*** — Attribute modifiers derived from primary statistics;
* **HP (PV)** — Current health points;
* **MAX_HP (PV_MAX)** — Maximum health points;
* **DEF** — Physical defense rating;
* **MANA** — Current mana resource;
* **MAX_MANA (MANA_max)** — Maximum mana capacity;
* **XP** — Accumulated experience points;
* **LVL (niv)** — Current character level;
* **BOUFF (bouff)** — Current sustenance / hunger level;
* **MAX_BOUFF (bouff_max)** — Maximum sustenance capacity;
* **SPEED (vitesse)** — Base tactical movement speed;
* **RANK (grade)** — Military rank designated when Army Mode is enabled.

---

## 2. Objectives

The statistics architecture is designed to:

* Accurately reflect character capabilities and physical attributes;
* Provide meaningful differentiation between survivor builds and classes;
* Supply validated numerical inputs to combat, crafting, and survival loops;
* Support a coherent and intuitive progression curve;
* Formulate deterministic derived combat parameters;
* Seamlessly reflect active and passive skill modifiers;
* Factor in weapon, armor, and gear bonuses;
* Dynamically mirror temporary character status, wounds, and environmental penalties.

---

## 3. Design Principles

### Coherence & Purpose
Every statistic fulfills an explicit, documented role within the game simulation.

### Gameplay Utility
Statistics directly feed into tactical actions, hazard survival, and resolution formulas.

### Inter-system Synergy
Attributes interact across multiple gameplay systems (e.g., Constitution influencing survival time and maximum HP).

### Mathematical Balance
Scaling formulas are carefully bounded to prevent single-attribute stacking from undermining diversity.

### Transparency & Readability
Core statistics and formulas must remain transparent and intuitive for players to inspect.

---

## 4. Statistical Categories

The character attributes are grouped into distinct systemic classifications:

### Primary Attributes
* `STR` (`FOR`)
* `DEX`
* `CON`
* `INT`
* `WIS` (`SAG`)
* `CHA`

### Attribute Modifiers
* `MOD_STR` (`MOD_FOR`)
* `MOD_DEX`
* `MOD_CON`
* `MOD_INT`
* `MOD_WIS` (`MOD_SAG`)
* `MOD_CHA`

### Combat & Vitality
* `HP` (`PV`)
* `MAX_HP` (`PV_MAX`)
* `DEF`
* `MANA`
* `MAX_MANA` (`MANA_max`)
* `BOUFF` (`bouff`)
* `MAX_BOUFF` (`bouff_max`)

### Progression
* `XP`
* `LVL` (`niv`)

### Locomotion
* `SPEED` (`vitesse`)

### Operational Status
* `RANK` (`grade`)

---

## 5. Primary Attributes

The six primary attributes are anchored in the `PersoCore` engine specification:

```python
STATS = ["FOR", "DEX", "CON", "INT", "SAG", "CHA"]
```

### STR (FOR) — Strength
Measures physical power, muscular force, melee striking damage, and encumbrance capacity.

* **ID:** `STAT-001`
* **Base Value:** Rolled and determined during character creation.

### DEX — Dexterity
Measures physical agility, manual dexterity, precision, evasion, and ranged projectile handling.

* **ID:** `STAT-002`
* **Base Value:** Rolled and determined during character creation.

### CON — Constitution
Measures physical endurance, health pool, disease resistance, and environmental stamina.

* **ID:** `STAT-003`
* Directly calculates Maximum Health Points:
  ```text
  PV_MAX = (CON // 2) + 12
  ```

### INT — Intelligence
Measures analytical deduction, technological literacy, terminal hacking proficiency, and scientific knowledge.

* **ID:** `STAT-004`
* **Base Value:** Rolled and determined during character creation.

### WIS (SAG) — Wisdom
Measures environmental intuition, perception, survival instincts, willpower, and mental resilience.

* **ID:** `STAT-005`
* **Base Value:** Rolled and determined during character creation.

### CHA — Charisma
Measures force of personality, leadership, barter persuasion, and diplomatic influence with wasteland factions.

* **ID:** `STAT-006`
* **Base Value:** Rolled and determined during character creation.

---

## 6. Attribute Modifiers

Each primary attribute produces an associated numerical modifier applied to relevant skill checks and combat actions:

* `MOD_FOR` (Strength Modifier)
* `MOD_DEX` (Dexterity Modifier)
* `MOD_CON` (Constitution Modifier)
* `MOD_INT` (Intelligence Modifier)
* `MOD_SAG` (Wisdom Modifier)
* `MOD_CHA` (Charisma Modifier)

The modifier mapping currently implemented in `PersoCore` is structured as follows:

| Attribute Value Range | Calculated Modifier |
| :---: | :---: |
| 1 – 2 | -4 |
| 3 – 4 | -3 |
| 5 – 6 | -2 |
| 7 – 8 | -1 |
| 9 – 10 | 0 |
| 11 – 12 | +1 |
| 13 – 14 | +2 |
| 15 – 16 | +3 |
| 17 – 18 | +4 |

The active evaluation function is:

```python
def get_modifier(value: int) -> int:
    modifiers = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
    index = (value - 1) // 2
    return modifiers[index] if 0 <= index < len(modifiers) else 0
```

*Values falling outside the standard indexed boundary default to `0` pending extended high-level scaling.*

---

## 7. Health Points (HP)

Health Points quantify a character's physical survival capacity:

* `PV_MAX` — Maximum health capacity;
* `PV` — Current active health.

Maximum health is computed directly from Constitution:

```text
PV_MAX = (CON // 2) + 12
```

Upon character generation and revival:

```text
PV = PV_MAX
```

Characters initialize with their maximum vitality fully replenished.

---

## 8. Defense

Defensive resistance is quantified through:

* `DEF` — Physical defense rating.

The base defense value is derived from the character's Dexterity modifier:

```text
DEF = 10 + MOD_DEX
```

Dexterity thus directly reinforces the survivor's natural evasive avoidance. Additional armor absorption, ballistic shielding, and cover modifiers will be integrated through the equipment system.

---

## 9. Mana

Mental and energetic capacity is tracked via mana reserves:

* `MANA_max` — Maximum mana capacity;
* `MANA` — Current mana points.

The baseline specification currently assigns:

```text
MANA_max = 100
```

Upon initialization:

```text
MANA = MANA_max
```

All newly initialized characters start with **100 mana points**. High-level mana scaling formulas tied to Intelligence/Wisdom will be calibrated in subsequent iterations.

---

## 10. Progression Metrics

Two fundamental metrics track character developmental growth:

### XP (Experience Points)
Quantifies cumulative experience earned toward the subsequent level threshold:

```text
XP = 0
```

### Level (`niv`)
Denotes the active character tier:

```text
niv = 1
```

The mathematical formula converting XP into level thresholds is governed by [`11_PROGRESSION_ENG.md`](11_PROGRESSION_ENG.md).

---

## 11. Food & Sustenance (Bouff)

The sustenance mechanic reflects the survivor's biological nutritional state:

* `bouff` — Current sustenance points;
* `bouff_max` — Maximum sustenance capacity.

Maximum sustenance scales with character level:

```text
bouff_max = niv × 10
```

Current sustenance initializes at maximum capacity:

```text
bouff = bouff_max
```

*For a starting Level 1 character: `bouff_max = 10`, `bouff = 10`.* Exhaustion effects, starvation penalties, and nutritional item consumption are governed under the survival gameplay systems.

---

## 12. Movement Speed

Tactical mobility in the world environment is initialized as:

```text
vitesse = 0.4
```

This parameter establishes base overland traversal velocity. The operational formula linking base speed to terrain friction, encumbrance load, footwear gear, and stamina sprints will be detailed in the movement specification.

---

## 13. Military Rank

Characters can hold an operational rank parameter:

```python
self.grade = grade
```

Rank is activated and managed when **Army Mode** (military hierarchy system) is active. The command structure, permissible ranks, and tactical authority bonuses will be detailed in the military subsystem specification.

---

## 14. Character Attribute Generation

During character creation, the six primary attributes are generated using standard tabletop dice simulation:

```python
valeurs = [
    sum(sorted([de.jet_de_des(6, 4)], reverse=True)[:3]) for _ in range(6)
]
```

The resulting six rolled values are assigned to:

```text
FOR (STR)
DEX (DEX)
CON (CON)
INT (INT)
SAG (WIS)
CHA (CHA)
```

Attribute modifiers are calculated immediately following roll allocation, followed by derived combat stats:

```text
PV_MAX = (CON // 2) + 12
PV = PV_MAX
DEF = 10 + MOD_DEX
```

Vital progression and sustenance parameters initialize to their base defaults:

```text
MANA_max = 100
MANA = MANA_max
XP = 0
niv = 1
bouff_max = niv × 10
bouff = bouff_max
```

---

## 15. Equipment Influence

Worn equipment and carried weapons modify character statistics:

* Direct bonuses or requirements for primary attributes;
* Armor absorption bonuses applied directly to `DEF`;
* Extra vitality modifiers added to `PV_MAX`;
* Auxiliary mana capacity boosts added to `MANA_max`;
* Movement speed penalties or bonuses applied to `vitesse`;
* Environmental hazard protections (radiation, toxic, ballistic).

Full equipment specifications are detailed in [`20_INVENTAIRE_ENG.md`](20_INVENTAIRE_ENG.md), [`21_EQUIPEMENT_ENG.md`](21_EQUIPEMENT_ENG.md), and [`22_OBJETS_ENG.md`](22_OBJETS_ENG.md).

---

## 16. Skill Influence

Invested skills directly augment baseline character capabilities:

* Permanent passive boosts to primary and derived attributes;
* Temporary tactical buffs activated in combat;
* Damage mitigation multipliers and critical hit scalers;
* Action speed and stamina consumption reductions.

The comprehensive skill tree is outlined in [`13_COMPETENCES_ENG.md`](13_COMPETENCES_ENG.md).

---

## 17. Status & Environmental Effects

Character statistics are subject to real-time status modifications:

* **Physical Trauma:** Bleeding, broken limbs, and concussions penalizing DEX and movement speed;
* **Fatigue & Hunger:** Depleted `bouff` inflicting stamina and regeneration penalties;
* **Toxic Contamination:** Radiation and biohazards depleting `PV` and degrading `CON`;
* **Beneficial Stimulants:** Combat drugs and adrenaline boosters granting temporary attribute spikes.

---

## 18. Statistics Master Table

| ID | Name | Category | Nature | Baseline / Calculation |
| :--- | :--- | :--- | :--- | :--- |
| `STAT-001` | **FOR** (STR) | Primary | Permanent | Generated (4d6 drop lowest) |
| `STAT-002` | **DEX** (DEX) | Primary | Permanent | Generated (4d6 drop lowest) |
| `STAT-003` | **CON** (CON) | Primary | Permanent | Generated (4d6 drop lowest) |
| `STAT-004` | **INT** (INT) | Primary | Permanent | Generated (4d6 drop lowest) |
| `STAT-005` | **SAG** (WIS) | Primary | Permanent | Generated (4d6 drop lowest) |
| `STAT-006` | **CHA** (CHA) | Primary | Permanent | Generated (4d6 drop lowest) |
| `STAT-007` | **MOD_FOR** | Modifier | Derived | Derived from `FOR` table |
| `STAT-008` | **MOD_DEX** | Modifier | Derived | Derived from `DEX` table |
| `STAT-009` | **MOD_CON** | Modifier | Derived | Derived from `CON` table |
| `STAT-010` | **MOD_INT** | Modifier | Derived | Derived from `INT` table |
| `STAT-011` | **MOD_SAG** | Modifier | Derived | Derived from `SAG` table |
| `STAT-012` | **MOD_CHA** | Modifier | Derived | Derived from `CHA` table |
| `STAT-013` | **PV_MAX** (MAX_HP) | Combat | Derived | `(CON // 2) + 12` |
| `STAT-014` | **PV** (HP) | Combat | Variable | Initialized to `PV_MAX` |
| `STAT-015` | **DEF** | Combat | Derived | `10 + MOD_DEX` |
| `STAT-016` | **MANA_max** | Resource | Variable | `100` |
| `STAT-017` | **MANA** | Resource | Variable | Initialized to `MANA_max` |
| `STAT-018` | **XP** | Progression | Variable | `0` |
| `STAT-019` | **niv** (LVL) | Progression | Variable | `1` |
| `STAT-020` | **bouff_max** | Resource | Derived | `niv × 10` |
| `STAT-021` | **bouff** | Resource | Variable | Initialized to `bouff_max` |
| `STAT-022` | **vitesse** | Locomotion | Variable | `0.4` |
| `STAT-023` | **grade** | Status | Variable | Controlled by Army Mode |

---

## 19. Related Documents

### GDD Documents

* 📄 [01 - Project Vision](01_VISION_ENG.md) — Overall project vision and pillars.
* 📄 [09 - Characters & NPCs](09_PERSONNAGES_ENG.md) — Non-player characters and survivor factions.
* 📄 [10 - Character Creation](10_CREATION_PERSONNAGE_ENG.md) — Initial character setup and attributes.
* 📄 [11 - Progression](11_PROGRESSION_ENG.md) — Character leveling and experience.
* 📄 [13 - Skills & Abilities](13_COMPETENCES_ENG.md) — Active and passive skill trees.
* 📄 [14 - Classes](14_CLASSES_ENG.md) — Character archetypes and specializations.
* 📄 [15 - General Gameplay](15_GAMEPLAY_ENG.md) — Core mechanics and player loop.
* 📄 [16 - Combat System](16_COMBAT_ENG.md) — Combat resolution and mechanics.
* 📄 [18 - Monsters & Mutants](18_MONSTRES_ENG.md) — Hostile creatures and enemy stats.
* 📄 [19 - Boss Encounters](19_BOSS_ENG.md) — Boss mechanics and difficulty scaling.
* 📄 [20 - Inventory System](20_INVENTAIRE_ENG.md) — Bag management and item storage.
* 📄 [21 - Equipment](21_EQUIPEMENT_ENG.md) — Weapons, armor, and gear slots.
* 📄 [22 - Items](22_OBJETS_ENG.md) — Consumables, materials, and stimulants.
* 📄 [29 - Professions](29_METIERS_ENG.md) — Crafting and harvesting professions.
* 📄 [30 - Crafting](30_CRAFT_ENG.md) — Item creation and crafting recipes.
* 📄 [31 - Harvesting](31_RECOLTE_ENG.md) — Resource gathering and nodes.
* 📄 [33 - Biomes](33_BIOMES_ENG.md) — Environmental ecosystems.
* 📄 [34 - Weather System](34_METEO_ENG.md) — Weather simulation and exposure hazards.
* 📄 [35 - Day / Night Cycle](35_JOUR_NUIT_ENG.md) — Day and night cycle mechanics.

### General Documentation

* 📄 [General Documentation](../README_ENG.md) — Main documentation index.
* 📄 [Project Roadmap](../ROADMAP_ENG.md) — Milestone roadmap.
* 📄 [Project Architecture](../ARCHITECTURE_ENG.md) — Technical architecture.

---

## 📌 Document Status

**Version:** 1.1.0  
**Status:** 🟡 In progress  
**Last updated:** October 2026  

This document incorporates all active character attributes, formulas, and data structures implemented in the core engine `PersoCore`. Extended high-level leveling formulas and auxiliary system interactions will be calibrated during upcoming balancing passes.

---

## Navigation

⬅️ [Progression](11_PROGRESSION_ENG.md)

➡️ [Skills & Abilities](13_COMPETENCES_ENG.md)


----
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />
