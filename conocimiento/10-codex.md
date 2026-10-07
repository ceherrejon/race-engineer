# 10 · Codex y la convivencia con Claude Code

Verificado contra la documentación oficial de Codex (`learn.chatgpt.com/docs`), el código de `codex-rs` (v0.161.0) y el CLI instalado (0.160.0), a 2026-10-07 (F010). Codex cambia rápido: conviene volver a verificar cada pocos meses.

## Tabla de equivalencias

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

## Prácticas

### P-CDX-01 · Cómo carga Codex los AGENTS.md  `[Codex]`
- **Qué:**
  - **Orden de carga:**
    - global: `~/.codex/AGENTS.override.md` si existe; si no, `AGENTS.md`;
    - después, desde la raíz del proyecto (marcador `.git`, configurable con `project_root_markers`) hasta el directorio actual, **un archivo por directorio**: `AGENTS.override.md` > `AGENTS.md` > nombres de `project_doc_fallback_filenames`;
    - se concatenan de la raíz hacia abajo; el más cercano va al final y prevalece.
  - **Límite:** `project_doc_max_bytes` = 32 KiB **en total**; lo que pasa de ahí no se carga.
  - **Recarga:** solo al iniciar la sesión. Tras editar, hay que reiniciar Codex.
  - **Imports:** no hay.
  - **Proyectos de confianza:** según el código, si el proyecto no es de confianza, el AGENTS.md del proyecto no se carga.
- **Cómo verificarla:** `codex --ask-for-approval never "Summarize the current instructions."`, o revisar `codex-tui.log` con `-c log_dir=...`.
- **Fuentes:** F010 · **Confianza:** alta

### P-CDX-02 · Configuración por proyecto en `.codex/`, solo si el proyecto es de confianza  `[Codex]`
- **Qué:**
  - `.codex/config.toml`, `.codex/hooks.json`, `.codex/rules/` y `.codex/agents/` solo se aplican si `[projects."<ruta>"] trust_level = "trusted"`.
  - En el config de proyecto se ignoran `notify`, `profile(s)`, `model_provider(s)` y las URLs base.
  - **Precedencia:** CLI y `-c` > proyecto > perfil > usuario > nube gestionada > `/etc/codex` > valores por defecto. `/debug-config` muestra las capas.
  - Los perfiles son archivos `~/.codex/<nombre>.config.toml`; desde la 0.134 ya no se leen `[profiles.x]` dentro de config.toml.
- **Por qué:** Si el proyecto no es de confianza, la configuración versionada se ignora en silencio.
- **Fuentes:** F010 · **Confianza:** alta

### P-CDX-03 · Sandbox y aprobaciones  `[Codex]`
- **Qué:**
  - **Combinación recomendada** en repos con git: `sandbox_mode = "workspace-write"` + `approval_policy = "on-request"` (el preset por defecto). Sin git, `read-only`.
  - **Red:** apagada por defecto (`[sandbox_workspace_write] network_access`).
  - **Rutas protegidas:** `.git`, `.agents` y `.codex` son de solo lectura dentro del espacio de trabajo, así que Codex pide aprobación para editar su propia configuración o sus skills.
  - **Windows nativo:** sandbox propio con `[windows] sandbox = "elevated"` (recomendado; se instala con `/setup-default-sandbox`) o `"unelevated"`.
  - **Opciones retiradas u obsoletas:** `--full-auto` (usar `--sandbox workspace-write`), `approval_policy = "untrusted"` (puede impedir el arranque) y `on-failure`.
  - **Opción nueva:** `--approve-for-me`, que envía las aprobaciones a una revisión automática.
  - `--yolo` / `--dangerously-bypass-approvals-and-sandbox` solo dentro de entornos ya aislados.
- **Fuentes:** F010 (opciones comprobadas en el CLI instalado) · **Confianza:** alta

### P-CDX-04 · Los secretos de las variables de entorno no se filtran por defecto  `[Codex]`
- **Qué:** `shell_environment_policy.ignore_default_excludes` vale `true` por defecto, así que las variables con `KEY`, `SECRET` o `TOKEN` en el nombre **sí** llegan a los comandos. Para evitarlo:
  - `ignore_default_excludes = false`;
  - o `inherit = "core"` con `set` para lo necesario;
  - o filtros explícitos.

  En CI, la credencial (`CODEX_API_KEY`) se pasa solo al paso de Codex.
- **Por qué:** Es la contraparte en Codex de P-AUT-04 y P-AUT-08.
- **Fuentes:** F010 · **Confianza:** alta

### P-CDX-05 · Revisar las reglas de ejecución acumuladas  `[Codex]`
- **Qué:** Las aprobaciones permanentes se guardan como `prefix_rule(...)` en `rules/*.rules` (usuario o proyecto). Conviene revisarlas de vez en cuando:
  - borrar las que aprobaban comandos de un solo uso, con rutas o scripts concretos;
  - sustituirlas por prefijos genéricos y seguros (por ejemplo `["rg"]`, `["git", "status"]`).
- **Por qué:** Con el tiempo se convierten en una lista larga que nadie revisa y que puede permitir más de lo pensado. Equivale a revisar `permissions.allow` en Claude.
- **Evidencia:** `~/.codex/rules/default.rules` del usuario ocupa 35 KB de aprobaciones puntuales (F010).
- **Fuentes:** F010 · **Confianza:** media

