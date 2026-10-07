---
name: race-engineer
description: Prepara un proyecto nuevo o audita uno existente para trabajar con Claude Code y/o Codex, cubriendo instrucciones (CLAUDE.md, AGENTS.md), skills, permisos, hooks, sandbox, secretos, subagentes, MCP, verificación y estado de tareas largas. Úsala al iniciar un proyecto con agentes, cuando el usuario pida revisar, mejorar o actualizar la configuración o las instrucciones de agentes de un proyecto, al combinar Claude y Codex en un mismo repositorio, o tras cambiar de modelo. Also use it to set up or audit a project's agent configuration (Claude Code, Codex, AGENTS.md, CLAUDE.md, hooks, permissions) in any language.
---

# Race Engineer · setup y auditoría de proyectos para agentes

El objetivo es que cada proyecto tenga, en el formato de cada herramienta que use, lo necesario para que el agente trabaje bien y con seguridad. Las capas están en `references/checklist.md`:

1. instrucciones;
2. procedimientos;
3. fuentes externas;
4. reglas de acción;
5. verificación;
6. modelo y esfuerzo;
7. terminado y estado;
8. código y commits;
9. equipo de agentes;
- transversales.

## Principios

- **No duplicar herramientas oficiales.** Si existen, se usan y se integran sus resultados (`references/herramientas.md`). Esta skill aporta lo que no cubren: convivencia Claude/Codex, hooks y permisos, secretos según el sistema operativo, y las capas 5 a 9.
- **Deducir antes de preguntar.** El inventario fija los supuestos y estos se declaran al principio. Se pregunta solo lo que no se pueda deducir, en un único mensaje.
- **Proponer antes de aplicar.** No se escribe nada sin aprobación. El nivel de usuario (`~/.claude`, `~/.codex`) solo se informa, salvo que el usuario pida cambiarlo; sus contradicciones con el proyecto van a «Necesita tu decisión».
- **Poco y priorizado:** como mucho 1–2 hallazgos por capa, y cada uno con su evidencia.
- **Nunca abrir secretos.** Ni `.env`, ni claves, ni `auth.json`. De los settings, solo las claves de permisos y hooks.
- **Sin nombres de modelo fijados** en lo que se genera.
- **Mover, no borrar.** Si unas instrucciones son largas, lo propio de una zona va a `.claude/rules/` o a un `AGENTS.md` anidado, y lo ocasional a skills. Solo se borra lo obsoleto o genérico.
- **Idioma del equipo.** Todo lo que se genera (instrucciones, guía de incorporación, informe) va en el idioma del equipo: el de las instrucciones que ya existan o el del usuario. Las plantillas están en español, y `AGENTS.md` también en inglés (`templates/en/`). Para cualquier otro idioma se traducen conservando la estructura.
- **Portable para todo el equipo.** Lo versionado debe funcionar en cualquier máquina: nada de rutas absolutas ni de usuario, y en los hooks `$CLAUDE_PROJECT_DIR` (Claude) y `$(git rev-parse --show-toplevel)` (Codex). Lo que cada persona tiene que hacer en su máquina se escribe en `docs/agentes/INCORPORACION.md`.
- **Hechos antes que prosa.** Si una regla escrita la puede imponer la herramienta, se propone la barrera y la prosa se reduce a una línea. Ejemplos: un hook, un permiso, el sandbox de Codex que deja `.git` en solo lectura.

## Paso 0 · Inventario y supuestos (siempre)

1. Ejecutar `python3 <carpeta de esta skill>/scripts/inventario.py <ruta del proyecto>` (o `python` si no existe `python3`) (con `--json` si se va a procesar). Es de solo lectura y devuelve:
   - herramientas, versiones y sistema operativo;
   - stack;
   - código que llama a modelos;
   - archivos de instrucciones y avisos de «quién lee qué»;
   - rutas citadas que no existen;
   - configuración de Claude y Codex (proyecto y usuario, incluidos el modelo y el esfuerzo por defecto de Codex);
   - confianza del proyecto en Codex;
   - secretos en el árbol (versionados, ignorados, cubiertos o no por la guardia) y secretos fuera del árbol citados en instrucciones o código.
