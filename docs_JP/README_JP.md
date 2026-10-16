# 📚 The Last Signal Online
<img width="1408" height="768" alt="The Last Signal Online" src="https://github.com/user-attachments/assets/b8f7d28b-d2b1-4b1b-96b1-6382d06b9b5d" />

## 🌐 README の言語
🇫🇷 **[Français](../README.md)**<br>
🇬🇧 **[English](../docs_ENG/README_ENG.md)**<br>
🇪🇸 **Español** — 準備中<br>
🇯🇵 **日本語** — 現在、日本語版を表示しています。

> プロジェクト公式ドキュメント

**The Last Signal Online** の公式ドキュメントへようこそ。

このドキュメントは、プロジェクトのさまざまな設計および技術ドキュメントを
簡単に参照できるよう、**Wiki** として構成されています。

---

# 🗂 ドキュメント

## 🎮 ゲームデザイン
> ゲームのビジョン、メカニクス、ルールを定義します。

| ドキュメント | 説明 |
|-----------|-------------|
| 📖 [Game Design Document (GDD)](gdd/README_JP.md) | ゲームデザインに関するすべてのドキュメントの入口です。 |

---

## 🏗 技術ドキュメント
> 内部アーキテクチャ、エンジン設計、サーバープロトコルについて説明します。

| ドキュメント | 説明 |
|-----------|-------------|
| 🏗 [Technical Design Document (TDD)](tdd/README_JP.md) | 技術アーキテクチャの概要です。 |
| 🖥 [アーキテクチャ](ARCHITECTURE_JP.md) | コード構成とモジュールの配置です。 |
| 🗄 [データベース](DATABASE_JP.md) | PostgreSQL データベースの構造です。 |
| 🌐 [ネットワーク](NETWORK_JP.md) | クライアント ↔ サーバー間のネットワーク通信です。 |

---

## 🌍 世界観とゲームプレイ

| ドキュメント | 説明 |
|-----------|-------------|
| 📚 [Lore](lore/README_JP.md) | 世界設定、物語、ナラティブの世界観です。 |
| 🎮 [Gameplay](gameplay/README_JP.md) | 中核となるゲームプレイシステムとメカニクスです。 |

---

## 📅 プロジェクト管理

| ドキュメント | 説明 |
|-----------|-------------|
| 📅 [Roadmap](ROADMAP_JP.md) | 開発ロードマップとスケジュールです。 |
| 👥 [チーム](TEAM_JP.md) | スタジオのチーム構成と役割です。 |
| 💻 [開発ルール](CODING_RULES_JP.md) | Git、Python、Rust の規約です。 |

---

## 📜 履歴

| ドキュメント | 説明 |
|-----------|-------------|
| 📝 [Changelog](../CHANGELOG_ENG.md) | プロジェクトのバージョン履歴と更新内容です。 |

---

# 📊 プロジェクトの状態

| モジュール | 状態 |
|---------|:----:|
| 📚 ドキュメント | 🟡 進行中 |
| 🐍 Python クライアント | 🟡 リファクタリング中 |
| 🦀 Rust サーバー | ⚪ 未着手 |
| 🌐 ネットワーク | ⚪ 未着手 |
| 🗄 データベース | ⚪ 未着手 |
| 🎮 ゲームプレイ | 🟢 プロトタイプ |
| 🌍 世界 | 🟢 プロトタイプ |

---

# 📂 ドキュメント構成

```text
docs_JP/
│
├── README_JP.md
│
├── gdd/
│   ├── README_JP.md
│   ├── 01_VISION_JP.md
│   ├── 02_UNIVERS_JP.md
│   ├── 03_SCENARIO_JP.md
│   ├── 04_CHRONOLOGIE_JP.md
│   ├── 05_FACTIONS_JP.md
│   ├── 06_REGIONS_JP.md
│   ├── 07_VILLES_JP.md
│   ├── 08_DONJONS_JP.md
│   ├── 09_PERSONNAGES_JP.md
│   ├── 10_CREATION_PERSONNAGE_JP.md
│   ├── 11_PROGRESSION_JP.md
│   ├── 12_STATISTIQUES_JP.md
│   ├── 13_COMPETENCES_JP.md
│   ├── 14_CLASSES_JP.md
│   ├── 15_GAMEPLAY_JP.md
│   ├── 16_COMBAT_JP.md
│   ├── 17_IA_JP.md
│   ├── 18_MONSTRES_JP.md
│   ├── 19_BOSS_JP.md
│   ├── 20_INVENTAIRE_JP.md
│   ├── 21_EQUIPEMENT_JP.md
│   ├── 22_OBJETS_JP.md
│   ├── 23_BANQUE_JP.md
│   ├── 24_COFFRES_JP.md
│   ├── 25_ECONOMIE_JP.md
│   ├── 26_COMMERCE_JP.md
│   ├── 27_HOTEL_DES_VENTES_JP.md
│   ├── 28_MONNAIES_JP.md
│   ├── 29_METIERS_JP.md
│   ├── 30_CRAFT_JP.md
│   ├── 31_RECOLTE_JP.md
│   ├── 32_CARTE_JP.md
│   ├── 33_BIOMES_JP.md
│   ├── 34_METEO_JP.md
│   ├── 35_JOUR_NUIT_JP.md
│   ├── 36_GUILDES_JP.md
│   ├── 37_GROUPES_JP.md
│   ├── 38_CHAT_JP.md
│   ├── 39_PVE_JP.md
│   ├── 40_PVP_JP.md
│   ├── 41_QUETES_JP.md
│   ├── 42_EVENEMENTS_JP.md
│   ├── 43_SUCCES_JP.md
│   ├── 44_HUD_JP.md
│   ├── 45_MENUS_JP.md
│   ├── 46_ACCESSIBILITE_JP.md
│   ├── 47_MUSIQUES_JP.md
│   ├── 48_AMBIANCES_JP.md
│   ├── 49_EFFETS_SONORES_JP.md
│   ├── 50_DIRECTION_ARTISTIQUE_JP.md
│   ├── 51_CONCEPT_ART_JP.md
│   ├── 52_MODELES_3D_JP.md
│   ├── 53_ANIMATIONS_JP.md
│   ├── 54_EXTENSIONS_JP.md
│   └── 55_IDEES_JP.md
│
├── tdd/
├── lore/
├── gameplay/
├── ARCHITECTURE_JP.md
├── DATABASE_JP.md
├── NETWORK_JP.md
├── ROADMAP_JP.md
├── TEAM_JP.md
└── CODING_RULES_JP.md
```

---

# 🚀 プロジェクトの目的

**The Last Signal Online** は、次の要素を備えた没入型ポストアポカリプス・サバイバル MMORPG の開発を目指します。

- 🌍 永続する世界
- 👥 同時にプレイする数百人のプレイヤー
- ⚔️ PvE と PvP の戦闘
- 🏰 ギルドと領地
- 💰 プレイヤー主導の経済
- 🛠️ 充実したクラフティングシステム
- 📖 進化するストーリー

---

# 👥 チーム

| 名前 | 役割 |
|------|------|
| Morgan Piva | ディレクター兼創設者 |
| Cyril Capiez | 副ディレクター兼リード開発者 |


---
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />
> **ドキュメントバージョン：** 1.0.0
