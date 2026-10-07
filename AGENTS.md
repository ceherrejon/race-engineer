# Race Engineer · instrucciones para agentes (Claude Code y Codex)

Proyecto de investigación y compilación: el usuario aporta fuentes (textos, enlaces, documentos) sobre buenas prácticas para trabajar con Claude Code y Codex. El objetivo final es la skill en `skill/race-engineer/`. Idioma de trabajo: español.

## Protocolo al recibir una fuente

1. **Ficha** — crear `fuentes/NNN-slug.md` (numeración correlativa) con la plantilla de `fuentes/_plantilla.md`. Guardar resumen y puntos clave con nuestras palabras; nunca copiar el texto íntegro de material con derechos de autor (citas breves solo si son imprescindibles).
2. **Índice** — añadir una fila a `fuentes/INDICE.md`.
3. **Extracción** — convertir cada consejo útil en una práctica atómica dentro del archivo de `conocimiento/` que corresponda:
   - Si ya existe una práctica equivalente: añadir la fuente a su lista y ajustar la confianza; no duplicar.
   - Si contradice algo existente: no sobrescribir; registrar en la sección «Conflictos» del archivo y explicar ambas posturas.
   - Si es específica de una herramienta, marcarla `[Claude]` o `[Codex]`; si aplica a ambas, `[Ambos]`.
4. **Skill** — solo pasar a `skill/` prácticas con confianza alta o validadas por el usuario.
5. **Registro** — una línea en `CHANGELOG.md`.
6. **Informe al usuario** — resumir qué aporta la fuente, qué es nuevo, qué confirma, qué contradice y qué se descartó (y por qué).

## Formato de una práctica

```
### P-<TEMA>-NN · Título corto  `[Ambos|Claude|Codex]`
- **Qué:** la práctica en una o dos frases, accionable.
- **Por qué:** el beneficio o el problema que evita.
- **Cómo verificarla en un proyecto existente:** señal concreta y comprobable.
- **Fuentes:** F001, F004 · **Confianza:** alta | media | baja
```

Confianza: **alta** = varias fuentes independientes o documentación oficial; **media** = una fuente sólida o conocimiento base; **baja** = opinión aislada o sin contrastar. Las prácticas marcadas con fuente `BASE` provienen del conocimiento previo de Claude y deben confirmarse con fuentes.

## Criterios

- Preferir lo accionable y verificable sobre lo genérico («escribe buenas instrucciones» no es una práctica).
- Anotar la fecha o versión cuando un consejo dependa de una funcionalidad concreta; estas herramientas cambian rápido.
- Desconfiar de afirmaciones sin evidencia; señalarlas como tales.

## Mantenimiento de la skill

Si una fuente cambia una práctica que la skill cita (columna «Ref.» de `skill/race-engineer/references/checklist.md`), actualiza esa comprobación y regenera el resumen que viaja con la skill: `python3 herramientas/generar_practicas.py`. No edites `references/practicas.md` a mano.

Tras cambiar un script, una plantilla o el manifiesto `.claude-plugin/marketplace.json`, ejecuta `python -m unittest discover -s tests` (el CI repite las pruebas en Linux, macOS y Windows). Al publicar una versión, sube `version` en el manifiesto.

## Privacidad

Este repositorio es público. Las pruebas sobre proyectos privados y el material de terceros van en `privado/`, que git ignora; en lo versionado, el proyecto privado de prueba se llama «proyecto piloto». Las rutas personales de secretos van en `.agents/guardia.local.txt`, también ignorado.

## Configuración de agentes

La guardia de secretos (`.agents/hooks/guardia.py`) revisa cada acción de Claude y de Codex. Si una lectura de secretos **no** queda bloqueada, avisa al usuario: probablemente falte un paso de `docs/agentes/INCORPORACION.md` en su máquina. Para escribir documentación que menciona rutas de secretos, usa las herramientas de edición: en la shell, la guardia revisa el comando completo, heredocs incluidos.
