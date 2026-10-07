# 05 · Flujo de trabajo y gestión del contexto

### P-FLU-01 · Explorar → planificar → implementar → verificar  `[Ambos]`
- **Qué:** En tareas no triviales, primero leer el código relevante, luego acordar un plan (modo plan), implementar y verificar con tests o ejecución real.
- **Por qué:** Saltar directamente a escribir código produce soluciones que resuelven el problema equivocado.
- **Fuentes:** BASE · **Confianza:** media

### P-FLU-02 · Darle al agente una forma de comprobar su trabajo  `[Ambos]`
- **Qué:** Tests, capturas de pantalla, salidas esperadas o un comando de verificación por tarea.
- **Por qué:** Es el factor que más mejora la calidad del resultado.
- **Fuentes:** BASE · **Confianza:** media

### P-FLU-03 · Contexto limpio entre tareas  `[Ambos]`
- **Qué:** Empezar una sesión nueva (o `/clear`) al cambiar de tarea; compactar en sesiones largas; dejar el estado en archivos (plan, notas, TODO) en vez de en la conversación. Con `/context` se ve qué ocupa el contexto.
- **Por qué:** El contexto acumulado e irrelevante degrada las respuestas. Tras compactar, solo el contexto del proyecto se recarga desde disco; lo que no esté en archivos se pierde.
- **Fuentes:** BASE, F007 · **Confianza:** alta

### P-FLU-04 · Peticiones específicas  `[Ambos]`
- **Qué:** Indicar archivos, restricciones, ejemplos y criterio de «terminado» en cada petición.
- **Fuentes:** BASE · **Confianza:** media

### P-FLU-05 · Control de versiones como red de seguridad  `[Ambos]`
- **Qué:** Trabajar en ramas o worktrees, commits pequeños y frecuentes, para poder revertir y paralelizar.
- **Fuentes:** BASE · **Confianza:** media

### P-FLU-06 · Elegir el modelo al principio; escalar con traspaso, no con el historial  `[Ambos]`
- **Qué:** Decidir el modelo en los primeros turnos, mientras el contexto es pequeño. Si una tarea hay que pasarla a un modelo más capaz, abrir una sesión nueva (o un subagente) con un traspaso corto: la tarea, el chequeo que falla y los archivos clave.
- **Por qué:** La caché de prompts es por modelo. Cambiar a mitad de sesión obliga a reescribir todo el contexto al precio del modelo nuevo ($1.50 a 300K en Opus 5.5, frente a $0.10 con un traspaso de 20K). Además, el modelo nuevo hereda los callejones sin salida del anterior. Con suscripción el coste es en cuota, no en dólares, pero el mecanismo es el mismo.
- **Cómo verificarla:** Ver si las instrucciones del proyecto definen cuándo escalar y con qué traspaso. Ejemplo: el «si Codex falla dos veces, la tarea regresa» del proyecto piloto no dice cómo se traspasa.
- **Fuentes:** F006 + skill `claude-api` (cachés por modelo) · **Confianza:** alta

### P-FLU-07 · Un chequeo temprano para detectar tareas difíciles  `[Ambos]`
- **Qué:** Que cada tarea tenga una verificación barata que se pueda ejecutar en los primeros turnos: compila, pasa la primera prueba, tocó los archivos correctos.
- **Por qué:** Permite decidir pronto si escalar, en lugar de descubrir el fracaso tras 40 turnos.
- **Fuentes:** F006 · **Confianza:** media

### P-FLU-08 · Nota de progreso con estructura fija, y probar que se puede retomar  `[Ambos]`
- **Qué:** En tareas de varias sesiones, mantener un `progress.md` (o equivalente) que se actualiza tras cada etapa:
  - **Tarea**
  - **Salidas** (rutas)
  - **Completado** (etapas y chequeos)
  - **Decisiones** (con su fuente)
  - **Pendientes** (evidencia que falta, bloqueos)
  - **Siguiente acción** (una sola, concreta)

  Probarla: en una sesión nueva, «lee `progress.md`, revisa lo referenciado y continúa». Si empieza de cero, a la nota le falta algo.
- **Por qué:** Es también el formato del traspaso limpio de P-FLU-06. Las guías de Anthropic para agentes de larga duración usan registros de progreso persistentes.
- **Fuentes:** F007, F006 · **Confianza:** alta

