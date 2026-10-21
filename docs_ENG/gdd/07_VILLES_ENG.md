[🏠 Documentation](../README_ENG.md) > [🎮 GDD](README_ENG.md)

# 🏙️ Cities & Settlements

> **Document:** Cities & Settlements  
> **Code:** GDD-007  
> **Version:** 1.0.0  
> **Status:** 🟡 In progress  
> **Last updated:** September 13, 2026  

---

## 📖 Table of Contents

1. [Overview](#1-overview)
2. [Role of Cities & Settlements](#2-role-of-cities-settlements)
3. [Settlement Archetypes](#3-settlement-archetypes)
4. [Structure of a Settlement](#4-structure-of-a-settlement)
5. [Demographics & Population](#5-demographics-population)
6. [Services & Facilities](#6-services-facilities)
7. [Urban Resources](#7-urban-resources)
8. [Hazards & Perils](#8-hazards-perils)
9. [Faction Control & Geopolitics](#9-faction-control-geopolitics)
10. [Exploration](#10-exploration)
11. [Lore & Environmental Storytelling](#11-lore-environmental-storytelling)
12. [Dynamic Settlement Evolution](#12-dynamic-settlement-evolution)
13. [Settlement Directory](#13-settlement-directory)
14. [Detailed Settlement Specification Template](#14-detailed-settlement-specification-template)
15. [Related Documents](#15-related-documents)

---

## 1. Overview

Cities and settlements are pivotal hubs across the world of **The Last Signal Online**.

They embody both the ruined remnants of pre-collapse human civilization and newly organized enclaves forged by survivors.

A settlement can be found in various states of occupancy and stability:

* Fully inhabited and fortified;
* Partially occupied by scavenging groups;
* Entirely abandoned to the elements;
* Structurally ruined or obliterated;
* Severely contaminated by biological or radiological fallout;
* Militarily occupied by a dominant faction;
* Overrun by mutants and transformed into high-threat hazard zones.

Cities serve central gameplay roles in exploration, commerce, social gathering, quest lines, and emergent environmental storytelling.

---

## 2. Role of Cities & Settlements

Cities and outposts fulfill essential gameplay and world design functions:

* Serving as social hubs and safe rallying points for players;
* Providing access to trading markets, rare vendors, and crafting stations;
* Enabling rich NPC dialogue, narrative exposition, and faction reputation quests;
* Grounding the territorial influence of major factions;
* Delivering structured quest hubs and dynamic mission boards;
* Imparting lore and documenting the downfall of civilization;
* Acting as prominent navigational landmarks across the map;
* Offering complex multi-level urban exploration and dungeon challenges;
* Permitting survivors to resupply, repair equipment, and prepare for dangerous expeditions into contaminated zones.

Not every settlement serves every function: some operate as heavily guarded trade bastions, while others are lawless ghost towns laden with traps and valuable salvage.

---

## 3. Settlement Archetypes

Inhabited and abandoned settlements take several distinct architectural and functional forms.

### 🏙️ Major City (Metropolis)

Expansive pre-war urban centers.

Major cities feature:

* Dense multi-story architecture and vertical exploration;
* Complex municipal infrastructure (subways, sewer networks, highways);
* Distinct city districts with varying threat tiers;
* Diverse salvage pools and high-tech components;
* Deeply contaminated quarantined zones;
* High-security government and corporate facilities.

---

### 🏘️ Small Town

Moderate settlements with fewer buildings and basic municipal services.

Small towns commonly function as key transit hubs and staging outposts connecting major wilderness regions.

---

### 🏚️ Village

Compact rural settlements comprising modest residential dwellings and farming infrastructure.

A village may be:

* Actively settled by peaceful survivor communities;
* Abandoned and reclaimed by overgrown vegetation;
* Destroyed by catastrophic events or mutant swarms;
* Garrisoned by bandit raiders or cult enforcers.

---

### 🏕️ Survivor Camp

Makeshift encampments erected following the Catastrophe.

Survivor camps serve as:

* Temporary or permanent emergency shelters;
* Vital field resupply and water purification points;
* Barter outposts and barter stations;
* Social meeting grounds for wanderers;
* Starting staging grounds for dangerous wilderness expeditions.

---

### 🏭 Industrial Facility

Heavy industrial zones consisting of factory plants, warehouses, refineries, or rail yards.

These complexes yield high-value manufacturing machinery, structural metals, and industrial salvage.

---

### 🪖 Military Base

Decommissioned or overrun military installations and fortified compounds.

These secure installations contain:

* Military-grade weapons, ordnance, and ballistic armor;
* Classified command archives and tactical maps;
* Military vehicles and transport scrap;
* Reinforced bunkers and secure fallout shelters;
* Tactical intelligence regarding the initial outbreak of the Catastrophe.

---

### 🧪 Scientific Research Facility

Classified research laboratories, testing ranges, and corporate think tanks.

These complexes are instrumental in uncovering the origins of the Catastrophe, experimental pathogen samples, and advanced pre-war technology blueprints.

---

## 4. Structure of a Settlement

Every settlement specification must document the following core properties:

| Property | Description |
| :--- | :--- |
| **Identifier** | Unique standardized ID (e.g., `CITY-001`) |
| **Name** | Official name of the city or settlement |
| **Region** | Host region in which the settlement is situated |
| **Archetype** | Functional archetype (Metropolis, Village, Outpost, etc.) |
| **Current State** | Physical and operational status (Inhabited, Ruined, Abandoned) |
| **Contamination** | Local contamination level |
| **Population** | Estimated resident population count and composition |
| **Dominant Faction** | Governing or influential faction |
| **Available Services** | Commercial, medical, crafting, and repair facilities |
| **Resources** | Notable salvage and material pools present |
| **Hazards** | Threat factors, mutant spawns, structural instabilities |
| **History & Lore** | Historical narrative pre- and post-collapse |
| **Points of Interest** | Prominent landmarks, plazas, and fortified sectors |

---

## 5. Demographics & Population

The resident population of a settlement reflects its political control, security tier, and history.

A settlement may host:

* Independent civilian survivors and scavengers;
* Quest-giving and lore-bearing NPCs;
* Specialized merchants and barter traders;
* Faction soldiers, officers, and sentries;
* Hostile bandit gangs or zealous cultists;
* Invasive mutant packs in ruined districts.

Certain settlements are completely devoid of human life. Demographic composition dynamically evolves over time in response to seasonal conflicts and storyline shifts.

---

## 6. Services & Facilities

Functioning settlements can offer an array of player amenities:

* **Commercial Barter:** Buying and selling consumables, gear, and raw resources;
* **Equipment Repair:** Restoring weapon and armor durability;
* **Crafting Workshops:** Advanced workbenches and assembly stations;
* **Secure Storage & Banking:** Personal and guild lockers to stash valuable gear;
* **Medical Aid:** Treating trauma, radiation sickness, and infection;
* **Information & Intel:** Purchasing maps, rumor logs, and bounty hints;
* **Mission Boards:** Accepting faction bounties and regional contracts;
* **Shelter & Housing:** Safe resting spots and player-rentable living quarters;
* **Gear Modification:** Upgrading weapon attachments, weapon tuning, and armor reinforcement.

Service availability is strictly tied to a settlement's physical condition; ruined towns provide no formal amenities without player restoration.

---

## 7. Urban Resources

Settlements are rich sources of specialized salvage and manufactured supplies:

* Processed food rations and purified water;
* Medical pharmaceuticals, bandages, and surgical equipment;
* Structural lumber, masonry, and reinforced glass;
* Scrap metal, sheet steel, and copper piping;
* Electronics, capacitors, wiring, and microcontrollers;
* Refined fuel, generator batteries, and lubricants;
* Technical schematics and precision tools.

Resource density is governed by the original function of the settlement and the degree of scavenging it has endured.

---

## 8. Hazards & Perils

Settlements—especially ruined or contested ones—harbor significant dangers:

* Pockets of concentrated radiation, chemical leaks, or bio-hazards;
* Ambushing mutant packs, infected stalkers, and apex nest lords;
* Structurally unsound buildings liable to collapse;
* Localized physical and electromagnetic anomalies;
* Hostile sniper patrols, bandit sentries, and cult inquisitors;
* Rigged tripwires, antipersonnel mines, and survivor traps;
* Dynamic hazard surges and weather incursions.

An abandoned city is rarely safe; silence often conceals lurking predators or territorial raiders.

---

## 9. Faction Control & Geopolitics

Key cities and fortifications are actively governed or contested by major factions.

A controlling faction can:

* Enforce municipal law and establish sentry checkpoints;
* Defend the settlement from mutant incursions and rival raiders;
* Monopolize regional resource extraction;
* Grant exclusive merchant discounts to friendly players;
* Impose tariffs or bar hostile survivors from entering;
* Launch military sorties into neighboring sectors.

Settlement ownership can change dynamically during server-wide faction warfare events. Complete faction details are cataloged in [`05_FACTIONS_ENG.md`](05_FACTIONS_ENG.md).

---

## 10. Exploration

Urban environments deliver intricate vertical and subterranean exploration gameplay.

Players can discover:

* Multi-level office complexes, shopping centers, and hospitals;
* Hidden supply stashes behind locked security doors;
* Deceased couriers carrying encrypted data drives;
* Stranded survivors offering emergency rescue quests;
* Unique pre-war collectibles and historical relics;
* Secret access tunnels linking basements to sewer networks;
* Fortified rooftop snipers' nests and observation posts;
* Hidden anomaly rifts and lost experimental labs.

Significant urban structures function as bespoke exploration mini-dungeons with multi-stage access requirements.

---

## 11. Lore & Environmental Storytelling

Cities serve as primary vessels for environmental storytelling.

Players piece together urban history by observing:

* The physical state and degradation of architecture;
* Abandoned vehicles, barricades, and evacuation checkpoints;
* Discarded emergency notices, diaries, and graffiti;
* Survivor audio logs and recorded police broadcasts;
* Military quarantine zones and emergency triage wards;
* Impact craters and explosive residue from desperate last stands;
* Automated distress beacons still broadcasting on loop.

Every street corner and decaying building offers clues about how its citizens reacted when the Catastrophe unfolded.

---

## 12. Dynamic Settlement Evolution

The world of **The Last Signal Online** is persistent.

Settlements are subject to dynamic evolution over time:

* Ruins can be rebuilt and repopulated through cooperative player initiatives;
* Settlements can be abandoned following severe mutant assaults or disease outbreaks;
* Faction governance can flip following territorial sieges;
* Ambient contamination can intensify following seasonal events;
* New trading posts can organically expand based on player economy activity;
* Security ratings can dynamically rise or fall depending on bandit raid frequencies.

All structural and political changes remain consistent with the broader world chronology and seasonal narrative arcs.

---

## 13. Settlement Directory

The catalog of world settlements is being developed alongside world map design.

| ID | Name | Region | Archetype | Current State | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **CITY-001** | *To be determined* | *To be determined* | *To be determined* | *To be determined* | 🟡 |
| **CITY-002** | *To be determined* | *To be determined* | *To be determined* | *To be determined* | 🟡 |
| **CITY-003** | *To be determined* | *To be determined* | *To be determined* | *To be determined* | 🟡 |
| **CITY-004** | *To be determined* | *To be determined* | *To be determined* | *To be determined* | 🟡 |

> Official settlement names and coordinates will be integrated once regional map boundaries and campaign quest paths are locked.

---

## 14. Detailed Settlement Specification Template

Every finalized city or settlement entry must follow this standardized template:

### [Settlement Name]

**ID:** CITY-XXX  
**Region:** *To be determined*  
**Archetype:** *To be determined*  
**Current State:** *To be determined*  
**Contamination Level:** *To be determined*  

### Description
Atmosphere, architectural theme, and visual layout of the settlement.

### History
Chronological history of the settlement prior to, during, and after the Catastrophe.

### Demographics & Population
Active population size, social dynamics, and civilian composition.

### Faction Governance
Dominant faction, administrative rules, and military defense posture.

### Available Services
List of functional facilities (trading, crafting workbenches, repairs, medical clinic).

### Resource Pools
Key salvage categories, scavenge rates, and unique regional commodities.

### Hazards & Security Threats
Localized hazards, ambient radiation, mutant infestation zones, and defensive traps.

### Notable Landmarks & Districts
Key points of interest, town squares, underground bunkers, and fortified zones.

### Secrets & Hidden Paths
Concealed entrances, locked vaults, basement corridors, and easter eggs.

### Dynamic Events & Quests
Localized world events, siege defense missions, and recurring bounty contracts.

### Transit & Connections
Connected roadways, transit tunnels, and neighboring wilderness zones.

---

## 15. Related Documents

### Game Design Documents (GDD)

* 📄 [01 - Project Vision](01_VISION_ENG.md) — Overall project vision and pillars.
* 📄 [02 - Universe](02_UNIVERS_ENG.md) — World setting and global lore.
* 📄 [03 - Story & Scenario](03_SCENARIO_ENG.md) — Narrative arc and main campaign.
* 📄 [04 - Chronology](04_CHRONOLOGIE_ENG.md) — Historical timeline of events.
* 📄 [05 - Factions](05_FACTIONS_ENG.md) — Faction dynamics and diplomatic relations.
* 📄 [06 - Regions](06_REGIONS_ENG.md) — Open-world regional framework.
* 📄 [07 - Cities & Settlements](07_VILLES_ENG.md) — Urban hubs and outposts.
* 📄 [08 - Dungeons](08_DONJONS_ENG.md) — High-threat dungeon environments.
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

Individual cities and outposts will be cataloged systematically based on region layouts, world map design, and storyline milestones.

---

## Navigation

⬅️ [Regions](06_REGIONS_ENG.md)

➡️ [Dungeons](08_DONJONS_ENG.md)


----
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />
