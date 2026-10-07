# 🎮 The Last Signal

<img width="1408" height="768" alt="The Last Signal" src="https://github.com/user-attachments/assets/b8f7d28b-d2b1-4b1b-96b1-6382d06b9b5d" />

## 🌐 README languages

🇫🇷 **Français** — [French version](README.md)<br>
🇬🇧 **English** — You are currently viewing the English version.<br>
🇪🇸 **Español** — [Spanish version](README_ESP.md)<br>
🇯🇵 **日本語** — [Japanese version](README_JP.md)

> **Post-apocalyptic survival MMORPG set in a persistent world.**

![Status](https://img.shields.io/badge/status-prototype-orange)
![Documentation](https://img.shields.io/badge/docs-active-blue)
![Python](https://img.shields.io/badge/client-Python-yellow)
![Rust](https://img.shields.io/badge/server-Rust-orange)

---

## 🎮 Current Project Status

**The Last Signal Online is currently in the prototype phase.**

The current prototype allows you to:

* 🎮 launch the game client;
* 🌐 connect to a local game server;
* 🧭 move around the world;
* 👥 see other connected players;
* 🧪 progressively test the game's systems.

The game server currently runs **locally**. A public server accessible over the Internet is not available yet.

The complete game is still under development. Many important systems will be progressively added and improved.

> 💡 **The project is still young enough for contributions to have a real impact on its evolution.**

---

## 🚀 Why Contribute Now?

The Last Signal is not a finished project.

That is precisely what allows contributors to participate directly in building it.

Contributions can currently focus on:

* 🦀 the Rust server;
* 🐍 the Python client;
* 🌐 networking and protocols;
* 🧪 testing;
* 🔐 security;
* ⚙️ CI/CD;
* 📚 documentation;
* 🎮 the prototype and gameplay;
* 🔧 development tools.

You do **not need to understand the entire project** to get started.

A small contribution is a way to progressively discover the project's architecture and codebase.

---

# 🧪 Test the Prototype

The game server currently runs **locally**.

To test the prototype, you need Python, Rust and the project dependencies.

## 📋 Requirements

You need:

* 🐍 **Python 3.14**
* 🦀 **Rust and Cargo**
* 🌿 **Git**

---

## 📥 1. Clone the Repository

```bash
git clone https://github.com/DDCoder23/The-last-signal-.git
cd The-last-signal-
```

---

## 🐍 2. Install Python Dependencies

From the **project root**:

```bash
pip install -r requirements.txt
```

---

## 🦀 3. Start the Rust Server

Open a first terminal and move into the server directory:

```bash
cd server_rust
```

Then start the server:

```bash
cargo run --locked
```

### 🧹 Clean Build — Optional

`cargo clean` is **not required every time you start the server**.

If you want to perform a clean rebuild:

```bash
cargo clean
cargo run --locked
```

Keep the server running in this terminal.

---

## 🎮 4. Start the Client

Open a **second terminal** and return to the project root:

```bash
cd The-last-signal-
```

Then start the client:

```bash
python -m client_python.main
```

The client will connect to the local server.

---

## 🌐 Current Architecture

The current setup uses a local client/server architecture:

```text
┌─────────────────────────┐
│      Python Client      │
│         🎮 Game         │
└────────────┬────────────┘
             │
             │ Network
             ▼
┌─────────────────────────┐
│       Rust Server       │
│    🦀 Game Server       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│         SQLite          │
│        🗄️ Data          │
└─────────────────────────┘
```

> 🌐 **Public server: not available yet.**
>
> For now, every contributor can run their own local server to test and develop the project.

---

# 🤝 Contributing

**The Last Signal** is an open-source project and welcomes contributions from developers, testers, writers, translators and other interested participants.

## 🟢 New to the Project?

You do not need to master the entire project.

You can start by:

* 🧪 adding or improving a test;
* 🐛 fixing a simple issue;
* 📚 improving the documentation;
* 🌍 improving a translation;
* 🔧 improving a development tool;
* 📝 improving code quality.

➡️ [Browse open Issues](../../issues)

---

## 🛠️ Are You a Developer?

Contributions are particularly welcome in:

* 🦀 **Rust** — server;
* 🐍 **Python** — client;
* 🌐 **Networking** — client/server communication and protocols;
* 🧪 **Testing** — unit and integration tests;
* 🔐 **Security**;
* ⚙️ **CI/CD**;
* 📚 **Documentation**.

---

# 🟢 Your First Contribution

You can choose a task that matches your experience and the amount of time you want to spend on the project.

| Level           | Estimated time | Examples                           |
| --------------- | -------------: | ---------------------------------- |
| 🟢 Easy         |      20–40 min | Add a test, fix documentation      |
| 🟡 Intermediate |          1–2 h | Improve validation, add more tests |
| 🟠 Advanced     |          2–4 h | Modify a client/server feature     |

➡️ We recommend starting with an issue marked **`good first issue`**.

A good issue should make it clear:

* 🎯 what needs to be done;
* 📂 which parts of the project are involved;
* 🧪 how to test the changes;
* ✅ what criteria determine whether the task is complete.

---

# 🔁 Finished Your First Contribution?

Your first Pull Request does not have to be your last one.

## 💬 Give Us Your Feedback

After completing your contribution, **feel free to leave feedback directly on the associated issue**.

You can tell us:

* 💬 what was clear or difficult to understand;
* 🧩 what information was missing;
* 🐛 what problems you encountered while developing;
* 💡 how the issue could be improved;
* 📚 what documentation could be improved.

**Your feedback helps us improve future issues and make contributions easier for everyone.**

> 💡 Even if you do not immediately want to work on another task, your feedback is still a valuable contribution to the project.

## 🚀 Continue After Your First Contribution

After your first contribution, you can continue with a task related to the area you have just discovered.

For example:

```text
🧪 Packet Tests
       ↓
🧪 Invalid Cases
       ↓
🌐 Network Tests
       ↓
🔧 Data Validation
       ↓
🎮 Client/Server Feature
```

This progression allows you to gradually discover the project without having to understand the entire architecture from your first contribution.

> ⭐ **Start small, give us your feedback, and progressively take on larger tasks.**

---

# 📐 Contribution Guidelines

Before submitting a modification:

* 📐 follow the project's conventions;
* 📚 document new features when necessary;
* 🧪 test your changes;
* 🌿 use a dedicated Git branch for each modification;
* 📝 clearly describe your changes in your Pull Request.

Before contributing, please read:

➡️ [📜 Development Rules](docs_ENG/CODING_RULES_ENG.md)

➡️ [📖 Documentation](docs_ENG/README_ENG.md)

---

# 🌍 Overview

**The Last Signal Online** is a survival MMORPG set in a persistent post-apocalyptic world.

After a mysterious event shattered civilization, the last survivors attempt to rebuild a new world while uncovering the origin of the last signal emitted