### P-FLU-09 · Definir «terminado» como entregables + evidencia  `[Ambos]`
- **Qué:** Cada tarea larga declara qué archivos deben existir, qué chequeos deben pasar y qué debe aparecer en el informe final (rutas y resultados de verificación).
  - En Claude Code, `/goal <condición>` evalúa esa condición entre turnos; `/goal clear` la quita.
  - Un límite de turnos escrito en la condición lo evalúa el modelo. Los límites estrictos van en controles de ejecución, como `maxTurns` en los subagentes.
- **Forma del encargo:** la tarea entera en un mensaje, «terminado significa…» y «para y pregunta solo si…» (F009). En ejecuciones desatendidas, un turno que acaba solo con texto suele ser un informe de estado, no el final: se contrasta con la lista de tareas y se devuelve lo pendiente, con un máximo de 2–3 continuaciones. La guía oficial pide además que las afirmaciones de progreso se comprueben contra los resultados de las herramientas.
- **Por qué:** Sin una condición comprobable, la ejecución termina cuando el modelo «cree» que terminó.
- **Fuentes:** F007 (`/goal` verificado; versión no documentada), F009, guía oficial · **Confianza:** alta

### P-FLU-10 · Comprobación previa antes de una tarea larga  `[Claude]`
- **Qué:** Antes de lanzar una tarea larga, comprobar qué está cargado: `/context` (instrucciones), `/agents` (subagentes), `/permissions` (reglas), `/mcp` (conectores), y una prueba rápida de cada pieza nueva.
- **Por qué:** Una pieza que falta se descubre en el minuto uno y no a mitad de la tarea.
- **Fuentes:** F007 · **Confianza:** media

### P-FLU-11 · Medir la configuración sobre trabajo aceptado, cambiando una pieza cada vez  `[Ambos]`
- **Qué:** Para evaluar un cambio de configuración (modelo, esfuerzo, skill, revisor), repetir la misma tarea con los mismos criterios de aceptación y comparar:
  - el resultado guardado;
  - el uso (`/usage`), incluidos el revisor y los reintentos;
  - el tiempo de revisión humana;
  - las correcciones que hizo falta aplicar.
- **Por qué:** Un resultado que necesita mucha reparación cambia el valor de toda la ejecución. Si se cambian varias cosas a la vez, no se sabe cuál influyó.
- **Fuentes:** F007, F003 (paso 7), F006 · **Confianza:** alta

### P-FLU-12 · El esfuerzo se configura, no se pide en prosa  `[Claude]`
- **Qué:** El nivel de razonamiento se fija con `--effort`, `/effort` o el campo `effort` de skills y subagentes. Opus 5.5 usa `medium` por defecto; las tareas de verificación o ambiguas pueden pedir `high`. Las frases tipo «piensa más» no cambian el esfuerzo configurado.
- **Al cambiar de modelo:** no arrastrar el esfuerzo del anterior. Opus 5.5 piensa más que Opus 5 a igual nivel; empezar en `medium` y probar también `low`.
- **Por qué:** El esfuerzo controla de verdad cuánto piensa el modelo y cuánto cuesta; el texto no.
- **Fuentes:** F003, F007, F009 + guía oficial · **Confianza:** alta

### P-FLU-13 · Revisión automática antes de la humana, solo con bloqueantes  `[Ambos]`
- **Qué:** Antes de revisar tú un cambio, pedir una revisión contra la rama base que liste **solo** los problemas que bloquearían el merge, cada uno con archivo, línea, por qué está mal y cómo demostrar que falla.
- **Por qué:** Pedir solo bloqueantes con forma de demostrarlos reduce las falsas alarmas. Según F009, un probador inicial vio a Opus 5.5 con esfuerzo bajo encontrar más fallos que Opus 5 en `high`; es un dato anecdótico.
- **Fuentes:** F009 · **Confianza:** media

### P-FLU-14 · Informe final con forma fija, empezando por lo que te bloquea  `[Ambos]`
- **Qué:** Terminar cada ejecución con los mismos encabezados, por ejemplo «Bloqueado por mí», «Cambiado» y «Encontrado», y leer primero el primero.
- **Por qué:** Un formato fijo permite revisar muchas ejecuciones sin reconstruir la conversación (F007), y lo que necesita una decisión tuya no queda escondido.
- **Fuentes:** F009, F007 · **Confianza:** media

## Conflictos

(ninguno todavía)
