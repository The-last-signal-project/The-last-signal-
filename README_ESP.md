# 🎮 The Last Signal

<img width="1408" height="768" alt="The Last Signal" src="https://github.com/user-attachments/assets/b8f7d28b-d2b1-4b1b-96b1-6382d06b9b5d" />

## 🌐 Idiomas del README

🇪🇸 **Español** — Estás viendo actualmente la versión en español.<br>
🇫🇷 **Français** — [Versión francesa](README.md)<br>
🇬🇧 **English** — [Versión inglesa](README_ENG.md)<br>
🇯🇵 **日本語** — [Versión japonesa](README_JP.md)

> **MMORPG de supervivencia postapocalíptica en un mundo persistente.**

![Estado](https://img.shields.io/badge/status-prototype-orange)
![Documentación](https://img.shields.io/badge/docs-active-blue)
![Python](https://img.shields.io/badge/client-Python-yellow)
![Rust](https://img.shields.io/badge/server-Rust-orange)

---

## 🎮 Estado actual del proyecto

**The Last Signal Online se encuentra actualmente en fase de prototipo.**

El prototipo actual permite:

* 🎮 iniciar el cliente del juego;
* 🌐 conectarse a un servidor local;
* 🧭 desplazarse por el mundo;
* 👥 ver a otros jugadores conectados;
* 🧪 probar progresivamente los sistemas del juego.

El servidor del juego funciona actualmente **en local**. Todavía no existe un servidor público accesible desde Internet.

El juego completo sigue en desarrollo. Muchos sistemas importantes se añadirán y mejorarán progresivamente.

> 💡 **El proyecto todavía es lo suficientemente joven como para que las contribuciones puedan tener un impacto real en su evolución.**

---

## 🚀 ¿Por qué contribuir ahora?

The Last Signal no es un proyecto terminado.

Precisamente por eso, los colaboradores pueden participar directamente en su construcción.

Actualmente, las contribuciones pueden centrarse en:

* 🦀 el servidor Rust;
* 🐍 el cliente Python;
* 🌐 la red y los protocolos;
* 🧪 los tests;
* 🔐 la seguridad;
* ⚙️ CI/CD;
* 📚 la documentación;
* 🎮 el prototipo y el gameplay;
* 🔧 las herramientas de desarrollo.

No necesitas **conocer todo el proyecto** para empezar.

Una pequeña contribución permite descubrir progresivamente la arquitectura y el código del proyecto.

---

# 🧪 Probar el prototipo

El servidor del juego funciona actualmente **en local**.

Para probar el prototipo, necesitas Python, Rust y las dependencias del proyecto.

## 📋 Requisitos

Necesitas:

* 🐍 **Python 3.14**
* 🦀 **Rust y Cargo**
* 🌿 **Git**

---

## 📥 1. Clonar el repositorio

```bash
git clone https://github.com/DDCoder23/The-last-signal-.git
cd The-last-signal-
```

---

## 🐍 2. Instalar las dependencias de Python

Desde la **raíz del proyecto**:

```bash
pip install -r requirements.txt
```

---

## 🦀 3. Iniciar el servidor Rust

Abre un primer terminal y entra en el directorio del servidor:

```bash
cd server_rust
```

A continuación, inicia el servidor:

```bash
cargo run --locked
```

### 🧹 Compilación limpia — opcional

`cargo clean` **no es necesario cada vez que se inicia el servidor**.

Si quieres realizar una compilación completamente limpia:

```bash
cargo clean
cargo run --locked
```

Deja el servidor funcionando en este terminal.

---

## 🎮 4. Iniciar el cliente

Abre un **segundo terminal** y vuelve a la raíz del proyecto:

```bash
cd The-last-signal-
```

A continuación, inicia el cliente:

```bash
python -m client_python.main
```

El cliente se conectará al servidor local.

---

## 🌐 Arquitectura actual

La configuración actual utiliza una arquitectura local cliente/servidor:

```text
┌─────────────────────────┐
│      Cliente Python     │
│         🎮 Juego        │
└────────────┬────────────┘
             │
             │ Red
             ▼
┌─────────────────────────┐
│      Servidor Rust      │
│    🦀 Servidor de juego │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│         SQLite          │
│       🗄️ Datos          │
└─────────────────────────┘
```

> 🌐 **Servidor público: todavía no disponible.**
>
> Por ahora, cada colaborador puede ejecutar su propio servidor local para probar y desarrollar el proyecto.

---

# 🤝 Contribuir

**The Last Signal** es un proyecto de código abierto y acepta contribuciones de desarrolladores, testers, escritores, traductores y otros participantes interesados.

## 🟢 ¿Eres nuevo en el proyecto?

No necesitas dominar todo el proyecto.

Puedes empezar por:

* 🧪 añadir o mejorar un test;
* 🐛 corregir un problema sencillo;
* 📚 mejorar la documentación;
* 🌍 mejorar una traducción;
* 🔧 mejorar una herramienta de desarrollo;
* 📝 mejorar la calidad del código.

➡️ [Consultar las Issues abiertas](../../issues)

---

## 🛠️ ¿Eres desarrollador?

Las contribuciones son especialmente bienvenidas en:

* 🦀 **Rust** — servidor;
* 🐍 **Python** — cliente;
* 🌐 **Redes** — comunicación cliente/servidor y protocolos;
* 🧪 **Tests** — tests unitarios y de integración;
* 🔐 **Seguridad**;
* ⚙️ **CI/CD**;
* 📚 **Documentación**.

---

# 🟢 Tu primera contr
