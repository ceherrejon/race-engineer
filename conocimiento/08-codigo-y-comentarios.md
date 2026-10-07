# 08 · Código, comentarios y commits

### P-COD-01 · Cada explicación en un solo sitio  `[Ambos]`
- **Qué:** Incluir en `AGENTS.md` / `CLAUDE.md` el fragmento `skill/race-engineer/templates/fragmentos/comentarios.md`:
  - el código dice cómo;
  - las pruebas, qué;
  - el commit, por qué (contexto, motivo, alternativas descartadas);
  - los comentarios, solo lo que el código no puede expresar y seguirá siendo cierto.
  - Excepciones: documentación de API pública, directivas de herramientas, avisos legales. Nada de código comentado.
- **Por qué:** Los comentarios que narran se quedan viejos y contradicen el código. El porqué en el commit queda atado al cambio exacto.
- **Cómo verificarla:** Ejecutar `limpiar-comentarios/scripts/comentarios.py inventario`. Muchos `a_revisar` narrativos, o commits de una línea, indican que la práctica no se cumple.
- **Evidencia:** experimento con 6 agentes: la versión reescrita dejó 1 bloque de comentario y commits de 190–226 palabras; el control, 2 bloques más narración en las pruebas y commits de 12–15 palabras.
- **Fuentes:** F005 · **Confianza:** media (n=2 por variante, solo Opus 5.5 y Python)

### P-COD-02 · La limpieza de comentarios es una tarea aparte y verificable  `[Ambos]`
- **Qué:** En código existente, limpiar los comentarios con la skill `limpiar-comentarios`:
  - inventario por categorías;
  - decisión por categoría;
  - lotes pequeños;
  - `comentarios.py verificar`, que debe responder «solo comentarios»;
  - compilar y pasar las pruebas.
  - Nunca se mezcla con cambios de código.
- **Por qué:** Una limpieza masiva hecha por un agente puede colar cambios de código. El verificador lo detecta: compara el AST en Python y el código sin comentarios en los demás lenguajes.
- **Fuentes:** F005 · **Confianza:** media

### P-COD-03 · No limpiar comentarios fuera del alcance de la tarea  `[Ambos]`
- **Qué:** Mientras se hace otra tarea, no se borran ni reescriben comentarios de código que la tarea no toca.
- **Por qué:** Ensancha el diff y dificulta la revisión. Además, una regla nueva sobre comentarios tienta al agente a «arreglar» todo lo que ve.
- **Fuentes:** F005 (deducción del diseño, coherente con la regla «un solo escritor / no ensanchar el diff» del proyecto piloto) · **Confianza:** media

## Conflictos

### C-02 · ¿Comentarios del «qué»?
- **F005 (aforismo):** los comentarios, solo para el «why not».
- **Hillel Wayne (2017):** un comentario que resume qué hace un bloque ahorra saltar entre funciones.
- **Resolución:** se permite el resumen cuando entender el código exigiría saltar entre varias funciones; la narración línea a línea, no. Queda recogido en el criterio de `limpiar-comentarios`.
