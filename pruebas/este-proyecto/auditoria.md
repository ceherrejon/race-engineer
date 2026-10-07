# Auditoría de «Skills para Proyectos» · 2026-10-07

Realizada con `race-engineer` v1 (entonces llamada `race-engineer`), Modo B.

## Supuestos
- **Herramientas:** Claude Code 2.1.289 (configurada). Codex 0.160 instalado, pero sin configuración en este proyecto. **Sistema:** Windows nativo. **Stack:** documentación en Markdown + scripts de Python (sin manifiesto).
- **Reparto:** solo Claude trabaja aquí, de momento.
- **Quién escribe el código:** Claude.
- **Particularidad:** desde este proyecto se ejecutan inventarios y auditorías **sobre otros proyectos** (el proyecto piloto), que tienen secretos fuera de su árbol.
- **Alcance:**
  - proyecto completo;
  - el nivel de usuario solo se informa;
  - **sin git**, así que no se puede ordenar contradicciones con `git blame`.
- **Herramientas oficiales:**
  - `claude-api prompt-audit`: no se ejecutó. El `CLAUDE.md` tiene 34 líneas y se revisó a mano con los grupos de la guía. La ejecución completa ya se había probado en el proyecto piloto.
  - `/doctor prompt-audit` y `/skill-doctor`: sugeridos al usuario (⏸).

## Lo más importante
1. **No hay control de versiones.** Ningún cambio de un agente se puede revertir ni revisar como diff, y la configuración que vamos a probar no se podría deshacer limpiamente.
2. **No hay ninguna barrera de secretos, en Windows.** El trabajo de este proyecto consiste en leer otros proyectos, y en ellos hay claves (`~/.piloto/`, `~/.codex/auth.json`). Hoy solo las protege que el agente decida no abrirlas.
3. **Los scripts de la skill no tienen pruebas automáticas.** Se probaron a mano con casos trampa, pero cada cambio puede romperlos sin que nadie lo note. Ya pasó: dos correcciones de hoy introdujeron errores que solo se vieron al volver a ejecutar.

## Por capa
| Capa | Estado | Resumen |
|---|---|---|
| 0 Contexto | ✓ | Deducido del inventario |
| 1 Instrucciones | ⚠ | `CLAUDE.md` breve y claro, pero sin comandos ni «terminado». La regla de mantenimiento de la checklist solo está en la memoria |
| 2 Procedimientos | ✓ | El protocolo de fuentes está en `CLAUDE.md` y se usa en cada sesión: no hace falta una skill |
| 3 Fuentes externas | n. a. | — |
| 4 Reglas de acción | ✗ | Sin permisos ni hooks; Windows sin sandbox |
| 5 Verificación | ✗ | Scripts sin pruebas automáticas |
| 6 Modelo y esfuerzo | n. a. | — |
| 7 Terminado y estado | ✓ | `CHANGELOG.md` + `fuentes/INDICE.md` hacen de registro de progreso |
| 8 Código y commits | ✗ | Sin git |
| 9 Equipo | n. a. | Los subagentes se usan sobre la marcha, con encargos acotados |
| T1 Claude/Codex | ⏸ | Solo Claude. Si se va a usar Codex aquí, falta `AGENTS.md` |
| T2 API | n. a. | — |

## Hallazgos

### 8 / P-FLU-05 · Sin control de versiones
- **Evidencia:** el inventario dice «Git: no es un repositorio».
- **Por qué importa:** no hay forma de revertir ni de revisar los cambios. Codex además usa `.git` para localizar la raíz del proyecto.
- **Propuesta:** `git init`, un `.gitignore` mínimo y un primer commit con el estado actual.
- **Confianza:** alta

### 4.2 / P-AUT-08 · Secretos de otros proyectos sin barrera (Windows)
- **Evidencia:** sin `.claude/settings.json` ni hooks. Las auditorías del proyecto piloto citan `~/.piloto/*.key`.
- **Por qué importa:** un `cat ~/.piloto/anthropic.key` desde la shell no lo frena nada.
- **Propuesta:**
  - `.claude/settings.json` de la plantilla;
  - `.agents/hooks/guardia.py`;
  - `.agents/guardia.txt` con `bloquear: [\\/]\.piloto[\\/]` y `bloquear: [\\/]\.codex[\\/]auth\.json`.
  - Sirve además como **prueba real del hook** en esta sesión.
