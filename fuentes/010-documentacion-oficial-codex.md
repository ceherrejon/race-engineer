# F010 · Documentación oficial de Codex + inspección del Codex instalado + interoperabilidad con Claude Code

- **Tipo:** documentación oficial y comprobación local
- **Origen:**
  - **Documentación de Codex:** `learn.chatgpt.com/docs/*`. Las URL `developers.openai.com/codex/*` redirigen ahí con un 308. Páginas principales: `agent-configuration/agents-md`, `config-file/config-basic|config-advanced|config-reference`, `agent-approvals-security`, `windows/windows-sandbox`, `agent-configuration/rules`, `build-skills`, `hooks`, `agent-configuration/subagents`, `custom-prompts`, `extend/mcp`, `customization/memories`, `developer-commands`, `non-interactive-mode`, `import`, `guides/best-practices`.
  - **Código fuente:** `github.com/openai/codex`, `codex-rs` en `main`; versión estable `rust-v0.161.0` del 2026-10-07.
  - **Estándar abierto:** https://agents.md (Agentic AI Foundation, Linux Foundation).
  - **Claude Code:** https://code.claude.com/docs/en/memory.md, secciones «AGENTS.md», «Choose which instruction files load» y «Audit your instruction files».
  - **Local:** `codex-cli 0.160.0` instalado: `codex --help`, `codex exec --help`, `codex features list`, estructura de `~/.codex/`. No se abrieron `auth.json` ni las sesiones.
- **Fecha de incorporación:** 2026-10-07
- **Aplica a:** Codex y la convivencia Claude/Codex
- **Calidad percibida:** alta. Contrasté directamente tres puntos clave:
  - la carga de AGENTS.md en Codex;
  - la lectura nativa de AGENTS.md en Claude Code;
  - las opciones de aprobación del CLI instalado: `--full-auto` ya no aparece y existe `--approve-for-me`.

## Resumen

**Codex tiene equivalentes de casi todo lo de Claude Code:**
- instrucciones jerárquicas (`AGENTS.md`);
- configuración por proyecto (`.codex/config.toml`);
- skills con el mismo estándar (`SKILL.md`);
- hooks con eventos y formato casi idénticos;
- subagentes en TOML;
- MCP;
- reglas de ejecución (`rules/*.rules`);
- memorias, `/goal`, `/review` e `/init`.

**Diferencias que importan:**
- La capa de proyecto (config, hooks, reglas e incluso el `AGENTS.md` del proyecto) **solo se carga si el proyecto es de confianza**.
- `AGENTS.md` se lee una vez por sesión y **no admite imports**.
- En Windows nativo **sí hay sandbox** (elevated / unelevated).
- Por defecto **no se filtran** las variables de entorno con secretos.
- Varias cosas cambiaron en 2026:
  - `--full-auto` está obsoleto;
  - `approval_policy = "untrusted"` ya no existe;
  - los perfiles son archivos aparte;
  - los prompts personalizados quedaron obsoletos en favor de las skills;
  - la ruta de skills de usuario es `~/.agents/skills`.

**Claude Code (v2.1.277+) lee `AGENTS.md` de forma nativa, pero solo cuando no hay `CLAUDE.md` ni `CLAUDE.local.md`.** Ignora `AGENTS.override.md` y `.agents/`. Codex no lee `CLAUDE.md` salvo con `project_doc_fallback_filenames`, y solo si falta `AGENTS.md`.

## Hallazgos locales (configuración de usuario; no se modificó nada)

- `~/.codex/AGENTS.md` dice que la skill de graphify está en `~/.Codex/skills/graphify/SKILL.md`, pero está en `~/.agents/skills/graphify`. Es una ruta rota (P-INS-13).
- `~/.codex/rules/default.rules` pesa 35 KB: son aprobaciones permanentes de comandos muy concretos, con rutas y scripts de una sola vez, que se acumularon.
- En `codex features list`, estas funciones están estables y activas:
  - `hooks`, `multi_agent`, `goals`, `plugins`, `skill_search`;
  - `worktrees`, `guardian_approval`, `fast_mode`.

  `memories` está estable pero apagada por defecto.

## Prácticas extraídas

| ID | Archivo | Tipo |
|---|---|---|
| P-CDX-01 a P-CDX-11 | 10-codex.md | Nuevas |
| Tabla de equivalencias Claude ↔ Codex | 10-codex.md | Nueva |
| P-INS-03 | 01 | Codex verificado |
| P-INS-04 | 01 | **Reescrita**: Claude ya lee AGENTS.md, con condiciones |
| C-01 | 01 | Actualizado: la doc oficial de Claude recomienda menos de 200 líneas |
| P-SKL-05 | 02 | Rutas de Codex verificadas |
| P-AUT-02 | 03 | Codex verificado |
| P-HER-02 | 06 | `/doctor prompt-audit` |
| P-HER-04 | 06 | Nueva (`/import` de Codex) |
| D-12 | 00 | Nueva |
