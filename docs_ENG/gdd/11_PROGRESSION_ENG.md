[🏠 Documentation](../README_ENG.md) > [🎮 GDD](README_ENG.md)

# 📈 Progression

> **Document:** Progression  
> **Code:** GDD-011  
> **Version:** 1.0.0  
> **Status:** 🟡 In progress  
> **Last updated:** October 2026  

---

## 📖 Table of Contents

1. [Overview](#1-overview)
2. [Objectives](#2-objectives)
3. [Progression Principles](#3-progression-principles)
4. [Character Level](#4-character-level)
5. [Experience](#5-experience)
6. [Experience Sources](#6-experience-sources)
7. [Progression Tiers](#7-progression-tiers)
8. [Progression Rewards](#8-progression-rewards)
9. [Statistics & Progression](#9-statistics-progression)
10. [Skills & Progression](#10-skills-progression)
11. [Classes & Progression](#11-classes-progression)
12. [Professions & Progression](#12-professions-progression)
13. [Horizontal Progression](#13-horizontal-progression)
14. [Progression Caps & Limits](#14-progression-caps-limits)
15. [Respec & Modifications](#15-respec-modifications)
16. [Progression Tracking](#16-progression-tracking)
17. [Progression Matrix](#17-progression-matrix)
18. [Related Documents](#18-related-documents)

---

## 1. Overview

Progression represents the systemic evolution of a character throughout their survival journey across **The Last Signal**.

It enables the player to gradually develop their character through diverse in-game activities: exploration, discoveries, combat engagements, skill mastery, profession crafting, and persistent world interactions.

The progression system is designed to reward curiosity and tactical initiative without reducing gameplay to repetitive level grinding.

---

## 2. Objectives

The character progression framework fulfills several key game design goals:

* **Sustained Growth:** Providing players with a tangible and satisfying sense of continuous evolution;
* **Activity Recognition:** Rewarding every meaningful action performed within the persistent world;
* **Build Diversity:** Accommodating multiple distinct character build orientations and playstyles;
* **Exploration Incentives:** Encouraging players to discover uncharted locations, hazards, and lore;
* **Meaningful Specialization:** Enabling distinct tactical roles within group and solo gameplay;
* **Clarity & Accessibility:** Preserving an intuitive, easily understood progression model;
* **Balanced Paths:** Preventing any single activity or grinding loop from becoming universally dominant;
* **Long-Term Engagement:** Maintaining player motivation and challenge across extended campaign lifecycles.

Progression must remain logically grounded in the lore and rules of the persistent wasteland universe.

---

## 3. Progression Principles

The progression architecture relies on five core design principles:

### Progressive Evolution
Characters unlock capabilities incrementally rather than gaining instantaneous access to top-tier abilities.

### Activity Diversity
A wide spectrum of gameplay loops—from wilderness survival and crafting to dungeon raids—contributes meaningfully to advancement.

### Strategic Specialization
Player choices guide characters toward specific tactical, operational, or trade archetypes.

### Tangible Consequences
Progression milestones produce direct, noticeable impacts on character survivability, efficiency, and capabilities.

### Player Agency
Players retain full freedom to shape their build according to their preferred survival style.

---

## 4. Character Level

Every character possesses a global level reflecting their overarching evolution and survival experience.

The character level governs:

* Unlocking world features, zones, and content milestones;
* Equipping level-gated weapons, gear, and technology;
* Accessing advanced skills and specialization trees;
* Establishing baseline systemic thresholds;
* Representing the survivor's global standing in the wasteland.

The definitive level ceiling will be calibrated during the gameplay balance phase.

> **Maximum Level:** To be determined (TBD).

The global level is designed to complement, rather than overshadow, specialized skill and profession systems.

---

## 5. Experience

Experience (XP) quantifies a character's progress toward their next level threshold.

When a character accumulates sufficient XP, they advance to the subsequent level.

### Core Experience Parameters

* **Current XP:** Accumulated experience points within the current level tier;
* **Required XP:** Target experience points needed to unlock the next level;
* **Current Level:** The active character level;
* **Total Accumulated XP:** Lifetime experience points tracked for statistics and analytics.

The progression curve and mathematical formula will be calibrated during balance testing.

> **Experience Formula:** To be determined (TBD).

---

## 6. Experience Sources

Experience is awarded across diverse gameplay activities to support multiple playstyles.

Primary sources of experience include:

* **Combat:** Eliminating hostile mutants, rogue survivors, and automated security units;
* **Quests & Missions:** Completing storyline contracts, bounty hunts, and outpost tasks;
* **World Exploration:** Uncovering hidden landmarks, bunkers, and uncharted sectors;
* **Dynamic Events:** Participating in regional emergencies, defense sieges, and public broadcast events;
* **Professions & Crafting:** Harvesting raw materials, refining scrap, and fabricating items;
* **Milestone Objectives:** Fulfilling personal and faction survival objectives;
* **Group Content:** Cooperating in high-threat incursions and coordinated outpost assaults;
* **PvE Challenges:** Clearing challenging underground facilities and boss arenas;
* **PvP Encounters:** Engaging in competitive faction skirmishes where permitted by system rules.

Reward scaling must remain balanced to prevent repetitive farming from trivializing other activities.

---

## 7. Progression Tiers

Character progression is structured across standardized developmental tiers:

| Tier | Level Range | Description |
| :--- | :---: | :--- |
| **Beginner** | TBD | Orientation, fundamental survival mechanics, and basic equipment handling |
| **Intermediate** | TBD | Expanded world exploration, archetype definition, and intermediate gear access |
| **Advanced** | TBD | Distinct character specialization, challenging facility raids, and faction missions |
| **Expert** | TBD | Mastery of advanced skill trees, prototype technology fabrication, and high-threat zones |
| **Endgame** | TBD | Pinnacle challenges, extreme survival conditions, world boss encounters, and competitive warfare |

*Final tier names, numerical boundaries, and level requirements will be calibrated during balance testing.*

---

## 8. Progression Rewards

Level milestones grant various character enhancements and gameplay unlocks.

Depending on the specific milestone reached, rewards include:

* Access to new active and passive abilities;
* Attribute enhancement points for customized stat distribution;
* Unlocked tiers of higher-grade weaponry, armor, and modules;
* Clearance for restricted world regions, high-tier bunkers, and narrative quests;
* Unlocked crafting schematics, blueprinted recipes, and refinement techniques;
* Access to specialized gameplay systems and faction ranks.

All progression rewards must remain aligned with the thematic identity of the reached level tier.

---

## 9. Statistics & Progression

Character statistics quantify physical, mental, and tactical performance in the world.

Progression directly drives statistical development under the framework specified in [`12_STATISTIQUES_ENG.md`](12_STATISTIQUES_ENG.md).

The progression subsystem governs:

* Milestone intervals at which stats improve;
* Attribution rules for unspent attribute points (if point distribution is utilized);
* Soft and hard caps preventing statistical inflation;
* Interplay between global level scaling and derived combat metrics.

---

## 10. Skills & Progression

Skills provide characters with specialized tactical tools and passive proficiencies.

Progression milestones facilitate:

* Unlocking novel skill branches and nodes;
* Upgrading existing skill tiers and potencies;
* Unlocking specialized path variants;
* Fine-tuning cooldowns, resource costs, and tactical effects.

Detailed mechanics are outlined in [`13_COMPETENCES_ENG.md`](13_COMPETENCES_ENG.md). The system ensures global character level alone does not automatically grant universal mastery over all skills.

---

## 11. Classes & Progression

Classes represent structured combat and operational specializations.

Progression enables characters to:

* Choose and formally unlock class paths;
* Deepen progression within chosen class disciplines;
* Unlock advanced class specializations and capstones;
* Expand situational loadout options and tactical roles.

Detailed rules and requirements are defined in [`14_CLASSES_ENG.md`](14_CLASSES_ENG.md). Classes offer guiding frameworks without rigidly constraining character freedom.

---

## 12. Professions & Progression

Professions provide an independent economic and crafting progression track.

Survivors can develop expertise across gathering, fabrication, and technological recycling disciplines.

Profession progression operates largely independently of character combat level:

* Practice-based advancement through resource extraction and item crafting;
* Successful refinement of rare materials and components;
* Discovery and deciphering of ancient technical schematics;
* Acquisition of specialized trade and engineering knowledge.

Full profession mechanics and recipes are detailed in [`29_METIERS_ENG.md`](29_METIERS_ENG.md).

---

## 13. Horizontal Progression

Progression in **The Last Signal** is not exclusively vertical power scaling.

Horizontal progression broadens tactical options, utility, and adaptability without escalating raw numerical power:

* Unlocking alternative skill mechanics and utility abilities;
* Discovering modular weapon modifications and equipment attachments;
* Learning specialized crafting recipes and field blueprints;
* Unlocking environmental navigation options and hazard resistances;
* Expanding faction reputation and diplomatic access privileges;
* Gaining specialized trade opportunities and settlement privileges.

This design guarantees meaningful diversity and distinct identities between characters of identical level.

---

## 14. Progression Caps & Limits

To maintain game balance and prevent power runaway, the progression system enforces clear constraints:

* Global maximum character level cap;
* Point investment caps on primary attributes and derived stats;
* Skill tree branch point constraints requiring selective specialization;
* Class and subclass exclusivity rules;
* Profession tier limitations and specializations;
* Gear requirement thresholds ensuring equipment matches survivor experience.

---

## 15. Respec & Modifications

Certain progression decisions may be reconfigured through designated in-game respec mechanisms.

The specification defines:

* Which attribute and skill choices can be reallocated;
* Resource, currency, or facility costs associated with respect;
* Cooldowns and contextual requirements (e.g., medical clinics, safe settlement resting);
* Permanent character traits that cannot be altered once selected.

> **Respec Framework:** To be determined (TBD).

All attribute and skill reset actions are strictly validated and recorded server-side to prevent exploits.

---

## 16. Progression Tracking

Players can monitor their development in real time through clear visual UI elements:

* Current level and experience progress bar on the HUD;
* Exact numerical XP values and points required for the next milestone;
* Notifications for unspent attribute and skill points;
* Detailed profession mastery tabs and current gathering ranks;
* Milestone guides outlining upcoming unlocks and requirements.

These visual representations are integrated into the HUD and character management panels.

---

## 17. Progression Matrix

The matrix summarizes the core progression subsystems, their functional roles, and system linkages:

| Subsystem | Functional Role | Calibration / Source Document |
| :--- | :--- | :--- |
| **Character Level** | Overall survivor evolution and tier gating | Calibrated during balancing passes |
| **Level Ceiling** | Global progression cap | To be determined (TBD) |
| **Experience (XP)** | Metric driving level advancement | Calibrated during balancing passes |
| **XP Curve Formula** | Mathematical requirement scaling | To be determined (TBD) |
| **Progression Rewards** | Stat points, gear access, and feature unlocks | Calibrated during balancing passes |
| **Skill Unlocks** | Ability unlocks, upgrades, and specializations | See [`13_COMPETENCES_ENG.md`](13_COMPETENCES_ENG.md) |
| **Class Evolution** | Combat archetypes and class disciplines | See [`14_CLASSES_ENG.md`](14_CLASSES_ENG.md) |
| **Professions** | Trade mastery, harvesting, and crafting | See [`29_METIERS_ENG.md`](29_METIERS_ENG.md) |
| **Attributes & Stats** | Character performance and combat parameters | See [`12_STATISTIQUES_ENG.md`](12_STATISTIQUES_ENG.md) |

---

## 18. Related Documents

### GDD Documents

* 📄 [01 - Project Vision](01_VISION_ENG.md) — Overall project vision and pillars.
* 📄 [02 - Universe](02_UNIVERS_ENG.md) — World setting and global lore.
* 📄 [09 - Characters & NPCs](09_PERSONNAGES_ENG.md) — Non-player characters and survivor factions.
* 📄 [10 - Character Creation](10_CREATION_PERSONNAGE_ENG.md) — Initial character setup and attributes.
* 📄 [11 - Progression](11_PROGRESSION_ENG.md) — Character leveling and experience.
* 📄 [12 - Statistics & Attributes](12_STATISTIQUES_ENG.md) — Core attributes and combat stats.
* 📄 [13 - Skills & Abilities](13_COMPETENCES_ENG.md) — Active and passive skill trees.
* 📄 [14 - Classes](14_CLASSES_ENG.md) — Character archetypes and specializations.
* 📄 [15 - General Gameplay](15_GAMEPLAY_ENG.md) — Core mechanics and player loop.
* 📄 [16 - Combat System](16_COMBAT_ENG.md) — Combat resolution and mechanics.
* 📄 [20 - Inventory System](20_INVENTAIRE_ENG.md) — Bag management and item storage.
* 📄 [21 - Equipment](21_EQUIPEMENT_ENG.md) — Weapons, armor, and gear slots.
* 📄 [29 - Professions](29_METIERS_ENG.md) — Crafting and harvesting professions.
* 📄 [30 - Crafting](30_CRAFT_ENG.md) — Item creation and crafting recipes.
* 📄 [31 - Harvesting](31_RECOLTE_ENG.md) — Resource gathering and nodes.
* 📄 [39 - PvE Content](39_PVE_ENG.md) — Dungeons, bosses, and PvE encounters.
* 📄 [40 - PvP System](40_PVP_ENG.md) — Player versus player combat rules.
* 📄 [41 - Quests](41_QUETES_ENG.md) — Missions and campaign progression.
* 📄 [42 - Events](42_EVENEMENTS_ENG.md) — World events and dynamic triggers.
* 📄 [43 - Achievements](43_SUCCES_ENG.md) — Progression milestones and badges.

### General Documentation

* 📄 [General Documentation](../README_ENG.md) — Main documentation index.
* 📄 [Project Roadmap](../ROADMAP_ENG.md) — Milestone roadmap.
* 📄 [Project Architecture](../ARCHITECTURE_ENG.md) — Technical architecture.

---

## 📌 Document Status

**Version:** 1.0.0  
**Status:** 🟡 In progress  
**Last updated:** October 2026  

This document defines the systemic framework for character progression. Numerical values, experience curves, leveling formulas, progression caps, and milestone rewards will be calibrated during gameplay balance passes.

---

## Navigation

⬅️ [Character Creation](10_CREATION_PERSONNAGE_ENG.md)

➡️ [Statistics & Attributes](12_STATISTIQUES_ENG.md)


----
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />
