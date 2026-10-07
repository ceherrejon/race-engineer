# 09 · Flujos con varios agentes

Aplica cuando un proyecto reparte el trabajo entre varios agentes: Claude que dirige y Codex que ejecuta, subagentes revisores, pipelines.

### P-EQU-01 · Empezar por el flujo manual y repartir: reglas → código, juicio → agente, irreversible → persona  `[Ambos]`
- **Qué:** Antes de diseñar agentes, escribir el flujo tal como se hace a mano (6–12 pasos) y clasificar cada paso:
  - los que siguen una regla exacta (enrutar, contar, normalizar, formatear) se hacen con **código**;
  - los que requieren juicio, con un **agente**;
  - el paso irreversible (enviar, fusionar, pagar, publicar), con **la persona**.
- **Por qué:** Un modelo ejecutando pasos deterministas es más caro y menos fiable que el código, y las acciones irreversibles necesitan un responsable.
- **Cómo verificarla:** Contar los puntos donde se llama a un modelo y preguntar en cada uno: ¿sus entradas determinan por completo la salida?
- **Fuentes:** F008, Building Effective Agents, F003 (Grupo 4) · **Confianza:** alta

### P-EQU-02 · El equipo más pequeño que funcione; un flujo fijo antes que un agente que elige  `[Ambos]`
- **Qué:** Empezar con la solución más simple: una llamada bien preparada, luego un flujo fijo (encadenar pasos, enrutar, paralelizar, evaluador-optimizador). Un agente que decide su propio camino solo se usa cuando la tarea no se puede especificar de antemano. Cada agente más tiene que justificarse.
- **Por qué:** Los agentes cambian latencia y coste por flexibilidad, y cada pieza más es algo que mantener.
- **Fuentes:** Building Effective Agents, F008, skill `claude-api` («Start simple») · **Confianza:** alta

### P-EQU-03 · Un agente, un trabajo; el rol se define por lo que no puede hacer  `[Ambos]`
- **Qué:** Cada agente tiene una ficha con:
  - su trabajo en una frase;
  - el modelo y por qué ese y no uno mayor;
  - las herramientas permitidas **y las denegadas**;
  - entradas y salidas definidas;
  - la prueba que demuestra que lo hizo bien;
  - qué hace si no puede terminar.

  En Claude se plasma en el frontmatter de `.claude/agents/*.md` (`tools`, `model`, `effort`, `maxTurns`).
- **Antipatrones:**
  - dos agentes compartiendo un trabajo;
  - un orquestador que solo reenvía mensajes;
  - un revisor que también escribió lo que revisa.
- **Por qué:** Los límites claros hacen predecible el comportamiento y localizables los fallos.
- **Evidencia:** en el proyecto piloto, el subagente `codex-rescue` solo reenviaba y además mataba el proceso al terminar (F004).
- **Fuentes:** F008, F004, P-SUB-02 · **Confianza:** alta

### P-EQU-04 · Cada traspaso es un archivo con un contrato fijo  `[Ambos]`
- **Qué:** Lo que un agente le pasa a otro va en un archivo que una persona puede leer, con:
  - la tarea en una línea accionable;
  - las entradas, nombradas;
  - el criterio de terminado, escrito **antes** de empezar;
  - la confianza y cómo se midió;
  - qué se intentó y falló;
  - quién se hace cargo si se detiene.
- **Por qué:** Un traspaso que cabe en un mensaje de chat no es un contrato: no se puede auditar ni retomar. Es el mismo formato que la nota de progreso (P-FLU-08) y el traspaso limpio al escalar de modelo (P-FLU-06).
- **Fuentes:** F008, F007, F006 · **Confianza:** media

### P-EQU-05 · Cada rol cierra con una compuerta que puede fallar  `[Ambos]`
- **Qué:** Tras cada paso, un control con resultado numérico o binario que queda en el log:
  - la rúbrica del crítico;
  - el código de salida de las pruebas;
  - un umbral calibrado con ejemplos reales;
  - la aprobación humana antes de lo irreversible.

  Hay que definir qué pasa si falla: reintentar, redirigir o parar. **Máximo 2 reintentos:** un tercer intento señala un problema de diseño (casi siempre en el encargo), no de suerte.
- **Por qué:** Una compuerta que nunca falla no controla nada, y los bucles de reintentos queman cuota sin mejorar el resultado.
- **Evidencia:** El proyecto piloto ya aplica «si Codex falla dos veces, la tarea regresa; antes de reintentar, revisar el encargo».
- **Fuentes:** F008, F004 · **Confianza:** media

### P-EQU-06 · Escalar en una línea, nunca en bucle  `[Ambos]`
- **Qué:** Cuando un agente no puede terminar, escribe una línea: qué estaba haciendo, qué tiene y qué necesita. Sin reintentos en bucle, sin disculpas y sin conjeturas. Solo se acude a la persona cuando esperar cuesta más que preguntar.
- **Fuentes:** F008 · **Confianza:** media

### P-EQU-07 · Introducir el equipo poco a poco y recortar lo que no se gana su sitio  `[Ambos]`
- **Qué:** En este orden:
  1. un agente, ejecutado a mano;
  2. su prueba de éxito;
  3. el segundo agente y su archivo de traspaso;
  4. el crítico;
  5. el umbral, calibrado con ~20 ejemplos propios;
  6. ejecución desatendida con registro de cada decisión;
  7. eliminar lo que no aportó.

  Durante la primera semana, leer a mano varias ejecuciones y provocar a propósito un fallo conocido.
- **Por qué:** Añadir piezas de una en una deja claro qué aporta cada una (P-FLU-11).
- **Fuentes:** F008 · **Confianza:** baja–media (heurística del autor)

### P-EQU-08 · Métricas del equipo, incluidos los silencios  `[Ambos]`
- **Qué:** Medir desde el primer día:
  - tiempo frente al camino manual;
  - coste por ejecución, por día y por mes, con los reintentos incluidos;
  - escaladas y si estaban justificadas;
  - **retrabajo** (salida que hubo que corregir antes de usar);
  - reintentos por ejecución completada;
  - **silencios**: ejecuciones que no produjeron nada y no avisaron.
- **Por qué:** Los silencios y el retrabajo son los costes que más se esconden. Complementa $/pass (P-API-04) y la medición sobre trabajo aceptado (P-FLU-11).
- **Fuentes:** F008, F006, F007 · **Confianza:** media

## Conflictos

(ninguno todavía)
