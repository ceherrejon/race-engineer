# Experimento: ¿la regla «How / What / Why / Why not» reduce los comentarios?

**Fecha:** 2026-10-07.

**Diseño:**
- **Tarea:** la misma para todos: un limitador de peticiones de ventana deslizante en Python, con sus pruebas y commit. Tiene casos límite pensados para tentar a comentar (reloj que retrocede, purga, límite 0).
- **Agentes:** subagentes de Claude Code (Opus 5.5), seis en total, dos por variante. Cada uno trabaja en un repositorio git limpio y lee su `AGENTS.md`.
- **Variantes:** el encargo es idéntico; lo único que cambia es el `AGENTS.md`.
  - **A · control:** solo la descripción del proyecto.
  - **B · regla literal:** «En el código, el How / En el código de pruebas, el What / En el registro de commits, el Why / En los comentarios del código, el Why not».
  - **C · regla reescrita:** cada tipo de información en un solo sitio, con motivos y excepciones. Es el texto de `skill/race-engineer/templates/fragmentos/comentarios.md`.

**Medición:** el inventario de `skill/limpiar-comentarios/scripts/comentarios.py`, agrupado en bloques de comentario consecutivos, y el número de palabras del mensaje de commit.

## Resultados

| Rep. | Código: bloques de comentario | Código: docstrings | Pruebas: bloques de comentario | Pruebas: docstrings | Palabras del commit |
|---|---|---|---|---|---|
| A1 | 2 | 3 | 6 | 0 | 12 |
| A2 | 2 | 3 | 7 | 0 | 15 |
| B1 | 4 | 2 | 8 | 0 | 120 |
| B2 | 3 | 0 | 0 | 15 | 97 |
| C1 | 1 | 5 | 1 | 0 | 189 |
| C2 | 1 | 4 | 0 | 0 | 226 |

**Qué hizo cada variante:**
- **A · control:** pocos comentarios en el código y razonables, pero las pruebas se llenan de narración («# 9 sale de la ventana», «# tratado como 100»). El commit trae solo el título: ningún «por qué».
- **B · regla literal:**
  - Los commits sí explican el porqué: multiplican por 7–8 el texto.
  - Los comentarios del código **aumentan**. Todos son «why not» de buena calidad («no se lanza excepción ante un reloj que retrocede: un ajuste de NTP tumbaría al llamador»), pero son más que en el control. El modelo lee la regla como «cada sitio tiene su tipo de texto» y la toma como invitación a llenar también el hueco de los comentarios.
  - El «What» en las pruebas se interpretó de forma inconsistente: B2 puso un docstring en cada prueba, mientras que B1 dejó 8 bloques de comentario.
- **C · regla reescrita:**
  - Es la variante con menos comentarios: un solo bloque en el código, el «why not» de la estructura de datos.
  - Conserva los docstrings de la API pública, que la regla permite expresamente.
  - Las pruebas quedan prácticamente sin comentarios.
  - Los commits son los más completos: contexto, decisión, alternativas descartadas y su motivo.

## Conclusión

1. **La idea funciona sobre todo en los commits.** El «Why» pasa del código al mensaje de commit en las dos variantes que lo piden.
2. **Tal como está escrita, no reduce los comentarios.** Cambia su tipo y en este experimento los aumentó. La formulación como aforismo de cuatro casillas invita a llenar las cuatro.
3. **La versión reescrita cumple el objetivo.** La diferencia está en enunciar que cada información vive en un solo sitio, dar el motivo, poner «solo» en los comentarios y listar las excepciones (API pública, directivas, avisos legales, nada de código comentado).

**Límites del experimento:** dos repeticiones por variante, una sola tarea, un solo lenguaje (Python) y un solo modelo. No se probó con Codex/GPT, que es quien lee `AGENTS.md` en un flujo real. Es un indicio, no una prueba.
