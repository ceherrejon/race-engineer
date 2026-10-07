<!-- Plantilla: borra las secciones que no apliquen. «Comandos» y «Terminado significa» son obligatorias: si faltan datos, pregúntalos. -->
# <Nombre del proyecto>

<Qué es, para quién y qué importa más, en 2–4 líneas. Es contexto que el agente no puede deducir del código.>

## Estructura

- `<carpeta>/`: <qué vive ahí>
- `<carpeta>/`: <qué vive ahí>

## Comandos

- Instalar dependencias: `<comando>`
- Ejecutar en local: `<comando>`
- Todas las pruebas: `<comando>`
- Una sola prueba: `<comando con ejemplo>`
- Lint / formato / tipos: `<comando>`

## Convenciones

<Solo lo que no es obvio leyendo el código, con su motivo. Por ejemplo: «Las fechas se guardan en UTC porque el servidor y la app están en zonas distintas».>

## Restricciones

<Lo que no se debe hacer y por qué. Por ejemplo: «No añadir dependencias sin preguntar: cada una pesa en el binario».>

## Terminado significa

- <archivos o resultados que deben existir>
- <pruebas o comprobaciones que deben pasar, con el comando>
- El informe final da las rutas cambiadas y el resultado de cada comprobación.

## Autonomía

Cuando un paso no necesita mi decisión, sigue: pon las notas de estado junto a tu siguiente acción, no en un turno aparte. Para y pregunta solo si no puedes avanzar sin mí o antes de algo destructivo o difícil de revertir: borrar datos, reescribir el historial de git, publicar o desplegar, tocar archivos fuera de este repositorio.

Termina cada tarea con tres apartados: **Bloqueado por mí** (lo que necesita mi decisión), **Cambiado** y **Encontrado** (lo que viste fuera del encargo; se reporta, no se arregla).

## Dónde va cada explicación

Cada tipo de información vive en un solo sitio, para que no se contradiga ni se quede vieja:

- **Cómo funciona:** lo dice el propio código, con nombres claros y funciones pequeñas. No escribas comentarios que narren lo que la línea siguiente ya dice.
- **Qué debe hacer:** lo dicen las pruebas; el nombre de cada prueba describe el comportamiento esperado.
- **Por qué se hizo el cambio:** va en el mensaje de commit (contexto, motivo, alternativas descartadas).
- **Comentarios en el código:** solo para lo que el código no puede expresar y seguirá siendo cierto mientras el código exista: por qué no se hizo de la forma obvia, una restricción externa o un workaround (con su referencia).

Se mantienen siempre: la documentación de la API pública, las directivas de herramientas (`# noqa`, `// eslint-disable-next-line`, `@Suppress`…) y los avisos legales. No dejes código comentado: git ya lo guarda. No limpies comentarios fuera del alcance de la tarea.

## Verificación

Antes de dar por buena una entrega, propia o de otro agente, pásala por el revisor del proyecto (subagente `revisor`) y comprueba su evidencia en los archivos, no en su informe.

## Configuración de agentes

La guardia de secretos (`.agents/hooks/guardia.py`) revisa cada acción. Si una lectura de secretos **no** queda bloqueada, avisa al usuario: probablemente falte un paso de `docs/agentes/INCORPORACION.md` en su máquina.

## Tareas largas

Para tareas de varias sesiones, copia `docs/agentes/plantillas/progress.md` junto a la tarea y actualízalo tras cada etapa: una sesión nueva debe poder continuar leyendo solo ese archivo. Los encargos grandes siguen `docs/agentes/plantillas/tarea.md`.