2. Decidir el **modo**: **nuevo** si no hay configuración de agentes; **existente** en caso contrario.
3. Escribir los supuestos:
   - herramientas;
   - reparto entre Claude y Codex (instrucciones comunes, o papeles distintos como «Claude dirige, Codex ejecuta»);
   - **quién escribe el código**;
   - si Codex se usa con interfaz o en segundo plano;
   - si es un **equipo** y con qué sistemas operativos. Esto decide el intérprete de los hooks: `python3` por defecto, que existe en macOS y Linux, y en Windows con el gestor `py`. Si alguien no lo tiene, se acuerda otro y se anota en la guía de incorporación;
   - el idioma de trabajo;
   - alcance;
   - si la auditoría es **solo lectura**.
4. Si los archivos de instrucciones o configuración tienen cambios sin commit, avisarlo: conviene hacer commit antes de aplicar, porque `git blame` no ordena lo que no está en el historial.
5. Los avisos del inventario son **candidatos**, no veredictos. Por ejemplo, un `AGENTS.md` que Claude no lee es correcto si los papeles son distintos a propósito, y una ruta «rota» puede ser generada. Se confirman leyendo.

## Modo A · Proyecto nuevo

1. **Propuesta de archivos.** Partir de `templates/` y rellenar lo que el inventario permita: comandos según el stack y estructura real.
   - Las secciones opcionales sin datos se borran.
   - «Comandos» y «Terminado significa» son obligatorias: lo que falte se pregunta.

   | Capa | Claude Code | Codex |
   |---|---|---|
   | 1 Instrucciones | `AGENTS.md` (contenido común). `CLAUDE.md` con `@AGENTS.md` **solo** si hay algo propio de Claude o la versión es anterior a 2.1.277 | `AGENTS.md` |
   | 4 Reglas de acción | `.claude/settings.json` (permisos + hook) | `.codex/config.toml` (hook con ruta portable) + la confianza del proyecto, que marca cada persona (guía de incorporación) |
   | 4 Secretos | `.agents/hooks/guardia.py` (copia de `scripts/guardia.py`) + `.agents/guardia.txt` con `bloquear:` para cada secreto que el inventario marque como no cubierto o citado fuera del árbol, y `preguntar:` para despliegues y publicaciones. En `.gitignore`, los que falten. Si un secreto está **versionado**: proponer `git rm --cached` y rotarlo («Necesita tu decisión») | igual (mismo script) |
   | 5 Verificación | `.claude/agents/revisor.md` | `.codex/agents/revisor.toml` |
   | 7 Estado | `docs/agentes/plantillas/progress.md` y `tarea.md` | igual |
   | Incorporación | `docs/agentes/INCORPORACION.md` (de `templates/INCORPORACION.md`, con el intérprete y un secreto **falso** de prueba ignorado por git) | igual: incluye la confianza del proyecto y la aprobación del hook en el CLI, que son pasos de cada persona |
   | 8 Código | La sección «Dónde va cada explicación» ya va en `AGENTS.md` | igual |
   | 9 Equipo | Solo si el usuario lo pide: preguntar el flujo manual, aplicar P-EQU-01/02 y `templates/fragmentos/traspaso-entre-agentes.md` | igual |

2. **Capas 2, 3 y 6:** solo si hay señales en el repo. Se usa el criterio de «Señal → recomendación» de `references/herramientas.md` y se descarta lo que ya está instalado.
3. **Si hay código que llama a modelos (capa T2):** invocar la skill `claude-api` con `prompt-audit <ruta del código>` y llevar sus hallazgos al informe como recomendaciones. No se cambia código de la app sin aprobación aparte.
4. **Mostrar** el árbol de archivos y el contenido; esperar aprobación. Después **escribir** lo aprobado y **comprobar**.

## Modo B · Proyecto existente (auditoría)

1. **Herramientas oficiales** (`references/herramientas.md`):
   - **Auditoría de texto:** invocar la skill `claude-api` con `prompt-audit <ruta del proyecto>`, **una sola vez**. Cubre las instrucciones y el código que llama a modelos. Su informe completo va como **anexo**; al informe principal pasan solo los hallazgos de mayor impacto, ubicados en su capa.
   - **Comandos del usuario:** `/doctor prompt-audit`, que incluye el nivel de usuario, y `/skill-doctor`. Se sugieren al usuario y se marcan como pendientes.