- **Confianza:** alta

### 5.1 / P-FLU-02 · Scripts sin pruebas automáticas
- **Evidencia:** `skill/*/scripts/*.py` no tiene pruebas. Hoy hubo dos regresiones (sintaxis y escapado) que solo aparecieron al volver a ejecutar.
- **Propuesta:** `pruebas/automaticas/` con `unittest`, convirtiendo en casos los que ya usamos a mano:
  - los 11 de la guardia;
  - las trampas de `comentarios.py`;
  - un proyecto de ejemplo para `inventario.py`.
- **Confianza:** alta

### 1.4–1.5 · `CLAUDE.md` sin comandos ni «terminado»; una regla vive solo en la memoria
- **Evidencia:** `CLAUDE.md` no explica cómo ejecutar los scripts ni sus pruebas. La regla de actualizar la checklist cuando cambia una práctica está en la memoria del agente, no en el proyecto.
- **Propuesta:** añadir a `CLAUDE.md` una sección de comandos, una de «terminado» (pruebas en verde e índices actualizados) y esa regla de mantenimiento.
- **Confianza:** media

## Nivel de usuario (solo informativo, ya conocido)
- Codex usa por defecto `gpt-6-sol` con esfuerzo `high`.
- `~/.codex/AGENTS.md` tiene una ruta rota a graphify.
- `~/.codex/rules`: 65 de 91 reglas son aprobaciones puntuales.

## Necesita tu decisión
- ¿Inicializar git en este proyecto?
- ¿Se usará Codex aquí? Si es así, `AGENTS.md` con el protocolo y `CLAUDE.md` importándolo.
- La imagen `Prompt For Agents.jpeg` está en la raíz: ¿moverla a `fuentes/adjuntos/`? (Resuelto después: no se publica, por derechos de autor; ver F008).

## Cómo verificar después de aplicar
- **Barreras:** en esta misma sesión, intentar leer un `.env` de prueba y `~/.piloto/anthropic.key`; los dos deben quedar bloqueados. Si no, abrir una sesión nueva y repetir, por si los hooks solo se cargan al iniciar.
- **Pruebas:** `python -m unittest discover pruebas/automaticas` en verde.
- **Configuración:** `/permissions` y `/hooks` muestran la configuración aplicada.

---

## Aplicación y verificación (2026-10-07)

**Aprobado y aplicado:**
- **Git:** `git init` y commit inicial `754ec17`, antes del resto de cambios.
- **Instrucciones:** `AGENTS.md` con el protocolo; `CLAUDE.md` reducido a `@AGENTS.md`.
- **Claude:** `.claude/settings.json` de la plantilla.
- **Codex:** `.codex/config.toml` de la plantilla, con la ruta absoluta de la guardia. Filtra los secretos del entorno; en la pregunta al usuario se describió por error como «sin filtrar».
- **Guardia:** `.agents/hooks/guardia.py` + `.agents/guardia.txt` (`.piloto/`, `.codex/auth.json`).
- **Secretos falsos de prueba:** en `pruebas/guardia/`, ignorados por git.

**Verificado en esta sesión de Claude Code 2.1.289, Windows nativo, sin reiniciar:**

| Intento | Herramienta | Resultado |
|---|---|---|
| Leer `pruebas/guardia/.env` | Read | Bloqueado por la regla `deny` de permisos |
| `cat …/.piloto/falsa.key` | Bash | Bloqueado por el hook (patrón de serie `*.key`) |
| `Get-Content …\.env` | PowerShell | Bloqueado por el hook: **el matcher `PowerShell` funciona** |
| Leer `…/.piloto/falsa.key` | Read | Bloqueado por el hook |
| `ls …/.piloto/` | Bash | Bloqueado por el patrón propio de `guardia.txt` |
| `git status`, `python -m json.tool` | Bash | Permitidos |
| Documentar los resultados con un heredoc en Bash que mencionaba esas rutas | Bash | **Bloqueado**: la guardia revisa el comando completo, heredoc incluido |

