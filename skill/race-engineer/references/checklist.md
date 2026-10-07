# Lista de revisión por capas

**Uso:** en un proyecto existente se recorre capa a capa; en uno nuevo sirve para decidir qué generar.

**Columnas:**
- **Aplica:** C = Claude Code, X = Codex, A = ambos.
- **Imp.** (impacto si falla):
  - **alto:** pierde instrucciones, expone secretos o deja pasar errores;
  - **medio:** desperdicia contexto o tiempo;
  - **bajo:** higiene.
- **Ref.:** prácticas en las que se apoya la comprobación. Qué pide cada una y por qué: `references/practicas.md`.

Las comprobaciones marcadas con ⚙ las resuelve `scripts/inventario.py`; el resto requiere leer o probar.

## 0 · Contexto (siempre primero)

| ID | Comprobación | Cómo verificar | Aplica | Imp. | Ref. |
|---|---|---|---|---|---|
| 0.1 ⚙ | Herramientas en uso y versiones | Inventario: `claude --version`, `codex --version`, archivos de configuración presentes | A | — | D-05, D-12 |
| 0.2 ⚙ | Sistema operativo | Inventario. En Windows nativo Claude no tiene sandbox de Bash (Codex sí) | A | — | D-10 |
| 0.3 ⚙ | Stack real, monorepo y CI | Inventario (marcadores de Gradle, Node, Python, Workers, .NET…) | A | — | D-07 |
| 0.4 | Quién escribe el código y cómo se reparten Claude y Codex | Leer las instrucciones; preguntar solo si no se deduce | A | — | D-07, D-12 |
| 0.5 ⚙ | ¿Hay código propio que llama a modelos? | Inventario. Si lo hay, se activa la capa T2 | A | — | 07 |

## 1 · Instrucciones y hechos

| ID | Comprobación | Cómo verificar | Aplica | Imp. | Ref. |
|---|---|---|---|---|---|
| 1.1 ⚙ | Cada herramienta lee las instrucciones que se cree que lee | Avisos del inventario: `AGENTS.md` sin importar habiendo `CLAUDE.md`, `AGENTS.override.md`, `CLAUDE.local.md` | A | alto | P-INS-04 |
| 1.2 | Las instrucciones de Claude y Codex no se contradicen en lo común | Leer ambos juntos; para ordenar, `git blame` | A | alto | P-INS-14 |
| 1.3 ⚙ | Las rutas, comandos y versiones citados existen | Inventario (rutas) + leer manifiestos y scripts (comandos) | A | alto | P-INS-13 |
| 1.4 | Hay comandos exactos de build, prueba (incluida una sola), lint y ejecución, y funcionan | Leer y ejecutar uno barato (en solo lectura: ⏸). Si falla, se documenta el que funciona y el arreglo va a «Necesita tu decisión» | A | alto | P-INS-02 |
| 1.5 | Define «terminado» y la regla de autonomía (cuándo seguir y cuándo parar) | Leer | A | medio | P-FLU-09, P-INS-20 |
| 1.6 ⚙ | `CLAUDE.md` por debajo de ~200 líneas; `AGENTS.md` del proyecto por debajo de 32 KiB en total | Inventario. Para corregirlo se **mueve** contenido a `.claude/rules/` o a skills, no se borra | C / X | medio | P-INS-01, C-01, P-CDX-01 |
| 1.7 | Sin texto antiguo: presión («CRITICAL»), andamiajes de razonamiento, fechas e incidentes, redacción relativa a versiones anteriores, reglas sin motivo | `/doctor prompt-audit` (Claude). En `AGENTS.md`, aplicar a mano los mismos grupos | A | medio | P-INS-05, 08, 12, 16, P-HER-02 |
| 1.8 | Lo temporal está en la tarea o en `progress.md`, no en las instrucciones | Leer: plazos, «ahora mismo», tareas en curso | A | bajo | P-INS-19 |
| 1.9 | Lo que solo vale para una zona está en `.claude/rules/` con `paths:` (Claude) o en un `AGENTS.md` anidado (Codex) | Leer secciones del tipo «en el servidor…» | A | medio | P-INS-18 |
| 1.10 | Nivel de usuario coherente con el proyecto y sin rutas rotas | Inventario (sección de usuario). **Solo se informa**; las contradicciones con el proyecto van a «Necesita tu decisión» | A | medio | P-INS-03, F003 |

## 2 · Procedimientos (skills)

| ID | Comprobación | Cómo verificar | Aplica | Imp. | Ref. |
|---|---|---|---|---|---|
| 2.1 | Los procedimientos largos u ocasionales de las instrucciones están en skills | Leer: secciones de «cómo se hace X» que no se usan en cada sesión | A | medio | P-SKL-04 |
| 2.2 ⚙ | Las skills tienen `description` por categorías de intención y sin detalles de implementación | Inventario (campos) + leer las descripciones | A | medio | P-SKL-01, P-SKL-07 |
| 2.3 ⚙ | Los archivos que cita cada skill existen | Inventario | A | alto | P-SKL-08 |
| 2.4 | Las skills con efectos (desplegar, publicar, enviar) no se invocan solas | Claude: `disable-model-invocation: true`. Codex: `agents/openai.yaml` → `allow_implicit_invocation: false` | A | alto | P-SKL-06, P-CDX-06 |
| 2.5 ⚙ | Las skills compartidas están en las dos rutas, o se decidió una sola herramienta | `.claude/skills/` frente a `.agents/skills/`. Codex: `.codex/skills` y `~/.codex/skills` están obsoletas | A | medio | P-INS-04, P-CDX-06 |
| 2.6 | Las skills se usan | `/skill-doctor` (Claude, v2.1.252+): skills nunca invocadas y coste en contexto | C | bajo | P-HER-03 |

