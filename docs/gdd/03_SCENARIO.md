[🏠 Documentation](../README.md) > [🎮 GDD](README.md)

# 🎭 **SCÉNARIOS & QUÊTES - The Last Signal**
> *Game Design Document - Version 1.0*
> **Dernière mise à jour** : 16/07/2026
> **Auteur** : Cyril
> **Statut** : 🟡 **En développement (80% complet - Scénario principal terminé)**

---

## 📌 **Sommaire**
1. [Contexte Global](#-contexte-global)
2. [Scénarios Principaux](#-scénarios-principaux)
3. [Quêtes Épiques](#-quêtes-épiques)
4. [Quêtes Secondaires](#-quêtes-secondaires)
5. [Système de Choix](#-système-de-choix)
6. [Éléments Clés du Lore](#-éléments-clés-du-lore)
7. [Intégration avec le Gameplay](#-intégration-avec-le-gameplay)

---

---
## 🌍 **1. Contexte Global**

### **Le Monde de The Last Signal**
En **2045**, une **impulsion électromagnétique (EMP) mondiale** a détruit toute technologie électronique, plongeant l’humanité dans le chaos.
**30 ans plus tard (2075)**, les survivants tentent de reconstruire un monde dans les ruines de l’ancienne civilisation.
Un **signal radio mystérieux** est émis toutes les **24 heures** par une ancienne infrastructure militaire : **"Le Phare"**.

### **L’Enjeu Principal**
- **Pour les optimistes** : Le signal pourrait être un **appel à l’aide** ou une **solution pour reconstruire**.
- **Pour les paranoïaques** : Ce pourrait être un **piège** ou un **message de mort**.
- **Pour les cultistes** : C’est la **voix d’une entité divine** (l’IA Prométhée).

> **Note** : Ce contexte est lié à [`02_UNIVERS.md`](02_UNIVERS.md) et [`04_CHRONOLOGIE.md`](04_CHRONOLOGIE.md).

---

---
## 🎬 **2. Scénarios Principaux**

---
### **🔴 Scénario Principal : "Le Mystère du Phare"**
**Type** : Quête obligatoire (fin du jeu).
**Durée estimée** : 15-20 heures.
**Niveau recommandé** : 1 → 30.

#### **📌 Résumé**
Le joueur, un survivant sans mémoire, découvre un **terminal militaire** dans les ruines de la **Base Alpha**.
En l’activant, il déclenche une **quête pour comprendre l’origine du signal** et atteindre **Le Phare**, la source du mystère.

---

#### **📋 Étapes Clés**
   Étape | Titre | Description | Lieu | Récompense | Conditions |
 |-------|-------|-------------|------|------------|------------|
 | **1** | **Le Réveil** | Le joueur se réveille dans les **ruines d’une ancienne ville**, blessé et sans souvenir. Un **PNJ nommé Léo** (survivant) lui offre un **couteau rouillé** et explique les bases : **déplacement (ZQSD)**, **interaction (E)**, **ramassage (F)**, **éviter les mutants**. **Tutoriel** : Trouver 3 objets (nourriture, eau, arme) pour survivre. | **Ruines (Zone de départ)** | Couteau rouillé + 3 potions de soin | Aucun |
 | **2** | **Premier Contact** | Léo mentionne un **signal radio étrange** et une **base militaire abandonnée** (Base Alpha). Il demande au joueur de **trouver des informations** sur ce signal. | **Campement de Léo (Ruines)** | Carte des alentours + Quête "Trouver le Terminal" | Avoir terminé le tutoriel |
 | **3** | **Trouver le Terminal** | Le joueur explore la **Base Alpha** et découvre un **terminal militaire endommagé**. En l’activant, il reçoit un **message crypté** : *"Le Phare vous attend. Coordonnées : [X:500, Y:300]."* | **Base Alpha (Ruines)** | Journal du Dr. Elias Voss + Clé de décryptage (niveau 1) | Niveau ≥ 3 |
 | **4** | **Décrypter le Message** | Le joueur doit **trouver 3 fragments de code** (cachés dans la Base Alpha) pour décrypter le message. **Mini-jeu** : Puzzle de type "assembler les morceaux". | **Base Alpha** | Clé de décryptage (niveau 2) + Localisation du Phare sur la carte | Avoir la Clé de décryptage (niveau 1) |
 | **5** | **Rencontrer les Factions** | En route vers le Phare, le joueur croise **3 factions** :
- **Les Survivants Pacifiques** (Campement de l’Espoir) → Proposent une **escorte**.
- **Les Bandits** (Forteresse de Jax) → Exigent un **paiement** pour passer.
- **Les Cultistes** (Temple des Ombres) → Veulent **recruter** le joueur. | **New Eden (Plaine Centrale)** | Accès aux quêtes de faction | Niveau ≥ 5 |
 | **6** | **Traversée de la Forêt Toxique** | Le joueur doit traverser un **biome dangereux** (plantes toxiques, mutants, pièges). **Événements aléatoires** :
- Attaque de mutants.
- Rencontre avec un **marchand nomade** (ressources).
- Découverte d’un **abri caché** (soin + sauvegarde). | **Forêt Toxique** | Équipement de survie (masque à gaz) | Niveau ≥ 10 |
 | **7** | **Infiltration du Phare** | Le Phare est **gardé par des robots** et des **mutants**. Le joueur doit :
1. **Désactiver les tourelles** (mini-jeu de hack).
2. **Affronter le Gardien** (boss : robot de sécurité).
3. **Trouver l’entrée du cœur**. | **Phare (Montagnes Gelées)** | Accès au cœur du Phare | Niveau ≥ 20 + Groupe de 2 joueurs |
 | **8** | **Révélation Finale** | Le joueur découvre que le signal est émis par **Prométhée**, une **IA militaire** devenue incontrôlable. **3 choix** :
- **Désactiver le Phare** → Fin "Chaos" (Prométhée se réveille).
- **Amplifier le Signal** → Fin "Espoir" (renforts militaires arrivent).
- **Pirater le Phare** → Fin "Pouvoir" (le joueur prend le contrôle). | **Cœur du Phare** | **Fin du jeu** + Déblocage du Mode Post-Générique | Avoir terminé toutes les étapes |

---

#### **🎯 Fins Alternatives**
 | Fin | Titre | Description | Conséquences |
 |-----|-------|-------------|---------------|
 | **🔵 Fin Neutre** | *"La Vérité"* | Le joueur **désactive le Phare**. Prométhée se réveille et **devient un boss mondial** (tous les joueurs doivent l’affronter). | Monde en chaos, nouveaux ennemis, quêtes post-générique. |
 | **🟢 Fin Bonne** | *"L’Espoir"* | Le joueur **amplifie le signal**, attirant des **renforts militaires** (PNJ alliés). La reconstruction commence. | Monde plus paisible, nouvelles quêtes de reconstruction. |
 | **🔴 Fin Mauvais** | *"Le Pouvoir"* | Le joueur **pirate le Phare** et prend le contrôle de Prométhée. | Le joueur devient un **leader** (ou un tyran), avec des **pouvoirs spéciaux**. |

---

---
## 🏆 **3. Quêtes Épiques** *(Optionnelles mais majeures)*
 | ID | Titre | Description | Niveau | Récompense | Lien avec le Scénario |
 |----|-------|-------------|--------|------------|-----------------------|
 | **QE-001** | **La Chute de New Eden** | Aider les **Miliciens** à reprendre le contrôle de la ville aux **Bandits**. | 15-25 | Territoire + Titre "Conquérant" | Renforce l’influence des Miliciens. |
 | **QE-002** | **L’Héritage du Dr. Voss** | Retracer les pas du **Dr. Elias Voss** (scientifique ayant étudié le signal) à travers ses **journaux et enregistrements**. | 5-15 | Équipement scientifique rare + Accès au laboratoire secret | Lore : Comprendre l’origine de Prométhée. |
 | **QE-003** | **Le Fléau des Mutants** | Éliminer un **nid de mutants** dans le **Désert Radioactif**. | 20-30 | Monture mutante + Réputation avec toutes les factions | Réduit les attaques de mutants dans le monde. |
 | **QE-004** | **La Trahison** | Infiltrer la **Forteresse de Jax** (Bandits) pour voler des **plans secrets**. | 10-20 | Équipement de camouflage + Récompense en monnaie | Affecte les relations avec les Bandits. |

---
---
## 🎯 **4. Quêtes Secondaires** *(Courtes et répétables)*
 | ID | Titre | Type | Description | Niveau | Récompense | Répétable ? |
 |----|-------|------|-------------|--------|------------|-------------|
 | **QS-001** | **Chasseur de Bandits** | PvE | Éliminer **5 Bandits** dans les Ruines. | 1-5 | 50 pièces d’or + Potion de soin | ✅ Oui (toutes les 24h) |
 | **QS-002** | **Récolte de Plantes Médicinales** | Exploration | Trouver **10 plantes** dans la Forêt Toxique. | 1-10 | 3 Potions de soin | ✅ Oui |
 | **QS-003** | **Réparation du Générateur** | Craft | Réparer un **générateur électrique** avec des pièces trouvées. | 5-15 | Accès à l’électricité dans le campement | ❌ Non |
 | **QS-004** | **Livraison de Ressources** | Logistique | Transporter des **ressources** d’un campement à un autre. | 1-20 | Réputation + 100 pièces d’or | ✅ Oui |
 | **QS-005** | **Chasse aux Trésors** | Exploration | Trouver un **coffre caché** dans les Ruines. | 10-25 | Objet aléatoire rare | ✅ Oui |

---
---
## 🔄 **5. Système de Choix**

### **Choix Moraux et Conséquences**
Chaque décision du joueur affecte :
- **Sa réputation** avec les factions.
- **L’histoire** (fins alternatives).
- **Le monde** (ex: une ville peut être détruite ou sauvée).
 | Choix | Exemple | Conséquence | Impact sur le Gameplay |
 |-------|---------|--------------|-----------------------|
 | **Aider un PNJ** | Soigner un blessé. | +10 Réputation (Survivants) | Accès à des quêtes exclusives. |
 | **Voler un PNJ** | Prendre ses ressources. | -15 Réputation (Survivants), +5 Réputation (Bandits) | Prix plus élevés chez les Survivants. |
 | **Tuer un prisonnier** | Exécution sommaire. | -20 Réputation (toutes factions sauf Cultistes) | Risque d’être attaqué à vue. |
 | **Libérer un prisonnier** | Sauver un otage. | +15 Réputation (Survivants/Miliciens) | Récompense en équipement. |
 | **Trahir une faction** | Donner des infos à l’ennemi. | -30 Réputation (faction trahie), +10 Réputation (ennemi) | Quêtes bloquées avec la faction trahie. |

---
---
## 📜 **6. Éléments Clés du Lore**

### **Personnages Importants**
 | Nom | Rôle | Description | Localisation | Lien avec le Scénario |
 |-----|------|-------------|--------------|-----------------------|
 | **Dr. Elias Voss** | Scientifique | A étudié le signal avant l’EMP. Ses **journaux** sont disséminés dans le monde. | Laboratoire souterrain (Désert) | Quête QE-002 ("L’Héritage du Dr. Voss"). |
 | **Commandant Rourke** | Militaire | Dernier commandant de la **Base Alpha**. Devenu fou après l’EMP. | Phare (Boss final) | Scénario principal (étape 8). |
 | **Léo** | Survivant | PNJ d’introduction. Guide le joueur au début. | Campement (Ruines) | Scénario principal (étape 1-2). |
 | **Jax** | Chef des Bandits | Contrôle les **ressources** dans le Désert Radioactif. | Forteresse de Jax | Quête QE-004 ("La Trahison"). |
 | **Le Prophète** | Chef des Cultistes | Croit que le signal est un **message divin**. | Temple des Ombres (Montagnes) | Scénario principal (étape 5). |

### **Lieux Clés**
 | Lieu | Biome | Importance | Niveau Recommandé |
 |------|-------|------------|-------------------|
 | **Base Alpha** | Ruines | Point de départ, terminal du signal. | 1-10 |
 | **New Eden** | Plaine Centrale | Ville fortifiée, contrôlée par les Miliciens. | 5-20 |
 | **Forêt Toxique** | Forêt | Biome dangereux, ressources rares. | 10-20 |
 | **Désert Radioactif** | Désert | Nid de mutants, Forteresse de Jax. | 15-25 |
 | **Le Phare** | Montagnes Gelées | Source du signal, fin du jeu. | 20-30 |

---
---
## 🎮 **7. Intégration avec le Gameplay**

### **Mécaniques Narratives**
 | Mécanique | Description | Exemple |
 |-----------|-------------|---------|
 | **Journal du Joueur** | Notes automatiques sur les quêtes et découvertes. | "J’ai trouvé le Journal du Dr. Voss dans la Base Alpha." |
 | **Enregistrements Audio** | Fichiers sonores à trouver pour le lore. | Enregistrement du Dr. Voss : *"Prométhée... elle nous a trahis."* |
 | **PNJ Dynamiques** | Les PNJ réagissent aux choix du joueur. | Si le joueur vole Léo, il ne lui parlera plus. |
 | **Événements Aléatoires** | Attaques, caravanes, tempêtes. | "Une caravane de Nomades est attaquée par des Bandits !" |
 | **Système de Rumeurs** | Les PNJ partagent des infos selon la réputation. | Un Bandit révèle l’emplacement d’un trésor... pour 100 pièces. |

### **Récompenses Narratives**
 | Type | Exemple | Utilité |
 |------|---------|---------|
 | **Objets de Lore** | Journal du Dr. Voss | Déblocage de dialogues secrets. |
 | **Titres** | "Décrypteur du Signal" | Prestige + Bonus de réputation. |
 | **Accès à des Zones Secrètes** | Laboratoire du Dr. Voss | Équipements uniques. |
 | **Quêtes Cachées** | La Vérité sur l’EMP | Lore supplémentaire. |

---
## 📚 Documents liés

- [🎮 Game Design Document](README.md)
- [🌍 Univers](02_UNIVERS.md)
- [📜 Scénario](03_SCENARIO.md)
- [Chronologie](04_CHRONOLOGIE.md)
- [Factions du jeu](05_FACTION.md)
- [Mobs](18_MONSTRES.md)
- [Boss](19_BOSS.md)
- [Guildes](36_GUILDES.md)
---

## Navigation

⬅️ [Retour au GDD](README.md)

➡️ [Chronologie](04_CHRONOLOGIE.md)


---

> **The Last Signal** — *"Le mystère du Phare vous attend."* 🚀


----
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />
