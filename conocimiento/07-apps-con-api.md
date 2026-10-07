# 07 · Proyectos que llaman a la API de Claude

Aplica cuando el proyecto, además de usar agentes para programar, tiene código propio que llama a un modelo, como el servidor del proyecto piloto, que genera textos con un modelo.

### P-API-01 · Registrar el uso de tokens por petición  `[Ambos]`
- **Qué:** Guardar `usage` (entrada, salida, caché) y el modelo de cada llamada en un log o en la base de datos.
- **Por qué:** Sin coste por tarea no se puede medir el efecto de ningún cambio de prompt, modelo o esfuerzo. Es el requisito previo de cualquier optimización.
- **Cómo verificarla:** Buscar dónde se lee `response.usage` / `final.usage`. Si no se lee en ninguna parte, se está descartando. Para poder medir el coste por tarea, cada registro debe llevar también un **id de tarea y su resultado** (aprobada o no).
- **Fuentes:** F003, F004, F006 · **Confianza:** alta

### P-API-02 · Los prompts de la app también se auditan al cambiar de modelo  `[Ambos]`
- **Qué:** Incluir en la auditoría los prompts y el código que arma las peticiones (thinking, effort, prefill, `tool_choice`, parámetros de muestreo), no solo `CLAUDE.md`.
- **Por qué:** Cada generación de modelos vuelve inválidos algunos parámetros (por ejemplo, prefill o `budget_tokens` devuelven error 400 en los modelos actuales) y vuelve innecesarios algunos andamiajes.
- **Cómo verificarla:** Ejecutar `/claude-api prompt-audit` sobre el código de la app; para migraciones, `/claude-api migrate`.
- **Fuentes:** F003 · **Confianza:** alta

### P-API-03 · Cada restricción del prompt, con su motivo  `[Ambos]`
- **Qué:** Acompañar cada regla del prompt de la razón de producto que la justifica (ejemplo del proyecto piloto: «no escribas "silencio": en la app esa palabra apaga los sonidos»).
- **Por qué:** El modelo generaliza mejor a los casos no previstos, y una auditoría futura sabe qué conservar.
- **Fuentes:** F003, F004 (la plantilla del proyecto piloto salió limpia por esto) · **Confianza:** alta

### P-API-04 · Elegir modelo y esfuerzo por coste por tarea aprobada  `[Ambos]`
- **Qué:** Comparar modelos y niveles de esfuerzo por **$ por tarea aprobada**, con los intentos fallidos incluidos, no por precio por token ni por petición. Medirlo con logs reales: turnos por tarea, $/turno y $/pass. F006 trae un script de ejemplo.
- **Por qué:** En bucles largos con caché, Opus 5.5 cuesta 1.26–1.9x por turno, no 2x. Si termina en bastantes menos turnos, sale igual o más barato. El thinking cuenta como salida, así que el esfuerzo pesa más que el modelo.
- **Fuentes:** F006 + skill `claude-api` («cost per completed task») · **Confianza:** alta

### P-API-05 · Cuidar la caché de prompts  `[Ambos]`
- **Qué:**
  - Mantener estable el prefijo (sistema, herramientas, contexto fijo primero).
  - No cambiar de modelo, esfuerzo global ni herramientas a mitad de sesión.
  - Usar caché de 1 h solo si hay pausas de más de 5 min cada ~45 turnos o menos.
  - No poner `max_tokens` bajo para «ahorrar».
  - Comprobar que `cache_read_input_tokens` no se queda en 0.
- **Por qué:** La lectura de caché cuesta un 10 % de la entrada fresca. Cada invalidación reescribe todo el contexto al precio de escritura.
- **Fuentes:** F006 + skill `claude-api` (caché, `max_tokens`) · **Confianza:** alta

### P-API-06 · Migrar a Opus 5.5 / Sonnet 5.5: lista mínima  `[Claude]`
- **Qué:**
  - Cambiar el ID del modelo.
  - Quitar todas las configuraciones de thinking desactivado o con presupuesto y todo `tool_choice` forzado (devuelven 400). En su lugar, `tool_choice: auto`, `strict: true` y, si hace falta, salidas estructuradas.
  - Poner el esfuerzo de forma explícita: `medium` en Opus 5.5 y repetir el barrido de niveles.
  - Dejar margen en `max_tokens` para el thinking: **~64K en turnos agénticos largos**, según la guía oficial; F009 dice 128K y no es correcto.
  - Leer los bloques por tipo y activar `display: "updates"` si el usuario debe ver el progreso entre llamadas a herramientas.
  - Mantener el historial solo-anexado.
  - En ejecuciones desatendidas largas que se quedan en silencio, añadir un aviso de una sola vez (`clear_at`) tras ~5 pasos sin texto.
  - Marcar el texto pegado por el usuario con etiquetas con un id aleatorio e indicar en el sistema que su contenido no son instrucciones. Esto último no está en la guía local.
- **Por qué:** Son los cambios que devuelven error o empeoran el resultado en silencio al migrar.
- **Fuentes:** F009 + guía oficial `model-migration.md` · **Confianza:** alta (salvo la línea marcada)

## Conflictos

### C-03 · ¿Cascada de modelos o un solo modelo?
- **F006:** empezar con Sonnet y escalar a Opus pronto y con traspaso limpio. Así se ahorran ~$710/mes en su ejemplo.
- **Skill `claude-api` (oficial):** antes de montar una cascada, medir el modelo más capaz con menos esfuerzo. Un solo modelo comparte una sola caché, y con menos esfuerzo los modelos nuevos a menudo igualan a los anteriores con más esfuerzo.
- **Resolución:** son pasos sucesivos, no opuestos. Primero se mide la opción de un solo modelo ajustando el esfuerzo. Si se adopta una cascada, se aplican las reglas de F006: decidir pronto y traspasar sin el historial (P-FLU-06).

### C-04 · ¿Cambiar el esfuerzo rompe la caché?
- **F006:** cambiar el esfuerzo global turno a turno invalida la caché.
- **Documentación de Claude Code (verificada en F007):** con Opus 5.5, Sonnet 5.5 y Fable 5.1, cambiar el esfuerzo en Claude Code **conserva** la caché.
- **Resolución:** F006 tiene razón para el parámetro `effort` global de la API. Claude Code y la API con esfuerzo por mensaje (beta) usan un mecanismo que conserva la caché. En apps propias se aplica la regla de F006; dentro de Claude Code se puede ajustar el esfuerzo sin ese coste.