## 3 · Fuentes externas (MCP)

| ID | Comprobación | Cómo verificar | Aplica | Imp. | Ref. |
|---|---|---|---|---|---|
| 3.1 ⚙ | Solo los MCP que el proyecto usa, declarados en el proyecto | `.mcp.json` / `[mcp_servers]`; preguntar para qué paso sirve cada uno | A | medio | P-MCP-01 |
| 3.2 | Las acciones que escriben en servicios externos piden aprobación | Claude: permisos; Codex: `default_tools_approval_mode = "writes"` o por herramienta | A | alto | P-MCP-02, P-CDX-09 |
| 3.3 | El MCP responde antes de depender de él | Recuperar un elemento conocido; `/mcp` | A | medio | P-MCP-02 |

## 4 · Reglas de acción (permisos, hooks, sandbox, secretos)

| ID | Comprobación | Cómo verificar | Aplica | Imp. | Ref. |
|---|---|---|---|---|---|
| 4.1 ⚙ | Los secretos del árbol están ignorados por git y fuera del alcance del agente | Inventario (secretos) + reglas `deny` + guardián | A | alto | P-AUT-03, P-AUT-04 |
| 4.2 | En Windows nativo, la protección de secretos no depende solo de `deny` | Hook `PreToolUse` que revise también la shell (`scripts/guardia.py`). Su matcher incluye `PowerShell`: las reglas `Bash(...)` no cubren esa herramienta | C | alto | P-AUT-08 |
| 4.3 | Codex: proyecto de confianza si se versiona configuración en `.codex/` | Inventario («confianza_de_este_proyecto»); `/debug-config` | X | alto | P-CDX-02 |
| 4.4 | Codex: `workspace-write` + `on-request` en uso interactivo; en segundo plano (`codex exec`, companion), `-a never` **con** sandbox; red apagada salvo necesidad; sin `--yolo` fuera de entornos aislados. Modelo y esfuerzo por defecto del usuario coherentes con lo que dicen las instrucciones | `.codex/config.toml`, `/status`, inventario (modelo y esfuerzo de usuario) | X | alto | P-CDX-03, P-FLU-12 |
| 4.5 ⚙ | Codex: las variables de entorno con secretos no llegan a los comandos | `shell_environment_policy.ignore_default_excludes = false` o `inherit = "core"`. Por defecto vale `true` y no filtra, así que sin la clave explícita cuenta como «no filtra» | X | alto | P-CDX-04 |
| 4.6 | Lo determinista va en hooks, permisos o el sandbox, no en texto («ejecuta siempre el formateador», «Codex no commitea», que ya impone el sandbox con `.git` en solo lectura). Si el código lo escribe Codex, los chequeos van en pruebas, en hooks de Codex o en un `Stop` de Claude | Leer las instrucciones y buscar reglas que podrían ser una barrera | A | medio | P-INS-07, P-AUT-01, P-AUT-05 |
| 4.7 | Las barreras se probaron **en las dos herramientas** | Pedir que lea un secreto **falso** y exigir el mensaje de bloqueo («Blocked by hook» / «Acceso bloqueado»). Un «hook failed» significa que **no** bloqueó. Claude: `/permissions`. Codex: aprobar el hook antes en el **CLI** (`/hooks`; en la app no funciona) | A | alto | P-AUT-07, P-CDX-07 |
| 4.8 | Sin acumulación de aprobaciones de un solo uso | `permissions.allow` y `~/.codex/rules/*.rules`: prefijos genéricos en vez de comandos concretos | A | bajo | P-CDX-05 |
| 4.9 | Las escrituras externas piden confirmación y no se reintentan a ciegas | Hook «preguntar» o `ask` para desplegar y publicar; regla de reintento en las instrucciones | A | medio | P-AUT-09 |
| 4.10 ⚙ | La configuración versionada funciona en la máquina de cualquier miembro: sin rutas absolutas ni de usuario en los hooks, con un intérprete que todos tienen, y en un repo de git si el hook de Codex lo usa | Avisos de portabilidad del inventario | A | alto | D-13 |
| 4.11 | Los pasos personales están documentados: confianza del proyecto y aprobación del hook en Codex, intérprete, prueba de barrera | `docs/agentes/INCORPORACION.md` existe y está al día | A | alto | D-13, P-CDX-07 |

## 5 · Verificación

