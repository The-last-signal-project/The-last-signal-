# 🎮 The Last Signal

<img width="1408" height="768" alt="The Last Signal" src="https://github.com/user-attachments/assets/b8f7d28b-d2b1-4b1b-96b1-6382d06b9b5d" />

## 🌐 README languages

🇫🇷 **Français** — You are currently viewing the French version.<br>
🇬🇧 **English** — [English version](README_ENG.md)<br>
🇪🇸 **Español** — [Spanish version](README_ESP.md)<br>
🇯🇵 **日本語** — [Japanese version](README_JP.md)

> **MMORPG de survie post-apocalyptique en monde persistant.**

![Status](https://img.shields.io/badge/status-prototype-orange)
![Documentation](https://img.shields.io/badge/docs-active-blue)
![Python](https://img.shields.io/badge/client-Python-yellow)
![Rust](https://img.shields.io/badge/server-Rust-orange)

---

# 🎮 Le projet en quelques mots

**The Last Signal Online** est un MMORPG de survie dans un monde post-apocalyptique persistant.

Le projet combine :

* 🌍 un monde persistant ;
* 👥 plusieurs joueurs évoluant dans le même monde ;
* ⚔️ des combats PvE et PvP ;
* 🏰 des guildes et territoires ;
* 💰 une économie dirigée par les joueurs ;
* 🛠️ un système d'artisanat ;
* 📖 une histoire évolutive ;
* 🔎 de l'exploration et de la découverte.

Le projet est actuellement en **phase de prototype**.

Le prototype permet déjà de :

* 🎮 lancer le client ;
* 🌐 se connecter à un serveur local ;
* 🧭 se déplacer dans le monde ;
* 👥 voir les autres joueurs connectés ;
* 🧪 tester progressivement les systèmes du jeu.

> 💡 **Le projet est encore jeune : les contributeurs peuvent donc réellement influencer sa construction.**

Le serveur public n'est pas encore disponible. Pour le moment, le serveur de jeu fonctionne localement sur la machine du développeur ou du contributeur.

---

# 🚀 Pourquoi contribuer ?

The Last Signal est développé comme un véritable projet open source.

Les contributions peuvent concerner :

* 🦀 **Rust** — serveur ;
* 🐍 **Python** — client ;
* 🌐 **Réseau** — communication client/serveur et protocoles ;
* 🧪 **Tests** — tests unitaires et d'intégration ;
* 🔐 **Sécurité** ;
* ⚙️ **CI/CD** ;
* 📚 **Documentation** ;
* 🌍 **Traductions** ;
* 🎮 **Gameplay** ;
* 🔧 **Outils de développement**.

Vous n'avez **pas besoin de comprendre tout le projet** pour contribuer.

Une première contribution peut être très petite.

---

# ⚡ Contribuer en 10–20 minutes

Vous voulez découvrir le projet sans passer une heure à comprendre son architecture ?

Commencez par une petite amélioration.

### 🧪 Ajouter un test

Trouvez une fonction ou un système existant dans `tests/` et ajoutez **un cas de test simple et ciblé**.

**Objectif :** ajouter un seul test utile.

### 📚 Améliorer la documentation

Trouvez une explication :

* incomplète ;
* ambiguë ;
* difficile à comprendre ;
* ou qui pourrait être plus claire.

Proposez une correction ciblée.

**Objectif :** améliorer une petite partie de la documentation.

### 🌍 Améliorer une traduction

Corrigez une traduction existante ou complétez une petite partie d'un document.

**Objectif :** améliorer un passage précis sans modifier le fonctionnement du projet.

### 🔧 Comment procéder ?

1. Choisissez **une seule petite amélioration**.
2. Consultez les [Issues ouvertes](../../issues).
3. Si vous avez un doute, posez votre question dans l'issue concernée ou dans les [Discussions](../../discussions).
4. Faites votre modification.
5. Testez-la lorsque cela est nécessaire.
6. Ouvrez une Pull Request.

> ⭐ **Vous n'avez pas besoin de connaître toute l'architecture avant votre première contribution.**
>
> Une petite correction est déjà une vraie contribution.

---

# 🧪 Tester le prototype

Le serveur fonctionne actuellement **en local**.

## 📋 Prérequis

Vous devez disposer de :

* 🐍 **Python 3.14**
* 🦀 **Rust et Cargo**
* 🌿 **Git**

---

## 📥 1. Cloner le dépôt

```bash
git clone https://github.com/DDCoder23/The-last-signal-.git
cd The-last-signal-
```

---

## 🐍 2. Installer les dépendances Python

Depuis la racine du projet :

```bash
pip install -r requirements.txt
```

---

## 🦀 3. Lancer le serveur Rust

Ouvrez un premier terminal et placez-vous dans le dossier du serveur :

```bash
cd server_rust
```

Puis lancez :

```bash
cargo run --locked
```

Laissez le serveur fonctionner dans ce terminal.

### 🧹 Compilation propre — optionnelle

`cargo clean` n'est **pas nécessaire à chaque lancement**.

Pour repartir d'une compilation propre :

```bash
cargo clean
cargo run --locked
```

---

## 🎮 4. Lancer le client

Ouvrez un deuxième terminal et revenez à la racine du projet :

```bash
cd The-last-signal-
```

Puis lancez :

```bash
python -m client_python.main
```

Le client se connectera alors au serveur local.

---

# 🌐 Architecture actuelle

Le prototype utilise actuellement une architecture client/serveur locale :

```text
┌─────────────────────────┐
│      Client Python      │
│         🎮 Jeu          │
└────────────┬────────────┘
             │
             │ Réseau
             ▼
┌─────────────────────────┐
│       Serveur Rust      │
│    🦀 Serveur de jeu    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│         SQLite          │
│       🗄️ Données       │
└─────────────────────────┘
```

> 🌐 **Serveur public : pas encore disponible.**
>
> Chaque contributeur peut actuellement lancer son propre serveur local pour développer et tester le projet.

---

# 🤝 Contribuer au projet

The Last Signal accueille les contributions de :

* 👨‍💻 développeurs ;
* 🧪 testeurs ;
* 📚 rédacteurs ;
* 🌍 traducteurs ;
* 🎮 passionnés de game development ;
* 🔐 personnes intéressées par la sécurité ;
* 🔧 contributeurs souhaitant améliorer les outils du projet.

Vous pouvez commencer sans connaître l'ensemble du code.

## 🟢 Vous débutez ?

Les meilleures premières contributions sont généralement :

* 🧪 ajouter ou améliorer un test ;
* 🐛 corriger un problème simple ;
* 📚 améliorer la documentation ;
* 🌍 améliorer une traduction ;
* 🔧 améliorer un outil ;
* 📝 améliorer la qualité du code.

➡️ [Consulter les Issues ouvertes](../../issues)

➡️ [Participer aux Discussions](../../discussions)

---

# 🛠️ Domaines de contribution

| Domaine          | Technologie / contenu                 |
| ---------------- | ------------------------------------- |
| 🦀 Serveur       | Rust                                  |
| 🐍 Client        | Python                                |
| 🌐 Réseau        | Protocoles client/serveur             |
| 🧪 Tests         | Unitaires et intégration              |
| 🔐 Sécurité      | Authentification et cryptographie     |
| ⚙️ CI/CD         | GitHub Actions et automatisation      |
| 📚 Documentation | Guides et documentation technique     |
| 🌍 Traductions   | Français, anglais, espagnol, japonais |
| 🎮 Gameplay      | Systèmes et fonctionnalités           |
| 🔧 Outils        | Scripts et outils de développement    |

---

# 🟢 Votre première contribution

Vous pouvez choisir une tâche en fonction de votre expérience.

| Niveau                | Durée indicative | Exemple                                         |
| --------------------- | ---------------: | ----------------------------------------------- |
| 🟢 Micro-contribution |    **10–20 min** | Petit test, correction documentaire, traduction |
| 🟢 Facile             |        20–40 min | Test supplémentaire, correction simple          |
| 🟡 Intermédiaire      |            1–2 h | Validation, amélioration de tests               |
| 🟠 Avancé             |            2–4 h | Fonctionnalité client/serveur                   |

Pour commencer, recherchez de préférence une issue marquée **`good first issue`**.

Une bonne issue doit permettre de comprendre :

* 🎯 ce qui doit être réalisé ;
* 📂 quelles parties du projet sont concernées ;
* 🧪 comment vérifier la modification ;
* ✅ quels critères permettent de considérer la tâche comme terminée.

---

# 🔁 Après votre première contribution

Une première Pull Request ne doit pas forcément être la dernière.

## 💬 Votre retour nous aide

Après votre contribution, vous pouvez laisser un commentaire sur l'issue associée.

Indiquez par exemple :

* 💬 ce qui était clair ou difficile ;
* 🧩 les informations qui vous ont manqué ;
* 🐛 les problèmes rencontrés ;
* 💡 ce qui pourrait être amélioré ;
* 📚 les éléments de documentation qui pourraient être plus clairs.

> 💡 **Même si vous ne continuez pas immédiatement, votre feedback aide à améliorer le projet pour les prochains contributeurs.**

## 🚀 Continuer progressivement

Vous pouvez ensuite approfondir progressivement le domaine que vous venez de découvrir.

Par exemple :

```text
🧪 Test simple
      ↓
🧪 Cas limites
      ↓
🌐 Tests réseau
      ↓
🔧 Validation des données
      ↓
🎮 Fonctionnalité client/serveur
```

Vous n'avez pas besoin de passer directement à une grosse fonctionnalité.

> ⭐ **Commencez petit → contribuez → donnez votre feedback → revenez sur une tâche un peu plus ambitieuse.**

---

# 📐 Règles de contribution

Avant de proposer une modification :

* 📐 respectez les conventions du projet ;
* 📚 documentez les nouvelles fonctionnalités lorsque nécessaire ;
* 🧪 testez vos modifications ;
* 🌿 utilisez une branche Git dédiée ;
* 📝 décrivez clairement vos changements dans la Pull Request.

Consultez également :

➡️ [📜 Règles de développement](docs/CODING_RULES.md)

➡️ [📖 Documentation](docs/README.md)

---

# 🌍 Univers

Après un événement mystérieux ayant bouleversé la civilisation, les derniers survivants tentent de reconstruire un monde nouveau tout en découvrant l'origine du dernier signal émis par une ancienne infrastructure oubliée.

Le projet vise à créer un monde dans lequel les joueurs peuvent :

* 🌍 explorer un monde persistant ;
* 👥 rencontrer d'autres joueurs ;
* ⚔️ combattre ;
* 🏰 créer des groupes et contrôler des territoires ;
* 💰 participer à une économie dirigée par les joueurs ;
* 🛠️ fabriquer et utiliser des objets ;
* 📖 découvrir une histoire évolutive ;
* 🔎 explorer et découvrir le monde.

---

# 🚀 Vision du projet

L'objectif de **The Last Signal Online** est de créer un MMORPG indépendant proposant :

* 🌍 un univers riche et cohérent ;
* 👥 une forte interaction entre les joueurs ;
* 🌎 des choix ayant un impact sur le monde ;
* 🧭 une progression libre ;
* 🏗️ une architecture capable d'évoluer sur le long terme.

Le développement s'appuie notamment sur :

* 📚 une documentation structurée ;
* 🏗️ une architecture pensée avant développement ;
* 🔄 l'intégration continue ;
* 🧪 des tests automatisés ;
* 📊 un suivi de la qualité du code.

---

# 🛠️ Technologies

## 🎮 Client

| Technologie | Utilisation           |
| ----------- | --------------------- |
| 🐍 Python   | Client principal      |
| 🎨 VisPy    | Rendu graphique       |
| 🖥️ PySide6 | Interface utilisateur |

## 🌐 Serveur

| Technologie   | Utilisation                  |
| ------------- | ---------------------------- |
| 🦀 Rust       | Serveur multijoueur          |
| 🌐 Networking | Communication client/serveur |
| 🗄️ SQLite    | Base de données              |

---

# 📂 Organisation du projet

```text
The-last-signal/
│
├── client_python/          # Client du jeu
├── server_rust/            # Serveur Rust
├── database/               # Scripts de base de données
├── assets/                 # Ressources graphiques et audio
│
├── docs/                   # Documentation
│   ├── gdd/                # Game Design Document
│   ├── tdd/                # Technical Design Document
│   └── ...
│
├── scripts/                # Outils de développement
├── tests/                  # Tests automatisés
│
├── README.md
└── LICENSE
```

---

# 📚 Documentation

La documentation complète est disponible ici :

➡️ [📖 Documentation officielle](docs/README.md)

Elle contient notamment :

* 🎮 Game Design Document (GDD) ;
* 🏗️ Technical Design Document (TDD) ;
* 🌍 lore du monde ;
* ⚔️ gameplay ;
* 🌐 architecture réseau ;
* 🗄️ structure des données ;
* 📅 roadmap.

---

# 📊 État du projet

| Module              |         État        |
| ------------------- | :-----------------: |
| 📚 Documentation    | 🟡 En développement |
| 🎮 Client Python    | 🟡 En développement |
| 🦀 Serveur Rust     | 🟡 En développement |
| 🌐 Réseau           | 🟡 En développement |
| 🗄️ Base de données | 🟡 En développement |
| 🎨 Assets           |    🟡 Préparation   |
| 🎮 Gameplay         |     🟢 Prototype    |
| 🌍 Univers          |     🟢 Prototype    |

### Légende

* 🟢 Fonctionnel / prototype
* 🟡 En développement
* ⚪ Prévu

---

# 🏗️ Architecture du développement

Le projet suit une organisation inspirée du développement logiciel professionnel :

```text
Conception
    ↓
Documentation
    ↓
Prototype
    ↓
Tests
    ↓
Développement
    ↓
Optimisation
```

Les fonctionnalités importantes doivent être documentées, testées et pensées avant leur évolution.

---

# ❓ FAQ

Vous avez une question sur le projet ?

➡️ [❓ Consulter la FAQ](docs/FAQ.md)

Vous pouvez également poser une question dans :

➡️ [💬 GitHub Discussions](../../discussions)

---

# 🎮 Commandes du jeu

Consultez :

➡️ [🎮 Commandes](touches_de_commandes)

---

# 📅 Roadmap

Consultez :

➡️ [📅 Roadmap](docs/ROADMAP.md)

---

# 👥 Équipe

| Nom          | Fonction                                  |
| ------------ | ----------------------------------------- |
| Morgan Piva  | Directeur                                 |
| Cyril Capiez | Directeur adjoint & Développeur principal |

---

# 📜 Licence

➡️ [📜 Licence](LICENSE)

---

<img width="1024" height="559" alt="The Last Signal" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />

> **The Last Signal — Quand le monde disparaît, un dernier signal demeure.**
