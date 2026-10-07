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

# 🟢 Tu primera contribución

Puedes elegir una tarea adaptada a tu experiencia y al tiempo que quieras dedicar al proyecto.

| Nivel         | Tiempo estimado | Ejemplos                                     |
| ------------- | --------------: | -------------------------------------------- |
| 🟢 Fácil      |       20–40 min | Añadir un test, corregir documentación       |
| 🟡 Intermedio |           1–2 h | Mejorar una validación, añadir más tests     |
| 🟠 Avanzado   |           2–4 h | Modificar una funcionalidad cliente/servidor |

➡️ Recomendamos empezar con una issue marcada como **`good first issue`**.

Una buena issue debería indicar claramente:

* 🎯 qué debe hacerse;
* 📂 qué partes del proyecto están involucradas;
* 🧪 cómo probar los cambios;
* ✅ qué criterios permiten considerar la tarea terminada.

---

# 🔁 ¿Has terminado tu primera contribución?

Tu primera Pull Request no tiene por qué ser la última.

## 💬 Danos tu feedback

Después de terminar tu contribución, **no dudes en dejar feedback directamente en la issue asociada**.

Puedes indicar:

* 💬 qué fue claro o difícil de entender;
* 🧩 qué información te faltó;
* 🐛 qué problemas encontraste durante el desarrollo;
* 💡 cómo podría mejorarse la issue;
* 📚 qué documentación podría mejorarse.

**Tu feedback nos ayuda a mejorar las próximas issues y a hacer que las contribuciones sean más fáciles para todos.**

> 💡 Aunque no quieras trabajar inmediatamente en otra tarea, tu feedback sigue siendo una contribución valiosa para el proyecto.

## 🚀 Continuar después de tu primera contribución

Después de tu primera contribución, puedes continuar con una tarea relacionada con el área que acabas de descubrir.

Por ejemplo:

```text
🧪 Tests de Packet
       ↓
🧪 Casos inválidos
       ↓
🌐 Tests de red
       ↓
🔧 Validación de datos
       ↓
🎮 Funcionalidad cliente/servidor
```

Esta progresión permite descubrir el proyecto poco a poco sin tener que comprender toda la arquitectura desde la primera contribución.

> ⭐ **Empieza con algo pequeño, danos tu feedback y ve asumiendo tareas más importantes progresivamente.**

---

# 📐 Reglas de contribución

Antes de proponer una modificación:

* 📐 respeta las convenciones del proyecto;
* 📚 documenta las nuevas funcionalidades cuando sea necesario;
* 🧪 prueba tus cambios;
* 🌿 utiliza una rama Git dedicada para cada modificación;
* 📝 describe claramente tus cambios en tu Pull Request.

Antes de contribuir, consulta:

➡️ [📜 Reglas de desarrollo](docs_ESP/CODING_RULES_ESP.md)

➡️ [📖 Documentación](docs_ESP/README_ESP.md)

---

# 🌍 Presentación

**The Last Signal Online** es un MMORPG de supervivencia ambientado en un mundo postapocalíptico persistente.

Después de un misterioso acontecimiento que destruyó la civilización, los últimos supervivientes intentan reconstruir un nuevo mundo mientras descubren el origen de la última señal emitida por una antigua infraestructura olvidada.

El proyecto tiene como objetivo crear una experiencia multijugador que combine:

* 🌍 un mundo persistente;
* 👥 jugadores compartiendo el mismo mundo;
* ⚔️ combates PvE y PvP;
* 🏰 gremios y territorios;
* 💰 una economía dirigida por los jugadores;
* 🛠️ un sistema de fabricación;
* 📖 una historia evolutiva;
* 🔎 exploración y descubrimiento.

---

# 🚀 Visión del proyecto

El objetivo de **The Last Signal Online** es crear un MMORPG independiente que ofrezca:

* 🌍 un universo rico y coherente;
* 👥 una fuerte interacción entre jugadores;
* 🌎 decisiones que tengan un impacto en el mundo;
* 🧭 libertad de progresión;
* 🏗️ una arquitectura capaz de evolucionar a largo plazo.

El proyecto se desarrolla con un enfoque inspirado en los estudios profesionales de videojuegos:

