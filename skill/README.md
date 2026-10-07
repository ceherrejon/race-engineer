# Skills

| Skill | Qué hace | Cuándo |
|---|---|---|
| [race-engineer](race-engineer/SKILL.md) | Prepara un proyecto nuevo o audita uno existente para Claude Code y/o Codex, por capas | Al empezar un proyecto, al revisar su configuración de agentes o al cambiar de modelo |
| [limpiar-comentarios](limpiar-comentarios/SKILL.md) | Limpia comentarios de código existente y verifica que solo cambiaron comentarios. **Opcional:** `race-engineer` la usa si está instalada | Como tarea aparte, cuando la auditoría detecta mucha narración |

Las dos siguen el estándar Agent Skills (`SKILL.md` con `name` y `description`), así que sirven en Claude Code y en Codex.

## Requisitos

- Python 3.11 o superior (los scripts solo usan la biblioteca estándar) y git.
- Para la lectura nativa de `AGENTS.md`: Claude Code 2.1.277 o superior. Para `/doctor prompt-audit`: 2.1.283 o superior.

## Instalación en Claude Code como plugin (recomendada)

```text
/plugin marketplace add ceherrejon/race-engineer
/plugin install race-engineer@race-engineer
/plugin install limpiar-comentarios@race-engineer
```

La segunda es opcional. Para actualizar: `/plugin marketplace update race-engineer`. Con el plugin, la skill se invoca como `/race-engineer:race-engineer`.

## Instalación manual (Codex, o Claude Code sin plugin)

| Herramienta | Carpeta de skills de usuario |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` (`~/.codex/skills` está obsoleta) |

Lo recomendable es **enlazar** la carpeta de cada skill en lugar de copiarla, para que las actualizaciones lleguen solas. Sustituye `<ruta>` por la carpeta donde tengas este repositorio.

**macOS / Linux**

```bash
ln -s "<ruta>/skill/race-engineer" ~/.claude/skills/race-engineer
```

```bash
ln -s "<ruta>/skill/race-engineer" ~/.agents/skills/race-engineer
```

**Windows** (unión de directorios; no necesita permisos de administrador). En PowerShell o cmd:

```bash
cmd /c mklink /J "%USERPROFILE%\.claude\skills\race-engineer" "<ruta>\skill\race-engineer"
```

```bash
cmd /c mklink /J "%USERPROFILE%\.agents\skills\race-engineer" "<ruta>\skill\race-engineer"
```

Repite lo mismo para `limpiar-comentarios` si la quieres. Si prefieres copiar en vez de enlazar, copia la carpeta entera: la skill necesita sus `scripts/`, `references/` y `templates/`.

## Uso

- **Claude Code:** `/race-engineer` (o `/race-engineer:race-engineer` si la instalaste como plugin), o pídelo en lenguaje natural: «revisa la configuración de agentes de este proyecto», «prepara este proyecto para Claude y Codex».
- **Codex:** `$race-engineer` o la misma petición en lenguaje natural.

Funciona en el idioma en que trabaje el equipo; las plantillas están en español, y `AGENTS.md` también en inglés.

## Estado

- **Probada** en Windows 11 con Claude Code 2.1.289 y Codex 0.160: proyecto nuevo, auditoría de un proyecto real y barreras verificadas en vivo en las dos herramientas.
- **Pruebas automáticas** de los scripts en Linux, macOS y Windows (`tests/`, GitHub Actions). La prueba en vivo con los agentes en macOS y Linux sigue pendiente.

## Mantenimiento (para quien mantiene este repositorio)

- **Prácticas citadas:** las comprobaciones de `race-engineer/references/checklist.md` citan prácticas de `../conocimiento/`. Si una cambia, actualiza la comprobación y regenera `references/practicas.md` con `python3 herramientas/generar_practicas.py`.
- **Revisiones periódicas:** las herramientas cambian rápido, así que conviene repasar `references/equivalencias.md` y `references/herramientas.md` cada pocos meses.
