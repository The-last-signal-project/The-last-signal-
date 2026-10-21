[🏠 Documentation](../README_ENG.md) > [🎮 GDD](README_ENG.md)

# 🎭 **SCENARIOS & QUESTS - The Last Signal**
> *Game Design Document - Version 1.0*  
> **Last updated**: July 16, 2026  
> **Author**: Cyril  
> **Status**: 🟡 **In Development (80% complete - Main campaign completed)**  

---

## 📌 **Table of Contents**
1. [Global Context](#1-global-context)
2. [Main Campaign Scenario](#2-main-campaign-scenario)
3. [Epic Quests](#3-epic-quests)
4. [Side Quests](#4-side-quests)
5. [Choice System & Consequences](#5-choice-system-consequences)
6. [Key Lore Elements](#6-key-lore-elements)
7. [Gameplay Integration](#7-gameplay-integration)

---

## 1. Global Context

### **The World of The Last Signal**
In **2045**, a worldwide **electromagnetic pulse (EMP)** crippled all electronic infrastructure, plunging humanity into chaos.  
**30 years later (2075)**, survivors strive to rebuild civilization amidst the ruins of the pre-catastrophe world.  
A **mysterious radio signal** is transmitted every **24 hours** from an ancient military facility known as **"The Lighthouse"**.

### **The Core Narrative Conflict**
- **For Optimists**: The signal could be a **distress beacon** or a **blueprint for reconstruction**.
- **For Paranoids**: It could be a **lethal trap** or a **harbinger of doom**.
- **For Cultists**: It is the **divine voice** of Prometheus, an emergent military AI.

> **Note**: This context directly connects to [`02_UNIVERS_ENG.md`](02_UNIVERS_ENG.md) and [`04_CHRONOLOGIE_ENG.md`](04_CHRONOLOGIE_ENG.md).

---

## 2. Main Campaign Scenario

### **🔴 Main Campaign: "The Mystery of the Lighthouse"**
- **Type**: Core storyline quest (Mandatory endgame progression)
- **Estimated Playtime**: 15–20 hours
- **Recommended Level**: Level 1 → 30

#### **📌 Summary**
The player, an amnesiac survivor, awakens and discovers an ancient **military terminal** inside the ruins of **Base Alpha**. Activating it initiates a perilous journey across diverse wasteland biomes to **uncover the signal's true origins** and reach **The Lighthouse**, the epicenter of the enigma.

---

#### **📋 Campaign Progression Overview**

| Step | Objective | Primary Location | Key Reward | Requirements |
|:----:|-----------|------------------|------------|:------------:|
| **1** | **The Awakening**<br>Recover from injuries and learn core survival skills | Ruins (Starting Zone) | Rusty Knife + 3 Potions | None |
| **2** | **First Contact**<br>Meet Leo and gather intel on the broadcast signal | Leo's Camp (Ruins) | Regional Map + Terminal Quest | Step 1 Complete |
| **3** | **Locating the Terminal**<br>Infiltrate Base Alpha and access military comms | Base Alpha (Ruins) | Voss Log + Tier 1 Key | Level ≥ 3 |
| **4** | **Decrypting the Message**<br>Recover 3 cipher fragments to pinpoint Lighthouse coordinates | Base Alpha | Tier 2 Key + Map Marker | Tier 1 Key |
| **5** | **Meeting the Factions**<br>Navigate diplomatic encounters with 3 rival factions | New Eden (Central Plains) | Faction Questline Access | Level ≥ 5 |
| **6** | **Crossing the Toxic Forest**<br>Survive bio-hazards, mutant packs, and environmental traps | Toxic Forest | Gas Mask & Hazard Gear | Level ≥ 10 |
| **7** | **Infiltrating the Lighthouse**<br>Hack defenses and defeat the Sentinel security mech boss | The Lighthouse | Reactor Core Access | Level ≥ 20 (2-Player) |
| **8** | **The Climax**<br>Confront the Prometheus AI and determine the world's fate | Lighthouse Core | Campaign Completion + Endgame | Steps 1–7 Complete |

---

#### **📖 Detailed Step Breakdown**

##### **Step 1: The Awakening**
- **Narrative**: The player awakens injured and amnesic amidst the debris of a ruined metropolis.
- **Mentor**: **Leo**, a veteran survivor, provides initial first aid and a **rusty knife**.
- **Tutorial Objectives**: Master basic movement (`WASD` / `ZQSD`), object interaction (`E`), scavenging (`F`), and evasive stealth against wandering mutants. Scavenge 3 survival essentials (food rations, potable water, defensive weapon).

##### **Step 2: First Contact**
- **Narrative**: Leo shares reports of a periodic radio broadcast and mentions an abandoned military outpost, **Base Alpha**.
- **Objectives**: Travel to Base Alpha's perimeter and establish a forward scouting position.

##### **Step 3: Locating the Terminal**
- **Narrative**: The player penetrates the outer perimeter of Base Alpha and discovers a damaged communications console.
- **Transmission**: *"The Lighthouse awaits. Coordinates: [X:500, Y:300]."*
- **Reward**: Recovers Dr. Elias Voss's personal audio log and a Tier 1 Decryption Key.

##### **Step 4: Decrypting the Message**
- **Narrative**: Complete a cipher reconstruction minigame by assembling 3 memory cores scattered across the base.
- **Outcome**: Unlocks precise navigational coordinates for the mountain summit.

##### **Step 5: Meeting the Factions**
- **Narrative**: Journey through the central plains and interact with three ideological forces:
  - **Peaceful Survivors (Hope Camp)**: Offer an escort and safe shelter in exchange for aid.
  - **Bandits (Jax's Fortress)**: Demand an expensive transit toll or combat trial.
  - **Cultists (Temple of Shadows)**: Seek to proselytize and recruit the player into their faith.

##### **Step 6: Crossing the Toxic Forest**
- **Narrative**: Traverse an extreme bio-hazard corridor filled with mutant ambushes, poisonous spores, and unstable terrain.
- **Dynamic Events**: Random mutant swarms, nomadic merchant encounters, and hidden emergency shelters.

##### **Step 7: Infiltrating the Lighthouse**
- **Narrative**: Overcome the automated defense matrix guarding the mountain stronghold.
- **Boss Encounter**: **The Sentinel** (Heavy Combat Mech). Requires cooperative tactical coordination or group composition.

##### **Step 8: The Climax**
- **Narrative**: Uncover **Prometheus**, the rogue pre-war military AI behind the 24-hour broadcast cycle.
- **The Choice**: Make a pivotal decision that permanently reshapes the game world.

---

#### **🎯 Alternative Endings**

| Ending | Alignment Title | Core Decision | World State Outcome |
|:------:|-----------------|---------------|---------------------|
| **🔵 Neutral** | *"The Truth"* | Deactivate the Lighthouse | Prometheus awakens as an open-world raid boss; chaos spreads across all biomes |
| **🟢 Good** | *"Hope"* | Amplify Signal Broadcast | Allied military reinforcements arrive; regional civilization rebuilding begins |
| **🔴 Tyrant** | *"Power"* | Hack & Commandeer the AI | Player usurps Prometheus's command network; gains unique authoritarian abilities |

---

## 3. Epic Quests

| Quest ID | Title | Level | Objectives & Narrative Impact | Key Rewards |
|:--------:|-------|:-----:|--------------------------------|-------------|
| **QE-001** | **The Fall of New Eden** | 15–25 | Aid the Militia in liberating the central city from occupying Bandits | Regional Territory Control + "Conqueror" Title |
| **QE-002** | **Dr. Voss's Legacy** | 5–15 | Recover pre-war research logs to uncover Prometheus's true genesis | Rare Scientific Gear + Secret Lab Keycard |
| **QE-003** | **The Mutant Scourge** | 20–30 | Eradicate a colossal mutant hive nest in the Radioactive Desert | Tamed Mutant Mount + Universal Faction Rep |
| **QE-004** | **The Betrayal** | 10–20 | Infiltrate Jax's Fortress to extract classified defense schematics | Stealth Camouflage Suit + Major Currency Bounty |

---

## 4. Side Quests

| Quest ID | Title | Type | Level | Objectives | Rewards | Repeatable |
|:--------:|-------|:----:|:-----:|------------|---------|:----------:|
| **QS-001** | **Bandit Hunter** | PvE | 1–5 | Eliminate 5 Bandits lurking in the Urban Ruins | 50 Gold + Health Potion | ✅ Daily |
| **QS-002** | **Medicinal Gathering** | Gathering | 1–10 | Harvest 10 medicinal herbs in the Toxic Forest | 3 Health Potions | ✅ Yes |
| **QS-003** | **Generator Repair** | Crafting | 5–15 | Restore power using scavenged generator components | Settlement Power Grid Access | ❌ No |
| **QS-004** | **Resource Convoy** | Escort | 1–20 | Transport supply cargo between survivor camps | Faction Rep + 100 Gold | ✅ Yes |
| **QS-005** | **Treasure Hunt** | Exploration | 10–25 | Decipher map clues and recover hidden ruins cache | Rare Random Equipment Loot | ✅ Yes |

---

## 5. Choice System & Consequences

### **Moral Decisions and Systemic Impact**
Player choices dynamically influence:
- **Faction Standing**: Elevating reputation with one group naturally antagonizes rivals.
- **Narrative Outcomes**: Unlocks distinct storyline branches, vendor discounts, and safehouse access.
- **Persistent World State**: Outposts can thrive, change governance, or succumb to raids.

| Decision Category | Action Taken | Immediate Consequence | Systemic Gameplay Impact |
|-------------------|--------------|-----------------------|--------------------------|
| **Aid NPC** | Administer medicine to a wounded scout | +10 Rep (Survivors) | Unlocks exclusive survivor questline |
| **Theft** | Plunder resources from an outpost pantry | -15 Rep (Survivors), +5 Rep (Bandits) | Merchant prices increase at Survivor hubs |
| **Execution** | Summary execution of a captured raider | -20 Rep (All except Cultists) | Risk of being attacked on sight by guards |
| **Rescue** | Liberate an abducted merchant | +15 Rep (Survivors / Militia) | Bonus high-grade survival gear reward |
| **Betrayal** | Leak outpost defense coordinates to enemy | -30 Rep (Betrayed), +10 Rep (Enemy) | Locked out of betrayed safehouses and shops |

---

## 6. Key Lore Elements

### **Important Characters**

| Character | Role | Primary Location | Narrative Significance |
|-----------|------|------------------|------------------------|
| **Dr. Elias Voss** | Lead Scientist | Underground Desert Lab | Pre-war researcher; central to Quest QE-002 ("Dr. Voss's Legacy") |
| **Commander Rourke** | Military Leader | The Lighthouse | Fallen garrison commander of Base Alpha; final campaign boss encounter |
| **Leo** | Veteran Survivor | Urban Ruins Outpost | Introductory mentor; guides newly awakened players through Steps 1–2 |
| **Jax** | Bandit Warlord | Jax's Fortress | Controls desert trade; central to Quest QE-004 ("The Betrayal") |
| **The Prophet** | Cult Leader | Temple of Shadows | Spiritual leader venerating the Signal as a deity; met in Step 5 |

### **Key World Locations**

| Location | Biome Region | Threat Level | Strategic Importance |
|----------|--------------|:------------:|----------------------|
| **Base Alpha** | Urban Ruins | Level 1–10 | Starting zone; contains the primary signal broadcast terminal |
| **New Eden** | Central Plains | Level 5–20 | Fortified regional capital under Militia governance |
| **Toxic Forest** | Mutated Woodland | Level 10–20 | High-hazard biome with rare medicinal flora and mutant packs |
| **Radioactive Desert** | Wasteland | Level 15–25 | Mutant hive nests and home to Jax's fortified stronghold |
| **The Lighthouse** | Frozen Peaks | Level 20–30 | Source of the daily radio broadcast; endgame campaign climax |

---

## 7. Gameplay Integration

### **Narrative Mechanics**

| Narrative Mechanic | System Function | Example Gameplay Occurrence |
|--------------------|-----------------|------------------------------|
| **Player Journal** | Automated quest and lore tracker | *"Discovered Dr. Voss's personal lab notebook in Base Alpha."* |
| **Audio Logs** | Collectible narrative recordings | Audio playback: *"Prometheus... she has betrayed us all."* |
| **Dynamic NPC Reactions** | Dialogue shifts based on faction standing | Stealing from Leo causes him to refuse future interactions. |
| **Dynamic World Events** | Ambient combat encounters and hazards | *"A Nomadic trade caravan is under siege by Bandits!"* |
| **Intel & Rumor System** | Coordinate trading for gold/favors | A Bandit reveals a hidden weapons cache for 100 gold. |

### **Narrative Rewards**

| Reward Category | Example Unlock | Systemic Value & Gameplay Utility |
|-----------------|----------------|-----------------------------------|
| **Lore Relics** | Dr. Voss's Lab Notebook | Unlocks classified dialogue trees with scholars and scientists |
| **Prestige Titles** | *"Signal Decryptor"* | Cosmetic title granting a +5% trading discount with factions |
| **Access Keycards** | Dr. Voss's Laboratory Card | Grants entrance to high-tier prototype crafting chambers |
| **Hidden Questlines** | EMP Truth Investigation | Unlocks exclusive story lore and rare weapon modifications |

---

## 📚 Related Documents

- [🎮 Game Design Document](README_ENG.md)
- [🌍 Universe](02_UNIVERS_ENG.md)
- [📜 Scenario & Quests](03_SCENARIO_ENG.md)
- [🗺 Chronology](04_CHRONOLOGIE_ENG.md)
- [⚔️ Factions](05_FACTIONS_ENG.md)
- [👾 Monsters](18_MONSTRES_ENG.md)
- [👹 Bosses](19_BOSS_ENG.md)
- [🏰 Guilds](36_GUILDES_ENG.md)

---

## Navigation

⬅️ [Universe](02_UNIVERS_ENG.md)

➡️ [Chronology](04_CHRONOLOGIE_ENG.md)

---

> **The Last Signal** — *"The mystery of the Lighthouse awaits."* 🚀


----
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />
