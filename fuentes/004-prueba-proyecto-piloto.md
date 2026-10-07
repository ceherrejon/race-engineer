# F004 · Prueba de `claude-code-setup` y `prompt-audit` sobre el proyecto piloto

- **Tipo:** prueba propia en un proyecto real
- **Origen:** un proyecto privado del autor (app Android + Worker de Cloudflare + scripts Python), al que aquí se llama «proyecto piloto». Los informes completos no se publican porque contienen código del proyecto.
- **Fecha de incorporación:** 2026-10-07
- **Aplica a:** Claude (las herramientas); el flujo con Codex como ejecutor afecta a Ambos
- **Calidad percibida:** alta como evidencia práctica (un solo proyecto, n=1)

## Qué se hizo

1. **Instalación:** `claude-code-setup` con alcance de proyecto. Solo añadió `.claude/settings.json` con `enabledPlugins`.
2. **Ejecución headless:** se intentó lanzar las dos herramientas con `claude -p` en modo solo lectura, y **falló** porque la sesión OAuth del CLI estaba caducada. La app de escritorio y el CLI de terminal se autentican por separado.
3. **Ejecución en sesión:**
   - `prompt-audit` se invocó con la skill `claude-api`;
   - el recomendador lo ejecutó un subagente siguiendo su `SKILL.md`.

## Resultados

- **`prompt-audit`:**
  - 18 hallazgos, 11 de ellos del Grupo 2: contradicciones entre `CLAUDE.md`, `AGENTS.md` y `GRAPHIFY.md`; una versión del CLI desmentida por el propio archivo; referencias de una skill a archivos que no existen; narrativas históricas.
  - Del Grupo 1 solo encontró problemas en la skill. El `CLAUDE.md`, bien escrito, apenas tenía patrones antiguos.
  - Los prompts de la app y la configuración de Sonnet 5.5 salieron limpios, salvo que no se registra el uso de tokens.
  - **El valor estuvo en la coherencia con el repositorio, no en el «estilo de los prompts».**
- **`claude-code-setup`:** sus recomendaciones fueron útiles (skill de release, guardia de despliegue y secretos, hook Stop para «Ã», subagentes de revisión y emulador, context7), pero solo porque el agente adaptó mucho la skill.
  - Su detección está pensada para npm y Python.
  - Le faltan filas para móvil.
  - No cruza con los plugins ya instalados, y habría recomendado duplicados.
  - Supone que Claude escribe el código.
  - No evalúa `CLAUDE.md`.
- **Se complementan:**
  - `prompt-audit` no juzga la longitud («cruft ≠ length»);
  - el recomendador propone **sacar a una skill** el procedimiento de despacho a Codex, que ocupa media `CLAUDE.md`. Es divulgación progresiva, no borrado.
- **Ninguna de las dos herramientas cubre:**
  - hooks y permisos existentes (`prompt-audit` no lee settings, a propósito);
  - `AGENTS.md` frente a los modelos de Codex;
  - el `.gitignore` de los secretos.

## Prácticas extraídas

| ID | Archivo | Tipo |
|---|---|---|
| P-HER-01, P-HER-02 | 06-herramientas.md | Refuerza + limitaciones observadas |
| P-SKL-04 | 02-skills.md | Refuerza (sube a alta) |
| P-AUT-05 | 03-automatizacion-y-permisos.md | Nueva |
| D-06, D-07, D-08 | 00-diseno-de-la-skill.md | Nuevas |
