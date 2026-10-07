# F001 · Plugin oficial `claude-code-setup`

- **Tipo:** texto pegado (post de redes) + verificación del plugin en el marketplace oficial
- **Origen:** post aportado por el usuario; código del plugin en `claude-plugins-official/plugins/claude-code-setup` (caché local del marketplace)
- **Autor / organización:** Anthropic (autora en el README: Isabella He)
- **Fecha de la fuente:** desconocida (plugin v1.0.0)
- **Fecha de incorporación:** 2026-10-07
- **Aplica a:** Claude
- **Calidad percibida:** post: media-baja (tono promocional); plugin: alta (oficial, revisado su contenido)

## Resumen

El post recomienda instalar el plugin `claude-code-setup` (`/plugin install claude-code-setup@claude-plugins-official`) porque analiza el proyecto y recomienda automatizaciones. Verificado: existe, es de Anthropic y contiene una única skill, `claude-automation-recommender`. Inspecciona el repositorio (lenguaje, framework, dependencias, tests, CI, configuración de Claude existente) y recomienda **1–2 elementos por categoría**: servidores MCP, skills, hooks, subagentes y plugins. Incluye tablas «señal del código → recomendación» y fragmentos de configuración.

## Puntos clave

- **Es de solo lectura:** recomienda, pero no crea ni modifica archivos. El post exagera al decir que «configura paso a paso»: da fragmentos de ejemplo y el usuario los aplica (o se lo pide a Claude aparte).
- **Recomienda poco, a propósito:** 1–2 por categoría, 3–5 solo si se pide una categoría concreta. Omite las categorías que no aplican.
- **Mapeo de señales a hooks:** Prettier → formatear tras editar; ESLint/Ruff → lint; TypeScript → typecheck; carpeta de tests → ejecutar tests relacionados; `.env` → bloquear edición; lockfiles → bloquear edición.
- **Control de invocación de skills:** `disable-model-invocation: true` (solo el usuario; para acciones con efectos: deploy, commit, enviar), `user-invocable: false` (solo Claude; conocimiento de fondo), `context: fork` (ejecución aislada).
- Versionar `.mcp.json` para que todo el equipo comparta los mismos MCP.
- Indica usar búsqueda web para ir más allá de sus tablas de referencia.
- No está instalado en este equipo; solo aparece en la caché del marketplace.

## Prácticas extraídas

| ID | Archivo de conocimiento | Nueva / Refuerza / Contradice |
|---|---|---|
| P-HER-01 | 06-herramientas.md | Nueva |
| P-SKL-06 | 02-skills.md | Nueva |
| P-AUT-01 | 03-automatizacion-y-permisos.md | Refuerza (+ mapeo de señales) |
| P-AUT-03 | 03-automatizacion-y-permisos.md | Refuerza |
| P-MCP-01 | 04-subagentes-y-mcp.md | Refuerza |
| D-02, D-03 | 00-diseno-de-la-skill.md | Nueva (diseño) |

## Descartado y motivo

- Recomendaciones concretas de MCP y plugins de terceros (context7, Supabase, etc.): dependen de cada proyecto. Se tratan como catálogo de referencia, no como práctica general.
