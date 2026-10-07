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

## 🎮 État actuel du projet

**The Last Signal Online est actuellement en phase de prototype.**

Le prototype actuel permet notamment de :

* 🎮 lancer le client du jeu ;
* 🌐 se connecter à un serveur local ;
* 🧭 se déplacer dans le monde ;
* 👥 voir les autres joueurs connectés ;
* 🧪 tester progressivement les systèmes du jeu.

Le serveur de jeu fonctionne actuellement **en local**. Un serveur public accessible depuis Internet n'est pas encore disponible.

Le jeu complet est encore en développement. Plusieurs systèmes importants seront progressivement ajoutés et améliorés.

> 💡 **Le projet est encore suffisamment jeune pour que les contributions puissent réellement influencer son évolution.**

---

## 🚀 Pourquoi contribuer maintenant ?

The Last Signal n'est pas un projet terminé.

C'est justement ce qui permet aux contributeurs de participer directement à sa construction.

Les contributions peuvent actuellement concerner :

* 🦀 le serveur Rust ;
* 🐍 le client Python ;
* 🌐 le réseau et les protocoles ;
* 🧪 les tests ;
* 🔐 la sécurité ;
* ⚙️ la CI/CD ;
* 📚 la documentation ;
* 🎮 le prototype et le gameplay ;
* 🔧 les outils de développement.

Vous n'avez **pas besoin de connaître tout le projet** pour commencer.

Une petite contribution permet de découvrir progressivement l'architecture et le fonctionnement du projet.

---

# 🧪 Tester le prototype

Le serveur de jeu fonctionne actuellement **en local**.

Pour tester le prototype, vous devez installer Python, Rust et les dépendances du projet.

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

Depuis la **racine du projet** :

```bash
pip install -r requirements.txt
```

---

## 🦀 3. Lancer le serveur Rust

Ouvrez un premier terminal et placez-vous dans le dossier du serveur :

```bash
cd server_rust
```

Puis lancez le serveur :

```bash
cargo run --locked
```

### 🧹 Compilation propre — optionnelle

`cargo clean` n'est **pas nécessaire à chaque lancement**.

Si vous souhaitez repartir d'une compilation propre :

```bash
cargo clean
cargo run --locked
```

Laissez le serveur fonctionner dans ce terminal.

---

## 🎮 4. Lancer le client

Ouvrez un **deuxième terminal** et revenez à la racine du projet :

```bash
cd The-last-signal-
```

Puis lancez le client :

```bash
python -m client_python.main
```

Le client se connectera alors au serveur local.

---

## 🌐 Architecture actuelle

Le fonctionnement actuel est basé sur une architecture client/serveur locale :

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
> Pour le moment, chaque contributeur peut lancer son propre serveur local afin de tester et développer le projet.

---

# 🤝 Contribuer

**The Last Signal** est un projet open source et accueille les contributions de développeurs, testeurs, rédacteurs, traducteurs et autres participants intéressés.

## 🟢 Vous débutez ?

Vous n'avez pas besoin de maîtriser l'ensemble du projet.

Vous pouvez commencer par :

* 🧪 ajouter ou améliorer un test ;
* 🐛 corriger un problème simple ;
* 📚 améliorer la documentation ;
* 🌍 améliorer une traduction ;
* 🔧 améliorer un outil de développement ;
* 📝 améliorer la qualité du code.

➡️ [Consulter les Issues ouvertes](../../issues)

---

## 🛠️ Vous êtes développeur ?

Les contributions sont particulièrement recherchées dans :

* 🦀 **Rust** — serveur ;
* 🐍 **Python** — client ;
* 🌐 **Réseau** — communication client/serveur et protocoles ;
* 🧪 **Tests** — tests unitaires et d'intégration ;
* 🔐 **Sécurité** ;
* ⚙️ **CI/CD** ;
* 📚 **Documentation**.

---

# 🟢 Votre première contribution

Vous pouvez choisir une tâche adaptée à votre expérience et au temps que vous souhaitez consacrer au projet.

| Niveau           | Durée indicative | Exemples                                      |
| ---------------- | ---------------: | --------------------------------------------- |
| 🟢 Facile        |        20–40 min | Ajouter un test, corriger la documentation    |
| 🟡 Intermédiaire |            1–2 h | Améliorer une validation, compléter des tests |
| 🟠 Avancé        |            2–4 h | Modifier une fonctionnalité client/serveur    |

➡️ Commencez de préférence par une issue marquée **`good first issue`**.

Une bonne issue doit permettre de comprendre :