| ID | Comprobación | Cómo verificar | Aplica | Imp. | Ref. |
|---|---|---|---|---|---|
| 5.1 | El agente puede comprobar su propio trabajo (pruebas, build, capturas) | Comandos de 1.4; si no hay pruebas, se señala como riesgo | A | alto | P-FLU-02 |
| 5.2 | Hay un revisor de solo lectura que devuelve evidencia, y el principal la comprueba en los archivos | `.claude/agents/` / `.codex/agents/` y la instrucción de verificarlo | A | medio | P-SUB-03 |
| 5.3 | Comprobación temprana definida para tareas largas | Plantilla de encargo (`tarea.md`) | A | medio | P-FLU-07 |

## 6 · Modelo y esfuerzo

| ID | Comprobación | Cómo verificar | Aplica | Imp. | Ref. |
|---|---|---|---|---|---|
| 6.1 | El esfuerzo se configura, no se pide en prosa, y no se arrastra el de un modelo anterior | Buscar «piensa más», «think hard»; revisar `effort` y `model_reasoning_effort` | A | medio | P-FLU-12 |
| 6.2 | Plantillas sin nombres de modelo fijados | Leer: los nombres de modelo envejecen | A | bajo | P-CDX-11 |
| 6.3 | Al escalar de modelo, sesión nueva con traspaso, no el historial | Instrucciones de escalado si existen | A | medio | P-FLU-06 |

## 7 · Terminado y estado

| ID | Comprobación | Cómo verificar | Aplica | Imp. | Ref. |
|---|---|---|---|---|---|
| 7.1 | Las tareas largas mantienen un `progress.md` con formato fijo y se pueden retomar | Plantilla `progress.md`; prueba de reanudación | A | medio | P-FLU-08 |
| 7.2 | Informe final con forma fija (Bloqueado por mí / Cambiado / Encontrado) | Leer instrucciones | A | bajo | P-FLU-14 |
| 7.3 | Lo que no esté en archivos se pierde al compactar | Las instrucciones no dependen del historial | A | medio | P-FLU-03 |

## 8 · Código y commits

| ID | Comprobación | Cómo verificar | Aplica | Imp. | Ref. |
|---|---|---|---|---|---|
| 8.1 | Regla de «dónde va cada explicación» en las instrucciones | Leer; fragmento `templates/fragmentos/comentarios.md` | A | bajo | P-COD-01 |
| 8.2 | Nivel de comentarios narrativos en el código | Muestra de ~20 comentarios (con `comentarios.py inventario` si la skill `limpiar-comentarios` está instalada). Si la mayoría narra, proponer la limpieza como tarea aparte | A | bajo | P-COD-02 |
| 8.3 | Los commits explican el porqué | `git log -10 --format=%B` | A | bajo | P-COD-01 |

## 9 · Equipo de agentes (solo si el proyecto reparte trabajo entre agentes)

| ID | Comprobación | Cómo verificar | Aplica | Imp. | Ref. |
|---|---|---|---|---|---|
| 9.1 | Ningún paso determinista lo hace un modelo | Contar los puntos donde se llama a un modelo: ¿la entrada determina la salida? | A | medio | P-EQU-01 |
| 9.2 | Cada agente tiene una ficha: trabajo, modelo, herramientas permitidas **y denegadas**, prueba de éxito | Definiciones de agentes o, si se lanzan sobre la marcha, la tabla de roles de las instrucciones | A | medio | P-EQU-03 |
| 9.3 | Sin orquestadores que solo reenvían ni revisores que revisan lo que escribieron | Mapa de traspasos | A | medio | P-EQU-03 |
| 9.4 | Los traspasos son archivos con contrato; cada rol tiene una compuerta y como máximo 2 reintentos | Instrucciones y fragmento `traspaso-entre-agentes.md` | A | medio | P-EQU-04, P-EQU-05 |
| 9.5 | Se miden retrabajo, reintentos y silencios | Logs o informes | A | bajo | P-EQU-08 |

## Transversales

| ID | Comprobación | Cómo verificar | Aplica | Imp. | Ref. |
|---|---|---|---|---|---|
| T1 | Equivalencias Claude ↔ Codex coherentes: cada capa existe en el formato de la herramienta que la usa | `references/equivalencias.md` | A | medio | D-12 |
| T2.1 | (Si llama a modelos) se registra el uso de tokens por tarea, con su resultado | Buscar dónde se lee `usage` | A | medio | P-API-01, P-API-04 |
| T2.2 | (Si llama a modelos) parámetros vigentes para el modelo: thinking, esfuerzo explícito, `max_tokens` con margen, sin `tool_choice` forzado | `/claude-api prompt-audit <ruta del código>`; `/claude-api migrate` si toca migrar | A | alto | P-API-02, P-API-06 |
| T2.3 | (Si llama a modelos) la caché no se rompe: prefijo estable, sin cambiar modelo o esfuerzo global a mitad de sesión | Revisar cómo se construye la petición. Si el prefijo está por debajo del mínimo cacheable (512–4096 tokens según el modelo) o son llamadas sueltas, n. a. | A | medio | P-API-05 |
| T2.4 | (Si llama a modelos) cada restricción del prompt lleva su motivo | Leer los prompts | A | bajo | P-API-03 |
