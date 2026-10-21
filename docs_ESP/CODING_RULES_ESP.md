[🏠 Documentación](README_ENG.md)

# 💻 Directrices de Desarrollo (Reglas de Código)

> **Proyecto:** The Last Signal Online

---

## 📋 Información

| Propiedad  | Valor |
|-----------|-------|
| **Documento** | Reglas de Código |
| **Código** | DOC-010 |
| **Versión** | 1.0.0 |
| **Estado** | 🟢 Active |
| **Última Actualización** | July 15, 2026 |

---

# 📖 Tabla de contenidos

1. Objetivo
2. Tecnologías Utilizadas
3. Arquitectura del proyecto y Organización
4. Estructura del Directorio
5. Convenciones de Nomenclatura
6. Estilo de Código de Python
7. Estilo de Código de Rust
8. Manejo de Errores
9. Documentación de Código
10. Estrategia de Ramificación de Git
11. GitHub Workflow
12. Pull Requests
13. Estándares de Pruebas
14. Reglas de Seguridad
15. Directrices de Optimización
16. Mejores Prácticas
17. Lista de Verificación Previa al Envío
18. Directrices de Contribución
19. Código de Conducta
20. Licencia

---

# 1. Objetivo

Este documento define las reglas oficiales de desarrollo y estándares de código para **The Last Signal Online**.

Su proposito es asegurar:

- una base de código limpia y homogénea;
- facilidad de mantenimiento y refactorización;
- colaboración efectiva entre los miembros del equipo;
- altos estándares de calidad y fiabilidad del software.

Estas reglas se aplican a todos los que contribuyan.

---

# 2. Tecnologías usadas

| Tecnología | Uso |
|-------------|-------|
| Python | Cliente del Juego y Herramientas |
| Rust | Servidor del Juego |
| PostgreSQL | Base de Datos Principal |
| Redis | Capa de Caché |
| WebSocket / TCP | Comunicación de Red |
| Docker | Contenerización y Despliegue |
| Git | Control de Versiones |
| GitHub Actions | Automatización CI/CD |
| Markdown | Documentación |

---

# 3. Arquitectura y Organización de Proyecto

El proyecto está estructurado en módulos independientes y desacoplados.

Cada módulo debe de seguir el Principio de Responsabilidad Única (SRP).

Las áreas clave incluyen:

- Red
- Jugador y Cuentas
- Inventario y Equipamiento
- Combate y Sistemas
- Mundo y Entornos
- AI y Entidades
- UI y HUD

---

# 4. Estructura del Directorio

Cada directorio tiene un responsabilidad bien definida.

Los archivos deben organizarse estrictamente según su dominio y funcionalidad.

Evite archivos monolíticos que contengan sistemas no relacionados.

---

# 5. Convenciones de Nomenclatura

- Python: `snake_case` para funciones y variables, `PascalCase` para clases, `UPPER_SNAKE_CASE` para constantes.
- Rust: `snake_case` para funciones/modulos/variables, `PascalCase` para structs/enums/traits, `SCREAMING_SNAKE_CASE` para constantes.
- Los nombres de funciones y variables deben utilizar caracteres latinos y nombres claros en Inglés.

---

# 6. Estilo de Código en Python

El código en Python debe cumplir los estándares PEP 8:

- Indicadores de tipo exhaustivos (`typing` / tipos integrados).
- Funciones breves y centradas en una tarea específica.
- Nombres de variables explícitos y descriptivos.
- Dependencia mínima de variables globales.

Todas las funciones, clases y métodos publicos deben tener una cadena de documentación descriptiva.

---

# 7. Estilo de Código en Rust

El código en Rust debe cumplir los estándares idiomáticos de Rust:

- Formateado con `cargo fmt`.
- Analizado con `cargo clippy` que no contenga advertencias.
- Gestión robusta de errores mediante `Result` y `Option` (evita utilizar `.unwrap()` en rutas de producción).
- Completa los comentarios de documentaicón (`///`) en funciones y estructuras públicas.

---

# 8. Manejo de Errores

Los errores nunca deben ignorarse en silencio ni pasarse por alto.

Siempre:

- Mostrar o devolver un contexto de error significativo.
- Registrar los errores en el subsistema de registro adecuado, indicando los niveles de gravedad.
- Gestionar de forma controlada los fallos recuperables y evitar cierres abruptos.

---

# 9. Documentación del código

Toda función o módulo que no sea trivial debe estar documentado.

Los comentarios deben explicar **por qué** existe el código, en lugar de limitarse a repetir **qué** hace la sintaxis.

Evite comentarios redundantes u obsoletos.

---

# 10. Estrategia de Ramificación de Git

Nunca hagas un commit directamente a la rama `main` (los administradores podrian realizar correciones de emergencia pero deben revisar el código).

Cada nueva funcionalidad o correción de bugs debe ser desarrollada en su propia rama dedicada.

Ejemplos de Nombres de Ramas:

```text
feature/login
feature/inventory
feature/chat
feature/world
```

Para correción de errores:

```text
fix/login
fix/database
```

Para documentación:

```text
docs/gdd
docs/readme
```

---

# 11. GitHub Workflow

La contribución estándar al flujo de trabajo es:

