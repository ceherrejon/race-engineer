# F005 · Regla «How / What / Why / Why not» para comentarios

- **Tipo:** texto pegado (consejo para `AGENTS.md`), más contraste y experimento propio
- **Origen:** aportado por el usuario. Es un aforismo que circula sin autor claro. Tiene ideas afines en [James Adam, «Two thoughts about maintainable software» (2020)](https://interblah.net/two-thoughts-about-maintainable-software), que propone poner el porqué en los commits, y una réplica en [Hillel Wayne, «What comments» (2017)](https://hillelwayne.com/post/what-comments/), que defiende los comentarios del «qué» cuando entender el código obliga a saltar entre funciones.
- **Fecha de incorporación:** 2026-10-07
- **Aplica a:** Ambos
- **Calidad percibida:** idea buena; formulación débil para agentes (ver el experimento)

## Resumen

Propone repartir cada tipo de explicación en un sitio:
- en el código, el *cómo*;
- en las pruebas, el *qué*;
- en el commit, el *por qué*;
- en los comentarios, solo el *por qué no*.

Busca que los agentes dejen de llenar el código de comentarios. Lo probé con 6 agentes (`pruebas/exp-comentarios/RESULTADOS.md`):
- **Commits:** la regla literal sí lleva el «por qué» a los commits, que pasan de unas 13 palabras a unas 110.
- **Comentarios:** no reduce los comentarios. Los cambia a «why not», de buena calidad, pero en mayor número.
- **Versión reescrita:** con motivos, «solo» y excepciones, logra a la vez la menor cantidad de comentarios y los commits más completos (más de 190 palabras).

## Puntos clave

- Los aforismos de casillas se leen como mandato para llenar cada casilla. Hay que enunciar el objetivo («cada información en un solo sitio») y el motivo.
- Excepciones imprescindibles: documentación de API pública, directivas de herramientas, avisos legales, el resumen de un algoritmo disperso (Wayne).
- Faltaba la parte de los proyectos con código existente. Se construyó la skill `limpiar-comentarios`, con un verificador que demuestra que solo cambiaron comentarios.

## Prácticas extraídas

| ID | Archivo | Tipo |
|---|---|---|
| P-COD-01 a P-COD-03 | 08-codigo-y-comentarios.md | Nuevas |
| C-02 | 08-codigo-y-comentarios.md | Conflicto registrado |
| P-INS-17 | 01-instrucciones.md | Nueva (enunciar objetivos en lugar de aforismos) |
