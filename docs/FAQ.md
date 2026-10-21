# ❓ FAQ — The Last Signal Online

Cette FAQ répond aux questions les plus fréquentes concernant le projet,
son développement et la contribution.

---

## 🎮 À propos du projet

### 1. Qu'est-ce que The Last Signal Online ?

**The Last Signal Online** est un MMORPG de survie post-apocalyptique
se déroulant dans un monde persistant.

Les joueurs devront explorer le monde, survivre, coopérer ou s'affronter,
développer leurs personnages et découvrir progressivement les secrets
du monde et l'origine du dernier signal.

Pour plus d'informations :
➡️ [Game Design Document](gdd/)

---

### 2. Dans quel état est actuellement le projet ?

Le projet est actuellement en **phase de prototype et de développement**.

Le serveur Rust, le client Python, le système réseau et plusieurs
éléments de documentation sont en cours de développement.

Certaines fonctionnalités prévues dans le Game Design Document ne sont
donc pas encore implémentées.

➡️ Voir [la roadmap](ROADMAP.md) pour suivre l'avancement du projet.

---

### 3. Le jeu est-il actuellement jouable ?

Le projet possède déjà des éléments fonctionnels du client et du serveur,
mais le jeu complet n'est pas encore disponible dans sa version finale.

Le développement se fait progressivement, en commençant par les
fondations techniques du jeu.

---

## 🛠️ Développement

### 4. Quelles technologies sont utilisées pour développer le jeu ?

Le projet utilise principalement :

- 🦀 **Rust** pour le serveur
- 🐍 **Python** pour le client
- 🗄️ **SQLite** pour la base de données actuelle
- 🌐 Un système de communication client/serveur
- ⚙️ **GitHub Actions** pour l'intégration et les tests automatisés

D'autres technologies peuvent être ajoutées au cours du développement.

---

### 5. Pourquoi utiliser Rust pour le serveur et Python pour le client ?

Rust est utilisé pour le serveur afin de bénéficier de bonnes performances,
d'une gestion sûre de la mémoire et d'une base solide pour un serveur
multijoueur.

Python est utilisé pour le client afin de faciliter le développement,
le prototypage et la création des différents systèmes du client.

Cette séparation permet également de faire évoluer indépendamment
le client et le serveur.

---

## 🤝 Contribution

### 6. Le projet est-il open source ?

Oui.

Le code source et la documentation du projet sont disponibles publiquement
sur GitHub.

Toute personne intéressée peut consulter le projet et proposer des
contributions.

---

### 7. Comment puis-je contribuer au projet ?

Tu peux contribuer de différentes manières :

- 🦀 Développement Rust
- 🐍 Développement Python
- 🌐 Réseau et protocoles
- 🧪 Tests
- 🔐 Sécurité
- ⚙️ CI/CD
- 📚 Documentation
- 🌍 Traductions
- 🎮 Game Design
- 📖 Lore
- 🎨 Assets

Les contributions sont proposées principalement via les **GitHub Issues**
et les **Pull Requests**.

➡️ [Voir les issues](https://github.com/DDCoder23/The-last-signal-/issues)

---

### 8. Puis-je contribuer si je suis débutant ?

Oui.

Tu n'as pas besoin de connaître l'intégralité du projet avant de
commencer.

Les petites corrections, tests, améliorations de documentation,
traductions et autres contributions simples sont de bonnes façons
de découvrir le projet.

➡️ Voir [New Contributor? Start Here!](https://github.com/DDCoder23/The-last-signal-/issues/97)

---

### 9. Quels types de contributions sont actuellement recherchés ?

Le projet recherche notamment des contributeurs intéressés par :

- 🦀 Rust et développement serveur
- 🐍 Python et développement client
- 🌐 Réseau
- 🧪 Tests
- 📚 Documentation
- 🇯🇵 Traduction japonaise
- 🇪🇸 Traduction espagnole
- 🔐 Sécurité et cryptographie expérimentale
- ⚙️ CI/CD

Les besoins peuvent évoluer avec l'avancement du projet.

➡️ Consulte les [issues ouvertes](https://github.com/DDCoder23/The-last-signal-/issues)
pour voir les besoins actuels.

---

### 10. Puis-je contribuer sans être développeur ?

Oui.

Le développement n'est qu'une partie du projet.

Tu peux notamment contribuer à :

- la documentation ;
- les traductions ;
- le lore ;
- le Game Design ;
- les tests ;
- les assets ;
- la recherche et les retours sur le projet.

---

### 11. Comment faire ma première Pull Request ?

Le fonctionnement général est :

1. Choisir une Issue.
2. Lire les informations et contraintes de l'Issue.
3. Créer une branche dédiée.
4. Effectuer les modifications.
5. Tester les modifications.
6. Faire un commit clair.
7. Envoyer la branche sur GitHub.
8. Ouvrir une Pull Request.

➡️ Pour un premier parcours, consulte
[New Contributor? Start Here!](https://github.com/DDCoder23/The-last-signal-/issues/97).

---

### 12. Où puis-je trouver la documentation et les tâches disponibles ?

La documentation se trouve dans le dossier [`docs/`](./).

Les tâches disponibles se trouvent dans les
[GitHub Issues](https://github.com/DDCoder23/The-last-signal-/issues).

Les documents techniques et de Game Design sont également disponibles
dans les dossiers correspondants.

---

## 👥 Communauté

### 13. Comment puis-je contacter les autres contributeurs ?

Le meilleur moyen est d'utiliser les **GitHub Issues** et les
**Pull Requests** du projet.

Pour une question concernant une contribution, il est préférable de
la poser directement dans l'Issue correspondante afin que les informations
restent accessibles aux autres contributeurs.

---

## 📌 Informations générales

### 14. Où puis-je suivre l'avancement du projet ?

L'avancement peut être suivi grâce à :

- la [Roadmap](ROADMAP.md) ;
- les GitHub Issues ;
- les Pull Requests ;
- la documentation ;
- les mises à jour du projet.

---

### 15. Puis-je proposer une nouvelle fonctionnalité ?

Oui.

Avant de commencer à développer une nouvelle fonctionnalité importante,
il est préférable de proposer l'idée et d'en discuter d'abord.

Cela permet de vérifier qu'elle correspond à la vision du projet et
d'éviter de développer une fonctionnalité qui entrerait en conflit
avec l'architecture ou le Game Design existant.

---

## ❓ Vous avez une autre question ?

Si votre question n'est pas présente dans cette FAQ, vous pouvez ouvrir
une **GitHub Issue** afin de demander des précisions ou proposer une
amélioration de cette FAQ.
