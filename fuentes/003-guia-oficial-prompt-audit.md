# F003 · Guía oficial `shared/prompt-audit.md` (skill `claude-api`)

- **Tipo:** documentación oficial, incluida en Claude Code v2.1.289
- **Origen:** `bundled-skills/2.1.289/.../claude-api/shared/prompt-audit.md` (237 líneas)
- **Autor / organización:** Anthropic
- **Fecha de la fuente:** caché del 2026-09-25
- **Fecha de incorporación:** 2026-10-07
- **Aplica a:** Claude. Los Grupos 2 y 4 aplican también a `AGENTS.md` y a cualquier agente.
- **Calidad percibida:** alta

## Resumen

Es el procedimiento completo detrás de `/claude-api prompt-audit`. El objetivo es encontrar **instrucciones concretas que ya no encajan**: con el modelo, con el proyecto o entre sí. Acortar no es el objetivo: «cada token se gana su sitio», pero nada se borra por largo. Entrega siempre dos cosas: un informe (`archivo:línea`, evidencia, patrón, motivo, confianza, acción) y un parche propuesto que no se aplica sin consentimiento. Organiza los problemas en cuatro grupos e incluye una «lista de lo que se conserva» tan vinculante como la de patrones.

## Puntos clave

- **Paso 0:** fijar el alcance y el modelo objetivo sin preguntar, y declararlos como supuestos al inicio del informe. La configuración de usuario (`~/.claude/`) solo entra si se pide expresamente.
- **Inventario:** todo lo que llega al modelo como texto. No lee `settings*.json` ni `.mcp.json`, porque pueden contener secretos.
- **Procedencia con `git blame`:** para cada línea enfática o prohibitiva, ¿qué fallo, en qué modelo, previno?
- **Regla para decidir qué se borra:** ¿podría el modelo saberlo ya? Lo que solo sabe el autor se conserva: público, producto, entorno, nivel de calidad y los **motivos** de cada restricción.
- **Grupo 1 · Texto con patrones antiguos:**
  - lenguaje de presión, en las dos direcciones: el énfasis inflado y también los «try to / if possible» puestos en requisitos;
  - andamiajes que hoy sustituye una función de la API (thinking, effort, structured outputs);
  - sobreespecificación: pasos rígidos, listas de prohibiciones, un único ejemplo de referencia, muros de viñetas, relleno, vocabulario de evaluación;
  - fósiles: redacción relativa a versiones anteriores, parches acumulados, reglas que nada hace cumplir, supresores de narración, reglas contra el formato;
  - cúmulos de prohibiciones: se juzgan por su procedencia.
- **Grupo 2 · Archivos de configuración frágiles:**
  - SKILL.md que explica lo que el modelo ya sabe;
  - grado de libertad mal ajustado;
  - «trampa de lo reciente»: un tropiezo de una sesión convertido en regla permanente;
  - datos volátiles: rutas, flags, versiones; hay que comprobar que existan;
  - archivos que se contradicen: gana el más reciente según `blame`, siempre como propuesta;
  - contenido con fecha;
  - narrativas históricas;
  - descripciones que enumeran disparadores en vez de categorías de intención.
- **Grupo 3 · Descripciones de herramientas:** se juzgan por precisión y fidelidad al contrato, no por brevedad. El fallo más común es quedarse corto.
- **Grupo 4 · Configuración de peticiones y arquitectura:**
  - parámetros fósiles de la API;
  - harness que edita el historial;
  - orden que rompe la caché;
  - un LLM ejecutando un plan determinista;
  - subagentes redundantes;
  - sin registro de tokens.
- **Lo que se conserva:**
  - el contexto nunca es relleno, y la longitud no es el criterio;
  - las operaciones frágiles mantienen guiones exactos;
  - las prohibiciones contra fallos que aún se reproducen se quedan;
  - el texto de disparo puede tener urgencia calibrada;
  - la redundancia que funciona no se toca;
  - una línea de rol está bien;
  - a veces ajustarse a un modelo nuevo significa **añadir** texto.
- **Paso 7:** cada eliminación es una hipótesis. Se prueba el comportamiento antes y después, un cambio a la vez, y la auditoría se repite con cada modelo nuevo.

## Prácticas extraídas

| ID | Archivo | Tipo |
|---|---|---|
| P-INS-01 | 01-instrucciones.md | Contradice en parte (criterio de longitud) → resuelto |
| P-INS-12 a P-INS-16 | 01-instrucciones.md | Nuevas |
| P-SKL-07, P-SKL-08 | 02-skills.md | Nuevas |
| P-API-01, P-API-02 | 07-apps-con-api.md | Nuevas |
| D-05 | 00-diseno-de-la-skill.md | Nueva |