```text
Issue
  ↓
Branch
  ↓
Development
  ↓
Automated Tests & Linting
  ↓
Pull Request
  ↓
Code Review
  ↓
Merge into main
```

Los pull request no deben de ser fusionados sin una previa revisión del código y aprobación formal de un administrador autorizado.

---

# 12. Pull Requests

Cada Pull Request debe:

- Tener un titulo claro y descriptivo.
- Detallar la justificación y el alcance de las modificaciones.
- Referenciar Issues relevantes en Github (`Fixes #123`, `Closes #456`).
- Ser revisado y aprobado por un administrador antes de fusionar.

---

# 13. Estándares de Pruebas

Antes de cualquier fusión:

- El proyecto debe compilar limpiamente sin errores.
- Todas las pruebas unitarias y de integración automatizadas deben aprobar.
- No debehaber advertencias criticas del compilador o del linter.
- No debe haber regresiones conocidas sin resolver.

Todas las nuevas funcionalidades y correciones a errores deben incluir la correspondiente prueba automatizada cuando sea factible.

---

# 14. Reglas de Seguridad

Está estrictamente prohibido:

- Subir contraseñas, credenciales en texto plano o secretos.
- Subir API keys o tokens privados.
- Subir Tokens de Acceso Personal de Github o llaves privadas SSH.
- Intencionalmente eludir o deshabilitar las comprobaciones de seguridad.

Los parámetros de configuración confidenciales deben suministrarse mediante variables de entorno o almacenes de secretos cifrados.

---

# 15. Pautas de optimización

El código debe ser:

- **Legible:** Nombres de funciones y variables en inglés estándar (alfabeto latino); consulta a una persona de habla inglesa si es necesario.
- **Mantenible:** Abstracciones limpias con baja complejidad ciclomática.
- **De alto rendimiento:** Algoritmos y gestión de memoria eficientes.

Evita la optimización prematura. Mide y analiza el rendimiento antes de optimizar, y optimiza únicamente cuando se identifique un cuello de botella cuantificable.

---

# 16. Mejores prácticas

Siempre:

- Escribe código limpio y autoexplicativo.
- Sigue el principio DRY (*Don't Repeat Yourself* / No te repitas).
- Prioriza funciones pequeñas y modulares.
- Respeta la arquitectura del sistema.
- Documenta las decisiones de diseño clave y las compensaciones arquitectónicas.

---

# 17. Lista de verificación previa al envío

Antes de enviar una *Pull Request*:

- [ ] El proyecto se construye y compila correctamente.
- [ ] Todas las suites de pruebas se ejecutan con éxito.
- [ ] El código cumple con las guías de estilo del lenguaje y las reglas de formato.
- [ ] La documentación está actualizada para reflejar los cambios.
- [ ] El archivo `CHANGELOG_ENG.md` está actualizado, si corresponde.
- [ ] No se han incluido secretos, claves ni credenciales en el repositorio.
- [ ] Los archivos nuevos están organizados correctamente en la estructura del proyecto.
- [ ] Se ha realizado una autoevaluación.

---

# 18. Directrices de contribución

## 📋 Requisitos

Antes de contribuir, por favor asegúrate de:

- Leer la documentación del proyecto.
- Cumplir con estas normas de codificación.
- Respetar el [Código de conducta](../docs_ESP/CODE_OF_CONDUCT_ESP.md).
- Seguir las prácticas estándar de ramificación en Git.

---

## 🚀 Primeros pasos

1. Haz un *fork* del repositorio (para colaboradores externos).
2. Clona tu *fork* localmente.
3. Crea una rama descriptiva para la nueva funcionalidad (`git checkout -b feature/my-feature`).
4. Implementa tus cambios.
5. Ejecuta la suite de pruebas y verifica la calidad del código.
6. Actualiza la documentación donde corresponda.
7. Abre un *Pull Request* dirigido a la rama `main`.

---

## 💬 Mensajes de commit

Utiliza los prefijos estándar de *Conventional Commits*:

```text
feat: add player inventory management system
fix: resolve client login authentication timeout
docs: update GDD narrative specifications
refactor: improve network packet serialization
test: add integration tests for socket connection
```

---

## 🔍 Revisión de código

Todos los PR se someten a revisión antes de su integración. Los comentarios de la revisión y los cambios solicitados deben atenderse antes de la aprobación final.

---

# 📜 Código de conducta

Trata a todos los miembros de la comunidad y a los colaboradores con respeto mutuo.

Todas las interacciones deben ser:

- Respetuosas
- Constructivas
- Profesionales

---

# 📄 Licencia

Al contribuir a **The Last Signal Online**, aceptas que tus contribuciones se licencien bajo la [LICENCIA](../LICENSE) de código abierto del proyecto.

---

¡Gracias por contribuir a **The Last Signal Online**! 🚀

# 📚 Documentos relacionados

- [🏠 Documentación](README_ESP.md)
- [🏗 Documento de diseño técnico](tdd/README_ESP.md)
- [🛣 Hoja de ruta](ROADMAP_ESP.md)
- [📝 Registro de cambios](../CHANGELOG_ENG.md)

---

## Navegación

⬅️ Volver: [Documentación](../README_ESP.md)
