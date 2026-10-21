[🏠 Documentation](../README_ENG.md) > [🎮 GDD](README_ENG.md)

# 🏰 Dungeons

> **Document:** Dungeons  
> **Code:** GDD-008  
> **Version:** 1.0.0  
> **Status:** 🟡 In progress  
> **Last updated:** September 19, 2026  

---

## 📖 Table of Contents

1. [Overview](#1-overview)
2. [Role of Dungeons](#2-role-of-dungeons)
3. [Dungeon Archetypes](#3-dungeon-archetypes)
4. [Structure of a Dungeon](#4-structure-of-a-dungeon)
5. [Exploration](#5-exploration)
6. [Hazards & Perils](#6-hazards-perils)
7. [Creatures & Mutants](#7-creatures-mutants)
8. [Resources & Rewards](#8-resources-rewards)
9. [Bosses & Elite Encounters](#9-bosses-elite-encounters)
10. [Puzzles & Mechanisms](#10-puzzles-mechanisms)
11. [Lore & Environmental Storytelling](#11-lore-environmental-storytelling)
12. [Dungeons & Contamination](#12-dungeons-contamination)
13. [Dynamic Dungeon Evolution](#13-dynamic-dungeon-evolution)
14. [Dungeon Directory](#14-dungeon-directory)
15. [Detailed Dungeon Specification Template](#15-detailed-dungeon-specification-template)
16. [Related Documents](#16-related-documents)

---

## 1. Overview

Dungeons are high-stakes, specialized exploration locations across the world of **The Last Signal Online**.

They encompass fortified structures, underground complexes, abandoned industrial facilities, military installations, and other sequestered environments that exhibit significantly higher threat ratings, environmental hazards, and valuable salvage opportunities than the surrounding wilderness.

A dungeon typically features:

* High-value salvage and technological resources;
* Mutated creatures and hostile defense mechanisms;
* Specialized gear and rare equipment;
* Decrypted research archives and military logs;
* Hidden rooms, shortcuts, and secret caches;
* Dynamic script events and environmental traps;
* Physical and electronic puzzles;
* Specialized containment infrastructure;
* One or more major elite adversaries or boss encounters.

Dungeons can serve as crucial milestones within the main storyline or provide self-contained, high-reward exploration challenges for solo players and coordinated squads.

---

## 2. Role of Dungeons

Dungeons fulfill distinct design and gameplay roles within the persistent world:

* Providing complex, multi-tiered indoor and underground exploration environments;
* Concentrating severe environmental hazards, radiation, and elite enemies;
* Yielding superior rewards, advanced blueprints, and unique weapon components;
* Deepening the narrative lore and revealing historical revelations behind the catastrophe;
* Establishing concrete exploration objectives and squad dungeon-crawling challenges;
* Introducing unique tactical enemies, security automatons, and mutated monstrosities;
* Hosting dynamic emergent encounters and territory conflicts;
* Challenging players with claustrophobic, resource-limited situations distinct from open-world survival.

A dungeon is not merely a combat gauntlet: depending on its archetype, it may emphasize stealth navigation, environmental puzzle solving, hazard mitigation, or narrative investigation.

---

## 3. Dungeon Archetypes

Dungeons take various structural and thematic forms throughout the post-collapse world.

### 🧪 Research Laboratory

Decommissioned scientific and corporate research installations.

Key characteristics:

* Cleanrooms, containment vaults, and testing chambers;
* Scientific data servers and research logs;
* High-tech instrumentation and chemical reagents;
* Biohazard specimens and mutant experimental subjects;
* Critical narrative logs detailing the origins of the catastrophe.

---

### 🪖 Military Installation

Fortified bunkers, command posts, missile silos, and armories.

Key characteristics:

* High-grade military hardware and ballistic weaponry;
* Encrypted military communications and strategic archives;
* Automated turret networks and reinforced security blast doors;
* Armored defensive corridors and underground staging areas.

---

### 🏭 Industrial Complex

Heavy industrial factories, manufacturing plants, refineries, and power stations.

Key characteristics:

* Abundant industrial components, machinery, and raw alloys;
* Structural hazards, steam leaks, high-voltage circuits, and molten slag;
* Vertical catwalk exploration and mechanical puzzles;
* Robotic assembly units and maintenance machines.

---

### 🕳️ Underground Facility

Subterranean complexes built far beneath the earth's surface.

Archetypes include:

* Anti-nuclear fallout shelters and subterranean bunkers;
* Metro rail networks and drainage maintenance tunnels;
* Deep subterranean mining shafts and geological labs;
* Clandestine black-site facilities.

---

### 🏚️ Abandoned Urban Building

Ruined civilian skyscrapers, municipal hospitals, commercial malls, and residential blocks.

Key characteristics:

* Atmospheric urban decay and environmental storytelling;
* Structural collapse risks, elevator shaft climbs, and broken stairwells;
* Scavenger camps, localized mutant nests, and civilian survival caches.

---

### ☢️ Contaminated Zone / Ground Zero

Locations severely affected by chemical, biological, or radiological fallout.

Key characteristics:

* Lethal ambient toxicity requiring advanced hazard filtration or leaded armor;
* Highly evolved biological mutations and grotesque anomalies;
* Corrosive atmospheres accelerating equipment degradation;
* Exclusively high-value prototype salvage found nowhere else.

---

## 4. Structure of a Dungeon

Every official dungeon specification must define the following core parameters:

| Property | Description |
|:---------|:------------|
| **Identifier** | Unique alphanumeric tracking ID (`DNG-XXX`) |
| **Name** | Official designation / Landmark title |
| **Region** | Host region where the entrance is located |
| **Archetype** | Dungeon category (Laboratory, Bunker, Industrial, etc.) |
| **Contamination** | Contamination tier (Tier 0 Safe to Tier IV Lethal) |
| **Difficulty** | Threat level rating and recommended squad size |
| **Access Point** | Ingress coordinates, keys, or activation method |
| **Hostile Fauna** | Encountered creature types, mutant strains, and security forces |
| **Resources** | Available materials, scrap pools, and technical components |
| **Rewards** | Boss drops, chest loot, and unique blueprint rewards |
| **Boss Encounter** | Major elite boss adversary and combat mechanics |
| **Lore Background** | Historical backstory before and after the collapse |

---

## 5. Exploration

Navigating a dungeon demands methodical reconnaissance and multi-stage zone progression.

A dungeon layout generally comprises:

* **Ingress / Surface Entrance:** The access threshold connecting the dungeon to the open world;
* **Primary Corridors & Chambers:** The main thoroughfare connecting major functional wings;
* **Secondary Wings & Utility Areas:** Optional exploration paths with bonus loot, resources, or narrative terminals;
* **Hidden Passages & Ventilation Ducts:** Secret crawlspaces, destructible walls, and tactical shortcuts;
* **Secure Vaults & Quarantine Chambers:** High-security sectors requiring specific keycards, terminal hacks, or power restoration;
* **Hazard Corridors:** Environmental gauntlets fraught with gas leaks, flooded sections, or high radiation;
* **Central Core / Boss Arena:** The deepest sector where the primary objective and climatic encounter reside.

Dungeon designs range from structured linear facilities to sprawling, non-linear multi-floor mazes with branching bypasses.

---

## 6. Hazards & Perils

Survival within dungeons is threatened by compounding environmental and tactical perils:

* **Hostile Fauna & Mutants:** Aggressive territorial creatures and apex mutations;
* **Severe Contamination:** Acute radiological, chemical, and biological hazard pockets;
* **Structural Instability:** Collapsing ceilings, compromised catwalks, pit falls, and unstable debris;
* **Active Automated Defenses:** Automated machine-gun turrets, laser tripwires, and electrified bulkheads;
* **Spatial Anomalies:** Localized physical distortions generated by scientific failure;
* **Mechanical Traps:** Deadfalls, pressure plates, and incendiary countermeasures left by scavengers;
* **Dynamic Emergencies:** Power grid surges, structural flooding, and oxygen depletion events;
* **Hostile Survivors & Rival Players:** Contested open-dungeon PvP encounters and rival faction fireteams.

All hazards must reflect the architectural purpose, historical context, and contamination tier of the facility.

---

## 7. Creatures & Mutants

The demographic of hostile entities inside a dungeon is determined by:

* Its ecological and architectural environment;
* The prevailing contamination tier;
* The facility's pre-war scientific or military activities;
* Geographic placement and regional ecosystem;
* Dungeon archetype and floor depth.

Subterranean and highly contaminated facilities often harbor deeply mutated, blind, or light-sensitive abominations, alongside dormant robotic security platforms that reactivate upon unauthorized entry.

---

## 8. Resources & Rewards

Dungeons represent the prime source of endgame progression assets:

* **Refined Materials:** High-purity alloys, polymers, and rare minerals;
* **Advanced Equipment:** Military-grade weapons, specialized tactical armor, and attachments;
* **Technological Schematics:** Blueprints for crafting rare weapons, vehicles, and base structures;
* **Critical Components:** Microchips, quantum cores, servos, and military communication modules;
* **Narrative Intel:** Encrypted datadrives, research papers, and military situation reports;
* **Lore Relics:** Unique artifacts that unlock hidden faction dialogue and special world quests.

The quality and rarity of dungeon loot scale directly with difficulty, hazard severity, and boss complexity.

---

## 9. Bosses & Elite Encounters

Major dungeons culminate in challenging encounters against powerful adversaries.

A dungeon boss may:

* Guard the central facility reactor or mainframe vault;
* Defend unique prototype weapons or narrative artifacts;
* Embody a horrific apex mutation spawned by failed scientific experimentation;
* Operate as a heavy military war machine or rogue combat AI;
* Trigger phased combat mechanics requiring squad coordination and environmental interaction.

Not every minor dungeon requires a dedicated boss; smaller facilities may feature elite squad ambushes or intense survival waves instead.

---

## 10. Puzzles & Mechanisms

Dungeons challenge players' problem-solving skills through interactive mechanical and electronic systems:

* **Power Grid Routing:** Repairing generators, replacing fuses, and rerouting circuit breakers to power blast doors and elevators;
* **Electronic Lockpicks & Terminals:** Hacking keycode panels and decrypting terminal files to unlock security rooms;
* **Automated Containment Overrides:** Balancing pressure valves, venting toxic gases, or draining flooded basements;
* **Environmental Sequence Logic:** Activating switches in deliberate order guided by scattered environmental clues and audio logs;
* **Physical Weight & Obstacle Puzzles:** Moving heavy crates or counterweights to breach collapsed passages.

---

## 11. Lore & Environmental Storytelling

Dungeons serve as living museums of the pre-collapse society and the disaster itself.

Players uncover historical revelations through:

* Recoverable audio recordings and terminal text files;
* Environmental clues (skeletal remains, abandoned work sites, barricades);
* Scientific lab notes describing failed containment protocols;
* Emergency evacuation logs and desperate distress transmissions;
* Corporate and military communiques uncovering faction intrigue;
* Cryptic clues pointing toward the true identity and origin of **The Last Signal**.

---

## 12. Dungeons & Contamination

The contamination rating of a dungeon dictates tactical preparation:

* **Tier 0 (Safe):** No specialized hazard gear required; standard survival equipment suffices;
* **Tier I (Low Hazard):** Basic particulate filtration mask required; minor chemical irritation;
* **Tier II (Moderate):** Full NBC gas mask and filtered air supply mandatory; localized rad spots;
* **Tier III (Severe):** Heavy lead-lined hazmat suit and anti-rad medicine required; aggressive mutations present;
* **Tier IV (Lethal):** Extreme bio/rad contamination; sealed environmental suits, rad injectors, and limited exposure timers required.

---

## 13. Dynamic Dungeon Evolution

Dungeons within the persistent world can undergo dynamic transformations over time:

* **Faction Occupation:** A dungeon cleared of mutants may be converted into a forward outpost by a rival faction;
* **Contamination Surges:** Weather storms or anomaly spikes can temporarily raise the contamination tier;
* **Dynamic Invasions:** Wandering mutant hordes or rogue bandit squads may reclaim previously secured sectors;
* **Timed Ingress Windows:** Submerged or blast-locked facilities accessible only during specific tidal or power grid conditions;
* **Structural Degradation:** Sectors collapsing or reopening following regional tectonic events.

---

## 14. Dungeon Directory

Official dungeons will be integrated into the world map systematically.

| ID | Dungeon Name | Region | Archetype | Difficulty | Status |
|:---|:---|:---|:---|:---:|:---:|
| `DNG-001` | Theta Research Complex | Plains Region | Research Laboratory | Tier 2 | 🟡 In Design |
| `DNG-002` | Bunker Alpha-7 | Toxic Wasteland | Military Installation | Tier 3 | 🟡 In Design |
| `DNG-003` | Metro Line 4 Hub | Ruined Metropolis | Underground Rail | Tier 1 | 🟡 In Design |
| `DNG-004` | Obsidian Power Station | Industrial Zone | Industrial Facility | Tier 4 | 🟡 In Design |

---

## 15. Detailed Dungeon Specification Template

Every new dungeon specification must adhere to the following markdown template:

```text
ID: DNG-XXX
Name: [Dungeon Name]
Region: [Host Region]
Archetype: [Laboratory / Military / Industrial / Underground / Urban / Contaminated]
Difficulty Rating: [Tier 1 to Tier 5 / Recommended Squad Size]
Contamination Tier: [Tier 0 to Tier IV]

### Description
Comprehensive physical and thematic overview of the facility.

### Lore & History
Historical narrative before the collapse, catastrophic events during the fall, and current state.

### Access & Ingress
Coordinates, entrance topography, required keys, security codes, or environmental prerequisites.

### Internal Architecture
Detailed floor-by-floor breakdown of wings, corridors, vaults, and secret passages.

### Hostile Entities
Catalog of mutant fauna, security automations, and hostile human combatants.

### Environmental Hazards
Active radiation, chemical leaks, structural collapses, and automated traps.

### Resource Pools
Types of scrap, raw materials, electronic components, and ammunition available for scavenging.

### Rewards & Unique Loot
Boss drop tables, container loot pools, schematics, and prototype weapons.

### Boss & Elite Encounters
Detailed combat mechanics, phases, vulnerability windows, and arena design.

### Puzzles & Interactive Mechanisms
Circuit routing, security terminal hacks, and valve override requirements.

### Secrets & Hidden Stashes
Concealed compartments, crawlspaces, and Easter egg locations.

### Dynamic Events
Dynamic scripted emergencies, faction counter-attacks, and emergency power failure events.

### World Connections
Transit routes linking the dungeon to nearby cities, wilderness regions, or sub-levels.
```

---

## 16. 📚 Related Documents

### GDD Documents

* 📄 [01 - Project Vision](01_VISION_ENG.md) — Overall project vision and pillars.
* 📄 [02 - Universe](02_UNIVERS_ENG.md) — World setting and global lore.
* 📄 [03 - Story & Scenario](03_SCENARIO_ENG.md) — Narrative arc and main campaign.
* 📄 [04 - Chronology](04_CHRONOLOGIE_ENG.md) — Historical timeline of events.
* 📄 [05 - Factions](05_FACTIONS_ENG.md) — Faction dynamics and diplomatic relations.
* 📄 [06 - Regions](06_REGIONS_ENG.md) — Open-world regional framework.
* 📄 [07 - Cities & Settlements](07_VILLES_ENG.md) — Urban hubs and outposts.
* 📄 [08 - Dungeons](08_DONJONS_ENG.md) — High-threat dungeon environments.
* 📄 [09 - Characters & NPCs](09_PERSONNAGES_ENG.md) — Non-player characters and survivor factions.
* 📄 [10 - Character Creation](10_CREATION_PERSONNAGE_ENG.md) — Initial character setup and attributes.
* 📄 [32 - World Map](32_CARTE_ENG.md) — Global cartography.
* 📄 [33 - Biomes](33_BIOMES_ENG.md) — Environmental ecosystems.
* 📄 [34 - Weather System](34_METEO_ENG.md) — Weather simulation.
* 📄 [35 - Day / Night Cycle](35_JOUR_NUIT_ENG.md) — Day and night cycle mechanics.

### General Documentation

* 📄 [General Documentation](../README_ENG.md) — Main documentation index.
* 📄 [Project Roadmap](../ROADMAP_ENG.md) — Milestone roadmap.
* 📄 [Project Architecture](../ARCHITECTURE_ENG.md) — Technical architecture.

### Subsystem Documentation

* 📄 [Lore & Worldbuilding](../lore/README_ENG.md) — Historical archives and world lore.
* 📄 [Gameplay Mechanics](../gameplay/README_ENG.md) — Core mechanics and player systems.

---

## 📌 Document Status

**Version:** 1.0.0  
**Status:** 🟡 In progress  

Individual dungeons and underground complexes will be fully detailed as regional layouts, world map zones, and narrative campaign acts are finalized.

---

## Navigation

⬅️ [Cities & Settlements](07_VILLES_ENG.md)

➡️ [Characters & NPCs](09_PERSONNAGES_ENG.md)


----
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />
