# Equivalencias Claude Code ↔ Codex

Verificado a 2026-10-07 (Claude Code 2.1.289, Codex CLI 0.160/0.161). Las dos herramientas cambian rápido: ante la duda, comprobar en `code.claude.com/docs` y en `learn.chatgpt.com/docs`.

## Quién lee qué

| Archivo | Claude Code | Codex |
|---|---|---|
| `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md` | Sí | No (solo si se añade a `project_doc_fallback_filenames` **y** falta `AGENTS.md`) |
| `AGENTS.md` | **Solo si no hay `CLAUDE.md` ni `CLAUDE.local.md`** en ese directorio o por encima (v2.1.277+), o si `CLAUDE.md` lo importa | Sí |
| `AGENTS.override.md` | **No** | Sí (sustituye a `AGENTS.md` en ese nivel) |
| `.agents/` (skills) | **No** | Sí |
| `.claude/` (skills, rules, agents) | Sí | No (`/import` lo convierte) |

**Recomendación:**
- **Contenido común:** va en `AGENTS.md`. Si hay algo propio de Claude, `CLAUDE.md` empieza con `@AGENTS.md` y añade solo eso.
- **Papeles distintos** (uno dirige y otro ejecuta): se aceptan dos archivos, siempre que cada uno diga a quién va dirigido y no se contradigan en lo común.
- **Nunca** poner reglas comunes en `AGENTS.override.md`.

## Tabla por capa

| Concepto | Claude Code | Codex |
|---|---|---|
| Instrucciones de usuario | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` (o `AGENTS.override.md`) |
| Instrucciones de proyecto | `CLAUDE.md` / `.claude/CLAUDE.md` en cada nivel; los de subcarpetas se cargan al tocarlas | `AGENTS.md` (o `AGENTS.override.md`) desde la raíz hasta el directorio actual, concatenados; se cargan al iniciar la sesión |
| Instrucciones locales sin versionar | `CLAUDE.local.md` | `AGENTS.override.md` (no está pensado para eso, pero sirve) |
| Imports | `@ruta` (hasta 4 niveles) | No existen; se citan otros archivos en el texto |
| Reglas por zona | `.claude/rules/*.md` con `paths:` | `AGENTS.md` anidados |
| Configuración de proyecto | `.claude/settings.json` (+ `settings.local.json`) | `.codex/config.toml` (solo en proyectos de confianza) |
| Configuración de usuario | `~/.claude/settings.json` | `~/.codex/config.toml`; perfiles en `~/.codex/<nombre>.config.toml` |
| Permisos | `permissions.allow/deny/ask` | `sandbox_mode` + `approval_policy` + reglas `rules/*.rules` (`prefix_rule`) |
| Sandbox | Bash sandbox: macOS, Linux, WSL2 | macOS (Seatbelt), Linux (bwrap + seccomp), **Windows nativo** (elevated/unelevated) |
| Hooks | `settings.json` → `hooks` | `config.toml` `[[hooks.<Evento>]]` o `hooks.json`; aprobación con `/hooks` |
| Skills de proyecto | `.claude/skills/<n>/SKILL.md` | `.agents/skills/<n>/SKILL.md` |
| Skills de usuario | `~/.claude/skills/` | `~/.agents/skills/` (`~/.codex/skills` está obsoleta) |
| Invocar una skill | `/nombre` | `$nombre` o `/skills` |
| Control de invocación | `disable-model-invocation`, `user-invocable` | `agents/openai.yaml` → `policy.allow_implicit_invocation` |
| Subagentes | `.claude/agents/*.md` (frontmatter YAML) | `.codex/agents/*.toml` (`name`, `description`, `developer_instructions`) |
| Comandos personalizados | Skills | Skills (`~/.codex/prompts` está obsoleto) |
| MCP | `.mcp.json` / `claude mcp add` | `[mcp_servers.x]` en config.toml / `codex mcp add` |
| Esfuerzo | `--effort`, `effort:` | `model_reasoning_effort` |
| Memoria automática | `~/.claude/projects/<p>/memory/` (activa) | `~/.codex/memories/` (apagada por defecto) |
| Objetivo de la tarea | `/goal` | `/goal` |
| Ver la configuración cargada | `/context`, `/permissions`, `/memory` | `/status`, `/debug-config` |
| Generar instrucciones iniciales | `/init` | `/init` |
| Auditar instrucciones | `/doctor prompt-audit` | No existe un equivalente oficial |
| Migrar de una a otra | — | `/import` (desde Claude Code o Cursor) |
| Modo no interactivo | `claude -p` | `codex exec` (sandbox de solo lectura por defecto) |

## Trampas silenciosas

- «Por encima» incluye las carpetas **superiores al repositorio**: un `CLAUDE.md` en `C:\Users\yo\Desktop\` cuenta. `~/.claude/CLAUDE.md` no cuenta. El inventario las revisa.

- Un `CLAUDE.local.md` personal hace que Claude deje de leer `AGENTS.md`. Se evita importándolo, o con `claude-md-and-agents-md` en `~/.claude/settings.json`.
- La capa `.codex/` del proyecto (config, hooks, reglas, agentes) **y** su `AGENTS.md` solo se cargan si el proyecto es de confianza.
- Codex lee `AGENTS.md` solo al iniciar la sesión: tras editarlo hay que reiniciar.
- Codex no expande `@imports`: en `AGENTS.md` se cita el archivo por su nombre.
- En `workspace-write`, `.git`, `.agents` y `.codex` son de solo lectura para Codex. Por eso «Codex no commitea» es un hecho del sandbox, no hace falta escribirlo como regla, y la guardia en `.agents/hooks/` no la puede modificar.
- Codex en segundo plano (`codex exec`, companion) con `approval_policy = "on-request"` se queda esperando: usar `-a never` manteniendo el sandbox.
- **Los hooks de proyecto de Codex no se ejecutan hasta aprobarlos en el CLI** (`/hooks`). En la app de escritorio, `/hooks` llega como mensaje, y al arrancar el CLI la opción por defecto es no aprobarlos. Mientras tanto, el sandbox no impide **leer** secretos.
- **En Windows, Codex lanza los hooks a través de PowerShell**, que convierte cualquier código de salida no cero en 1 («hook failed», deja pasar). Para bloquear hay que responder JSON (`permissionDecision: "deny"`) con código 0, como hace `scripts/guardia.py`. En las dos herramientas, un hook que falla deja pasar.
- Los hooks de Codex se aprueban con `/hooks` y la aprobación va ligada al hash: si el hook cambia, hay que volver a aprobarlo.
- Opciones obsoletas o retiradas en Codex:
  - `--full-auto` (usar `--sandbox workspace-write`);
  - `approval_policy = "untrusted"`;
  - perfiles dentro de `config.toml`;
  - `~/.codex/prompts`;
  - `~/.codex/skills`.