### P-CDX-06 · Skills en Codex  `[Codex]`
- **Qué:**
  - **Rutas:** `.agents/skills/` (proyecto, de la carpeta actual hacia arriba hasta la raíz) y `~/.agents/skills/` (usuario). `~/.codex/skills` está obsoleta pero se sigue leyendo.
  - **Frontmatter:** solo `name` y `description`; el resto se ignora.
  - **Política de invocación:** en `agents/openai.yaml`, `policy.allow_implicit_invocation: false`, que equivale a `disable-model-invocation`.
  - **Invocación:** `$nombre`.
  - Los prompts personalizados (`~/.codex/prompts`) están obsoletos: se migran a skills.
- **Fuentes:** F010 · **Confianza:** alta

### P-CDX-07 · Hooks en Codex  `[Codex]`
- **Qué:**
  - **Estado:** estables y activos por defecto.
  - **Eventos:** `SessionStart/End`, `SubagentStart/Stop`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact/PostCompact`, `UserPromptSubmit`, `Stop`, `Interrupt`.
  - **Matchers:** `Bash`, `apply_patch` (alias `Edit`/`Write`), `mcp__srv__tool`.
  - **Bloquear:** `permissionDecision: "deny"` o salir con código 2.
  - **Aprobación:** cada hook no gestionado se aprueba con `/hooks`, y la aprobación va ligada a su hash, así que si el hook cambia hay que volver a aprobarlo.
  - **Proyecto:** solo se cargan en proyectos de confianza.
  - **`notify`:** solo se dispara al terminar el turno y solo en la configuración de usuario.
- **Por qué:** El formato es casi idéntico al de Claude Code, así que un mismo script de hook puede servir para los dos.
- **Verificado en uso real** (CLI 0.160.0, Windows nativo; `pruebas/este-proyecto/auditoria.md`):
  - La aprobación se hace en el **CLI**. En la app de escritorio, `/hooks` llega al modelo como un mensaje.
  - Al arrancar con un hook nuevo, la opción seleccionada por defecto es «Continue without trusting (hooks won't run)».
  - Una vez aprobado, cambiar el script del hook **no** obliga a aprobarlo otra vez; cambiar la configuración, sí.
  - **En Windows, Codex lanza los hooks a través de PowerShell**, que convierte cualquier código de salida distinto de cero en 1. Un `exit 2` acaba como «hook failed» y **deja pasar**. Para bloquear hay que responder JSON con `hookSpecificOutput.permissionDecision = "deny"` y salir con 0.
  - El sandbox de Codex no protege la lectura: sin el hook aprobado, Codex leyó un `.env` de prueba.
- **Fuentes:** F010, prueba propia · **Confianza:** alta

### P-CDX-08 · Subagentes en Codex  `[Codex]`
- **Qué:**
  - **Definición:** archivos TOML en `.codex/agents/` o `~/.codex/agents/`.
  - **Campos obligatorios:** `name`, `description`, `developer_instructions`.
  - **Opcionales:** `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`.
  - **Integrados:** `default`, `worker`, `explorer`.
  - **Cuándo se crean:** solo cuando se pide o cuando lo indican las instrucciones o una skill.
  - **Valores globales en `[agents]`:** `max_concurrent_threads_per_session`, `default_subagent_model`, `default_subagent_reasoning_effort`.
- **Fuentes:** F010 · **Confianza:** alta

### P-CDX-09 · MCP en Codex  `[Codex]`
- **Qué:**
  - **Definición:** `[mcp_servers.<n>]` en config.toml, de usuario o de proyecto de confianza.
  - **Tipos:**
    - stdio: `command`, `args`, `env`, `env_vars`, `cwd`;
    - HTTP: `url`, `bearer_token_env_var`, `auth = "oauth"`.
  - **Herramientas:** `enabled_tools` y `disabled_tools` para limitarlas.
  - **Aprobación:** `default_tools_approval_mode` (`auto|prompt|writes|approve`), ajustable por herramienta.
  - **Arranque:** `required = true` hace que falle el arranque si el servidor no levanta, lo que sirve en CI.
- **Fuentes:** F010 · **Confianza:** alta

### P-CDX-10 · Memorias de Codex: apagadas por defecto; las reglas, en AGENTS.md  `[Codex]`
- **Qué:** Las memorias son experimentales (`[features] memories = true`, guardadas en `~/.codex/memories/`). La documentación pide mantener las reglas obligatorias en AGENTS.md y no en memorias.
- **Fuentes:** F010 · **Confianza:** alta

### P-CDX-11 · No fijar nombres de modelo en plantillas  `[Ambos]`
- **Qué:** Las plantillas de la skill no fijan `model` ni nombres de modelos (`gpt-6.1-sol`, `claude-opus-5-5`…). Lo dejan en la configuración de usuario, o con un comentario que diga dónde comprobar el actual.
- **Por qué:** Los nombres cambian cada pocos meses. Es la «narrativa con modelos fijados» de F003.
- **Fuentes:** F010, F003 · **Confianza:** media

## Conflictos

(ninguno todavía)
