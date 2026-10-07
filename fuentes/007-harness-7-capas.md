# F007 · «Make Opus 5.5 Finish Long Tasks: A Reusable Harness Engineering Setup»

- **Tipo:** artículo en X
- **Origen:** https://x.com/beamnxw/status/2107522996046905797, leído con el navegador integrado
- **Autor:** @beamnxw
- **Fecha de la fuente:** 2026-10-06
- **Fecha de incorporación:** 2026-10-07
- **Aplica a:** Claude (las funciones). La estructura por capas y la nota de progreso aplican a Ambos.
- **Calidad percibida:** alta. Contrasté 16 afirmaciones técnicas con la documentación oficial de Claude Code (code.claude.com/docs):
  - 14 verificadas;
  - 1 parcial: el sandbox de Bash no existe en Windows nativo;
  - 1 sin dato: la versión en la que apareció `/goal`.

## Resumen

Un *harness* es todo lo que rodea al modelo: instrucciones, herramientas, permisos, estado y verificaciones. El artículo lo organiza en 7 capas, cada una con su sitio en Claude Code. El ejemplo es un flujo de redacción con `sources/`, `drafts/` y `published/`. La idea central: antes de una tarea larga, decidir qué resultado se podrá abrir, qué evidencia se podrá revisar y qué progreso quedará guardado para continuar otro día.

1. **Hechos del proyecto** (`CLAUDE.md`):
   - solo lo que sigue siendo útil entre tareas; lo temporal va con la tarea;
   - los hechos llevan su fuente y la fecha en que se verificaron;
   - una preferencia descubierta en un borrador solo se convierte en regla tras confirmarla;
   - los `@imports` se cargan igual al inicio, así que los procedimientos ocasionales van a skills.
2. **Procedimiento repetido** (skill con `$ARGUMENTS`):
   - cada paso tiene un resultado observable;
   - la publicación va separada de la preparación;
   - cuando una corrección se repite, se edita la skill.
3. **Fuentes** (MCP):
   - solo cuando sirve a un paso concreto;
   - antes de depender de él, se prueba recuperando un elemento conocido;
   - se indica qué extraer y qué acciones puede hacer;
   - se desactiva lo que no se usa.
4. **Reglas de acción:**
   - `permissions.deny` para lectura y edición;
   - un hook `PreToolUse` cuando la decisión depende de los argumentos;
   - comprobar las reglas efectivas con `/permissions` y con una prueba inofensiva que deba ser bloqueada;
   - los permisos de archivo no cubren procesos arbitrarios;
   - ante un timeout en una escritura externa, mirar el destino antes de reintentar.
5. **Revisor que devuelve evidencia:**
   - subagente con herramientas de solo lectura y `effort: high`;
   - tabla de afirmación, veredicto (verificada / incorrecta / sin resolver), fuente y corrección;
   - el agente principal corrige;
   - se comprueba el resultado guardado, no lo que dice la conversación.
6. **Esfuerzo:**
   - se configura (`--effort`, frontmatter de skills y subagentes), no se pide en prosa;
   - `medium` por defecto en la sesión principal y `high` para el revisor;
   - cada cambio de esfuerzo se decide midiendo una tarea concreta.
7. **Qué debe demostrar la ejecución:**
   - `/goal` con una condición de terminado basada en archivos y evidencia;
   - el límite de turnos lo evalúa el modelo, así que los límites estrictos requieren controles de ejecución;
   - `/rewind` no deshace los cambios hechos por la shell; git sí.

**Además:**
- `progress.md` con una estructura fija (tarea, salidas, completado, decisiones, pendientes, siguiente acción), y una prueba de que una sesión nueva sabe continuar desde ahí;
- comprobación previa con `/context`, `/agents` y `/permissions`;
- medir sobre el trabajo aceptado, incluido el tiempo de revisión y las correcciones, cambiando una sola pieza cada vez.

## Verificación contra la documentación oficial (resumen)

| Afirmación | Resultado |
|---|---|
| `.claude/rules/*.md` con frontmatter `paths:` se cargan al tocar esos archivos; sin `paths:`, al inicio | Verificada |
| Los `@imports` se cargan al inicio (máx. 4 niveles; rutas relativas al archivo que importa) | Verificada |
| Los `CLAUDE.md` de subcarpetas se cargan cuando Claude usa Read/Write/Edit allí | Verificada |
| Tras compactar se recarga el contexto del proyecto desde disco | Verificada |
| Skills: `$ARGUMENTS`, `$0`, `$1`, `${CLAUDE_SKILL_DIR}`; campos `disable-model-invocation`, `user-invocable`, `context: fork`, `allowed-tools`, `model`, `effort` | Verificada |
| Subagentes: `name`, `description`, `tools`, `model`, `effort`, `permissionMode`, `maxTurns` | Verificada |
| `claude --model … --effort low/medium/high/xhigh/max` | Verificada. En Opus 5.5, Sonnet 5.5 y Fable 5.1, cambiar el esfuerzo en Claude Code **conserva la caché**. |
| Los permisos Edit/Read no frenan scripts arbitrarios; existe el «Bash sandbox» | Parcial: el sandbox **solo funciona en macOS, Linux y WSL2**, no en Windows nativo, y no cubre las herramientas de archivo ni los MCP. |
| `PreToolUse` puede permitir, denegar o preguntar según la entrada | Verificada |
| `/goal [condición\|clear]` | Existe; la versión en que apareció no está documentada |
| `/rewind` solo restaura ediciones de Edit/Write | Verificada |
| `/memory`, `/context`, `/agents`, `/permissions`, `/mcp`, `/usage` | Verificada |
| Memoria automática en `~/.claude/projects/<proyecto>/memory/`; se desactiva con `autoMemoryEnabled: false` o `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` | Verificada |
| (pista F006) `promptCacheTtl`: `5m` o `1h`; con suscripción, 1 h en la conversación principal y 5 m en el resto; con API key, 5 m en todo; `subagentPromptCacheTtl` para los subagentes; v2.1.242+ | Verificada. `modelPicker` no aparece en la referencia de ajustes. |
| (pista F002) `/skill-doctor`: coste en contexto y uso a 7 días de cada skill, skills nunca invocadas, plugins sin usar; v2.1.252+ | Verificada |

URLs principales: `code.claude.com/docs/en/` → `memory.md`, `skills.md`, `sub-agents.md`, `cli-reference.md`, `sandboxing.md`, `hooks-guide.md`, `checkpointing.md`, `commands.md`, `prompt-caching.md`, `mcp.md`.

## Prácticas extraídas

| ID | Archivo | Tipo |
|---|---|---|
| P-INS-03 | 01 | Refuerza (sube a alta) |
| P-INS-18, P-INS-19 | 01 | Nuevas |
| P-SKL-06 | 02 | Refuerza (+ campos verificados) |
| P-SKL-09 | 02 | Nueva |
| P-AUT-06 | 03 | Sube a alta (verificada) |
| P-AUT-07 a P-AUT-09 | 03 | Nuevas |
| P-SUB-02 | 04 | Refuerza (campos verificados) |
| P-SUB-03 | 04 | Nueva |
| P-MCP-02 | 04 | Nueva |
| P-FLU-03 | 05 | Refuerza |
| P-FLU-08 a P-FLU-11 | 05 | Nuevas |
| P-HER-03 | 06 | Nueva (`/skill-doctor`) |
| C-04 | 07 | Matiz sobre F006 (esfuerzo y caché) |
| D-09 | 00 | Nueva: estructura de la auditoría por capas |
