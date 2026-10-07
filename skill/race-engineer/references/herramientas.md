# Herramientas oficiales que la skill usa en vez de duplicarlas

Si están disponibles, se ejecutan **dentro de la sesión** y sus resultados se integran en el informe. Si no lo están, se indica cómo obtenerlas.

- Las auditorías no se lanzan con `claude -p` ni `codex exec`: el CLI puede no tener la sesión iniciada aunque la app sí.
- Los comandos con `/` los ejecuta el usuario en una sesión interactiva.
- Las skills (como `claude-api`) las puede invocar el agente.

## Señal → recomendación (criterio de `claude-code-setup`, sin necesidad de instalarlo)

Como mucho 1–2 por categoría, solo con una señal real en el repo y descartando lo que ya existe:

| Señal en el repo | Recomendación |
|---|---|
| Formateador configurado (Prettier, Black, ktlint…) | Hook tras editar que lo ejecute. Si escribe Codex, hook `Stop` sobre `git diff` |
| Linter / tipos (ESLint, Ruff, tsc) | Igual que el formateador |
| Pruebas rápidas | Hook o paso de «Terminado» que las ejecute. Si tardan minutos (Gradle), solo en «Terminado» |
| Secretos (`.env`, claves, credenciales, carpetas de claves fuera del árbol) | Guardia `PreToolUse` + patrones del proyecto |
| Despliegue o publicación (wrangler, npm publish, fastlane…) | `preguntar:` en la guardia o `ask` en permisos; skill de despliegue con `disable-model-invocation` |
| Procedimiento que se repite a mano (release, migraciones) | Skill del proyecto con un script de verificación |
| Librerías recientes o de API cambiante | MCP de documentación (p. ej. context7), solo si de verdad se consulta |
| Servicio externo que se consulta a menudo (base de datos, observabilidad) | MCP en solo lectura; las escrituras con aprobación |
| Revisión de entregas o auditorías repetidas | Subagente revisor de solo lectura |
| Prueba en dispositivo o emulador | Subagente con el procedimiento fijo; sin builds concurrentes |

| Herramienta | Qué aporta | Requisito | Capa |
|---|---|---|---|
| `/doctor prompt-audit [ruta]` | Auditoría del texto de instrucciones (patrones antiguos, rutas inexistentes, contradicciones) con informe y parche propuesto. Por defecto cubre `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, reglas, skills, comandos y subagentes de `.claude/` **y de `~/.claude/`** | Claude Code v2.1.283+ | 1, 2 |
| `/claude-api prompt-audit <ruta>` | El mismo motor, aplicado a una ruta. Sirve para auditar los prompts y el código de peticiones de una app que llama a la API | Claude Code v2.1.221+ | T2 |
| `/claude-api migrate` | Migración de código de API a un modelo nuevo | — | T2 |
| `/skill-doctor` | Coste en contexto y uso a 7 días de cada skill; avisa de skills nunca usadas y plugins sin usar | Claude Code v2.1.252+ | 2 |
| Plugin `claude-code-setup` | Recomienda 1–2 automatizaciones por categoría (MCP, skills, hooks, subagentes) a partir de señales del repo | `/plugin install claude-code-setup@claude-plugins-official` | 2, 3, 4, 5 |
| `/init` (Claude y Codex) | Borrador inicial de `CLAUDE.md` / `AGENTS.md` a partir del repo | — | 1 |
| `/import` (Codex) | Copia `CLAUDE.md`, skills, settings, hooks, MCP y subagentes de Claude al formato de Codex | Codex reciente | T1 |
| `/context`, `/permissions`, `/agents`, `/mcp`, `/memory` (Claude) | Ver lo que está cargado de verdad | — | comprobación previa |
| `/status`, `/debug-config`, `/hooks` (Codex) | Ver capas de configuración, sandbox, aprobaciones y hooks aprobados | — | comprobación previa |

## Limitaciones de `claude-code-setup`, observadas en una prueba real

- Su detección del stack está pensada para npm y Python: hay que darle el stack que encontró el inventario (Gradle, Android, Workers…).
- No cruza con lo ya instalado: se descartan sus recomendaciones duplicadas.
- Supone que el código lo escribe Claude: si lo escribe Codex, los chequeos van en un hook `Stop`, no en `PostToolUse`.
- No revisa el texto de las instrucciones ni Codex.

## Lo que ninguna herramienta oficial cubre (lo aporta esta skill)

- Quién lee qué entre Claude y Codex, y las trampas silenciosas (`references/equivalencias.md`).
- La auditoría de `AGENTS.md` desde el lado de Codex: proyecto de confianza, límite de 32 KiB, `AGENTS.override.md`.
- Hooks, permisos y sandbox existentes. `prompt-audit` no lee los settings, porque pueden contener secretos.
- Secretos según el sistema operativo y la guardia de shell en Windows.
- Capas de verificación, estado, comentarios y equipos de agentes.
