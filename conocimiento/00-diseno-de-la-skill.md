# 00 · Decisiones de diseño de nuestra skill

Lecciones sobre **cómo debe comportarse** `race-engineer`, extraídas de las fuentes.

### D-01 · Orquestar herramientas oficiales, no duplicarlas
- **Decisión:** Si el entorno tiene `claude-code-setup` o `/claude-api prompt-audit`, la skill los usa (o le indica al usuario que los ejecute) e integra sus resultados en un único informe. Nuestro valor añadido está en lo que ellos no cubren:
  - compatibilidad con Codex (`AGENTS.md`);
  - coherencia entre niveles de instrucciones;
  - permisos;
  - flujo de trabajo;
  - prácticas propias de esta base de conocimiento.
- **Por qué:** Las herramientas oficiales se mantienen al día con cada versión; nuestra copia se quedaría desfasada.
- **Fuentes:** F001, F002

### D-02 · Recomendar poco y priorizado
- **Decisión:** Por defecto, como mucho 1–2 recomendaciones por categoría y en orden de impacto. Si el usuario pide más sobre una categoría concreta, ampliar. Omitir las categorías que no aplican.
- **Por qué:** Una lista larga abruma y no se aplica.
- **Fuentes:** F001

### D-03 · Proponer primero, aplicar solo con aprobación
- **Decisión:** La auditoría no modifica archivos. Presenta los cambios (diff o fragmento) y aplica solo los que apruebe el usuario.
- **Por qué:** Así lo hacen ambas herramientas oficiales, y las instrucciones de un proyecto son decisiones del equipo.
- **Fuentes:** F001, F002

### D-05 · Supuestos declarados, sin interrogatorio; secretos intactos
- **Decisión:** Al empezar, la skill fija el alcance, las herramientas en uso (Claude, Codex o ambos) y el modelo objetivo a partir del repositorio. Los declara al inicio del informe en lugar de preguntar todo. Pregunta solo lo que no se puede deducir. Nunca abre archivos de secretos; de los `settings*.json` lee solo las claves de hooks y permisos.
- **Por qué:** Así funciona `prompt-audit` (F003). Además, los settings pueden contener tokens.
- **Fuentes:** F003, F004

### D-06 · Cruzar con lo ya instalado antes de recomendar
- **Decisión:** Inventariar plugins, skills, MCP y configuración de usuario (`~/.claude/`, `~/.codex/`) antes de recomendar, para no proponer duplicados.
- **Por qué:** El recomendador oficial no lo hace y en el proyecto piloto habría propuesto tres duplicados (F004).
- **Fuentes:** F004

### D-07 · Detectar cualquier stack, no solo npm y Python
- **Decisión:** La detección del proyecto debe cubrir Gradle/Android, iOS, .NET, Go, Rust, JVM, monorepos con varias partes, servidores serverless, etc. También debe identificar quién escribe el código: Claude, Codex u otro agente, porque eso cambia dónde van los hooks (P-AUT-05).
- **Fuentes:** F004

### D-08 · Ejecutar las herramientas dentro de la sesión
- **Decisión:** Invocar `prompt-audit` y el recomendador desde la propia sesión (skill o subagente), no con `claude -p`.
- **Por qué:** El CLI headless puede no tener sesión iniciada, aunque la app de escritorio sí la tenga (F004).
- **Fuentes:** F004

### D-09 · Organizar la auditoría y la generación por capas del harness
- **Decisión:** La lista de revisión (`references/checklist.md`) y lo que se genera en un proyecto nuevo se estructuran por capas. Cada capa remite a sus prácticas de `conocimiento/`:
  1. **Hechos e instrucciones:** `CLAUDE.md`/`AGENTS.md`, `.claude/rules/`, coherencia entre niveles (01).
  2. **Procedimientos:** skills, uso real con `/skill-doctor` (02, 06).
  3. **Fuentes externas:** MCP (04).
  4. **Reglas de acción:** permisos, hooks, sandbox, secretos (03).
  5. **Verificación:** subagente revisor con evidencia, chequeo temprano (04, 05).
  6. **Modelo y esfuerzo:** configuración, escalado con traspaso, caché (05, 07).
  7. **Terminado y estado:** definición de terminado, `progress.md`, reanudación (05).
  8. **Código y commits:** comentarios y mensajes de commit (08). Es una capa propia de esta skill.
  - Transversales: compatibilidad Claude/Codex y apps que llaman a la API (07).
