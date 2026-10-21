# ❓ FAQ — The Last Signal Online

Esta FAQ responde a las preguntas más frecuentes sobre el proyecto,
su desarrollo y la contribución.

---

## 🎮 Sobre el proyecto

### 1. ¿Qué es The Last Signal Online?

**The Last Signal Online** es un MMORPG de supervivencia postapocalíptico
ambientado en un mundo persistente.

Los jugadores deberán explorar el mundo, sobrevivir, cooperar o enfrentarse
entre sí, desarrollar sus personajes y descubrir progresivamente los secretos
del mundo y el origen de la última señal.

Para obtener más información:
➡️ [Game Design Document](gdd/)

---

### 2. ¿Cuál es el estado actual del proyecto?

El proyecto se encuentra actualmente en **fase de prototipo y desarrollo**.

El servidor Rust, el cliente Python, el sistema de red y varios
elementos de la documentación están actualmente en desarrollo.

Por lo tanto, algunas funcionalidades previstas en el Game Design Document
todavía no han sido implementadas.

➡️ Consulta la [hoja de ruta](ROADMAP_ESP.md) para seguir el progreso del proyecto.

---

### 3. ¿El juego se puede jugar actualmente?

El proyecto ya cuenta con componentes funcionales tanto en el cliente
como en el servidor, pero el juego completo todavía no está disponible
en su versión final.

El desarrollo avanza progresivamente, comenzando por los
fundamentos técnicos del juego.

---

## 🛠️ Desarrollo

### 4. ¿Qué tecnologías se utilizan para desarrollar el juego?

El proyecto utiliza principalmente:

* 🦀 **Rust** para el servidor
* 🐍 **Python** para el cliente
* 🗄️ **SQLite** para la base de datos actual
* 🌐 Un sistema de comunicación cliente/servidor
* ⚙️ **GitHub Actions** para la integración continua y las pruebas automatizadas

Se podrán añadir otras tecnologías a medida que avance el desarrollo.

---

### 5. ¿Por qué utilizar Rust para el servidor y Python para el cliente?

Rust se utiliza para el servidor para proporcionar un buen rendimiento,
seguridad de memoria y una base sólida para un servidor multijugador.

Python se utiliza para el cliente para facilitar el desarrollo,
el prototipado y la creación de los diferentes sistemas del cliente.

Esta separación también permite que el cliente y el servidor
evolucionen de forma independiente.

---

## 🤝 Contribución

### 6. ¿El proyecto es de código abierto?

Sí.

El código fuente y la documentación del proyecto están disponibles
públicamente en GitHub.

Cualquier persona interesada puede consultar el proyecto
y proponer contribuciones.

---

### 7. ¿Cómo puedo contribuir al proyecto?

Puedes contribuir de muchas maneras diferentes:

* 🦀 Desarrollo en Rust
* 🐍 Desarrollo en Python
* 🌐 Redes y protocolos
* 🧪 Pruebas
* 🔐 Seguridad
* ⚙️ CI/CD
* 📚 Documentación
* 🌍 Traducciones
* 🎮 Game Design
* 📖 Lore
* 🎨 Assets

Las contribuciones se proponen principalmente mediante
**GitHub Issues** y **Pull Requests**.

➡️ [Ver las issues](https://github.com/DDCoder23/The-last-signal-/issues)

---

### 8. ¿Puedo contribuir si soy principiante?

Sí.

No es necesario conocer todo el proyecto antes de empezar.

Las pequeñas correcciones, pruebas, mejoras de documentación,
traducciones y otras contribuciones sencillas son buenas formas
de descubrir el proyecto.

➡️ Consulta [New Contributor? Start Here!](https://github.com/DDCoder23/The-last-signal-/issues/97)

---

### 9. ¿Qué tipos de contribuciones se necesitan actualmente?

El proyecto busca especialmente colaboradores interesados en:

* 🦀 Rust y desarrollo del servidor
* 🐍 Python y desarrollo del cliente
* 🌐 Redes
* 🧪 Pruebas
* 📚 Documentación
* 🇯🇵 Traducción al japonés
* 🇪🇸 Traducción al español
* 🔐 Seguridad y criptografía experimental
* ⚙️ CI/CD

Las necesidades del proyecto pueden cambiar a medida que avance
el desarrollo.

➡️ Consulta las [issues abiertas](https://github.com/DDCoder23/The-last-signal-/issues)
para conocer las necesidades actuales.

---

### 10. ¿Puedo contribuir sin ser desarrollador?

Sí.

El desarrollo es solo una parte del proyecto.

Puedes contribuir en:

* documentación;
* traducciones;
* lore;
* Game Design;
* pruebas;
* assets;
* investigación y comentarios sobre el proyecto.

---

### 11. ¿Cómo hago mi primera Pull Request?

El proceso general es:

1. Elegir una Issue.
2. Leer la información y los requisitos de la Issue.
3. Crear una rama dedicada.
4. Realizar los cambios.
5. Probar los cambios.
6. Crear un commit claro.
7. Subir la rama a GitHub.
8. Abrir una Pull Request.

➡️ Para una primera contribución, consulta
[New Contributor? Start Here!](https://github.com/DDCoder23/The-last-signal-/issues/97).

---

### 12. ¿Dónde puedo encontrar la documentación y las tareas disponibles?

La documentación se encuentra en el directorio [`docs_ESP/`](./).

Las tareas disponibles se encuentran en las
[GitHub Issues](https://github.com/DDCoder23/The-last-signal-/issues).

Los documentos técnicos y de Game Design también están disponibles
en sus respectivos directorios.

---

## 👥 Comunidad

### 13. ¿Cómo puedo contactar con otros colaboradores?

La mejor manera es utilizar las **GitHub Issues**
y las **Pull Requests** del proyecto.

Para una pregunta relacionada con una contribución, es preferible
hacerla directamente en la Issue correspondiente para que la información
siga siendo accesible para los demás colaboradores.

---

## 📌 Información general

### 14. ¿Dónde puedo seguir el progreso del proyecto?

El progreso del proyecto se puede seguir mediante:

* la [Roadmap](ROADMAP.md);
* las GitHub Issues;
* las Pull Requests;
* la documentación;
* las actualizaciones del proyecto.

---

### 15. ¿Puedo proponer una nueva funcionalidad?

Sí.

Antes de comenzar a desarrollar una nueva funcionalidad importante,
es preferible proponer la idea y debatirla primero.

Esto permite comprobar que encaja con la visión del proyecto
y evitar desarrollar una funcionalidad que pueda entrar en conflicto
con la arquitectura o el Game Design existentes.

---

## ❓ ¿Tienes otra pregunta?

Si tu pregunta no aparece en esta FAQ, puedes abrir una
**GitHub Issue** para solicitar aclaraciones o proponer
una mejora de esta FAQ.
