# Prueba de `race-engineer` v1 (entonces llamada `race-engineer`) (2026-10-07)

**Método:** dos agentes sin el contexto de esta conversación, cada uno con la skill como única guía.

| Prueba | Proyecto | Modo | Resultado |
|---|---|---|---|
| A | Proyecto desechable (Node/Express que llama a Claude, con `.env` **versionado**) en el scratchpad | Nuevo, con escritura | Generó `AGENTS.md`, `.claude/settings.json`, `.codex/config.toml`, la guardia, los revisores y las plantillas de estado. La guardia bloqueó 9 de 9 accesos a `.env` y permitió `.env.example` y `npm test`. Detectó que los comandos documentados (`npm test`, `npm run lint`) fallaban y los corrigió en `AGENTS.md` |
| B | Proyecto piloto (privado) | Auditoría, **solo lectura** | Informe no publicado (contiene código del proyecto). Repitió lo que ya habíamos encontrado a mano y añadió **tres hallazgos nuevos**: secretos de `~/.piloto` y despliegues sin barrera en Windows; Codex casi sin reglas (lo importante solo está en `CLAUDE.md`); y el modelo por defecto de Codex del usuario, caro y con esfuerzo alto, que contradice la tabla de enrutado de `CLAUDE.md` |

Ninguno de los dos modificó nada fuera de lo permitido. El `.gitignore` del proyecto piloto cambió durante la prueba por trabajo paralelo en el proyecto, no por la auditoría.

## Problemas encontrados y corrección aplicada

| Problema | Corrección |
|---|---|
| `.env` ya versionado: `.gitignore` no lo protege y el inventario no lo distinguía | El inventario marca «VERSIONADO en git»; la skill propone `git rm --cached` y rotar el secreto, como decisión del usuario |
| La guardia revisaba el contenido escrito: bloqueaba editar `AGENTS.md` o `.gitignore` si mencionaban `.env` | Revisa solo rutas (`file_path`, `path`, cabeceras de `apply_patch`) y comandos |
| Mensajes de la guardia mal codificados en Windows | stdout y stderr en UTF-8 |
| Secretos fuera del árbol (`~/.piloto/*.key`) invisibles para el inventario | Nueva sección «secretos fuera del proyecto citados en instrucciones o código» |
| La lista de secretos del inventario y la de la guardia no coincidían | El inventario usa la de la guardia e indica qué patrones hay que añadir a `guardia.txt` |
| Rutas «rotas» falsas (`ui/narrar/` dentro de un paquete Kotlin) | Se resuelven por sufijo dentro del árbol |
| Tamaño en bytes subestimado con CRLF | Se mide sobre el archivo |
| `git status` podía escribir en `.git/index` | `GIT_OPTIONAL_LOCKS=0` |
| No veía el modelo y el esfuerzo por defecto de Codex ni el detalle de `rules` | Se extraen; `rules`: total y aprobaciones puntuales (en el proyecto piloto, 65 de 91) |
| No miraba los `CLAUDE.md` de carpetas superiores al repositorio | Se revisan; `~/.claude/CLAUDE.md` se excluye, porque no cuenta |
| No había modo «solo lectura» | Estado ⏸ pendiente en el informe; la skill lo prevé |
| No estaba claro cómo encajar `prompt-audit` en el informe | Una sola ejecución; informe completo como anexo |
| El criterio de `claude-code-setup` no estaba escrito | Tabla «señal → recomendación» en `references/herramientas.md`, sin necesidad del plugin |
| Faltaban Codex en segundo plano y código escrito por Codex | Sección «Casos especiales» y comprobaciones 4.4 y 4.6 |
| Qué hacer si un comando documentado falla | Se documenta el que funciona; el arreglo pasa a «Necesita tu decisión» |
| Plantillas: rutas de `progress.md`, revisor solo en `CLAUDE.md`, ejemplos de directivas solo de Python, ruta relativa del hook de Codex, red apagada sin aviso | Corregidas |

## Pendiente de verificar en una sesión real (no se puede desde un subagente)

- ~~Que Claude Code ejecute el hook con `$CLAUDE_PROJECT_DIR` en Windows y con la herramienta PowerShell~~: **verificado** en este proyecto (ver `pruebas/este-proyecto/auditoria.md`).
- ~~Que Codex dispare el hook con los nombres de herramienta reales y lo deje aprobar con `/hooks`~~: **verificado**, tras corregir la guardia para que bloquee con JSON y no con el código de salida (ver `pruebas/este-proyecto/auditoria.md`).
- Probar `/context`, `/status` y `/debug-config` después de aplicar la plantilla.
