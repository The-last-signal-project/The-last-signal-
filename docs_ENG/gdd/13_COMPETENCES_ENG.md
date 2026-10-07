[🏠 Documentation](../README_ENG.md) > [🎮 GDD](README_ENG.md)

# 🧠 Skills & Abilities

> **Document:** Skills & Abilities  
> **Code:** GDD-013  
> **Version:** 1.0.0  
> **Status:** 🟡 In progress  
> **Last updated:** October 8, 2026  

---

## 📖 Table of Contents

1. [Overview](#1-overview)
2. [Objectives](#2-objectives)
3. [Core Principles](#3-core-principles)
4. [Skill Tree Architecture](#4-skill-tree-architecture)
5. [Skill Trees & Branches](#5-skill-trees-branches)
6. [Skill Unlocking Mechanisms](#6-skill-unlocking-mechanisms)
7. [Skill Tiers & Level Scaling](#7-skill-tiers-level-scaling)
8. [Gameplay Integration](#8-gameplay-integration)
9. [Balancing Framework](#9-balancing-framework)
10. [User Interface & HUD](#10-user-interface-hud)
11. [Technical Architecture](#11-technical-architecture)
12. [Master Skill Directory](#12-master-skill-directory)
13. [Related Documents](#13-related-documents)

---

## 1. Overview

The skills and abilities system empowers players to customize, specialize, and enhance their survivor's combat and utility capabilities throughout their journey across **The Last Signal**.

The master skill matrix is organized into **three primary specializations**:

* ⚔️ **Combat & Tactics**
* ☣️ **Survival & Adaptation**
* 📡 **Infra-Tech & Signal**

Every individual ability is assigned:

* A standardized unique identifier (`COMP-XXX`);
* An official skill name;
* An execution type (*Active* or *Passive*);
* Defined mechanical effects and modifiers;
* An architectural branch and discipline classification.

The baseline framework catalogs **34 distinct abilities**:

* **21 Active Abilities**
* **13 Passive Proficiencies**

---

## 2. Objectives

The skill system is engineered to fulfill several core gameplay pillars:

* **In-Depth Specialization:** Providing deep build diversity and tactical role definition;
* **Playstyle Expression:** Supporting distinct solo, cooperative, stealth, and aggressive approaches;
* **Synergy & Group Roles:** Fostering party complementarity through synergistic abilities;
* **Long-Term Progression:** Granting rewarding horizontal and vertical mastery milestones;
* **Meaningful Trade-offs:** Encouraging deliberate point allocation rather than homogeneous all-in-one builds;
* **Thematic Alignment:** Maintaining immersion firmly grounded in post-apocalyptic wasteland survival.

---

## 3. Core Principles

### 3.1 Specialization
The three branches correspond to distinct survivor archetypes. Players can focus heavily into a single discipline for high-tier capstone abilities or distribute points across branches for flexible hybrid versatility.

### 3.2 Active Abilities
Active skills require deliberate, manual activation by the player. They feature:

* Calibrated cooldown timers;
* Active durations;
* Effective ranges and projectile arcs;
* Areas of effect (AoE);
* Situational triggers and resource requirements (e.g., Stamina, Mana, ammunition).

*Specific numerical parameters and balance values will be calibrated during testing.*

### 3.3 Passive Proficiencies
Passive abilities trigger and persist automatically upon unlocking. They modify baseline statistics, enhance status resistances, improve item efficiency, or alter fundamental interactions.

### 3.4 Unique Identifiers
Every ability possesses an immutable, unique identifier formatted as:

`COMP-XXX`

Identifiers remain permanent and are never repurposed across different skills.

---

## 4. Skill Tree Architecture

The master skill tree is partitioned into three disciplines:

### Branch 1 — Combat & Tactics
Focuses on kinetic warfare, ballistics, heavy firepower, explosive ordnance, martial close-quarters combat, and defensive posture.

### Branch 2 — Survival & Adaptation
Focuses on physical endurance, biochemical resilience, field medicine, emergency triage, stealth navigation, and wilderness tracking.

### Branch 3 — Infra-Tech & Signal
Focuses on terminal intrusion, electronic warfare, long-range communication signals, autonomous drone deployment, fortifications, and robotic maintenance.

---

## 5. Skill Trees & Branches

### ⚔️ Branch 1: Combat & Tactics

#### 🎯 Marksmanship & Ballistics

* **[COMP-001] Suppressive Fire** *(Active)*: Unleashes continuous sustained fire over a targeted sector, reducing enemy movement speed and heavily degrading target aim accuracy.
* **[COMP-002] Armor Piercing Shot** *(Active)*: High-precision shot calibrated to bypass a substantial percentage of the target's physical armor defense.
* **[COMP-003] Tactical Reload** *(Active)*: Instantly accelerates reload speed on the equipped weapon and grants a burst of fire rate for 4 seconds.
* **[COMP-004] Eagle Eye** *(Passive)*: Extends effective maximum weapon engagement range and increases critical strike chance against distant targets.
* **[COMP-005] Recoil Mastery** *(Passive)*: Significantly dampens vertical and horizontal weapon climb during continuous automatic fire.

#### 💣 Guerrilla Warfare & Demolitions

* **[COMP-006] Proximity Mine** *(Active)*: Conceals an explosive charge on terrain or surfaces that detonates upon hostile proximity.
* **[COMP-007] Smoke Screen Grenade** *(Active)*: Deploys a dense volumetric smoke cloud breaking line-of-sight and disrupting automated turret tracking.
* **[COMP-008] Breaching Charge** *(Active)*: Plants a timed shaped explosive on reinforced structures, blast doors, or enemy vehicles.
* **[COMP-009] Volatile Chemistry** *(Passive)*: Expands blast radius and increases base explosive damage dealt by improvised and crafted ordnance.
* **[COMP-010] Serrated Shrapnel** *(Passive)*: Detonations inflict lingering, heavy laceration bleed damage on all caught targets.

#### 🛡️ Close Quarters & Defense

* **[COMP-011] Riot Shield Charge** *(Active)*: Sprints forward with raised protection, violently knocking back and stunning the primary target impacted.
* **[COMP-012] Reflex Parry** *(Active)*: Briefly assumes a defensive guard, parrying frontal melee strikes and slashing incoming damage.
* **[COMP-013] Juggernaut** *(Passive)*: Enhances the baseline physical armor rating and damage absorption afforded by all equipped armor pieces.
* **[COMP-014] Resolute Stance** *(Passive)*: Reduces the duration and effectiveness of crowd control debuffs (stuns, knockdowns, movement slows).

---

### ☣️ Branch 2: Survival & Adaptation

#### 🧬 Bio-Resistance & Physical Conditioning

* **[COMP-015] Second Wind** *(Active)*: Instantly restores stamina reserves and halts fatigue accumulation for a limited duration.
* **[COMP-016] Adrenaline Surge** *(Active)*: Dramatically boosts tactical sprint speed and confers temporary immunity to movement slows for 6 seconds.
* **[COMP-017] Mutated Resilience** *(Passive)*: Elevates natural radiation resistance and slows down toxic infection meter escalation.
* **[COMP-018] Iron Gut** *(Passive)*: Renders the survivor immune to food poisoning and diseases contracted from consuming irradiated food or contaminated water.

#### 🚑 Field Medicine & Support

* **[COMP-019] Rapid Suture Kit** *(Active)*: Instantly seals severe hemorrhaging wounds and applies progressive regenerative healing to self or targeted ally.
* **[COMP-020] Field Defibrillator** *(Active)*: Revives an incapacitated squadmate in the heat of combat with a baseline portion of health restored.
* **[COMP-021] Antiseptic Vapor** *(Active)*: Deploys an aerosolized medicinal cloud continuously healing all friendly operatives in the perimeter.
* **[COMP-022] Optimized Transfusion** *(Passive)*: Increases the healing and restorative potency of all consumed medical supplies by 25%.

#### 🎒 Infiltration & Tracking

* **[COMP-023] Shadow Concealment** *(Active)*: Drastically narrows detection radius against mutants and hostile scouts for a covert window.
* **[COMP-024] Hunter's Mark** *(Active)*: Flags a target, outlining their silhouette and health gauge through structural cover for the entire squad.
* **[COMP-025] Muffled Footsteps** *(Passive)*: Minimizes ambient acoustic noise emitted during walking and tactical sprinting.

---

### 📡 Branch 3: Infra-Tech & Signal

#### 💻 Cyberwarfare & Signal Intelligence

* **[COMP-026] EMP Pulse** *(Active)*: Discharges an electromagnetic wave disabling automated defense turrets and overloading enemy shield capacitors.
* **[COMP-027] Radio Intercept** *(Active)*: Scans the electromagnetic spectrum to detect unauthorized radio transmissions and hostile player presence within a sector.
* **[COMP-028] Remote Uplink Hack** *(Active)*: Wirelessly overrides electronic blast doors, surveillance sensors, and security terminals from distance.
* **[COMP-029] Cryptanalysis** *(Passive)*: Accelerates decryption speed and lowers complexity thresholds when cracking encrypted terminals and vaults.

#### 🤖 Autonomous Drones & Robotics

* **[COMP-030] Recon Drone** *(Active)*: Launches an aerial drone conducting terrain surveillance and marking threats on the tactical world map.
* **[COMP-031] Deployable Sentry** *(Active)*: Constructs a portable automated turret providing defensive fire against encroaching hostiles.
* **[COMP-032] High-Density Capacitor** *(Passive)*: Extends operational flight duration, battery lifespan, and control range for all autonomous drones.

#### 🛠️ Field Engineering & Construction

* **[COMP-033] Field Nanite Welder** *(Active)*: Restores structural integrity and repair points on defensive fortifications, bunker gates, or allied vehicles.
* **[COMP-034] Scavenger's Efficiency** *(Passive)*: Grants bonus chances to recover pristine and rare technical components when salvaging wasteland scrap.

---

## 6. Skill Unlocking Mechanisms

The skill unlocking framework dictates progressive character customization:

* Milestone level thresholds governing access to advanced nodes;
* Prerequisite tier investments required within earlier branch tiers;
* Consumed Skill Point (SP) pools allocated upon leveling up;
* Pre-requisite parent skills on specific branching pathways;
* Class discipline alignments and equipment proficiencies;
* Wasteland schematics and training manuals discovered in hidden vaults.

---

## 7. Skill Tiers & Level Scaling

Abilities may feature multi-rank upgrades across their lifecycle:

* Tiered rank increments (e.g., Rank 1 to Rank 3);
* Scaling magnitude of primary buffs, healing, or damage coefficients;
* Shortened cooldown durations at higher ranks;
* Reduced activation resource costs;
* Extended range and area-of-effect expansions.

---

## 8. Gameplay Integration

Skills interface directly with the primary game loops:

* **Combat & Skirmishes:** Modulating damage, crowd control, and defense mechanics;
* **Wilderness Survival:** Overcoming toxic biomes, radiation hot zones, and starvation;
* **Exploration & Dungeons:** Overriding security networks, hacking blast doors, and uncovering stashes;
* **PvE & Boss Encounters:** Managing squad aggro, sustaining group health, and neutralizing shields;
* **Faction PvP Skirmishes:** Countering rival survivor tactics with utility and suppression;
* **Economic & Field Crafting:** Salvaging high-tier electronic components and repairing fortifications;
* **Vehicles & Outposts:** Maintaining field machinery, barricades, and automated defenses.

---

## 9. Balancing Framework

Calibration guidelines ensure long-term competitive health:

* Base numerical values, cooldowns, and activation costs calibrated against PvE encounter pacing;
* Symmetrical tuning for PvP skirmishes preventing unavoidable stun-locks or uncounterable burst damage;
* Resource expenditure (mana, stamina, battery charge) balancing instantaneous potency;
* Clear audiovisual telegraphs enabling counterplay against high-impact abilities.

---

## 10. User Interface & HUD

The skill interface ensures transparent build inspection:

* Visual presentation of the three distinct specialization constellations;
* Unambiguous status indicators (Unlocked, Available to Learn, Locked);
* Complete tooltip breakdowns showing exact damage formulas, cooldowns, and costs;
* Dedicated HUD hotbar slots for active abilities with cooldown timers and buff indicators;
* Real-time tracking of passive proficiency procs and durations.

---

## 11. Technical Architecture

All skills operate under strict client-server network authority:

* **Server Authority:** Authoritative cooldown tracking, line-of-sight validation, damage resolution, status application, and skill point validation;
* **Client Implementation:** Responsive input buffering, visual animations, particle effects, sound design, and local HUD telemetry;
* **State Synchronization:** Reliable replication of active cooldowns, buffs, and drone entities across connected clients.

---

## 12. Master Skill Directory

| ID | Ability Name | Nature | Specialization Discipline |
| :--- | :--- | :---: | :--- |
| `COMP-001` | **Suppressive Fire** | Active | Combat & Tactics (Marksmanship) |
| `COMP-002` | **Armor Piercing Shot** | Active | Combat & Tactics (Marksmanship) |
| `COMP-003` | **Tactical Reload** | Active | Combat & Tactics (Marksmanship) |
| `COMP-004` | **Eagle Eye** | Passive | Combat & Tactics (Marksmanship) |
| `COMP-005` | **Recoil Mastery** | Passive | Combat & Tactics (Marksmanship) |
| `COMP-006` | **Proximity Mine** | Active | Combat & Tactics (Demolitions) |
| `COMP-007` | **Smoke Screen Grenade** | Active | Combat & Tactics (Demolitions) |
| `COMP-008` | **Breaching Charge** | Active | Combat & Tactics (Demolitions) |
| `COMP-009` | **Volatile Chemistry** | Passive | Combat & Tactics (Demolitions) |
| `COMP-010` | **Serrated Shrapnel** | Passive | Combat & Tactics (Demolitions) |
| `COMP-011` | **Riot Shield Charge** | Active | Combat & Tactics (Defense) |
| `COMP-012` | **Reflex Parry** | Active | Combat & Tactics (Defense) |
| `COMP-013` | **Juggernaut** | Passive | Combat & Tactics (Defense) |
| `COMP-014` | **Resolute Stance** | Passive | Combat & Tactics (Defense) |
| `COMP-015` | **Second Wind** | Active | Survival & Adaptation (Conditioning) |
| `COMP-016` | **Adrenaline Surge** | Active | Survival & Adaptation (Conditioning) |
| `COMP-017` | **Mutated Resilience** | Passive | Survival & Adaptation (Conditioning) |
| `COMP-018` | **Iron Gut** | Passive | Survival & Adaptation (Conditioning) |
| `COMP-019` | **Rapid Suture Kit** | Active | Survival & Adaptation (Field Medicine) |
| `COMP-020` | **Field Defibrillator** | Active | Survival & Adaptation (Field Medicine) |
| `COMP-021` | **Antiseptic Vapor** | Active | Survival & Adaptation (Field Medicine) |
| `COMP-022` | **Optimized Transfusion** | Passive | Survival & Adaptation (Field Medicine) |
| `COMP-023` | **Shadow Concealment** | Active | Survival & Adaptation (Infiltration) |
| `COMP-024` | **Hunter's Mark** | Active | Survival & Adaptation (Infiltration) |
| `COMP-025` | **Muffled Footsteps** | Passive | Survival & Adaptation (Infiltration) |
| `COMP-026` | **EMP Pulse** | Active | Infra-Tech & Signal (Cyberwarfare) |
| `COMP-027` | **Radio Intercept** | Active | Infra-Tech & Signal (Cyberwarfare) |
| `COMP-028` | **Remote Uplink Hack** | Active | Infra-Tech & Signal (Cyberwarfare) |
| `COMP-029` | **Cryptanalysis** | Passive | Infra-Tech & Signal (Cyberwarfare) |
| `COMP-030` | **Recon Drone** | Active | Infra-Tech & Signal (Robotics) |
| `COMP-031` | **Deployable Sentry** | Active | Infra-Tech & Signal (Robotics) |
| `COMP-032` | **High-Density Capacitor** | Passive | Infra-Tech & Signal (Robotics) |
| `COMP-033` | **Field Nanite Welder** | Active | Infra-Tech & Signal (Engineering) |
| `COMP-034` | **Scavenger's Efficiency** | Passive | Infra-Tech & Signal (Engineering) |

---

## 13. Related Documents

### GDD Documents

* 📄 [01 - Project Vision](01_VISION_ENG.md) — Overall project vision and pillars.
* 📄 [10 - Character Creation](10_CREATION_PERSONNAGE_ENG.md) — Initial character setup and attributes.
* 📄 [11 - Progression](11_PROGRESSION_ENG.md) — Character leveling and experience.
* 📄 [12 - Statistics & Attributes](12_STATISTIQUES_ENG.md) — Core attributes and combat stats.
* 📄 [14 - Classes](14_CLASSES_ENG.md) — Character archetypes and specializations.
* 📄 [15 - General Gameplay](15_GAMEPLAY_ENG.md) — Core mechanics and player loop.
* 📄 [16 - Combat System](16_COMBAT_ENG.md) — Combat resolution and mechanics.
* 📄 [17 - AI Systems](17_IA_ENG.md) — Enemy behaviors and reaction parameters.
* 📄 [20 - Inventory System](20_INVENTAIRE_ENG.md) — Bag management and item storage.
* 📄 [21 - Equipment](21_EQUIPEMENT_ENG.md) — Weapons, armor, and gear slots.
* 📄 [29 - Professions](29_METIERS_ENG.md) — Crafting and harvesting professions.
* 📄 [30 - Crafting](30_CRAFT_ENG.md) — Item creation and crafting recipes.
* 📄 [36 - Guilds](36_GUILDES_ENG.md) — Guild mechanics and shared outposts.
* 📄 [37 - Groups & Parties](37_GROUPES_ENG.md) — Party management and squad synergies.
* 📄 [39 - PvE Content](39_PVE_ENG.md) — Dungeons, bosses, and PvE encounters.
* 📄 [40 - PvP System](40_PVP_ENG.md) — Player versus player combat rules.
* 📄 [44 - HUD](44_HUD_ENG.md) — Head-up display layout and ability slots.
* 📄 [45 - Menus](45_MENUS_ENG.md) — Character and skill tree menu interfaces.

### General Documentation

* 📄 [General Documentation](../README_ENG.md) — Main documentation index.
* 📄 [Project Roadmap](../ROADMAP_ENG.md) — Milestone roadmap.
* 📄 [Project Architecture](../ARCHITECTURE_ENG.md) — Technical architecture.

---

## 📌 Document Status

**Version:** 1.0.0  
**Status:** 🟡 In progress  
**Last updated:** October 2026  

The **34 abilities** cataloged above define the baseline skill tree matrix. Precise cooldown values, scaling damage formulas, skill point unlock requirements, and animation schemas will be iteratively refined alongside combat prototype balance testing.

---

## Navigation

⬅️ [Statistics & Attributes](12_STATISTIQUES_ENG.md)

➡️ [Classes](14_CLASSES_ENG.md)


----
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />
