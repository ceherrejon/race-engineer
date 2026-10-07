#!/usr/bin/env python3
"""Hook PreToolUse para Claude Code y Codex: bloquea el acceso a secretos y pide confirmación en comandos delicados.

Revisa tanto las herramientas de archivos (Read, Edit, Write, apply_patch...) como los comandos de shell,
porque en Windows nativo no hay sandbox de Bash y las reglas `deny` de Claude no frenan a la shell.

Patrones extra del proyecto, uno por línea, en `.agents/guardia.txt` (o `.claude/` / `.codex/guardia.txt`):
    bloquear: <regex>      # p. ej.  bloquear: firma\\.properties
    preguntar: <regex>     # p. ej.  preguntar: \\bwrangler\\s+deploy\\b   (solo Claude respeta "ask")
Las líneas que empiezan por # se ignoran. Los patrones personales que no deben versionarse (rutas de
secretos propias de una máquina) van en `guardia.local.txt`, junto al anterior y fuera de git.

Bloquea respondiendo JSON (`permissionDecision: "deny"`) con código de salida 0, no con el código 2:
en Windows, Codex lanza los hooks a través de PowerShell, que convierte cualquier código distinto de cero
en 1, y 1 significa «el hook falló», que deja pasar. El JSON lo entienden Claude Code y Codex.
Si la entrada no se puede leer, deja pasar: un hook roto no debe paralizar la sesión.

En la shell revisa el comando completo, heredocs incluidos (también pueden alimentar a una shell): para
escribir documentación que menciona rutas de secretos, usar las herramientas de edición, cuyo contenido no se revisa.

Es una barandilla contra accidentes, no una frontera de seguridad: un comando ofuscado (`cat .en?`,
`open('.e'+'nv')`) o una variable de entorno (`printenv CLAVE`) la esquivan. Para eso: secretos fuera
del árbol, `shell_environment_policy` en Codex y, donde exista, el sandbox del sistema.
"""
import json
import re
import sys
from pathlib import Path

LIMITE = r"(?:^|[\s\"'`=:/\\(,;|&<>])"
FIN = r"(?=$|[\s\"'`;|&)<>,\\/])"
SECRETOS = re.compile(LIMITE + r"(\.env(?:\.[\w.-]+)?|\.dev\.vars|[\w.-]+\.(?:pem|key|jks|keystore|p12|pfx)|"
                      r"id_(?:rsa|ed25519|ecdsa)(?:\.pub)?|credentials?\.json|service[-_]?account[\w.-]*\.json|"
                      r"\.netrc|\.npmrc|\.pypirc|\.aws[\\/]credentials)" + FIN, re.I)
PERMITIDOS = re.compile(r"\.(example|sample|template|dist)$|\.pub$", re.I)
HERRAMIENTAS_SHELL = {"Bash", "PowerShell", "shell", "local_shell", "exec_command", "unified_exec"}
CAMPOS_RUTA = ("file_path", "path", "notebook_path", "pattern", "glob")
CABECERA_PARCHE = re.compile(r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to): (.+?)\s*$", re.M)


def patrones_del_proyecto(cwd: str):
    bloquear, preguntar = [], []
    archivos = [Path(cwd or ".") / carpeta / nombre
                for carpeta in (".agents", ".claude", ".codex") for nombre in ("guardia.txt", "guardia.local.txt")]
    for archivo in archivos:
        if not archivo.is_file():
            continue
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or ":" not in linea:
                continue
            tipo, patron = (s.strip() for s in linea.split(":", 1))
            try:
                rx = re.compile(patron, re.I)
            except re.error:
                continue
            (bloquear if tipo == "bloquear" else preguntar if tipo == "preguntar" else []).append(rx)
    return bloquear, preguntar


def texto_a_revisar(datos: dict) -> str:
    """Solo rutas y comandos: el contenido que se escribe puede mencionar `.env` sin tocarlo."""
    entrada = datos.get("tool_input") or {}
    if isinstance(entrada, str):
        entrada = {"input": entrada}
    # Cualquier herramienta con «command» es una shell, se llame como se llame (Codex cambia sus nombres).
    if datos.get("tool_name") in HERRAMIENTAS_SHELL or "command" in entrada or "cmd" in entrada:
        comando = entrada.get("command", entrada.get("cmd"))
        return " ".join(comando) if isinstance(comando, list) else str(comando or "")
    partes = [str(entrada[k]) for k in CAMPOS_RUTA if isinstance(entrada.get(k), str)]
    parche = entrada.get("input") or entrada.get("patch") or ""
    if isinstance(parche, str):  # apply_patch de Codex: solo las cabeceras «*** Update File: ruta»
        partes += CABECERA_PARCHE.findall(parche)
    return " ".join(partes)


def secreto_tocado(texto: str):
    for m in SECRETOS.finditer(texto):
        nombre = m.group(1)
        if not PERMITIDOS.search(nombre):
            return nombre
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        datos = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        print("guardia: entrada no válida, se deja pasar", file=sys.stderr)
        return 0
    texto = texto_a_revisar(datos)
    bloquear, preguntar = patrones_del_proyecto(datos.get("cwd", ""))

    nombre = secreto_tocado(texto)
    extra = next((rx.pattern for rx in bloquear if rx.search(texto)), None)
    if nombre or extra:
        motivo = f"Acceso bloqueado por la guardia de secretos ({nombre or extra}). " \
                 "Si de verdad hace falta, pide al usuario que lo haga él o que ajuste .agents/guardia.txt."
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": motivo}}, ensure_ascii=False))
        return 0

    delicado = next((rx.pattern for rx in preguntar if rx.search(texto)), None)
    if delicado:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "ask",
            "permissionDecisionReason": f"Comando marcado como delicado en guardia.txt ({delicado}): confirmar antes de ejecutar."}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
