# 01 · Archivos de instrucciones (CLAUDE.md / AGENTS.md)

### P-INS-01 · Instrucciones breves, específicas y accionables  `[Ambos]`
- **Qué:** El archivo raíz contiene solo lo que el agente no puede deducir del código: comandos de build/test/lint, convenciones no obvias, decisiones de arquitectura, cosas prohibidas. Nada de descripciones genéricas («escribe código limpio»).
- **Por qué:** Se carga en cada sesión y consume contexto; las instrucciones obsoletas o genéricas diluyen las importantes.
- **Cómo verificarla:** Cada línea responde a «¿podría el modelo saberlo ya?». Lo que solo sabe el autor (producto, entorno, nivel de calidad, motivos) se queda.
  - **Tamaño (Claude):** la documentación oficial recomienda **menos de 200 líneas por `CLAUDE.md`**. Por encima, el archivo consume más contexto y el modelo lo sigue peor.
  - Si se pasa, no se borra contexto: lo que solo vale para una zona va a `.claude/rules/` (P-INS-18) y los procedimientos ocasionales, a skills (P-SKL-04). Ver C-01.
  - **Contenido mínimo recomendado por OpenAI para `AGENTS.md`:** estructura del repo, cómo ejecutarlo, comandos de build/test/lint, convenciones, restricciones y qué significa «terminado». Empezar con `/init` y editar.
- **Fuentes:** BASE, F003, F004, F010 + `code.claude.com/docs/en/memory.md` · **Confianza:** alta

### P-INS-02 · Comandos exactos de verificación  `[Ambos]`
- **Qué:** Incluir los comandos exactos para compilar, ejecutar tests (incluido uno solo), lint y typecheck.
- **Por qué:** Que el agente pueda comprobar su propio trabajo es la mejora de calidad más grande.
- **Cómo verificarla:** Existe una sección de comandos y los comandos funcionan tal cual.
- **Fuentes:** BASE · **Confianza:** media

### P-INS-03 · Jerarquía y alcance  `[Ambos]`
- **Qué:** Separar instrucciones globales (usuario), de proyecto (compartidas, en el repo) y locales/personales (fuera del control de versiones). En subdirectorios con reglas propias, archivos anidados.
  - `[Claude]` `~/.claude/CLAUDE.md` → `CLAUDE.md` del repo → `CLAUDE.md` en subdirectorios (se cargan al trabajar ahí). Importación con `@ruta/archivo`.
  - `[Codex]` `~/.codex/AGENTS.md` → `AGENTS.md` desde la raíz del repo hasta el directorio actual. Se concatenan, uno por directorio, y prevalece el más cercano. `AGENTS.override.md` sustituye al del mismo nivel. El límite es de 32 KiB **en total**, se lee solo al iniciar la sesión y no admite imports. Detalle en P-CDX-01.
- **Por qué:** Evita repetir reglas y mezclar preferencias personales con normas del equipo.
- **Cómo verificarla:** No hay preferencias personales en el archivo versionado; no hay reglas duplicadas entre niveles.
- **Verificado en Claude (F007):**
  - Los `CLAUDE.md` de subcarpetas se cargan cuando Claude usa Read/Write/Edit allí.
  - Los `@imports` se cargan **al inicio**, con un máximo de 4 niveles: sirven para organizar, no para ahorrar contexto.
  - Tras compactar, el contexto del proyecto se recarga desde disco.
- **Fuentes:** BASE, F007, F010 · **Confianza:** alta

### P-INS-04 · Claude y Codex: saber quién lee qué, y una sola fuente para lo común  `[Ambos]`
- **Quién lee qué (verificado):**

  | Archivo | Claude Code | Codex |
  |---|---|---|
  | `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md` | Sí | No (solo si se añade a `project_doc_fallback_filenames` **y** falta `AGENTS.md`) |
  | `AGENTS.md` | **Solo si no hay `CLAUDE.md` ni `CLAUDE.local.md`** en ese directorio o por encima (v2.1.277+), o si `CLAUDE.md` lo importa | Sí |
  | `AGENTS.override.md` | **No** | Sí (sustituye a `AGENTS.md` en ese nivel) |
  | `.agents/` (skills) | **No** | Sí |
  | `.claude/` (skills, rules, agents) | Sí | No (`/import` lo convierte) |

- **Qué:**
  - **Si las instrucciones son comunes:** el contenido va en `AGENTS.md`. Si además hace falta algo propio de Claude, `CLAUDE.md` empieza con `@AGENTS.md` y añade solo eso.
    - El import funciona en cualquier versión y configuración, y Claude no lee dos veces un `AGENTS.md` importado.
    - Sin contenido propio de Claude, basta con `AGENTS.md`.
    - Atención: añadir un `CLAUDE.local.md` personal hace que Claude deje de leer `AGENTS.md`, salvo que se importe o que se configure `claude-md-and-agents-md` en `~/.claude/settings.json`.
  - **Si los papeles son distintos** (por ejemplo, Claude dirige y Codex ejecuta, como en el proyecto piloto): dos archivos separados son válidos. Cada uno debe decir a quién va dirigido y no debe contradecir al otro en lo común (P-INS-14).
  - **Nunca poner reglas comunes en `AGENTS.override.md`:** Claude no lo lee.
  - **Skills compartidas:** Claude las busca en `.claude/skills/` y Codex en `.agents/skills/`. Hace falta tenerlas en las dos rutas (copia o enlace simbólico) o elegir una herramienta.
- **Por qué:** Dos archivos paralelos con el mismo contenido divergen. Además, la carga condicional de Claude puede dejar sin leer el `AGENTS.md` sin que nadie lo note.
- **Cómo verificarla:**
  - existencia de `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md` y `AGENTS.override.md` en cada nivel;
  - si `CLAUDE.md` importa `@AGENTS.md`;
  - texto duplicado o contradictorio entre ellos.
  - Al iniciar, Claude muestra «AGENTS.md loaded: …» cuando lo carga.
- **Fuentes:** F010 (`code.claude.com/docs/en/memory.md#agents-md`; documentación de Codex) · **Confianza:** alta

### P-INS-05 · Énfasis con moderación  `[Ambos]`
- **Qué:** Reservar «IMPORTANTE», «NUNCA», mayúsculas, etc., para las pocas reglas críticas.
- **Por qué:** Si todo es importante, nada lo es. Los modelos actuales ya siguen bien las instrucciones, y el lenguaje de presión («CRITICAL: YOU MUST ALWAYS») los lleva a sobreaplicar la regla.
- **Cómo verificarla:** Contar marcadores de énfasis; más de 3–5 es señal de alerta. Antes de suavizar una regla enfática, revisar con `git blame` por qué se añadió: puede responder a un fallo real.
- **Fuentes:** BASE, F002 · **Confianza:** alta

### P-INS-06 · Las instrucciones son código: se iteran  `[Ambos]`
- **Qué:** Cuando el agente comete un error repetido, añadir o corregir la regla correspondiente; eliminar reglas obsoletas. Versionar el archivo.
- **Por qué:** Un archivo generado una vez y nunca revisado se desfasa con el proyecto.
- **Cómo verificarla:** Historial de cambios del archivo; referencias a rutas/comandos que aún existen. Cada cambio importante se trata como una hipótesis y se comprueba con una o dos tareas reales antes de darlo por bueno.
- **Fuentes:** BASE, F002 · **Confianza:** media

### P-INS-07 · Lo determinista no va en instrucciones  `[Ambos]`
- **Qué:** Reglas que deben cumplirse siempre (formato, bloquear comandos peligrosos) se implementan con linters, hooks o permisos, no con texto.
- **Por qué:** Las instrucciones son orientativas; las herramientas son obligatorias.
- **Cómo verificarla:** Reglas tipo «siempre ejecuta prettier» en el archivo → candidatas a hook.
- **Fuentes:** BASE · **Confianza:** media
- **Relacionado:** `03-automatizacion-y-permisos.md`

### P-INS-08 · Sin andamiaje de razonamiento artificial  `[Claude]`
- **Qué:** Eliminar «piensa paso a paso», bloques `<scratchpad>` o `<thinking>` y las instrucciones redundantes del tipo «sé exhaustivo, no pares antes de tiempo».
- **Por qué:** Los modelos actuales razonan de forma nativa; ese andamiaje se diseñó para modelos anteriores y hoy estorba o gasta tokens.
- **Cómo verificarla:** Buscar esas expresiones en CLAUDE.md, skills y prompts.
- **Fuentes:** F002 · **Confianza:** media (confirmar con la guía oficial de prompting)