2. **Recorrer `references/checklist.md`** capa por capa:
   - las comprobaciones ⚙ salen del inventario y el resto se resuelve leyendo;
   - contradicciones entre archivos del proyecto: `git blame` y gana la más reciente, como propuesta;
   - contradicciones con el nivel de usuario: a «Necesita tu decisión»;
   - equivalencias y trampas silenciosas: `references/equivalencias.md`.
3. **Comentarios (capa 8):** leer una muestra de ~20 comentarios del código fuente (sin recursos tipo `strings.xml`).
   - Si la skill `limpiar-comentarios` está instalada, su script `comentarios.py inventario` da la muestra y los totales por categoría.
   - Si la mayoría narra lo que hace el código, proponer la limpieza como tarea aparte: con esa skill si existe, o a mano, sin mezclarla con cambios de código.
4. **Informe** con `references/informe.md`. En auditorías de solo lectura, las comprobaciones que exigen ejecutar se marcan **⏸ pendiente**, no ✓.
5. **Aplicar** solo lo aprobado, un cambio por bloque. Después, **comprobar**.

## Comprobar (ambos modos)

- **Instrucciones cargadas.** Son comandos del usuario en una sesión interactiva; un subagente no puede ejecutarlos:
  - Claude: `/context` y `/memory`; al iniciar, la línea «AGENTS.md loaded».
  - Codex: primero marcar el proyecto como de confianza; después, **en el CLI** (en la app no funciona), aprobar los hooks con `/hooks`. Al arrancar, la opción por defecto es no aprobarlos. Por último, `/status` y `/debug-config`.
- **Barreras:**
  - pedir una acción inofensiva que debería bloquearse (leer un `.env` **falso**) y confirmar el mensaje de bloqueo **en cada herramienta**. Un «hook failed» no es un bloqueo: deja pasar;
  - probar `guardia.py` con entradas JSON simuladas;
  - en Windows, confirmar que el hook se dispara también con PowerShell y que `$CLAUDE_PROJECT_DIR` se expande.
- **Comandos documentados:** ejecutar uno barato. Si falla:
  - no se tocan manifiestos ni código fuera de la propuesta aprobada;
  - se documenta el comando que sí funciona;
  - el arreglo va a «Necesita tu decisión».
- **Lo no verificado** se dice explícitamente en el cierre.

## Casos especiales

- **Codex escribe el código:**
  - los chequeos automáticos van en pruebas, en hooks de Codex o en un hook `Stop` de Claude sobre `git diff --name-only`, no en `PostToolUse` de Claude, que no ve sus cambios;
  - sus reglas tienen que estar en `AGENTS.md`, no solo en `CLAUDE.md`.
- **Codex en segundo plano** (`codex exec`, companion): `approval_policy = "on-request"` lo dejaría esperando. Para esas ejecuciones, `--sandbox workspace-write -a never`: el sandbox sigue limitando, solo se quitan las preguntas.

## Recursos

| Archivo | Para qué |
|---|---|
| `scripts/inventario.py` | Datos del proyecto y avisos deterministas (solo lectura; no escribe en `.git`) |
| `scripts/guardia.py` | Hook `PreToolUse` para Claude y Codex: bloquea secretos en rutas y comandos de shell; `preguntar:` para comandos delicados. Es una barandilla contra accidentes, no una frontera de seguridad |
| `references/checklist.md` | Comprobaciones por capa con impacto y práctica de referencia |
| `references/equivalencias.md` | Quién lee qué, tabla Claude ↔ Codex y trampas silenciosas |
| `references/herramientas.md` | Herramientas oficiales, sus límites y el criterio «señal → recomendación» |
| `references/informe.md` | Formato del informe de auditoría |
| `references/practicas.md` | Qué pide y por qué cada práctica citada (P-…, D-…, C-…). Se genera desde la base de conocimiento del proyecto de origen |
| `templates/` | `AGENTS.md` (también `en/AGENTS.md`), `CLAUDE.md`, `INCORPORACION.md`, `claude/settings.json`, `codex/config.toml`, revisores, regla por zona, `progress.md`, `tarea.md`, `guardia.txt`, fragmentos |

**Requisitos:** Python 3.11+ para los scripts y git en el proyecto, que lo necesitan el hook de Codex y la detección de secretos versionados. Probada en Windows 11 con Claude Code 2.1.289 y Codex 0.160. En macOS y Linux los scripts pasan las pruebas automáticas, pero la skill **todavía no se ha usado en vivo** con los agentes.
