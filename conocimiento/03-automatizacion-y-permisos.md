# 03 · Automatización (hooks) y permisos

### P-AUT-01 · Hooks para garantías deterministas  `[Claude]`
- **Qué:** Usar hooks en `.claude/settings.json` (p. ej. `PostToolUse` para formatear tras editar, `PreToolUse` para bloquear comandos o rutas, `Stop` para exigir que pasen los tests).
- **Por qué:** Se ejecutan siempre, sin depender de que el modelo «recuerde».
- **Cómo verificarla:** Reglas de formato o seguridad en texto que no tienen hook equivalente.
- **Hooks según lo que se detecte en el proyecto:**

  | Si el proyecto tiene… | Hook recomendado |
  |---|---|
  | Prettier | `PostToolUse` → formatear tras editar |
  | ESLint / Ruff | `PostToolUse` → lint |
  | TypeScript | `PostToolUse` → typecheck |
  | Carpeta de tests | `PostToolUse` → ejecutar los tests relacionados |
  | Archivos `.env` | `PreToolUse` → bloquear su edición |
  | Lockfiles | `PreToolUse` → bloquear su edición |
  | Código sensible (auth, pagos) | `PreToolUse` → pedir confirmación |
- **Fuentes:** BASE, F001 · **Confianza:** alta

### P-AUT-02 · Permisos explícitos y versionados  `[Ambos]`
- **Qué:** Declarar en la configuración del proyecto qué comandos están permitidos sin preguntar (tests, lint, git de solo lectura) y cuáles denegados (secretos, `rm -rf`, push forzado).
  - `[Claude]` `permissions.allow` / `permissions.deny` en `.claude/settings.json`; lo personal en `.claude/settings.local.json`.
  - `[Codex]` `sandbox_mode` (`read-only`, `workspace-write`, `danger-full-access`) + `approval_policy` (`on-request`, `never` o `granular`) en `config.toml`, más reglas `prefix_rule` en `rules/*.rules`. La configuración de proyecto solo se aplica si el proyecto es de confianza. Detalle en P-CDX-02 a P-CDX-05.
- **Por qué:** Menos interrupciones sin abrir la puerta a acciones destructivas.
- **Higiene:** con el tiempo, las aprobaciones permanentes («permitir siempre») se acumulan en `permissions.allow` o en `rules/*.rules`. Conviene revisarlas y sustituir las de un solo uso por prefijos genéricos y seguros (P-CDX-05).
- **Fuentes:** BASE, F010 · **Confianza:** alta

### P-AUT-03 · Proteger secretos  `[Ambos]`
- **Qué:** Denegar lectura de `.env`, claves y credenciales; no incluir secretos en archivos de instrucciones.
- **Fuentes:** BASE, F001 · **Confianza:** media

### P-AUT-04 · Bloquear los secretos reales del proyecto, no solo `.env`  `[Ambos]`
- **Qué:** Identificar dónde vive cada secreto: `.dev.vars`, `firma.properties`, `*.jks`, `*.key`, cuentas de servicio, carpetas de credenciales fuera del repo. Pedir confirmación (`ask`) o denegar el acceso a todos ellos, y a los comandos de despliegue o de escritura remota (`wrangler deploy`, `--remote`, `secret put`).
- **Por qué:** Las plantillas genéricas solo piensan en `.env`; cada stack guarda sus secretos en otro sitio.
- **Fuentes:** F004 · **Confianza:** media

### P-AUT-05 · Si otro agente escribe el código, los hooks de verificación van en `Stop`  `[Claude]`
- **Qué:** Cuando Codex u otro proceso edita archivos fuera de las herramientas de Claude, los chequeos de calidad (codificación, lint) van en un hook `Stop` sobre `git diff --name-only`, no en `PostToolUse`.
- **Por qué:** `PostToolUse` solo se dispara con las ediciones de Claude.
- **Fuentes:** F004 · **Confianza:** media

### P-AUT-06 · TTL de la caché según el ritmo de trabajo  `[Claude]`
- **Qué:** Ajustes `promptCacheTtl` (conversación principal) y `subagentPromptCacheTtl` (subagentes), con valores `5m` o `1h`; requieren v2.1.242 o posterior.
  - **Por defecto con suscripción:** 1 h en la conversación principal y 5 m en el resto.
  - **Por defecto con API key o proveedor cloud:** 5 m en todo.
  - **Recomendación:** con API key y sesiones con pausas, poner `promptCacheTtl: "1h"`. Con suscripción ya viene así.
- **Por qué:** Cada pausa de más de 5 minutos reescribe todo el contexto. La caché de 1 h compensa si hay al menos una pausa cada ~45 turnos (P-API-05).
- **Fuentes:** F006, F007 (verificada en `prompt-caching.md#cache-lifetime`) · **Confianza:** alta

### P-AUT-07 · Probar las barreras, no solo escribirlas  `[Claude]`
- **Qué:** Después de configurar permisos o hooks:
  - revisar las reglas efectivas con `/permissions`, porque la configuración de usuario y la gestionada también cuentan;
  - pedir una acción inofensiva que debería quedar bloqueada, como editar un archivo de prueba protegido, y confirmar que se deniega.
- **Por qué:** Una regla mal escrita falla en silencio.
- **Fuentes:** F007 · **Confianza:** media

### P-AUT-08 · Los permisos de archivo no frenan la shell; en Windows nativo no hay sandbox  `[Claude]`
- **Qué:** Las reglas `Read(...)` y `Edit(...)` solo aplican a las herramientas de archivo de Claude. Un script de Bash, Python o PowerShell puede leer o escribir igualmente. El sandbox de Bash, que sí lo impide a nivel de sistema, solo existe en macOS, Linux y WSL2, y no cubre los MCP. En **Windows nativo**, para proteger secretos o carpetas críticas:
  - hooks `PreToolUse` sobre los comandos de shell;
  - reglas `deny` sobre comandos concretos;
  - mantener los secretos fuera del árbol del proyecto.
- **Por qué:** Un `deny: Read(.env)` da una falsa sensación de seguridad si la shell puede hacer `cat .env`.
- **Verificado en uso real** (Claude Code 2.1.289, Windows nativo; `pruebas/este-proyecto/auditoria.md`):
  - un hook `PreToolUse` con matcher `Bash|PowerShell|Read|…` bloqueó la lectura de secretos falsos por Bash, PowerShell y Read;
  - `$CLAUDE_PROJECT_DIR` se expande bien;
  - el hook se aplicó a mitad de sesión, sin reiniciar.
  - **Limitación:** en la shell, el hook ve el comando completo, heredocs incluidos. Para escribir documentación que menciona rutas de secretos se usan Write/Edit.
- **Fuentes:** F007 (verificada en `sandboxing.md`), prueba propia · **Confianza:** alta

### P-AUT-09 · Escrituras externas: contenido exacto aprobado y reintentos con cuidado  `[Ambos]`
- **Qué:** Antes de una escritura externa (publicar, enviar, desplegar), identificar el destino y el contenido exacto que se aprueba; si el contenido cambia, se vuelve a aprobar. Ante un timeout, mirar el destino antes de reintentar.
- **Por qué:** El primer intento puede haberse completado, y reintentar duplica.
- **Fuentes:** F007 · **Confianza:** media

## Conflictos

(ninguno todavía)