* 📚 documentación estructurada;
* 🏗️ arquitectura diseñada antes del desarrollo;
* 🔄 integración continua;
* 🧪 tests automatizados;
* 📊 seguimiento de la calidad del código.

---

# 🛠️ Tecnologías utilizadas

## 🎮 Cliente

| Tecnología                  | Uso                 |
| --------------------------- | ------------------- |
| 🐍 Python                   | Cliente principal   |
| 🎨 VisPy                    | Renderizado gráfico |
| 🖥️ Qt for Python (PySide6) | Interfaz de usuario |

## 🌐 Servidor

| Tecnología    | Uso                           |
| ------------- | ----------------------------- |
| 🦀 Rust       | Servidor multijugador         |
| 🌐 Networking | Comunicación cliente/servidor |
| 🗄️ SQLite    | Base de datos                 |

---

# 📂 Organización del proyecto

```text
The-last-signal/
│
├── client_python/          # Cliente del juego
├── server_rust/            # Servidor Rust
├── database/               # Scripts de bases de datos
├── assets/                 # Recursos gráficos y de audio
│
├── docs/                   # Documentación completa (Francés)
│   ├── gdd/                # Game Design Document
│   ├── tdd/                # Technical Design Document
│   └── ...
│
├── docs_ENG/               # Documentación completa (Inglés)
│   ├── gdd/                # Game Design Document
│   ├── tdd/                # Technical Design Document
│   └── ...
│
├── scripts/                # Herramientas de desarrollo
├── tests/                  # Tests automatizados
│
├── README.md
└── LICENSE
```

---

# 📚 Documentación

La documentación completa del proyecto está disponible aquí:

➡️ [📖 Documentación oficial](docs_ESP/README_ESP.md)

Incluye:

* 🎮 Game Design Document (GDD);
* 🏗️ Technical Design Document (TDD);
* 🌍 lore del mundo;
* ⚔️ gameplay;
* 🌐 arquitectura de red;
* 🗄️ estructura de datos;
* 📅 roadmap.

---

# 📊 Estado del proyecto

| Módulo            |      Estado      |
| ----------------- | :--------------: |
| 📚 Documentación  | 🟡 En desarrollo |
| 🎮 Cliente Python | 🟡 En desarrollo |
| 🦀 Servidor Rust  | 🟡 En desarrollo |
| 🌐 Red            | 🟡 En desarrollo |
| 🗄️ Base de datos | 🟡 En desarrollo |
| 🎨 Assets         |  🟡 Preparación  |
| 🎮 Gameplay       |   🟢 Prototipo   |
| 🌍 Universo       |   🟢 Prototipo   |

### Leyenda

* 🟢 Funcional / Prototipo
* 🟡 En desarrollo
* ⚪ Previsto

---

# 🏗️ Proceso de desarrollo

El proyecto sigue una organización inspirada en los estudios profesionales de videojuegos:

```text
Diseño
    ↓
Documentación
    ↓
Prototipo
    ↓
Tests
    ↓
Desarrollo
    ↓
Optimización
```

Cada funcionalidad importante debe estar documentada y planificada antes de su implementación.

---

# ❓ FAQ

¿Tienes alguna pregunta sobre el proyecto?

➡️ [❓ Consulta la FAQ completa](docs_ESP/FAQ_ESP.md)

---

# 🎮 Controles del juego

Consulta el siguiente archivo para conocer los controles disponibles:

➡️ [🎮 Controles](touches_de_commandes)

---

# 📅 Roadmap

Consulta la hoja de ruta del proyecto:

➡️ [📅 Roadmap](docs_ESP/ROADMAP_ESP.md)

---

# 👥 Equipo

| Nombre       | Función                                    |
| ------------ | ------------------------------------------ |
| Morgan Piva  | Director                                   |
| Cyril Capiez | Director adjunto y desarrollador principal |

---

# 📜 Licencia

➡️ [📜 Licencia](LICENSE)

---

<img width="1024" height="559" alt="The Last Signal" src="https://github.com/user-attachments/assets/d96d0663-e01c-4911-841e-838f23e0e7cb" />

> **The Last Signal — Cuando el mundo desaparece, una última señal permanece.**