- **Para un proyecto nuevo:** la skill propone plantillas para las capas 1, 4, 5 y 7 (instrucciones, permisos de base, revisor, plantilla de `progress.md` y de ficha de tarea) y solo lo de las demás capas que el proyecto necesite.
- **Por qué:** Es una estructura completa y comprobable, cada capa tiene su sitio en la herramienta, y deja ver qué capa falta en un proyecto existente.
- **Fuentes:** F007 + toda la base

### D-10 · Detectar el sistema operativo
- **Decisión:** La skill comprueba en qué sistema corre. En Windows nativo no recomienda el sandbox de Bash como protección y propone hooks `PreToolUse` y secretos fuera del árbol (P-AUT-08).
- **Fuentes:** F007 (verificación oficial)

### D-11 · Capa de equipo de agentes, solo si el proyecto la tiene
- **Decisión:** Si el proyecto reparte el trabajo entre varios agentes (Claude + Codex, subagentes, pipelines), la auditoría añade la capa 9 (`09-equipos-de-agentes.md`):
  - ¿hay pasos deterministas hechos por un modelo?;
  - ¿cada agente tiene una ficha con herramientas denegadas?;
  - ¿los traspasos son archivos con contrato?;
  - ¿cada rol tiene una compuerta y un límite de reintentos?;
  - ¿se miden retrabajo y silencios?

  En un proyecto nuevo que lo necesite, la skill pregunta por el flujo manual y propone el equipo mínimo (P-EQU-01, P-EQU-02). No obliga a montar uno.
- **Fuentes:** F008, Building Effective Agents

### D-12 · Compatibilidad Claude/Codex como chequeo explícito
- **Decisión:** La skill determina primero qué herramientas usa el proyecto (Claude, Codex o ambas) y cómo se reparten el trabajo (instrucciones comunes o papeles distintos). Con eso:
  - aplica la tabla «quién lee qué» (P-INS-04) y avisa de los casos silenciosos: `CLAUDE.local.md` que anula `AGENTS.md`, reglas en `AGENTS.override.md`, skills solo en una de las dos rutas, proyecto de Codex no marcado como de confianza;
  - genera o audita cada capa en el formato de cada herramienta con la tabla de equivalencias de `10-codex.md`;
  - para arrancar Codex desde Claude puede proponer `/import` de Codex (P-HER-04) y después revisar el resultado.
- **Fuentes:** F010

### D-13 · Portable para equipos: nada de una sola máquina en lo versionado
- **Decisión:**
  - Lo que la skill genera y se versiona funciona en la máquina de cualquier miembro del equipo:
    - hooks con `$CLAUDE_PROJECT_DIR` (Claude) y `$(git rev-parse --show-toplevel)` (Codex), sin rutas absolutas;
    - `python3` como intérprete por defecto, o el que acuerde el equipo;
    - generación en el idioma del equipo.
  - Lo que cada persona tiene que hacer una vez va en `docs/agentes/INCORPORACION.md`: la confianza del proyecto y la aprobación del hook en Codex, el intérprete y la prueba de barrera.
  - El inventario avisa de rutas de máquina, intérpretes ausentes y hooks que dependen de git sin repo.
- **Por qué:** Un hook que falla en la máquina de otro miembro **deja pasar sin avisar**: la barrera desaparece justo para quien no la configuró. Lo vimos en la v1: la ruta del hook de Codex era la del autor.
- **Verificación:** el comando portable bloquea a través de PowerShell (Windows/Codex) y de sh (Claude, macOS, Linux), desde la raíz y desde subcarpetas, con `python` y con `python3`. **En vivo:** Claude Code 2.1.289 (Read y PowerShell bloqueados) y Codex CLI 0.160 («Blocked by hook»), los dos en Windows 11. Falta probarlo en macOS y Linux reales.
- **Fuentes:** prueba propia (pruebas/este-proyecto), F010

### D-04 · Basar cada recomendación en una señal del proyecto
- **Decisión:** Cada recomendación cita la evidencia que la motiva (archivo, dependencia, configuración detectada) y la práctica de `conocimiento/` en la que se apoya.
- **Por qué:** Recomendaciones genéricas no son accionables; las justificadas se pueden evaluar.
- **Fuentes:** F001
