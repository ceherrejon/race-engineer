# F009 · «The Claude Opus 5.5 Setup Guide: How to Get Maximum Quality for Minimum Cost»

- **Tipo:** artículo en X
- **Origen:** https://x.com/zodchiii/status/2102703913195729398, leído con el navegador integrado
- **Autor:** @zodchiii, el mismo de F008
- **Fecha de la fuente:** 2026-09-23 (un día después del lanzamiento de Opus 5.5)
- **Fecha de incorporación:** 2026-10-07
- **Aplica a:** Claude. La parte de API, a apps propias; la parte «In Claude Code», a la configuración de proyectos.
- **Calidad percibida:** media-alta. Contrastado con la guía oficial `claude-api/shared/model-migration.md` (secciones Opus 5.5 y Sonnet 5.5, caché del 2026-09-25).

## Verificación

| Afirmación | Resultado |
|---|---|
| $4 / $20; escritura en caché $5 (5 min) y $8 (1 h); lectura $0.20 (0.05x); batch $2 / $10 | Verificada |
| «40 % más barato que Opus 5» (titular) | **Inexacta**: es un 20 % por token y un 60 % en lectura de caché. El ahorro del 40 % lo atribuye después al esfuerzo. |
| El esfuerzo por defecto pasa de `high` a `medium`; a igual nivel, 5.5 piensa más que Opus 5; no arrastrar `effort: "high"` | Verificada |
| Cuatro cambios que devuelven 400 (thinking desactivado o con presupuesto, `tool_choice` forzado, bloques de thinking ligados, `computer_20251124`) | Verificada |
| 5.5 lee los bloques de thinking de Opus 5; editar el historial devuelve 400 en cuentas creadas después del 31 de agosto | Verificada |
| Esfuerzo por mensaje sin perder la caché (beta `mid-conversation-output-config-2026-07-01`) | Verificada |
| «La cifra de Anthropic para turnos agénticos largos es `max_tokens` 128.000» | **Incorrecta**: la guía dice que para turnos largos de código agéntico «64K ha funcionado bien». 128K es el máximo, no la recomendación. |
| `display: "updates"`, leer los bloques por tipo y aviso de una sola vez tras ~5 pasos sin texto (`clear_at`) | Verificada. El aviso aparece en la sección de Sonnet 5.5 de la guía. |
| «Answer directly», patrones de frontend con nombre, lectura de gráficos, `reasoning_extraction` | Verificada |
| «Tratar como cerradas las respuestas ya dadas» | Verificada, aunque en la sección de Sonnet 5.5 y no en la de Opus 5.5 |
| «No terminar el turno para informar», «explorar antes de actuar», «elapsed 340s / 1200s», envolver el texto pegado en `<pasted_content id=…>` | **No encontradas** en la guía local. El patrón de `pasted_content` sí se usa en el harness de Claude Code. La guía tiene una idea afín: exigir que las afirmaciones de progreso se contrasten con los resultados de las herramientas. |
| «Sonnet 5 para el día a día» | Desfasada: Sonnet 5.5 ya es el Sonnet actual, al mismo precio |

## Resumen (lo aplicable a configurar proyectos)

**En Claude Code:**
- **Forma del encargo:** la tarea entera en un mensaje, qué significa «terminado» y cuándo parar.
- **Regla para `CLAUDE.md`:** seguir trabajando cuando un paso no necesita al usuario, poner las notas de estado junto a la siguiente acción y parar solo si no se puede continuar o antes de algo destructivo. Los avisos de permiso siguen siendo la barrera.
- **Subagentes con control de evidencia:** el agente principal comprueba la evidencia de cada subagente antes de aceptarla.
- **Lista de tareas en archivo** (`TASKS.md`): sobrevive a la compactación. Se lee el archivo, no el historial.
- **Revisión antes que la humana:** solo problemas que bloquearían el merge, con archivo, línea, por qué y cómo demostrar el fallo.
- **Informe final con tres encabezados:** «Bloqueado por mí», «Cambiado», «Encontrado».
- **`/fast`** para trabajo interactivo; desactivado en ejecuciones desatendidas.

**Elección de modelo:** Opus 5.5 con `medium` como opción por defecto para lo que antes iba a Fable; Fable solo cuando una medición lo justifique.

**En la API:** checklist de migración (esfuerzo explícito, `max_tokens` con margen para el thinking, `display: "updates"`, leer por tipo), apertura con una línea para ejecuciones desatendidas y marcado del contenido pegado.

**Errores comunes:**
- arrastrar el esfuerzo del modelo anterior;
- `max_tokens` pequeño;
- mostrar solo los bloques de texto;
- cambiar el esfuerzo global en cada petición;
- tomar un turno que termina solo con texto como «tarea completada».

## Prácticas extraídas

| ID | Archivo | Tipo |
|---|---|---|
| P-INS-20 | 01 | Nueva |
| P-SUB-01 | 04 | Matiz (subagentes multiplican el coste; guía oficial) |
| P-SUB-03 | 04 | Refuerza |
| P-FLU-08, P-FLU-09, P-FLU-12 | 05 | Refuerza |
| P-FLU-13, P-FLU-14 | 05 | Nuevas |
| P-API-02 | 07 | Refuerza |
| P-API-06 | 07 | Nueva |
