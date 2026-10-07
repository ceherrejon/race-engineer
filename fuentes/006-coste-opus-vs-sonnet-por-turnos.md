# F006 · «Opus 5.5 Is 2x the Price on Paper. In a Long Agent Loop It's 1.26x»

- **Tipo:** artículo en X (hilo largo)
- **Origen:** https://x.com/gippp69/status/2106744347836153989, leído con el navegador integrado porque WebFetch devuelve 402
- **Autor / organización:** Gipp (@gippp69)
- **Fecha de la fuente:** 2026-10-04 (precios del 2026-10-03)
- **Fecha de incorporación:** 2026-10-07
- **Aplica a:** Claude (las cifras). Los principios de caché por modelo y traspaso aplican a Ambos.
- **Calidad percibida:** alta en lo verificable. Los precios coinciden con la tabla oficial de la skill `claude-api` (caché del 2026-09-25) y recalculé toda la aritmética: sale idéntica. El propio autor declara qué no ha medido.

## Resumen

En un bucle de agente con caché, cada turno tiene tres partes: lectura de todo el contexto (precio de lectura de caché, $0.20/M, **igual en Opus y Sonnet**), escritura de lo nuevo y salida (incluido el thinking). Solo las dos últimas cuestan el doble en Opus. Por eso la diferencia por turno baja de 1.88x con 20K de contexto a 1.26x con 400K. Lo que decide el coste es **turnos por tarea terminada**: con 150K, a Opus le basta terminar en un 33 % menos de turnos para empatar.

El error caro es otro: escalar tarde. La caché es por modelo, así que pasar una sesión de Sonnet a Opus con 300K de contexto cuesta $1.50 solo en reescribir la caché. Con un traspaso de 20K cuesta $0.10.

## Puntos clave

- **Coste por tarea** = coste por turno × turnos hasta terminar. La métrica es **$ por tarea aprobada** ($/pass), con los intentos fallidos incluidos.
- **El thinking oculto se cobra como salida.** El nivel de esfuerzo mueve el ratio más que el tamaño del contexto.
- **Escalar pronto y limpio:**
  - decidir el modelo en los primeros turnos;
  - si hay que cambiar, sesión nueva con un traspaso corto: la tarea, el chequeo que falla y los 3 archivos clave, **no el historial**;
  - el traspaso además es mejor entrada, porque el modelo nuevo no hereda los callejones sin salida del anterior.
- **Detectar pronto las tareas difíciles:** un chequeo temprano (¿compila?, ¿pasa la primera prueba?, ¿tocó los archivos correctos?) hace posible escalar en el turno 6 y no en el 40.
- **Pausas y caché:** la caché dura 5 minutos por defecto. Con 150K, un fallo de caché cuesta $0.38 en Sonnet y $0.75 en Opus. La caché de 1 hora compensa si hay al menos una pausa de más de 5 min cada ~45 turnos.
- **Lo que rompe la caché o desperdicia dinero:**
  - cambiar de modelo a mitad de sesión;
  - cambiar el esfuerzo turno a turno;
  - un prefijo inestable;
  - poner `max_tokens` bajo para «ahorrar» (respuesta cortada y segunda ejecución).
- **Incluye un script** que calcula $/turno, turnos medios y $/pass por modelo a partir de un `usage.jsonl` con id de tarea y resultado.

## Contraste con fuentes oficiales

- **Coincide** con la skill `claude-api`: «judge cost per completed task, not per request»; las cachés son por modelo; cambiar el esfuerzo global invalida la caché; no rebajar `max_tokens`.
- **Matiz** (ver C-03 en `07-apps-con-api.md`): la guía oficial pide medir primero la alternativa simple, el modelo más capaz con menos esfuerzo, antes de montar una cascada Sonnet→Opus. Una sola caché evita el impuesto de escalada.
- **Relacionado:** Claude Code v2.1.243–245 añadió `promptCacheTtl`, que permite caché de 1 h en la conversación principal y de 5 min en los subagentes. Según una fuente secundaria ([classmethod](https://dev.classmethod.jp/en/articles/20260825-cc-updates-v2-1-245/)), aplica a usuarios con API key o proveedor cloud. **Pendiente de confirmar** con la documentación oficial.

## Lo que el autor no midió (lo declara)

La forma del turno (5.500 tokens nuevos y 1.500 de salida), cuántos turnos menos necesita Opus en trabajo real, la tasa real de fallos de caché y el ejemplo mensual son supuestos, no datos.

## Prácticas extraídas

| ID | Archivo | Tipo |
|---|---|---|
| P-FLU-06, P-FLU-07 | 05-flujo-y-contexto.md | Nuevas |
| P-API-01 | 07-apps-con-api.md | Refuerza (+ id de tarea y resultado) |
| P-API-04, P-API-05 | 07-apps-con-api.md | Nuevas |
| C-03 | 07-apps-con-api.md | Matiz registrado |
| P-AUT-06 | 03-automatizacion-y-permisos.md | Nueva (`promptCacheTtl`, confianza baja) |
