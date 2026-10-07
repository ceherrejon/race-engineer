# 06 · Herramientas existentes de configuración y auditoría

Herramientas que ya hacen parte del trabajo. Nuestra skill debería **apoyarse en ellas** cuando estén disponibles, no reimplementarlas (ver D-01).

### P-HER-01 · `claude-code-setup` (plugin oficial)  `[Claude]`
- **Qué hace:** Analiza el repositorio y recomienda 1–2 automatizaciones por categoría (MCP, skills, hooks, subagentes, plugins), con fragmentos de configuración. Solo lectura.
- **Instalación:** `/plugin install claude-code-setup@claude-plugins-official`
- **Uso:** «recomienda automatizaciones para este proyecto», «ayúdame a configurar Claude Code».
- **Cuándo usarla:** Al preparar un proyecto nuevo o al revisar uno existente, para la parte de automatización.
- **Limitaciones observadas en el proyecto piloto (F004):**
  - La detección de la Fase 1 está pensada para npm y Python: en un proyecto Android/Gradle solo habría visto el `package.json` del servidor.
  - Sus tablas no tienen filas para móvil ni hooks de Kotlin.
  - No cruza con los plugins ni la configuración de usuario ya instalados, y recomienda duplicados.
  - Supone que el código lo escribe Claude.
  - No revisa la calidad de CLAUDE.md, no cubre Codex y no aplica cambios.
- **Valor real:** el criterio «señal del repo → 1–2 recomendaciones» y su catálogo de patrones, siempre que el agente adapte la detección al stack.
- **Fuentes:** F001, F004 · **Confianza:** alta

### P-HER-02 · `/claude-api prompt-audit`  `[Claude]`
- **Qué hace:** Audita todo lo que llega al modelo como texto (CLAUDE.md, SKILL.md, reglas, descripciones de herramientas, código de llamadas a la API). Detecta patrones obsoletos (lenguaje de presión, andamiaje de razonamiento, redundancias, contradicciones, pasos rígidos, ejemplos sin marcar) y propone un parche sin aplicarlo.
- **Requisito:** Claude Code v2.1.221 o posterior (skill `claude-api`, incluida de serie).
- **Cuándo usarla:** Al revisar un proyecto existente y siempre que cambie el modelo.
- **Procedimiento:** guía completa en `claude-api/shared/prompt-audit.md`, resumida en F003. Entrega un informe con `archivo:línea` y confianza, y un parche que no aplica por su cuenta.
- **Limitaciones:**
  - Sin argumentos no incluye `~/.claude/CLAUDE.md`.
  - No lee `settings*.json` ni `.mcp.json` (pueden contener secretos), así que **no audita hooks ni permisos**.
  - Juzga `AGENTS.md` solo contra el repositorio, no contra los modelos de Codex.
  - Sus propuestas son hipótesis que conviene validar.
- **Valor real observado (F004):** lo más útil fue el Grupo 2, que encontró contradicciones entre archivos de instrucciones, datos que el propio repo desmiente y referencias rotas, todo comprobado con `git blame` y `test -e`. En un CLAUDE.md bien escrito encuentra poco del Grupo 1.
- **Cómo ejecutarla:** dentro de una sesión.
  - **`/doctor prompt-audit`** (v2.1.283+, la vía documentada en `memory.md`) cubre por defecto `CLAUDE.md`, `CLAUDE.local.md` y `AGENTS.md`, además de las reglas, skills, comandos, subagentes y estilos de salida de `.claude/` **y de `~/.claude/`**. Se le puede pasar una ruta.
  - `/claude-api prompt-audit <ruta>` usa el mismo motor; sin argumentos no incluye la configuración de usuario.
  - En modo headless (`claude -p`) hace falta que el CLI tenga la sesión iniciada.
- **Fuentes:** F002, F003, F004, F010 · **Confianza:** alta

### P-HER-03 · `/skill-doctor`  `[Claude]`
- **Qué hace:** Muestra cuánto contexto cuesta cada skill y cuánto se usó en los últimos 7 días (tokens y usos), y avisa de skills nunca invocadas y plugins sin usar.
- **Requisito:** Claude Code v2.1.252 o posterior.
- **Cuándo usarla:** En la auditoría de un proyecto existente, para decidir qué skills o plugins desactivar. Complementa a P-SKL-04: sacar procedimientos a skills tiene sentido si esas skills se usan.
- **Fuentes:** F007 (verificada en `commands.md`) · **Confianza:** alta

### P-HER-04 · `/import` de Codex  `[Codex]`
- **Qué hace:** Copia `CLAUDE.md` a `AGENTS.md` y `.claude/skills` a `.agents/skills`. Convierte `settings.json` a `config.toml`, junto con hooks, MCP y subagentes, y transforma los slash commands en skills. También importa desde Cursor.
- **Cuándo usarla:** Para arrancar la configuración de Codex en un proyecto que ya tiene la de Claude. Después hay que revisar el resultado: copia, no mantiene sincronizado, así que tras usarla hay que decidir cuál es la fuente de verdad (P-INS-04).
- **Fuentes:** F010 (`learn.chatgpt.com/docs/import`) · **Confianza:** alta

## Pendientes de analizar

- `/init` (genera un CLAUDE.md inicial).
- ~~Equivalentes en Codex para auditar `AGENTS.md`~~: no hay ninguno oficial (F010). Es un hueco que cubre nuestra skill; `/doctor prompt-audit` de Claude sí incluye `AGENTS.md` en su alcance.

## Conflictos

(ninguno todavía)
