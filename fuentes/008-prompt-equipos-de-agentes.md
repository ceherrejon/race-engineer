# F008 · Prompt para diseñar equipos de agentes (imagen «Anthropic Engineer's Prompt for Agent Teams»)

- **Tipo:** imagen (JPEG) con un prompt estructurado en secciones XML, aportada por el usuario. La imagen no se publica en este repositorio porque tiene derechos de su autor; aquí solo va el resumen con nuestras palabras.
- **Autor real:** @zodchiii, según el pie de la propia imagen.
  - **Atribución engañosa:** el título y la foto sugieren que es de Erik Schluntz (Anthropic), pero el pie aclara que solo sigue el enfoque de «Building Effective Agents», que Schluntz coescribió, y que **él no lo escribió ni lo respalda**.
- **Base contrastada:** [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents), de Erik Schluntz y Barry Zhang, Anthropic, 2024-12-19.
- **Fecha de incorporación:** 2026-10-07
- **Aplica a:** Ambos (diseño de flujos con varios agentes: Claude + Codex + subagentes)
- **Calidad percibida:** media-alta. Es coherente con la guía oficial y con F003 (Grupo 4: «un LLM ejecutando un plan determinista», subagentes redundantes). Las cifras concretas (2 reintentos, 5 ejecuciones revisadas a mano, plan de 7 días) son heurísticas del autor.

## Resumen

Es un meta-prompt para pedir a Opus 5.5 el **equipo mínimo de agentes** que complete un flujo de principio a fin, junto con los prompts de cada uno.

**Antes de diseñar,** obliga a escribir el flujo manual en 6–12 pasos y a clasificarlos:
- los pasos con una regla exacta se convierten en **código**;
- los que requieren **juicio**, en agentes;
- el paso **irreversible** se queda con la persona.

**Después:**
- decidir entre un flujo fijo o un agente que elige, y por defecto usar cuatro roles: líder, trabajador, crítico y escriba;
- definir cada rol con una ficha;
- definir cada traspaso como un archivo con un contrato fijo;
- cerrar cada rol con una compuerta que pueda fallar.

**Incluye también:** antipatrones, modelo de costes, verificación, plan de introducción en 7 días, métricas y una regla de escalada.

## Puntos clave (con nuestras palabras)

- **Principios:**
  - un agente, un trabajo;
  - un rol se define por lo que **no** puede hacer;
  - cada traspaso es un archivo que una persona puede leer;
  - nadie revisa su propio trabajo;
  - los modelos baratos hacen la parte repetitiva;
  - enviar, fusionar y pagar quedan en manos humanas;
  - una compuerta que no puede fallar es decoración.
- **Contrato de traspaso:**
  - la tarea en una línea accionable;
  - las entradas, nombradas;
  - qué cuenta como terminado, escrito antes de empezar;
  - la confianza y cómo se midió;
  - qué se intentó y falló;
  - quién se hace cargo si se detiene.
- **Ficha de rol:**
  - el trabajo en una frase;
  - el modelo y por qué ese y no uno mayor;
  - las herramientas permitidas y las **denegadas**;
  - entradas y salidas tipadas;
  - la prueba que demuestra el éxito;
  - qué hace si no puede terminar.
- **Antipatrones:**
  - un orquestador que solo reenvía;
  - dos agentes compartiendo un trabajo;
  - un revisor que también lo escribió;
  - la memoria como volcado (todo se guarda y nada se recupera);
  - umbrales ajustados «a ojo» en vez de con ejemplos.
- **Compuertas:**
  - una rúbrica del crítico con puntuación;
  - el código de salida de las pruebas;
  - un umbral calibrado con ejemplos reales;
  - la persona antes de lo irreversible.

  Cada compuerta da un número que queda en el log y decide entre reintentar, redirigir o parar. Máximo 2 reintentos: un tercero indica un fallo de diseño.
- **Verificación:**
  - una línea de log por agente;
  - leer a mano las primeras ejecuciones;
  - provocar a propósito un fallo conocido;
  - definir qué señal obliga a reescribir en vez de ajustar.
- **Métricas:**
  - tiempo frente al camino manual;
  - coste por ejecución, por día y por mes;
  - escaladas y si estaban justificadas;
  - retrabajo;
  - reintentos;
  - **silencios** (ejecuciones que no produjeron nada sin avisar).
- **Escalada:** una sola línea con qué hacía, qué tiene y qué necesita. Nunca un bucle de reintentos, una disculpa o una conjetura.
- **Introducción gradual:** un agente a mano → su prueba de éxito → un segundo agente con su archivo de traspaso → el crítico → el umbral → ejecución desatendida → recortar lo que no se ganó su sitio.
- **Autonomía:** que el modelo discrepe por escrito, proponga menos agentes si bastan y nombre el supuesto del que está menos seguro.

## Evidencia en nuestras pruebas

En el proyecto piloto, el subagente `codex-rescue` era un «orquestador que solo reenvía». Además se moría al terminar el subagente, y el proyecto acabó lanzando el companion directamente (F004). La regla de «2 fallos → la tarea vuelve a mí» del proyecto piloto coincide con el límite de reintentos.

## Prácticas extraídas

| ID | Archivo | Tipo |
|---|---|---|
| P-EQU-01 a P-EQU-08 | 09-equipos-de-agentes.md | Nuevas |
| P-SUB-02, P-SUB-03 | 04 | Refuerza |
| P-FLU-08 | 05 | Refuerza (contrato de traspaso) |
| P-API-04 | 07 | Refuerza (modelo caro solo donde el razonamiento cambia el resultado) |
| D-11 | 00 | Nueva |
