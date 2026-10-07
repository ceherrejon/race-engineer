# Índice de fuentes

| ID | Título | Tipo | Aplica a | Fecha incorporación | Prácticas |
|---|---|---|---|---|---|
| BASE | Conocimiento previo de Claude (pendiente de contrastar) | — | Ambos | 2026-10-07 | ver `conocimiento/` |
| [F001](001-plugin-claude-code-setup.md) | Plugin oficial `claude-code-setup` | post + plugin verificado | Claude | 2026-10-07 | P-HER-01, P-SKL-06, D-01–D-04 |
| [F002](002-claude-api-prompt-audit.md) | `/claude-api prompt-audit` | post + artículos | Claude | 2026-10-07 | P-HER-02, P-INS-08–11 |
| [F003](003-guia-oficial-prompt-audit.md) | Guía oficial `prompt-audit.md` (skill `claude-api`) | documentación oficial | Claude (+Ambos) | 2026-10-07 | P-INS-12–16, P-SKL-07, P-API-01–02, D-05 |
| [F004](004-prueba-proyecto-piloto.md) | Prueba de ambas herramientas en el proyecto piloto | prueba propia | Claude (+Ambos) | 2026-10-07 | P-SKL-08, P-AUT-04–05, P-API-03, D-06–08 |
| [F005](005-regla-how-what-why-whynot.md) | Regla «How / What / Why / Why not» + experimento | consejo + prueba propia | Ambos | 2026-10-07 | P-COD-01–03, P-INS-17, C-02 |
| [F006](006-coste-opus-vs-sonnet-por-turnos.md) | Opus vs Sonnet: coste por turno y por tarea en bucles de agente | artículo (X) verificado | Claude (+Ambos) | 2026-10-07 | P-FLU-06–07, P-API-04–05, P-AUT-06, C-03 |
| [F007](007-harness-7-capas.md) | Harness de 7 capas para tareas largas (@beamnxw), 16 afirmaciones verificadas en docs oficiales | artículo (X) verificado | Claude (+Ambos) | 2026-10-07 | P-INS-18–19, P-SKL-09, P-AUT-07–09, P-SUB-03, P-MCP-02, P-FLU-08–12, P-HER-03, C-04, D-09–10 |
| [F008](008-prompt-equipos-de-agentes.md) | Prompt para diseñar equipos de agentes (imagen; autor real @zodchiii, basado en «Building Effective Agents») | imagen + artículo oficial | Ambos | 2026-10-07 | P-EQU-01–08, D-11 |
| [F009](009-guia-configuracion-opus-5-5.md) | Guía de configuración de Opus 5.5 (@zodchiii), contrastada con la guía oficial de migración | artículo (X) verificado | Claude | 2026-10-07 | P-INS-20, P-FLU-13–14, P-API-06, refuerzos en 04/05 |
| [F010](010-documentacion-oficial-codex.md) | Documentación oficial de Codex + Codex instalado + lectura de AGENTS.md en Claude Code | doc. oficial + local | Codex / Ambos | 2026-10-07 | P-CDX-01–11, P-INS-04 (reescrita), C-01 (actualizado), P-HER-04, D-12 |

## Pistas pendientes

- ~~`/skill-doctor`~~: resuelta en F007 (P-HER-03).
- Guía oficial de prompting de Anthropic para los modelos actuales.
- ~~`promptCacheTtl`~~: resuelta en F007 (P-AUT-06). `modelPicker` no aparece en la referencia oficial de ajustes.
- ~~Documentación oficial de Codex~~: resuelta en F010.
- Guías de Anthropic citadas en F007: «context engineering», «long-running harnesses», «writing effective tools», «agent evaluations».
