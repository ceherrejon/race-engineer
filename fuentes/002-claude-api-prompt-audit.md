# F002 · `/claude-api prompt-audit`

- **Tipo:** texto pegado (post de redes) + verificación en artículos y changelog
- **Origen:** post aportado por el usuario; verificación en [wmedia.es](https://wmedia.es/es/tips/claude-code-auditar-claude-md-prompt-audit), [dev.classmethod.jp (v2.1.221)](https://dev.classmethod.jp/en/articles/20260804-cc-updates-v2-1-221/), [aident.ai](https://aident.ai/blog/audit-claude-md-for-newer-models)
- **Autor / organización:** funcionalidad de Anthropic incluida en Claude Code
- **Fecha de la fuente:** disponible desde Claude Code v2.1.221 (agosto de 2026)
- **Fecha de incorporación:** 2026-10-07
- **Aplica a:** Claude (la herramienta); los principios aplican en parte a Ambos
- **Calidad percibida:** post: baja (sensacionalista e inexacto); funcionalidad: alta (confirmada por varias fuentes independientes)

## Resumen

`prompt-audit` es un subcomando de la skill `claude-api`, que viene incluida en Claude Code. Inventaría todo lo que le llega al modelo como texto (`CLAUDE.md`, `SKILL.md`, archivos de reglas, descripciones de herramientas y, si el proyecto llama a la API, el código que construye las peticiones). Señala por archivo y línea los patrones pensados para modelos anteriores y propone un parche. No cambia nada sin consentimiento.

## Puntos clave

- **Patrones que detecta:**
  - lenguaje de presión («CRITICAL: YOU MUST ALWAYS», «IMPORTANT!!!»);
  - andamiaje de razonamiento («piensa paso a paso», `<scratchpad>`, `<thinking>`);
  - instrucciones redundantes («sé exhaustivo, no pares antes de tiempo»);
  - pasos numerados en tareas de criterio;
  - ejemplos únicos sin marcar como ilustrativos;
  - reglas contradictorias;
  - instrucciones obsoletas.
- Consulta `git blame` para entender por qué se añadió cada línea enfática.
- Postura explícita: sin evals, cada cambio es una hipótesis.
- Sin argumentos no audita el `~/.claude/CLAUDE.md` global; el alcance depende de dónde se lance y de las rutas indicadas.
- Conviene repetirlo cuando cambia el modelo.
- **Correcciones al post:**
  - no lo «acaba de soltar un ingeniero»: es una funcionalidad publicada en una versión;
  - no «borra» nada, propone;
  - lo de «5 minutos» no está verificado.

## Prácticas extraídas

| ID | Archivo de conocimiento | Nueva / Refuerza / Contradice |
|---|---|---|
| P-INS-05 | 01-instrucciones.md | Refuerza (sube a confianza alta) |
| P-INS-06 | 01-instrucciones.md | Refuerza (+ validar con tareas de prueba) |
| P-INS-08 | 01-instrucciones.md | Nueva |
| P-INS-09 | 01-instrucciones.md | Nueva |
| P-INS-10 | 01-instrucciones.md | Nueva |
| P-INS-11 | 01-instrucciones.md | Nueva |
| P-HER-02 | 06-herramientas.md | Nueva |

## Descartado y motivo

- «Reescribir todo con la guía oficial»: no se adopta como reescritura masiva. Se adopta la auditoría con cambios aprobados uno a uno.

## Pistas abiertas

- `/skill-doctor`: aparece en los resultados de búsqueda como otra herramienta de auditoría de skills y contexto ([implicator.ai](https://www.implicator.ai/anthropic-claude-code-skill-doctor-context-audit.md)). Pendiente de analizar.
- Guía oficial de prompting para los modelos actuales: es la base de los criterios de `prompt-audit`. Conviene incorporarla como fuente directa.
