## Dónde va cada explicación

Cada tipo de información vive en un solo sitio, para que no se contradiga ni se quede vieja:

- **Cómo funciona:** lo dice el propio código, con nombres claros y funciones pequeñas. No escribas comentarios que narren lo que la línea siguiente ya dice.
- **Qué debe hacer:** lo dicen las pruebas; el nombre de cada prueba describe el comportamiento esperado.
- **Por qué se hizo el cambio:** va en el mensaje de commit (contexto, motivo, alternativas descartadas).
- **Comentarios en el código:** solo para lo que el código no puede expresar y seguirá siendo cierto mientras el código exista: por qué no se hizo de la forma obvia, una restricción externa o un workaround (con su referencia).

Se mantienen siempre: la documentación de la API pública (docstrings), las directivas de herramientas (`# noqa`, `// eslint-disable-next-line`, `@Suppress`…) y los avisos legales. No dejes código comentado: git ya lo guarda.
