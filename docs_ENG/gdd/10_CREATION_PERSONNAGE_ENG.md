[🏠 Documentation](../README_ENG.md) > [🎮 GDD](README_ENG.md)

# 🧬 Character Creation

> **Document:** Character Creation  
> **Code:** GDD-010  
> **Version:** 1.0.0  
> **Status:** 🟡 In progress  
> **Last updated:** September 19, 2026  

---

## 📖 Table of Contents

1. [Overview](#1-overview)
2. [Design Objectives](#2-design-objectives)
3. [Character Creation Workflow](#3-character-creation-workflow)
4. [Identity Parameters](#4-identity-parameters)
5. [Appearance & Visual Customization](#5-appearance-visual-customization)
6. [Character Origin](#6-character-origin)
7. [Initial Specialization](#7-initial-specialization)
8. [Character Naming Rules](#8-character-naming-rules)
9. [Server-Side Validation](#9-server-side-validation)
10. [Technical Architecture](#10-technical-architecture)
11. [Restrictions & Constraints](#11-restrictions-constraints)
12. [Post-Creation Character Evolution](#12-post-creation-character-evolution)
13. [Character Parameter Matrix](#13-character-parameter-matrix)
14. [Related Documents](#14-related-documents)

---

## 1. Overview

Character creation serves as the initial gateway for players entering the persistent world of **The Last Signal Online**.

It represents the very first step in the player's journey, enabling them to sculpt a distinct avatar, configure personal identity attributes, and establish their initial thematic background while adhering to post-apocalyptic world rules.

The creation process is designed to be streamlined yet expressive, ensuring that all created avatars remain visually and narratively grounded within the harsh atmosphere of the universe.

---

## 2. Design Objectives

The character creation system fulfills several critical game design and technical goals:

* **Individual Uniqueness:** Empowering players to build visually distinct and personalized wasteland survivors;
* **Identity Grounding:** Establishing player identity through name, background origin, and aesthetic appearance;
* **Server Data Preparation:** Formatting and packaging character attributes into a verified payload for server persistence;
* **Integrity & Exploit Prevention:** Enforcing strict server-side validation to reject invalid stats, prohibited names, or hacked parameters;
* **Ecosystem Balance:** Ensuring starting choices provide flavor and initial playstyle guidance without granting irreversible, overpowered advantages over other players;
* **Seamless System Integration:** Maintaining full architectural compatibility with subsequent progression, inventory, stat, and class systems.

---

## 3. Character Creation Workflow

The creation workflow guides the player through six intuitive steps:

```
[ Step 1: Identity ] ➡️ [ Step 2: Appearance ] ➡️ [ Step 3: Origin ]
                                                      ⬇️
[ Step 6: Confirmation ] ⬅️ [ Step 5: Verification ] ⬅️ [ Step 4: Specialization ]
```

### Step 1 — Identity
The player enters their character's name, optional handle or callsign, and selects their identity preferences.

### Step 2 — Appearance
The player customizes physical morphology, facial structure, hair style/color, skin tone, eye color, and initial rugged clothing presets.

### Step 3 — Origin
The player selects a background origin archetype that establishes their thematic context and pre-catastrophe narrative background.

### Step 4 — Initial Specialization
The player chooses a starting survival focus, allocating a small initial pool of baseline skills or selecting a starter utility kit.

### Step 5 — Verification & Review
The client conducts local sanity checks and presents a summary card of the chosen avatar for final player inspection.

### Step 6 — Server Confirmation & Spawning
Upon player confirmation, the payload is transmitted to the server. Following authoritative validation, the character entity is saved in the database, and the player spawns at the designated starter zone.

---

## 4. Identity Parameters

Identity attributes uniquely identify the survivor within server databases and player social interactions:

| Parameter | Type | Description |
|:----------|:----:|:------------|
| **Character ID** | `UUID / u64` | Unique system identifier assigned upon creation |
| **Character Name** | `String` | Public display name visible to other survivors |
| **Given Name / Nickname** | `String` | Optional narrative moniker or callsign |
| **Gender / Pronouns** | `Enum` | Character demographic configuration |
| **Origin Archetype** | `Enum` | Chosen background heritage and narrative context |
| **Creation Timestamp** | `DateTime` | Real-world date and server tick of character inception |

---

## 5. Appearance & Visual Customization

Players can tailor their survivor's appearance using options aligned with the project's art direction:

* **Body Build & Morphology:** Height, build slider (lean, athletic, muscular, stocky);
* **Facial Sculpting:** Face presets, jawline, nose structure, and aging/weathering details;
* **Hairstyles & Colors:** Scavenger hairstyles, military buzzcuts, braids, and wasteland dyes;
* **Eyes & Complexion:** Iris pigmentation, skin tone, blemishes, sun exposure, and dirt layers;
* **Wasteland Scars & Markings:** War scars, burn marks, biological anomaly lesions, and survival tattoos;
* **Starter Attire:** Functional scavenged clothing (jackets, patched trousers, combat boots, respirators).

Visual customization is purely aesthetic and does not directly grant combat or survival statistic advantages.

---

## 6. Character Origin

The Origin system grounds the character within the historical timeline and geography of **The Last Signal Online**.

Origins provide thematic flavor and may connect to:

* Specific geographic regions (e.g., Plains scavenger, Subterranean metro dweller, Industrial refinery worker);
* Pre-collapse civilian or technical professions (e.g., Field Technician, Paramedic, Agriculturalist, Machinist);
* Survival enclaves and communal traditions;
* Initial narrative motivations for investigating the radio broadcast from **The Lighthouse**.

Origin choices are strictly narrative backgrounds and do not lock the player into rigid character classes or professions.

---

## 7. Initial Specialization

To help players tailor their early gameplay experience, the creation system may offer initial guidance choices:

* **Starter Weapon Preference:** Basic melee weapon (e.g., Pipe Wrench / Machete) vs. basic ranged firearm (e.g., Scavenged Pistol);
* **Starter Utility Package:** Medical first-aid kit, engineering repair tools, or field gathering supplies;
* **Minor Skill Allocation:** Minor initial bonus to Survival (hunger/thirst efficiency), Athletics (stamina), or Scavenging (scrap extraction rate).

These starting perks provide early quality-of-life adjustments without predetermining long-term endgame builds.

---

## 8. Character Naming Rules

Character names must adhere to strict formatting and moderation standards:

* **Length Constraints:** Minimum of 3 characters, maximum of 20 characters;
* **Allowed Character Set:** Standard Latin alphanumeric characters (`[A-Za-z0-9]`), single spaces, and hyphens (`-`);
* **Prohibited Formatting:** No consecutive spaces, trailing/leading whitespace, or excessive punctuation;
* **Uniqueness:** Character names must be globally unique across the active game server;
* **Blacklist Filtering:** Automated rejection of profanity, hate speech, offensive phrases, and reserved system names (e.g., `Admin`, `Prometheus`, `Server`, `System`).

All name validation rules are authoritatively enforced on the Rust server.

---

## 9. Server-Side Validation

The client application is inherently untrusted. The Rust backend performs rigorous validation before saving any character entity:

```
[ Client Creation UI ] ──( Creation Payload JSON )──> [ Rust Server Gateway ]
                                                             │
                                                     [ Auth & Token Check ]
                                                     [ Name Uniqueness & Blacklist ]
                                                     [ Attribute Bounds Verification ]
                                                     [ Option Availability Check ]
                                                             │
                                                ┌────────────┴────────────┐
                                                ▼                         ▼
                                           [ REJECT ]                [ ACCEPT ]
                                     ( Return Error Code )    ( Save to PostgreSQL DB )
                                                              ( Instantiate in World )
```

Key validation checks include:

1. **Payload Completeness:** Ensuring all mandatory fields (Name, Origin, Gender, Visual Presets) are provided;
2. **Value Bounds Checking:** Confirming all slider and index values fall strictly within valid server-defined ranges;
3. **Stat Integrity:** Verifying that starting attribute pools and skill allocations do not exceed the authorized point budget;
4. **Account Character Limit:** Verifying the account has available character slots.

---

## 10. Technical Architecture

Character creation spans three primary software layers:

### Python Client Layer (`client_python/`)
* Renders the 3D/2D visual preview and real-time customization UI;
* Formats user input into structured network packets;
* Displays immediate client-side validation hints (e.g., character count, prohibited characters);
* Transmits the final creation request over secure WebSocket protocols.

### Rust Server Layer (`server_rust/`)
* Intercepts the creation request and authenticates the player's account session token;
* Executes the authoritative validation pipeline;
* Generates system UUIDs and initial database records;
* Initializes starting inventory containers, health meters, and position coordinates;
* Broadcasts successful spawn events to nearby clients.

### Database Layer (`database/` / PostgreSQL)
* Commits the character record within an atomic transaction;
* Links the character ID to the master player account ID;
* Isolates public character entity data from private security credentials and billing records.

---

## 11. Restrictions & Constraints

The system imposes the following operational restrictions:

* **Slot Limits:** Standard accounts are limited to a fixed number of active character slots (e.g., 3 to 5 slots);
* **Name Reserving:** Deleted character names enter a 30-day cooldown period before becoming available to other accounts;
* **Creation Cooldown:** Anti-spam rate limiting prevents automated script flood of creation requests.

---

## 12. Post-Creation Character Evolution

Character creation represents only the starting baseline. Once in the world, the character evolves dynamically through gameplay systems:

* **Level Progression:** Accumulating experience points through exploration, combat, and crafting ([`11_PROGRESSION_ENG.md`](11_PROGRESSION_ENG.md));
* **Attributes & Stats:** Enhancing strength, agility, endurance, and intelligence ([`12_STATISTIQUES_ENG.md`](12_STATISTIQUES_ENG.md));
* **Skill Masteries:** Unlocking active combat techniques and survival abilities ([`13_COMPETENCES_ENG.md`](13_COMPETENCES_ENG.md));
* **Class Archetypes:** Specializing into tactical roles and advanced masteries ([`14_CLASSES_ENG.md`](14_CLASSES_ENG.md));
* **Professions & Crafting:** Mastering engineering, metallurgy, medicine, and scavenging ([`29_METIERS_ENG.md`](29_METIERS_ENG.md));
* **Equipment & Gear:** Upgrading wasteland armor, weapons, and hazard suits ([`21_EQUIPEMENT_ENG.md`](21_EQUIPEMENT_ENG.md)).

---

## 13. Character Parameter Matrix

| Category | Parameter Name | Mandatory | Modifiable Post-Creation | System Authority |
|:---|:---|:---:|:---:|:---:|
| **Identity** | Character Name | Yes | Paid / Special Item Only | Server |
| **Identity** | Nickname / Callsign | No | Yes (Freely) | Server |
| **Identity** | Gender / Pronouns | Yes | Cosmetic Clinic Only | Server |
| **Appearance** | Facial Structure | Yes | Cosmetic Clinic Only | Server |
| **Appearance** | Hairstyle & Hair Color | Yes | Yes (Barber / Crafting) | Server |
| **Appearance** | Skin Complexion | Yes | Cosmetic Clinic Only | Server |
| **Appearance** | Scars & Tattoos | No | Yes (Tattoo Artist NPC) | Server |
| **Appearance** | Starting Garments | Yes | Yes (Equipment System) | Server |
| **Origin** | Origin Background | Yes | No (Permanent Lore) | Server |
| **Progression** | Starter Utility Focus | Yes | Overridden by Normal Progression | Server |

---

## 14. 📚 Related Documents

### GDD Documents

* 📄 [01 - Project Vision](01_VISION_ENG.md) — Overall project vision and pillars.
* 📄 [02 - Universe](02_UNIVERS_ENG.md) — World setting and global lore.
* 📄 [03 - Story & Scenario](03_SCENARIO_ENG.md) — Narrative arc and main campaign.
* 📄 [05 - Factions](05_FACTIONS_ENG.md) — Faction dynamics and diplomatic relations.
* 📄 [06 - Regions](06_REGIONS_ENG.md) — Open-world regional framework.
* 📄 [07 - Cities & Settlements](07_VILLES_ENG.md) — Urban hubs and outposts.
* 📄 [08 - Dungeons](08_DONJONS_ENG.md) — High-threat dungeon environments.
* 📄 [09 - Characters & NPCs](09_PERSONNAGES_ENG.md) — Non-player characters and survivor factions.
* 📄 [10 - Character Creation](10_CREATION_PERSONNAGE_ENG.md) — Initial character setup and attributes.
* 📄 [11 - Progression](11_PROGRESSION_ENG.md) — Character leveling and experience.
* 📄 [12 - Statistics & Attributes](12_STATISTIQUES_ENG.md) — Core attributes and combat stats.
* 📄 [13 - Skills & Abilities](13_COMPETENCES_ENG.md) — Active and passive skill trees.
* 📄 [14 - Classes](14_CLASSES_ENG.md) — Character archetypes and specializations.
* 📄 [15 - General Gameplay](15_GAMEPLAY_ENG.md) — Core mechanics and player loop.
* 📄 [20 - Inventory System](20_INVENTAIRE_ENG.md) — Bag management and item storage.
* 📄 [21 - Equipment](21_EQUIPEMENT_ENG.md) — Weapons, armor, and gear slots.
* 📄 [29 - Professions](29_METIERS_ENG.md) — Crafting and harvesting professions.

### General Documentation

* 📄 [General Documentation](../README_ENG.md) — Main documentation index.
* 📄 [Project Roadmap](../ROADMAP_ENG.md) — Milestone roadmap.
* 📄 [Project Architecture](../ARCHITECTURE_ENG.md) — Technical architecture.

---

## 📌 Document Status

**Version:** 1.0.0  
**Status:** 🟡 In progress  

This specification defines the baseline architecture for character creation. Detailed UI mockups, facial preset meshes, and network serialization schemas will be refined alongside client-server prototype integration.

---

## Navigation

⬅️ [Characters & NPCs](09_PERSONNAGES_ENG.md)

➡️ [Progression](11_PROGRESSION_ENG.md)


----
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />
