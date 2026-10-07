# 02 · Skills (habilidades)

### P-SKL-01 · La descripción decide cuándo se activa  `[Ambos]`
- **Qué:** El campo `description` del frontmatter debe decir qué hace la skill y **cuándo** usarla, con las palabras que usaría el usuario.
- **Por qué:** El agente solo ve nombre y descripción hasta que decide cargarla.
- **Cómo verificarla:** La descripción incluye disparadores concretos («úsala cuando…»).
- **Fuentes:** BASE · **Confianza:** media

### P-SKL-02 · Divulgación progresiva  `[Ambos]`
- **Qué:** `SKILL.md` breve con el flujo principal; detalles en `references/`, plantillas en `assets/` o `templates/`, lógica determinista en `scripts/`, cargados solo cuando hacen falta.
- **Por qué:** Ahorra contexto y mantiene la skill legible.
- **Cómo verificarla:** `SKILL.md` por debajo de ~500 líneas; referencias enlazadas desde el cuerpo.
- **Fuentes:** BASE · **Confianza:** media

### P-SKL-03 · Scripts para lo repetible y verificable  `[Ambos]`
- **Qué:** Si un paso es mecánico (validar, contar, generar), escribir un script en vez de describirlo en prosa.
- **Por qué:** Resultado reproducible y menos tokens.
- **Fuentes:** BASE · **Confianza:** media

### P-SKL-04 · Convertir procesos repetidos en skills  `[Ambos]`
- **Qué:** Cuando un procedimiento se explica al agente más de dos veces (despliegue, revisión, release), extraerlo a una skill del proyecto.
- **Por qué:** Saca contenido ocasional del archivo de instrucciones permanente.
- **Cómo verificarla:** Secciones largas de procedimiento en CLAUDE.md/AGENTS.md → candidatas a skill. Ejemplo real: en el proyecto piloto, el procedimiento de despacho a Codex ocupa media `CLAUDE.md` y se carga en cada sesión aunque no se despache nada.
- **Fuentes:** BASE, F004 · **Confianza:** alta

### P-SKL-05 · Ubicaciones  `[Claude]` `[Codex]`
- **Qué:**
  - `[Claude]` `.claude/skills/<nombre>/SKILL.md` (proyecto) y `~/.claude/skills/` (usuario).
  - `[Codex]` mismo estándar `SKILL.md` en `.agents/skills/` (proyecto, buscando hacia arriba hasta la raíz) y `~/.agents/skills/` (usuario). `~/.codex/skills` está obsoleta. Solo lee `name` y `description`. Detalle en P-CDX-06.
  - Ninguna de las dos herramientas lee la carpeta de la otra. Para compartir una skill hay que copiarla o enlazarla en las dos rutas (P-INS-04).
- **Fuentes:** BASE, F001, F010 · **Confianza:** alta

### P-SKL-06 · Controlar quién puede invocar cada skill  `[Claude]`
- **Qué:** En el frontmatter:
  - `disable-model-invocation: true` → solo el usuario puede invocarla. Para skills con efectos: deploy, commit, envíos.
  - `user-invocable: false` → solo Claude puede invocarla. Para conocimiento de fondo, como las convenciones del proyecto.
  - `context: fork` → se ejecuta aislada del contexto principal.
- **Por qué:** Evita que el modelo lance por su cuenta acciones con efectos, y que el usuario vea en `/` skills que no son para él.
- **Cómo verificarla:** Skills con efectos externos que no tienen `disable-model-invocation: true`.
- **Otros campos verificados (F007):** `allowed-tools`, `model` y `effort`. En el cuerpo se pueden usar `$ARGUMENTS`, `$0`, `$1` y `${CLAUDE_SKILL_DIR}`.
- **Fuentes:** F001, F007 · **Confianza:** alta

### P-SKL-07 · Descripción por categorías de intención, sin detalles de implementación  `[Ambos]`
- **Qué:** La `description` nombra las categorías de petición que la activan. No es una lista numerada que crece con cada disparo fallido, ni lleva el «cómo» (qué herramienta genera las imágenes, qué llave no hace falta).
- **Por qué:** La descripción viaja en cada petición; las enumeraciones generalizan peor y el detalle de implementación pertenece al cuerpo. Puede tener urgencia calibrada, porque las skills tienden a activarse menos de lo debido.
- **Fuentes:** F003, F004 · **Confianza:** media

### P-SKL-08 · Los archivos que referencia la skill existen  `[Ambos]`
- **Qué:** Cada `references/…`, `assets/…` o `scripts/…` citado en `SKILL.md` debe existir. Al copiar una skill de otro repositorio, copiar la carpeta entera.
- **Por qué:** Una referencia rota hace que el modelo busque en vano o invente el contenido.
- **Cómo verificarla:** Listar las rutas relativas citadas y probar que existen.
- **Fuentes:** F004 · **Confianza:** alta

### P-SKL-09 · Cada paso con un resultado observable; preparar y publicar, por separado  `[Ambos]`
- **Qué:** Cada paso del procedimiento deja algo comprobable: una selección de fuentes, un archivo guardado, una tabla de hallazgos. «Revisa la precisión» no basta; hay que nombrar quién revisa, contra qué y en qué formato informa. La acción con efectos (publicar, desplegar, enviar) es una skill o un paso aparte, con su propia aprobación.
- **Por qué:** Los pasos vagos dejan decisiones abiertas, y mezclar preparación con publicación quita el punto de control.
- **Fuentes:** F007 · **Confianza:** media

## Conflictos

(ninguno todavía)
