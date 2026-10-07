---
name: limpiar-comentarios
description: Limpia los comentarios de código ya escrito para que solo queden los que explican lo que el código no puede decir. Úsala cuando el usuario pida limpiar, reducir o revisar comentarios de un proyecto o carpeta, o adoptar una regla de comentarios en código existente. No cambia código, solo comentarios, y lo verifica.
disable-model-invocation: true
---

# Limpiar comentarios

El objetivo es que cada explicación viva en un solo sitio:
- **el código** dice cómo;
- **las pruebas**, qué;
- **el commit**, por qué;
- **los comentarios**, solo lo que el código no puede expresar y seguirá siendo cierto mientras exista: por qué no se hizo de la forma obvia, restricciones externas, workarounds.

Esta skill **solo toca comentarios**. Si un comentario existe porque el código es confuso, lo correcto es renombrar o extraer una función, pero eso es otra tarea: aquí el comentario se queda y se anota la sugerencia.

## Antes de empezar

- Que el árbol de trabajo esté limpio (`git status`) o, mejor, en una rama propia. Si hay otro agente escribiendo en el repositorio (Codex, un worktree), esperar a que termine.
- Que las pruebas pasen. Ese estado es la línea base.
- Acordar el alcance: qué carpetas entran. Quedan fuera el código generado, el de terceros (vendor) y las migraciones ya aplicadas.

## Proceso

1. **Inventario.** Ejecutar `python scripts/comentarios.py inventario <rutas>`. Clasifica cada comentario de forma determinista en `directiva`, `licencia`, `pendiente`, `documentacion`, `codigo_comentado` y `a_revisar`. Enseñar los totales al usuario antes de tocar nada.
2. **Decidir por categoría:**

   | Categoría | Acción |
   |---|---|
   | `directiva` (`noqa`, `eslint-disable`, `@Suppress`, `# type: ignore`, regiones) | Conservar siempre: cambian el comportamiento de herramientas. |
   | `licencia` | Conservar siempre. |
   | `documentacion` de API pública (docstrings, KDoc, JSDoc) | Conservar. Si contradice el código, se anota, no se reescribe aquí. En funciones privadas, un docstring que solo repite el nombre se puede quitar. |
   | `codigo_comentado` | Quitar después de leerlo: git lo conserva. Si parece una alternativa deliberada, se convierte en un «why not» de una línea. |
   | `pendiente` (TODO/FIXME) | No borrar en silencio. Se lista para el usuario: los que tienen referencia y siguen vigentes se quedan; los demás pasan al gestor de tareas o al backlog si el usuario lo aprueba. |
   | `a_revisar` | Decidir uno por uno con el criterio de abajo. |

3. **Criterio para `a_revisar`.** La pregunta es: ¿lo puede saber quien lee el código, sin el comentario, en el mismo sitio?
   - **Quitar:**
     - narración de lo que hace la línea siguiente;
     - historia («antes hacía X», fechas, autores, «arreglo del bug 12»), que pertenece al commit;
     - separadores decorativos;
     - comentarios en pruebas que repiten lo que dice el nombre de la prueba o la aserción.
   - **Conservar:**
     - por qué no se hizo de la forma obvia;
     - restricciones externas (API, hardware, normativa);
     - workarounds con su referencia;
     - unidades y rangos que el tipo no expresa;
     - el resumen de un algoritmo cuando entenderlo exigiría saltar entre varias funciones.
   - **Acortar:** un «por qué» válido escrito en tres párrafos se deja en una o dos frases.
   - **Ante la duda, conservar.** Un comentario de más cuesta poco; perder un motivo cuesta caro.
4. **Aplicar por lotes pequeños.** Un módulo o una carpeta por commit, para que la revisión sea posible. Si un comentario de historia contenía un motivo útil, ese motivo va al mensaje del commit de limpieza.
5. **Verificar cada lote.**
   - Ejecutar `python scripts/comentarios.py verificar --base <ref>`. Debe terminar en «solo comentarios»:
     - en Python compara el AST;
     - en los lenguajes tipo C, de `#` y de marcado compara el código sin comentarios;
     - `SOLO DOCSTRINGS` en Python es aceptable solo si lo que se quitó fue intencionado.
     - `CAMBIA CÓDIGO` obliga a deshacer y revisar el lote.
     - `NO SOPORTADO` exige revisar el diff a mano.
   - Compilar y correr las pruebas: siguen pasando.
6. **Informe:**
   - totales antes y después por categoría;
   - los TODO que necesitan decisión;
   - los comentarios conservados que delatan código confuso, como candidatos a refactor en otra tarea.

## Reglas

- Nunca mezclar la limpieza con cambios de código, ni en el mismo commit ni en el mismo lote.
- Al hacer otras tareas, no se limpian comentarios fuera del alcance de la tarea: ensancha el diff y dificulta la revisión. La limpieza es siempre una tarea propia.
- No inventar motivos: un «por qué» que no se conoce no se escribe.
- Para que no vuelva a pasar, proponer al usuario que añada a su `AGENTS.md` / `CLAUDE.md` el fragmento de `race-engineer/templates/fragmentos/comentarios.md`. La formulación de cuatro casillas («How / What / Why / Why not») no basta por sí sola: en una prueba aumentó los comentarios en vez de reducirlos.
