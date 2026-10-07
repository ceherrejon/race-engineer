# Formato del informe de auditoría

Un solo informe, con este orden. Breve en lo que está bien y concreto en lo que falla.

```markdown
# Auditoría de <proyecto> · <fecha>

## Supuestos
- Herramientas: <Claude Code x.y / Codex x.y> · Sistema: <…> · Stack: <…>
- Reparto: <instrucciones comunes | Claude dirige y Codex ejecuta | …>
- Alcance: <proyecto; nivel de usuario solo informativo | rutas concretas>
- Herramientas oficiales ejecutadas: <prompt-audit, skill-doctor, …> (o por qué no)
<Si un supuesto está mal, se corrige y se repite la auditoría.>

## Lo más importante
1. <hallazgo de mayor impacto, en una frase, y su consecuencia>
2. <…>
3. <…>

## Por capa
Estados:
- ✓ verificado y bien;
- ⚠ mejorable;
- ✗ falla;
- ⏸ pendiente (exige ejecutar o un comando del usuario);
- n. a.

| Capa | Estado | Resumen |
|---|---|---|
| 1 Instrucciones | ✓ / ⚠ / ✗ / ⏸ / n. a. | <una línea> |
| … | | |

## Hallazgos
Máximo 1–2 por capa, contando las transversales T1 y T2 como capas propias. Se amplían si el usuario lo pide. Ordenados por impacto. Un hallazgo que cruza capas se pone en la principal y se menciona en las otras:

### <ID de la lista> · <título>
- **Evidencia:** `archivo:línea`, salida de un comando o dato del inventario
- **Por qué importa:** <consecuencia concreta en este proyecto> (ref. <práctica>)
- **Propuesta:** <cambio exacto: diff, archivo nuevo o ajuste de configuración>
- **Confianza:** alta / media / baja

## Nivel de usuario (solo informativo)
- <hallazgos en ~/.claude o ~/.codex; no se tocan sin pedirlo>

## Necesita tu decisión
- <conflictos que el historial no ordena, cambios que debilitan una regla de seguridad, reparto Claude/Codex…>

## Anexo · prompt-audit
<informe completo de `claude-api prompt-audit`, si se ejecutó>

## Cómo verificar después de aplicar
- <prueba de barreras, /context o /status, una tarea corta de prueba…>
```

**Reglas:**
- Cada hallazgo cita su evidencia y su práctica. Lo que no tiene evidencia va como pregunta en «Necesita tu decisión», no como hallazgo.
- No se proponen cambios por longitud sola: se mueve contenido, no se borra contexto.
- Si una capa está bien, una línea basta.
- No se aplica nada al escribir el informe: los cambios se aplican después y solo los que el usuario apruebe.