### P-INS-09 · Sin reglas contradictorias  `[Ambos]`
- **Qué:** Revisar que ninguna regla choque con otra, tampoco entre niveles (global, proyecto, subdirectorio, skills).
- **Por qué:** Ante dos reglas que se contradicen, el comportamiento del modelo es impredecible.
- **Cómo verificarla:** Leer juntos todos los archivos que se cargan a la vez y buscar pares que se contradigan.
- **Fuentes:** F002 · **Confianza:** media

### P-INS-10 · Revisar las instrucciones al cambiar de modelo  `[Ambos]`
- **Qué:** Cada vez que se adopta un modelo nuevo, volver a auditar las instrucciones y los prompts.
- **Por qué:** Instrucciones escritas para modelos anteriores pueden frenar a los nuevos.
- **Cómo verificarla:** Fecha de la última revisión frente a la fecha del cambio de modelo.
- **Fuentes:** F002 · **Confianza:** media

### P-INS-11 · Pasos numerados solo para procedimientos; ejemplos marcados como ilustrativos  `[Ambos]`
- **Qué:** Usar listas numeradas para secuencias que deben seguirse en orden, no para tareas que requieren criterio. Si se da un único ejemplo, indicar que es ilustrativo.
- **Por qué:** Los pasos rígidos encorsetan las tareas de criterio, y un ejemplo único sin aviso se copia literalmente.
- **Cómo verificarla:** Revisar listas numeradas y ejemplos en instrucciones y skills.
- **Fuentes:** F002 · **Confianza:** media

### P-INS-12 · Reglas vigentes, sin narrativa histórica  `[Ambos]`
- **Qué:** Enunciar la regla actual y, si hace falta, su motivo en una frase. Quitar fechas («desde el 2 oct»), hashes de commit, nombres de tareas e incidentes («se quemó la cuota en NormaFIRA»).
- **Por qué:** La autoridad de una regla está en lo que manda hacer; la arqueología se pudre y desvía la atención.
- **Cómo verificarla:** Buscar fechas, hashes, pasados verbales y «ya falló una vez» en los archivos de instrucciones.
- **Fuentes:** F003, F004 · **Confianza:** alta

### P-INS-13 · Rutas, comandos y versiones citados deben existir  `[Ambos]`
- **Qué:** Comprobar que cada ruta del proyecto, comando o versión citados en las instrucciones siguen siendo ciertos.
- **Por qué:** Las instrucciones se desfasan cuando cambia el código, y nada las revisa por defecto. En el proyecto piloto, una skill citaba tres archivos que nunca existieron y `CLAUDE.md` fijaba una versión del CLI que él mismo desmentía más abajo.
- **Cómo verificarla:** Extraer las rutas citadas y probarlas con `test -e`. Las rutas fuera del proyecto o generadas no cuentan como fallo.
- **Fuentes:** F003, F004 · **Confianza:** alta

### P-INS-14 · Resolver contradicciones entre archivos de instrucciones por antigüedad  `[Ambos]`
- **Qué:** Si `CLAUDE.md`, `AGENTS.md`, las skills o los documentos que estos mandan leer dicen cosas distintas sobre lo mismo, la versión más reciente según `git blame` (nunca según la fecha del archivo) indica la regla vigente. Se propone corregir la antigua; no se aplica sin confirmación. Si el historial no permite ordenarlas, se señala para que decida el usuario.
- **Por qué:** Claude y Codex leen archivos distintos y acaban recibiendo instrucciones distintas.
- **Excepción:** un archivo más específico (de subcarpeta o de una tarea) que justifica su diferencia es una excepción legítima, no un conflicto.
- **Fuentes:** F003, F004 · **Confianza:** alta

### P-INS-15 · El contexto no es relleno  `[Ambos]`
- **Qué:** Al limpiar, conservar el contexto que solo conoce el autor (público, producto, entorno, nivel de calidad, motivos de las restricciones) y los guiones exactos de las operaciones frágiles (despliegues, firmas, comandos destructivos). Las prohibiciones con motivo se quedan.
- **Por qué:** Una limpieza que solo acorta borra justo las palabras más valiosas.
- **Fuentes:** F003 · **Confianza:** alta

### P-INS-16 · Escribir como si las reglas actuales fueran las únicas  `[Ambos]`
- **Qué:** Evitar redacción relativa a versiones anteriores: «ya no se usa la API de Gemini», «no hace falta llave», «ahora funciona distinto».
- **Por qué:** El modelo nunca vio la versión anterior; esas frases sugieren alternativas que ya no existen.
- **Fuentes:** F003, F004 · **Confianza:** media

