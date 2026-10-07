## Traspasos entre agentes

Cuando un agente le pasa trabajo a otro, lo hace con un archivo que una persona pueda leer, no con un mensaje. El archivo lleva:

- la tarea, en una línea accionable;
- las entradas, nombradas;
- qué cuenta como terminado, escrito antes de empezar;
- la confianza en el resultado y cómo se midió;
- qué se intentó y falló;
- quién se hace cargo si el trabajo se detiene.

Cada paso termina con una comprobación que puede fallar (pruebas, rúbrica, umbral, aprobación humana). Tras dos intentos fallidos la tarea vuelve a quien la encargó: un tercer intento con el mismo encargo es un problema de diseño, no de suerte. Antes de reintentar, revisa el encargo.

Si un agente no puede terminar, escribe una línea: qué estaba haciendo, qué tiene y qué necesita. Nada de reintentos en bucle ni conjeturas.