* 🎯 ce qui doit être réalisé ;
* 📂 quelles parties du projet sont concernées ;
* 🧪 comment vérifier la modification ;
* ✅ quels critères permettent de considérer la tâche comme terminée.

---

# 🔁 Vous avez terminé votre première contribution ?

Une première Pull Request ne doit pas forcément être la dernière.

## 💬 Donnez votre feedback

Après avoir terminé votre contribution, **n'hésitez pas à laisser un feedback directement sur l'issue associée**.

Vous pouvez notamment indiquer :

* 💬 ce qui était clair ou difficile à comprendre ;
* 🧩 les informations qui vous ont manqué ;
* 🐛 les problèmes rencontrés pendant le développement ;
* 💡 vos suggestions pour améliorer l'issue ;
* 📚 les éléments de documentation qui pourraient être améliorés.

**Votre feedback permet d'améliorer les prochaines issues et de rendre les contributions plus accessibles aux futurs contributeurs.**

> 💡 Même si vous ne souhaitez pas continuer immédiatement sur une autre tâche, votre feedback reste une contribution utile au projet.

## 🚀 Continuer après une première contribution

Après une première contribution, vous pouvez continuer avec une tâche liée au domaine que vous venez de découvrir.

Par exemple :

```text
🧪 Tests Packet
       ↓
🧪 Cas invalides
       ↓
🌐 Tests réseau
       ↓
🔧 Validation des données
       ↓
🎮 Fonctionnalité client/serveur
```

Cette progression permet de découvrir progressivement le projet sans devoir comprendre toute l'architecture dès la première contribution.

> ⭐ **Commencez petit, donnez votre feedback, puis prenez progressivement des tâches plus importantes.**

---

# 📐 Règles de contribution

Avant de proposer une modification :

* 📐 respectez les conventions du projet ;
* 📚 documentez les nouvelles fonctionnalités lorsque cela est nécessaire ;
* 🧪 testez vos modifications ;
* 🌿 utilisez une branche Git dédiée pour chaque modification ;
* 📝 décrivez clairement vos changements dans votre Pull Request.

Avant de contribuer, consultez :

➡️ [📜 Règles de développement](docs/CODING_RULES.md)

➡️ [📖 Documentation](docs/README.md)

---

# 🌍 Présentation

**The Last Signal Online** est un MMORPG de survie dans un monde post-apocalyptique persistant.

Après un événement mystérieux ayant bouleversé la civilisation, les derniers survivants tentent de reconstruire un monde nouveau tout en découvrant l'origine du dernier signal émis par une ancienne infrastructure oubliée.

Le projet vise à créer une expérience multijoueur combinant :

* 🌍 un monde persistant ;
* 👥 des joueurs évoluant dans un même monde ;
* ⚔️ des combats PvE et PvP ;
* 🏰 des guildes et territoires ;
* 💰 une économie dirigée par les joueurs ;
* 🛠️ un système d'artisanat ;
* 📖 une histoire évolutive ;
* 🔎 de l'exploration et de la découverte.

---

# 🚀 Vision du projet

L'objectif de **The Last Signal Online** est de créer un MMORPG indépendant proposant :

* 🌍 un univers riche et cohérent ;
* 👥 une forte interaction entre les joueurs ;
* 🌎 des choix ayant un impact sur le monde ;
* 🧭 une progression libre ;
* 🏗️ une architecture capable d'évoluer sur le long terme.

Le projet est développé avec une approche inspirée du fonctionnement des studios professionnels :

* 📚 documentation structurée ;
* 🏗️ architecture pensée avant développement ;
* 🔄 intégration continue ;
* 🧪 tests automatisés ;
* 📊 suivi de la qualité du code.

---

# 🛠️ Technologies utilisées

## 🎮 Client

| Technologie                 | Utilisation           |
| --------------------------- | --------------------- |
| 🐍 Python                   | Client principal      |
| 🎨 VisPy                    | Rendu graphique       |
| 🖥️ Qt for Python (PySide6) | Interface utilisateur |

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

La documentation complète du projet est disponible ici :

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

# 📊 État détaillé du projet

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

Le projet suit une organisation inspirée des studios professionnels :

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

Chaque fonctionnalité importante doit être documentée et pensée avant son implémentation.

---

# ❓ FAQ

Vous avez une question sur le projet ?

➡️ [❓ Consulter la FAQ complète](docs/FAQ.md)

---

# 🎮 Commandes du jeu

Consultez le fichier suivant pour connaître les commandes disponibles :

➡️ [🎮 Commandes](touches_de_commandes)

---

# 📅 Roadmap

Consultez la roadmap du projet :

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