### P-INS-17 · Objetivos con motivo, no aforismos  `[Ambos]`
- **Qué:** Las reglas para el agente se escriben como objetivo + motivo + excepciones, no como lemas o casillas («En el código, el How…»).
- **Por qué:** El modelo sigue las instrucciones al pie de la letra. Una lista de casillas se lee como mandato de llenar cada una: en el experimento de F005, la regla literal aumentó los comentarios en vez de reducirlos.
- **Fuentes:** F003, F005 · **Confianza:** media

### P-INS-18 · Reglas por zona del código con `.claude/rules/`  `[Claude]`
- **Qué:** Las reglas que solo valen para una parte del proyecto (la app Android, el servidor, las pruebas) van en `.claude/rules/<tema>.md` con frontmatter `paths:` (lista de patrones). Se cargan solo cuando Claude toca archivos que coinciden. Las reglas sin `paths:` se cargan al inicio.
- **Por qué:** Así el `CLAUDE.md` raíz se queda en lo común y el contexto solo lleva lo relevante.
- **Cómo verificarla:** Secciones de `CLAUDE.md` del tipo «en el servidor…» o «en la app…» son candidatas a regla con `paths:`.
- **Fuentes:** F007 (verificada en `memory.md#path-specific-rules`) · **Confianza:** alta

### P-INS-19 · Hechos estables en las instrucciones; lo temporal, con la tarea  `[Ambos]`
- **Qué:** El archivo de instrucciones guarda lo que sigue siendo útil entre tareas. Plazos, dudas abiertas y decisiones de una tarea van en su nota de tarea o de progreso. Los hechos externos (versiones, APIs) llevan su fuente y la fecha en que se verificaron. Una preferencia descubierta durante una tarea se convierte en regla permanente solo cuando el usuario confirma que aplica a todas.
- **Por qué:** Evita la «trampa de lo reciente» (F003): un tropiezo de una sesión convertido en regla para siempre. También deja claro qué información sigue vigente.
- **Fuentes:** F003, F007 · **Confianza:** alta

### P-INS-20 · Decir cuándo seguir y cuándo parar  `[Ambos]`
- **Qué:** Incluir en las instrucciones una regla de autonomía explícita:
  - cuando un paso no necesita al usuario, seguir;
  - las notas de estado van junto a la siguiente acción, no en un turno aparte;
  - parar solo cuando no se puede avanzar sin el usuario o antes de algo destructivo (borrar datos, `push --force`, tocar algo fuera del repo).

  Los permisos siguen siendo la barrera real para lo destructivo; la regla reduce las paradas, no sustituye a los permisos.
- **Por qué:** Opus 5.5 a veces termina el turno para informar en lugar de seguir. Una regla que nombra las paradas buenas y las malas lo corrige sin quitar control.
- **Cómo verificarla:** El archivo de instrucciones dice cuándo pedir confirmación. En proyectos con mucho trabajo interactivo puede ser al revés: más paradas, no menos.
- **Fuentes:** F009 (no aparece literal en la guía oficial; es coherente con «finish-the-whole-task» de la sección de Opus 5) · **Confianza:** media

## Conflictos

### C-01 · ¿Límite de longitud? (P-INS-01)
- **Postura BASE:** archivo raíz de menos de ~200 líneas.
- **Postura F003 (oficial):** «cruft ≠ length»; nunca se justifica un borrado solo por el número de caracteres.
- **Resolución inicial:** la longitud no es motivo para borrar. Sí es una señal para revisar si hay procedimientos ocasionales que conviene sacar a skills y si hay instrucciones obsoletas.
- **Actualización (F010):** la documentación oficial de Claude Code **sí** fija un objetivo de menos de 200 líneas por `CLAUDE.md`, porque los archivos largos se siguen peor. Las dos fuentes son oficiales y se combinan así:
  - el objetivo de ~200 líneas se mantiene como **meta de organización**;
  - se alcanza **moviendo** contenido a `.claude/rules/` con `paths:` o a skills, no **borrando** contexto valioso;
  - solo se borra lo obsoleto o genérico, según F003.
  - Los `@imports` no cuentan como solución, porque también se cargan al inicio.