**Conclusiones:**
- `$CLAUDE_PROJECT_DIR` se expande bien en Windows.
- Un hook añadido a `.claude/settings.json` **a mitad de sesión** se aplica sin reiniciar (en esta versión).
- **Limitación:** en la shell, la guardia no distingue datos de órdenes. Un heredoc también puede alimentar una shell, así que bloquearlo es lo conservador. Para escribir documentación que menciona rutas de secretos se usan las herramientas de edición (Write/Edit), cuyo contenido no se revisa.

**Lado Codex (CLI 0.160.0, Windows nativo). El usuario lo ejecutó y yo leí la terminal:**

| Paso | Resultado |
|---|---|
| App de escritorio: `/hooks` | No abre el panel: llega al modelo como un mensaje. La aprobación de hooks hay que hacerla en el **CLI** |
| App de escritorio: «lee pruebas/guardia/.env» (hook sin aprobar) | **Lo leyó.** El sandbox de Codex no protege la lectura |
| CLI al arrancar | «Hooks need review: 1 hook is new or changed». La opción seleccionada por defecto es **«Continue without trusting (hooks won't run)»** |
| CLI `/hooks` tras aprobar | PreToolUse 1/1 activo |
| CLI: «lee pruebas/guardia/.env» (guardia con salida por código 2) | «Hook failed — hook exited with code 1» y **lo leyó** |
| Diagnóstico | Reproducido: a través de `powershell -Command`, el `exit 2` del script llega como **1**. Codex lanza los hooks con PowerShell en Windows, y 1 significa «falló», no «bloquea» |
| Corrección | La guardia bloquea respondiendo JSON (`permissionDecision: "deny"`) con código 0. 12 de 12 casos correctos, directos y a través de PowerShell |
| CLI: «lee pruebas/guardia/.env» (guardia corregida) | **«Blocked by hook — Acceso bloqueado por la guardia de secretos (.env)»** ✓. No hizo falta volver a aprobar: solo cambió el script, no la configuración |
| Claude tras la corrección | Read y PowerShell siguen bloqueados con el JSON ✓ |

**Lecciones para la skill:**
1. En Codex, un hook **configurado** no basta: hay que **aprobarlo en el CLI** (`/hooks`). El valor por defecto al arrancar es no aprobarlo.
2. El sandbox de Codex limita la escritura, **no la lectura**: sin hook aprobado, lee cualquier secreto.
3. En Windows, un hook que debe bloquear tiene que responder con JSON y código 0, no con el código 2.
4. Un hook que falla (código distinto de 0 y 2) **deja pasar** en las dos herramientas. La prueba de barreras tiene que mirar el mensaje «Blocked by hook», no solo que «haya pasado algo».

**v1.1 portable (mismo día):** con el hook de Codex en `python3 "$(git rev-parse --show-toplevel)/.agents/hooks/guardia.py"` y el de Claude en `python3 "$CLAUDE_PROJECT_DIR/…"`:
- Codex CLI respondió «Blocked by hook» al pedirle leer el secreto falso.
- Claude bloqueó Read y PowerShell.
- Avisos que aparecieron al arrancar el CLI, sin relación con la skill:
  - un servidor de Codex en segundo plano con funciones distintas (se eligió «Run without daemon this time», para no cambiar la configuración compartida);
  - la oferta de actualizar a 0.161 (se pospuso para no cambiar dos cosas a la vez).

**Incidente durante el diagnóstico (provocado por mí, ya reparado):**
- **Qué pasó:** para reproducir el hook lancé `python` con el directorio de trabajo en el proyecto y **sin `LOCALAPPDATA`**. El gestor de instalación de Python tomó entonces la carpeta del proyecto como destino:
  - instaló Python 3.14.8 en `Python/` (151 MB) y dejó una carpeta `%SystemDrive%/`;
  - redirigió hacia esa copia la clave de registro `HKCU\Software\Python\PythonCore\3.14` y los accesos del menú Inicio.
- **Reparación** (aprobada por el usuario): borradas las tres rutas creadas y `py install --refresh`. Se verificó que el registro y los accesos vuelven a `AppData\Local\Python\pythoncore-3.14-64`, y que `python --version` da 3.14.6.
- **Lección:** las pruebas que quitan variables de entorno se ejecutan desde una carpeta temporal y nunca quitan `LOCALAPPDATA`, `APPDATA` ni `USERPROFILE` en Windows. Algunos lanzadores, como el de Python o los de npm, instalan o escriben en rutas que dependen de ellas.
