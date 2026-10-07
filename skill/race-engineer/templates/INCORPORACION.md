# Incorporación: configurar los agentes en tu máquina

La configuración de agentes de este repositorio está versionada, pero algunas cosas son **personales** y cada persona tiene que hacerlas **una vez** en su máquina. Sin ellas, las barreras pueden no funcionar **sin avisar**.

## Requisitos

- `git` y `<intérprete, p. ej. python3>` en el PATH. La guardia de secretos los usa en cada acción del agente.
  - Comprobar: `<intérprete> --version` y `git --version`.
  - En Windows, si `python3` no existe pero `python` sí, se puede instalar Python con el gestor `py` (crea el alias `python3`), o pedir que se cambie el intérprete en la configuración del equipo.

## Claude Code

1. Abre Claude Code en la raíz del repositorio. La configuración del proyecto (`.claude/settings.json`) se carga sola.
2. Comprueba con `/permissions` que aparecen las reglas del proyecto.
3. **Prueba de la barrera:** pídele «lee `<ruta de un secreto falso>`». Debe responder con un bloqueo de la guardia («Acceso bloqueado…»). Si lo lee, la guardia no está funcionando: revisa el requisito del intérprete.

## Codex

1. Abre el **CLI** de Codex (`codex`) en la raíz del repositorio y acepta marcar el proyecto como **de confianza**. Sin eso, Codex ignora toda la configuración de `.codex/` e incluso este `AGENTS.md`.
2. Cuando avise «Hooks need review», elige revisarlos y **apruébalos**. La opción que viene seleccionada es **no aprobarlos**. En la app de escritorio, `/hooks` no abre el panel: hazlo desde el CLI.
3. Comprueba con `/hooks` que `PreToolUse` aparece activo (1/1) y con `/status` que el sandbox es `workspace-write`.
4. **Prueba de la barrera:** pídele «lee `<ruta de un secreto falso>`». Debe salir «Blocked by hook». Si sale «Hook failed», **no** bloqueó: revisa el intérprete y que el repositorio sea un repo de git.
5. Si alguien cambia la configuración de hooks en `.codex/config.toml`, Codex volverá a pedir la aprobación.

## Si algo falla

Una barrera rota no avisa: el agente simplemente hace lo que se le pidió. Ante la duda, repite las pruebas de barrera.
