# Race Engineer

[![Pruebas](https://github.com/ceherrejon/race-engineer/actions/workflows/pruebas.yml/badge.svg)](https://github.com/ceherrejon/race-engineer/actions/workflows/pruebas.yml)
[![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE)

**Prepara o audita cualquier proyecto para trabajar con Claude Code y Codex**, con una skill que deja cada cosa en el formato que lee cada herramienta y la comprueba en vivo.

Como el ingeniero de pista de un equipo de F1 con dos pilotos: prepara el coche de cada uno (Claude y Codex), lee la telemetría del proyecto y propone ajustes, pero no toca nada sin tu visto bueno.

[English](README.en.md)

## Qué hace

`race-engineer` tiene dos modos:

- **Proyecto nuevo:** genera `AGENTS.md` (y `CLAUDE.md` solo si hace falta), permisos y hooks para Claude Code (`.claude/settings.json`) y Codex (`.codex/config.toml`), una **guardia de secretos** común a las dos herramientas, un subagente revisor, plantillas de estado para tareas largas y una guía de incorporación para cada persona del equipo.
- **Proyecto existente:** audita su configuración en 9 capas (instrucciones, procedimientos, fuentes externas, reglas de acción, verificación, modelo y esfuerzo, estado, código y commits, equipo de agentes) y entrega un informe priorizado, con evidencia, y una propuesta de cambios que solo se aplica con tu aprobación.

En los dos modos, primero hace un inventario de solo lectura, después propone, espera tu aprobación, aplica y comprueba.

### Por qué no basta con las herramientas oficiales

Las usa: `prompt-audit` de la skill `claude-api`, `/doctor prompt-audit` y `/skill-doctor`, e integra sus resultados. Pero ninguna cubre:

- la **convivencia de Claude y Codex** en un mismo repositorio (quién lee `AGENTS.md`, qué rompe un `CLAUDE.local.md`, equivalencias de configuración);
- los **hooks y permisos** reales, incluidas trampas silenciosas como que Codex en Windows convierte el bloqueo de un hook en «hook failed», que deja pasar;
- los **secretos** según el sistema operativo (en Windows nativo no hay sandbox para la shell de Claude);
- la verificación, el estado de las tareas largas y los equipos de agentes.

### Ejemplo

[Auditoría de este mismo repositorio](pruebas/este-proyecto/auditoria.md), hecha con la skill. Un extracto:

| Capa | Estado | Resumen |
|---|---|---|
| 1 Instrucciones | ⚠ | `CLAUDE.md` breve y claro, pero sin comandos ni «terminado» |
| 4 Reglas de acción | ✗ | Sin permisos ni hooks; Windows sin sandbox |
| 5 Verificación | ✗ | Scripts sin pruebas automáticas |
| 8 Código y commits | ✗ | Sin git |

## Instalación

### Claude Code (plugin)

```text
/plugin marketplace add ceherrejon/race-engineer
/plugin install race-engineer@race-engineer
```

Opcional, la skill auxiliar que limpia comentarios de código existente:

```text
/plugin install limpiar-comentarios@race-engineer
```

### Codex (o Claude Code sin plugin)

Clona el repositorio y enlaza la carpeta de la skill en tu carpeta de skills de usuario. Así las actualizaciones llegan con un `git pull`:

```bash
git clone https://github.com/ceherrejon/race-engineer.git
```

```bash
ln -s "$PWD/race-engineer/skill/race-engineer" ~/.agents/skills/race-engineer
```

En Windows, en lugar de un enlace, usa una unión de directorios (no necesita permisos de administrador). Los comandos para cada sistema y para Claude Code están en [skill/README.md](skill/README.md).

## Uso

- **Claude Code:** `/race-engineer:race-engineer` si la instalaste como plugin (o `/race-engineer` si la enlazaste a mano), o pídelo con tus palabras: «revisa la configuración de agentes de este proyecto», «prepara este proyecto para Claude y Codex».
- **Codex:** `$race-engineer` o la misma petición en lenguaje natural.

Trabaja en el idioma del equipo. Las plantillas están en español y `AGENTS.md` también en inglés.

## Requisitos

- Python 3.11 o superior (los scripts solo usan la biblioteca estándar) y git.
- Claude Code 2.1.277 o superior para la lectura nativa de `AGENTS.md`; 2.1.283 o superior para `/doctor prompt-audit`.

## Estado

- **v1.1.** Probada en vivo en Windows 11 con Claude Code 2.1.289 y Codex 0.160: proyecto nuevo, auditoría de un proyecto real y barreras de secretos verificadas en las dos herramientas.
- Las pruebas automáticas de los scripts corren en Linux, macOS y Windows en cada cambio. La prueba en vivo con los agentes en macOS y Linux sigue pendiente.
- La guardia de secretos es una **barandilla contra accidentes, no una frontera de seguridad**: un comando ofuscado la esquiva. Lo explica [su propio código](skill/race-engineer/scripts/guardia.py).

## Cómo se construyó

Cada comprobación de la skill cita una práctica de la base de conocimiento, y cada práctica cita sus fuentes:

| Ruta | Contenido |
|---|---|
| [`skill/`](skill/) | Las skills que se instalan |
| [`conocimiento/`](conocimiento/) | Prácticas atómicas por tema, cada una con su confianza y sus fuentes |
| [`fuentes/`](fuentes/) | Una ficha por fuente analizada (documentación oficial, artículos, pruebas propias), con un [índice](fuentes/INDICE.md) |
| [`pruebas/`](pruebas/) | Resultados de probar la skill y los experimentos |
| [`tests/`](tests/) | Pruebas automáticas de los scripts y del empaquetado |

## Contribuir

- Las fuentes nuevas siguen el protocolo de [AGENTS.md](AGENTS.md): ficha, prácticas atómicas y, cuando maduran, la skill.
- Antes de proponer un cambio, ejecuta las pruebas:

```bash
python -m unittest discover -s tests
```

## Licencia

[MIT](LICENSE).
